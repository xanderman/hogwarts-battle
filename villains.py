from functools import reduce

import curses
import operator
import random

class VillainDeck(object):
    def __init__(self, window, game_num):
        self._window = window
        self._init_window()
        self._pad = curses.newpad(100, 100)
        self._deck = reduce(operator.add, VILLAINS[:game_num])
        self._max = MAX_VILLAINS[game_num]
        self._voldemort = None
        if game_num == 5:
            self._voldemort = GameFiveVoldemort()
        elif game_num == 6:
            self._voldemort = GameSixVoldemort()
        elif game_num == 7:
            self._voldemort = GameSevenVoldemort()

        random.shuffle(self._deck)
        self.current = []

    def _init_window(self):
        self._window.box()
        self._window.addstr(0, 1, "Dark Arts Deck")
        self._window.noutrefresh()
        beg = self._window.getbegyx()
        self._pad_start_line = beg[0] + 1
        self._pad_start_col = beg[1] + 1
        end = self._window.getmaxyx()
        self._pad_end_line = self._pad_start_line + end[0] - 3
        self._pad_end_col = self._pad_start_col + end[1] - 3

    def display_state(self, resize=False, size=None):
        if resize:
            self._window.resize(*size)
            self._window.clear()
            self._init_window()
        self._window.clear()
        self._window.box()
        left_str = f"({len(self._deck)}"
        if self._voldemort is not None:
            left_str += " + Voldemort"
        self._window.addstr(0, 1, f"Villains {left_str} left)")
        self._window.noutrefresh()

        self._pad.clear()
        for i, villain in enumerate(self.current):
            villain.display_state(self._pad, i)
        if self.voldemort_active():
            self._display_voldemort()
        self._pad.noutrefresh(0,0, self._pad_start_line,self._pad_start_col, self._pad_end_line,self._pad_end_col)

    def _display_voldemort(self):
        self._pad.addstr("Voldemort:")
        if self.voldemort_vulnerable():
            self._pad.addstr(" *vulnerable*\n", curses.A_BOLD | curses.color_pair(1))
        else:
            self._pad.addstr(" *invulnerable*\n", curses.A_BOLD | curses.color_pair(2))
        self._voldemort.display_state(self._pad, 'v')

    def play_turn(self, game):
        game.log("-----Villain phase-----")
        self.all_villains.play_turn(game)

    def reveal(self, game):
        for villain in self.all_villains:
            villain.took_damage = False
        while len(self.current) < self._max and len(self._deck) > 0:
            death_eaters = sum(1 for v in game.villain_deck.current if v.name == "Death Eater")
            villain = self._deck.pop()
            self.current.append(villain)
            villain.on_reveal(game)
            if death_eaters > 0:
                game.log(f"Death Eater (x{death_eaters}): Villain revealed, ALL heroes lose {death_eaters}💜")
                game.heroes.all_heroes.remove_health(game, death_eaters)

    def voldemort_active(self):
        return self._voldemort is not None and len(self._deck) == 0

    def voldemort_vulnerable(self):
        return self.voldemort_active() and len(self.current) == 0

    @property
    def choices(self):
        choices = [str(i) for i in range(len(self.current))]
        if self.voldemort_active():
            choices.append('v')
        return choices

    def __len__(self):
        voldemort = 1 if self._voldemort is not None else 0
        return len(self._deck) + len(self.current) + voldemort

    def __getitem__(self, key):
        if key == 'v':
            return self._voldemort
        return self.current[int(key)]

    @property
    def all_villains(self):
        if self.voldemort_active():
            return VillainList(*self.current, self._voldemort)
        return VillainList(*self.current)


class VillainList(list):
    def __init__(self, *args):
        super().__init__(args)

    def __getattr__(self, attr):
        def f(game, *args, **kwargs):
            for villain in self:
                getattr(villain, attr)(game, *args, **kwargs)
        return f

    def effect(self, game, effect=lambda game, villain: None):
        for villain in self:
            effect(game, villain)


class Villain(object):
    def __init__(self, name, description, reward_desc, health, effect=lambda game: None, on_reveal=lambda game: None,
                 reward=lambda game: None, on_stun=lambda game: None, on_recover_from_stun=lambda game:None):
        self.name = name
        self.description = description
        self.reward_desc = reward_desc
        self._health = health
        self.effect = effect
        self.on_reveal = on_reveal
        self._reward = reward
        self._on_stun = on_stun
        self._on_recover_from_stun = on_recover_from_stun

        self._damage = 0
        self.took_damage = False
        self._stunned = False
        self._stunned_by = None

    def display_state(self, window, i):
        window.addstr(f"{i}: {self.name} ({self._damage}↯/{self._health}💜)")
        if self._stunned:
            window.addstr(" *stunned*", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f"\n     {self.description}")
        window.addstr(f"\n     Reward: {self.reward_desc}\n")

    def play_turn(self, game):
        if self._stunned:
            game.log(f"Villain: {self.name} ({self._damage}/{self._health}) is stunned!")
            if game.heroes.active_hero == self._stunned_by:
                game.log(f"{self.name} was stunned by {self._stunned_by.name}, so recovers")
                self._stunned = False
                self._stunned_by = None
                self._on_recover_from_stun(game)
            return
        game.log(f"Villain: {self}")
        self.effect(game)

    def __str__(self):
        return f"{self.name} ({self._damage}/{self._health}), {self.description}"

    def add_damage(self, game, amount=1):
        self.took_damage = True
        self._damage += amount
        if self._damage >= self._health:
            self.reward(game)
            if self == game.villain_deck._voldemort:
                game.villain_deck._voldemort = None
            else:
                game.villain_deck.current.remove(self)
            return True
        return False

    def remove_damage(self, game, amount=1):
        self._damage -= amount
        if self._damage < 0:
            self._damage = 0

    def stun(self, game):
        self._stunned = True
        self._stunned_by = game.heroes.active_hero
        self._on_stun(game)

    def reward(self, game):
        game.log(f"{self.name} defeated! {self.reward_desc}")
        self._reward(game)


class Draco(Villain):
    def __init__(self):
        super().__init__("Draco Malfoy", "When 💀 is added, active hero loses 2💜",
                         "Remove 1💀", 6,
                         on_reveal=lambda game: game.locations.add_control_callback(game, self),
                         reward=self.__reward)

    def control_callback(self, game, amount):
        if amount < 1:
            return
        if self._stunned:
            game.log(f"{self.name} is stunned! No penalty for added 💀")
            return
        game.log(f"{self.name}: {amount}💀 added, {game.heroes.active_hero.name} loses 2💜 for each")
        for _ in range(amount):
            game.heroes.active_hero.remove_health(game, 2)

    def __reward(self, game):
        game.locations.remove_control_callback(game, self)
        game.locations.remove_control(game)


class Crabbe(Villain):
    def __init__(self):
        super().__init__("Crabbe & Goyle", "When forced to discard, lose 1💜",
                         "ALL heroes draw 1 card", 5,
                         on_reveal=lambda game: game.heroes.add_discard_callback(game, self),
                         reward=self.__reward)

    def discard_callback(self, game, hero):
        if self._stunned:
            game.log(f"{self.name} is stunned! No penalty for discard")
            return
        game.log(f"{self.name}: {hero.name} discarded, so loses 1💜")
        hero.remove_health(game, 1)

    def __reward(self, game):
        game.heroes.remove_discard_callback(game, self)
        game.heroes.all_heroes.draw(game)


game_one_villains = [
    Draco(),
    Crabbe(),
    Villain("Quirinus Quirrell", "Active hero loses 1💜",
            "ALL heroes gain 1💜 and 1💰", 6,
            effect=lambda game: game.heroes.active_hero.remove_health(game),
            reward=lambda game: game.heroes.all_heroes.add(game, influence=1, hearts=1)),
]

class Lucius(Villain):
    def __init__(self):
        super().__init__("Lucius Malfoy", "When 💀 is added, all villains heal 1↯",
                         "ALL heroes gain 1💰, remove 1💀", 7,
                         on_reveal=lambda game: game.locations.add_control_callback(game, self),
                         reward=self.__reward)

    def control_callback(self, game, amount):
        if amount < 1:
            return
        if self._stunned:
            game.log(f"{self.name} is stunned! No penalty for added 💀")
            return
        game.log(f"{self.name}: {amount}💀 added, all Villains heal 1↯ for each")
        for _ in range(amount):
            game.villain_deck.all_villains.remove_damage(game, 1)

    def __reward(self, game):
        game.locations.remove_control_callback(game, self)
        game.heroes.all_heroes.add_influence(game, 1)
        game.locations.remove_control(game)

def basilisk_reward(game):
    game.heroes.basilisk_defeated(game)
    game.heroes.all_heroes.draw(game)
    game.locations.remove_control(game)

def riddle_effect(game):
    hero = game.heroes.active_hero
    allies = sum(1 for card in hero._hand if card.is_ally())
    if allies == 0:
        game.log(f"{hero.name} has no allies in hand, safe!")
        return
    game.log(f"{hero.name} has {allies} allies in hand")
    for _ in range(allies):
        choices = ['h'] + [str(i) for i in range(len(hero._hand))]
        choice = game.input(f"Choose a card for {hero.name} to discard or (h) to lose 2💜: ", choices)
        if choice == 'h':
            hero.remove_health(game, 2)
        else:
            choice = int(choice)
            hero.discard(game, choice)

def riddle_reward(game, hero):
    allies = [card for card in hero._discard if card.is_ally()]
    if len(allies) == 0:
        game.log(f"{hero.name} has no allies in discard, gaining 2💜")
        hero.add_health(game, 2)
        return
    game.log(f"Allies in {hero.name}'s discard:")
    for i, ally in enumerate(allies):
        game.log(f" {i}: {ally}")
    choices = ['h'] + [str(i) for i in range(len(allies))]
    choice = game.input(f"Choose an ally for {hero.name} to take or (h) to gain 2💜: ", choices)
    if choice == 'h':
        hero.add_health(game, 2)
        return
    ally = allies[int(choice)]
    hero._discard.remove(ally)
    hero._hand.append(ally)

game_two_villains = [
    Lucius(),
    # TODO also creature
    Villain("Basilisk", "Heroes cannot draw extra cards",
            "ALL heroes draw a card; remove 1💀", 8,
            on_reveal=lambda game: game.heroes.basilisk_revealed(game),
            reward=basilisk_reward, on_stun=lambda game: game.heroes.basilisk_defeated(game),
            on_recover_from_stun=lambda game: game.heroes.basilisk_revealed(game)),
    Villain("Tom Riddle", "For each Ally in hand, lose 2💜 or discard",
            "ALL heroes gain 2💜 or take Ally from discard", 6,
            effect=riddle_effect, reward=lambda game: game.heroes.all_heroes.effect(game, riddle_reward)),
]

def dementor_reward(game):
    game.heroes.all_heroes.add_health(game, 2)
    game.locations.remove_control(game)

def pettigrew_effect(game):
    hero = game.heroes.active_hero
    card = hero.reveal_top_card(game)
    if card is None:
        game.log(f"{hero.name} has no cards left to reveal")
        return
    game.log(f"{hero.name} revealed {card}")
    if card.cost >= 1:
        game.heroes.active_hero.discard_top_card(game)
        game.locations.add_control(game)

def pettigrew_reward(game):
    game.locations.remove_control(game)
    game.heroes.all_heroes.effect(game, pettigrew_per_hero)

def pettigrew_per_hero(game, hero):
    spells = [card for card in hero._discard if card.is_spell()]
    if len(spells) == 0:
        game.log(f"{hero.name} has no spells in discard")
        return
    if len(spells) == 1:
        spell = spells[0]
        game.log(f"{hero.name} has only one spell in discard, taking {spell}")
        hero._discard.remove(spell)
        hero._hand.append(spell)
        return
    game.log(f"Spells in {hero.name}'s discard:")
    for i, spell in enumerate(spells):
        game.log(f" {i}: {spell}")
    # TODO allow to skip?
    choice = game.input(f"Choose a spell for {hero.name} to take: ", range(len(spells)))
    spell = spells[int(choice)]
    hero._discard.remove(spell)
    hero._hand.append(spell)

game_three_villains = [
    # TODO also creature
    Villain("Dementor", "Active hero loses 2💜",
            "ALL heroes gain 2💜; remove 1💀", 8,
            effect=lambda game: game.heroes.active_hero.remove_health(game, 2),
            reward=dementor_reward),
    Villain("Peter Pettigrew", "Reveal top card of deck, if costs 1💰 or more, discard and add 1💀",
            "ALL heroes may take Spell from discard; remove 1💀", 7,
            effect=pettigrew_effect, reward=pettigrew_reward),
]

def death_eater_reward(game):
    game.heroes.all_heroes.add_health(game, 1)
    game.locations.remove_control(game)

def crouch_reward(game):
    game.locations.allow_remove_control(game)
    game.locations.remove_control(game, 2)

game_four_villains = [
    # TODO villain revealed callback
    Villain("Death Eater", "If Morsmordre or new Villain revealed, ALL Heroes lose 1💜",
            "ALL heroes gain 1💜; remove 1💀", 7,
            reward=death_eater_reward),
    Villain("Barty Crouch Jr.", "Heroes cannot remove 💀", "Remove 2💀", 7,
            on_reveal=lambda game: game.locations.disallow_remove_control(game),
            reward=crouch_reward, on_stun=lambda game: game.locations.allow_remove_control(game),
            on_recover_from_stun=lambda game: game.locations.disallow_remove_control(game)),
]

class Umbridge(Villain):
    def __init__(self):
        super().__init__("Dolores Umbridge", "If acquire card with cost 4💰 or more, lose 1💜",
                         "ALL heroes gain 1💰 and 2💜", 7,
                         on_reveal=lambda game: game.heroes.add_acquire_callback(game, self),
                         reward=self.__reward),

    def acquire_callback(self, game, hero, card):
        if card.cost >= 4:
            if self._stunned:
                game.log(f"{self.name} is stunned! No penalty for acquire")
                return
            game.log(f"{self.name}: {game.heroes.active_hero.name} acquired {card.name}, so loses 1💜")
            hero.remove_health(game, 1)

    def __reward(self, game):
        game.heroes.remove_acquire_callback(game, self)
        game.heroes.all_heroes.add(game, influence=1, hearts=2)

game_five_villains = [
    Umbridge(),
    Villain("Death Eater", "If Morsmordre or new Villain revealed, ALL Heroes lose 1💜",
            "ALL heroes gain 1💜; remove 1💀", 7,
            reward=death_eater_reward),
]

class GameFiveVoldemort(Villain):
    # TODO can't be damaged until all other villains defeated
    def __init__(self):
        super().__init__("Lord Voldemort", "Active hero loses 1💜 and discards a card",
                         "You win!", 10, effect=lambda game: game.heroes.active_hero.add(game, hearts=-1, cards=-1))

def bellatrix_reward(game):
    game.locations.remove_control(game, 2)
    game.heroes.all_heroes.effect(game, bellatrix_per_hero)

def bellatrix_per_hero(game, hero):
    items = [card for card in hero._discard if card.is_item()]
    if len(items) == 0:
        game.log(f"{hero.name} has no items in discard")
        return
    game.log(f"Items in {hero.name}'s discard:")
    for i, item in enumerate(items):
        game.log(f" {i}: {item}")
    # TODO allow to skip?
    choice = game.input(f"Choose an item for {hero.name} to take: ", range(len(items)))
    item = items[int(choice)]
    hero._discard.remove(item)
    hero._hand.append(item)

def greyback_reward(game):
    game.heroes.greyback_defeated(game)
    game.heroes.all_heroes.add_health(game, 3)
    game.locations.remove_control(game, 2)

game_six_villains = [
    Villain("Bellatrix Lestrange", "Reveal an additional Dark Arts event each turn",
            "ALL heroes may take Item from discard; remove 2💀", 9,
            effect=lambda game: game.dark_arts_deck.play(game, 1),
            reward=bellatrix_reward),
    Villain("Fenrir Greyback", "Heroes cannot gain 💜", "ALL heroes gain 3💜, remove 2💀", 8,
            on_reveal=lambda game: game.heroes.greyback_revealed(game),
            reward=greyback_reward, on_stun=lambda game: game.heroes.greyback_defeated(game),
            on_recover_from_stun=lambda game: game.heroes.greyback_revealed(game)),
]

class GameSixVoldemort(Villain):
    def __init__(self):
        super().__init__("Lord Voldemort", "Roll the Slytherin die",
                         "You win!", 15, effect=self.__effect)

    def __effect(self, game):
        die_result = random.choice("↯↯↯💰💜🃏")
        if game.heroes.active_hero._proficiency.can_reroll_house_dice and game.input(f"Rolled {die_result}, (a)ccept or (r)eroll?", "ar") == "r":
            die_result = random.choice("↯↯↯💰💜🃏")
        if die_result == "↯":
            game.log("Rolled ↯, ALL heroes lose 1💜")
            game.heroes.all_heroes.remove_health(game, 1)
        elif die_result == "💰":
            game.log("Rolled 💰, adding 1💀 to the location")
            game.locations.add_control(game)
        elif die_result == "💜":
            game.log("Rolled 💜, ALL Villains heal 1↯")
            game.villain_deck.all_villains.remove_damage(game, 1)
        elif die_result == "🃏":
            game.log("Rolled 🃏, ALL heroes discard a card")
            game.heroes.all_heroes.choose_and_discard(game)

game_seven_villains = [
]

def GameSevenVoldemort(Villain):
    def __init__(self):
        super().__init__("Lord Voldemort", "Add 1💀; each time 💀 is removed, ALL heroes lose 1💜",
                         "You win!", 20, effect=lambda game: game.locations.add_control(game),
                         on_reveal=lambda game: game.locations.add_control_callback(game, self),
                         reward=lambda game: game.locations.remove_control_callback(game, self))

    def control_callback(self, game, amount):
        if amount > -1:
            return
        if self._stunned:
            game.log(f"{self.name} is stunned! No penalty for removed 💀")
            return
        game.log(f"{self.name}: 💀 removed, ALL heroes lose 1💜 for each")
        for _ in range(-amount):
            game.heroes.all_heroes.remove_health(game, 1)

VILLAINS = [
    game_one_villains,
    game_two_villains,
    game_three_villains,
    game_four_villains,
    game_five_villains,
    game_six_villains,
    game_seven_villains,
]

MAX_VILLAINS = [-1, 1, 1, 2, 2, 3, 3, 3]
