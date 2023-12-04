from functools import reduce

import curses
import operator
import random

import constants

class VillainDeck(object):
    def __init__(self, window, game_num, encounters):
        self._window = window
        self._init_window()
        self._pad = curses.newpad(100, 100)
        self._deck = build_deck(game_num, encounters)
        self._discard = []
        self._max = max_villains(game_num)
        self._voldemort = build_voldemort(game_num)
        self._rewards_allowed = True

        random.shuffle(self._deck)
        self.current = []

    def _init_window(self):
        self._window.box()
        self._window.addstr(0, 1, "Villains")
        self._window.noutrefresh()
        beg = self._window.getbegyx()
        self._pad_start_line = beg[0] + 1
        self._pad_start_col = beg[1] + 1
        end = self._window.getmaxyx()
        self._pad_end_line = self._pad_start_line + end[0] - 3
        self._pad_end_col = self._pad_start_col + end[1] - 3

    def display_state(self, game, resize=False, size=None):
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
            self._display_voldemort(game)
        self._pad.noutrefresh(0,0, self._pad_start_line,self._pad_start_col, self._pad_end_line,self._pad_end_col)

    def _display_voldemort(self, game):
        self._pad.addstr("Voldemort:")
        if self.voldemort_vulnerable(game):
            self._pad.addstr(" *vulnerable*\n", curses.A_BOLD | curses.color_pair(1))
        else:
            self._pad.addstr(" *invulnerable*\n", curses.A_BOLD | curses.color_pair(2))
        self._voldemort.display_state(self._pad, 'v')

    def play_turn(self, game):
        game.log("-----Villain phase-----")
        self.all.play_turn(game)

    def reveal(self, game):
        self.all.end_turn(game)
        voldemort_was_active = self.voldemort_active()
        while len(self.current) < self._max and len(self._deck) > 0:
            death_eaters = sum(1 for v in game.villain_deck.current if v.name == "Death Eater" and not v._stunned)
            villain = self._deck.pop()
            self.current.append(villain)
            game.log(f"Revealed {villain.type_name}: {villain.name}")
            villain._on_reveal(game)
            if death_eaters > 0 and villain.is_villain:
                game.log(f"Death Eater (x{death_eaters}): Villain revealed, ALL heroes lose {death_eaters}{constants.HEART}")
                game.heroes.all_heroes.remove_hearts(game, death_eaters)
        if self.voldemort_active() and not voldemort_was_active:
            game.log("Voldemort revealed!")
            self._voldemort._on_reveal(game)
            if death_eaters > 0:
                game.log(f"Death Eater (x{death_eaters}): Villain revealed, ALL heroes lose {death_eaters}{constants.HEART}")
                game.heroes.all_heroes.remove_hearts(game, death_eaters)

    def voldemort_active(self):
        return self._voldemort is not None and len(self._deck) == 0

    def voldemort_vulnerable(self, game):
        return self.voldemort_active() and len(self.current) == 0 and (game.encounters is None or game.encounters.all_complete)

    def disallow_rewards(self):
        self._rewards_allowed = False

    def allow_rewards(self):
        self._rewards_allowed = True

    def last_defeated_villain_reward(self, game):
        if len(self._discard) == 0:
            return
        villain = self._discard[-1]
        game.log(f"Last defeated villain: {villain.name}, Reward: {villain.reward_desc}")
        villain.reward(game)

    @property
    def choices(self):
        choices = [str(i) for i in range(len(self.current))]
        if self.voldemort_active():
            choices.append('v')
        return choices

    @property
    def villain_choices(self):
        choices = [str(i) for i in range(len(self.current)) if self.current[i].is_villain]
        if self.voldemort_active():
            # Voldemort is always a Villain
            choices.append('v')
        return choices

    @property
    def creature_choices(self):
        # Voldemort is never a creature
        return [str(i) for i in range(len(self.current)) if self.current[i].is_creature]

    def __len__(self):
        voldemort = 1 if self._voldemort is not None else 0
        return len(self._deck) + len(self.current) + voldemort

    def __getitem__(self, key):
        if key == 'v':
            return self._voldemort
        return self.current[int(key)]

    @property
    def all(self):
        if self.voldemort_active():
            return VillainList(*self.current, self._voldemort)
        return VillainList(*self.current)

    @property
    def all_villains(self):
        villains = filter(lambda foe: foe.is_villain, self.current)
        if self.voldemort_active():
            return VillainList(*villains, self._voldemort)
        return VillainList(*villains)

    @property
    def all_creatures(self):
        creatures = filter(lambda foe: foe.is_creature, self.current)
        return VillainList(*creatures)


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


def max_villains(game_num):
    if game_num == 1 or game_num == 2:
        return 1
    if game_num == 3 or game_num == 4:
        return 2
    return 3


def build_deck(game_num, encounters):
    if isinstance(game_num, int):
        return [v() for villains in BASE_VILLAINS[:game_num] for v in villains]
    total_villains = VILLAIN_DECK_SIZE[game_num]
    names = set(encounters.required_villains())
    available = list(VILLAINS_BY_NAME.keys())
    while len(names) < total_villains:
        # TODO: there are two Death Eaters
        names.add(random.choice(available))
    return [VILLAINS_BY_NAME[name]() for name in names]

VILLAINS_BY_NAME = {}


def build_voldemort(game_num):
    if game_num == 5 or game_num == "m1":
        return GameFiveVoldemort()
    if game_num == 6 or game_num == "m2":
        return GameSixVoldemort()
    if game_num == 7 or game_num == "m3":
        return GameSevenVoldemort()
    if game_num == "m4":
        # TODO: add m4 voldemort
        return None
    return None


class Foe(object):
    def __init__(self, name, description, reward_desc, hearts=0, cost=0):
        self.name = name
        self.description = description
        self.reward_desc = reward_desc
        self._hearts = hearts
        self._cost = cost

        self._damage = 0
        self.took_damage = False
        self._influence = 0
        self.took_influence = False
        self._stunned = False
        self._stunned_by = None

    def display_state(self, window, i):
        window.addstr(f"{i}: {self.name}")
        if self._hearts > 0:
            window.addstr(f" ({self._damage}/{self._hearts}{constants.HEART})")
        if self._cost > 0:
            window.addstr(f" ({self._influence}/{self._cost}{constants.INFLUENCE})")
        window.addstr(f" {self.type_name}", curses.A_BOLD)
        if self._stunned:
            window.addstr(" *stunned*", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f"\n     {self.description}")
        window.addstr(f"\n     Reward: {self.reward_desc}\n")

    def play_turn(self, game):
        if self._stunned:
            game.log(f"Villain: {self.name} ({self._damage}/{self._hearts}) is stunned!")
            if game.heroes.active_hero == self._stunned_by:
                game.log(f"{self.name} was stunned by {self._stunned_by.name}, so recovers")
                self._stunned = False
                self._stunned_by = None
                self._on_recover_from_stun(game)
            return
        game.log(f"Villain: {self}")
        self._effect(game)

    def _on_reveal(self, game):
        pass

    def _on_stun(self, game):
        pass

    def _on_recover_from_stun(self, game):
        pass

    def _effect(self, game):
        raise ValueError(f"Programmer Error! Forgot to implement effect for {self.name}")

    def end_turn(self, game):
        self.took_damage = False
        self.took_influence = False

    def __str__(self):
        return f"{self.name}: {self.description}"

    @property
    def is_villain(self):
        return False

    @property
    def is_creature(self):
        return False

    @property
    def type_name(self):
        return "ERROR! Forgot to override type_name in subclass!"

    def add_damage(self, game):
        if self._hearts == 0:
            raise Exception(f"Prgammer Error! {self.name} cannot take damage!")
        self.took_damage = True
        self._damage += 1
        if self._defeated:
            self._apply_defeat(game)
            return True
        return False

    def remove_damage(self, game, amount=1):
        self._damage -= amount
        if self._damage < 0:
            self._damage = 0

    def add_influence(self, game):
        if self._cost == 0:
            raise Exception(f"Programmer Error! {self.name} cannot take influence!")
        if self.took_influence:
            raise Exception(f"Programmer Error! {self.name} cannot take influence twice!")
        self.took_influence = True
        self._influence += 1
        if self._defeated:
            self._apply_defeat(game)
            return True
        return False

    def remove_influence(self, game, amount=1):
        self._influence -= amount
        if self._influence < 0:
            self._influence = 0

    def stun(self, game):
        self._stunned = True
        self._stunned_by = game.heroes.active_hero
        self._on_stun(game)

    @property
    def _defeated(self):
        return self._damage >= self._hearts and self._influence >= self._cost

    def _apply_defeat(self, game):
        self.remove_callbacks(game)
        if game.villain_deck._rewards_allowed:
            self.reward(game)
        else:
            # TODO: rewards that remove callbacks need to be fixed
            game.log(f"{self.name} defeated, but rewards are not allowed!")
        if self == game.villain_deck._voldemort:
            game.villain_deck._voldemort = None
        else:
            game.villain_deck.current.remove(self)
        game.villain_deck._discard.append(self)

    def remove_callbacks(self, game):
        pass

    def reward(self, game):
        game.log(f"{self.name} defeated! {self.reward_desc}")
        self._reward(game)

    def _reward(self, game):
        raise ValueError(f"Programmer Error! Forgot to implement reward for {self.name}")


class Villain(Foe):
    @property
    def is_villain(self):
        return True

    @property
    def type_name(self):
        return "Villain"


class Creature(Foe):
    @property
    def is_creature(self):
        return True

    @property
    def type_name(self):
        return "Creature"


class VillainCreature(Foe):
    @property
    def is_villain(self):
        return True

    @property
    def is_creature(self):
        return True

    @property
    def type_name(self):
        return "Villain-Creature"


class Draco(Villain):
    def __init__(self):
        super().__init__(
                "Draco Malfoy",
                f"When {constants.CONTROL} is added, active hero loses 2{constants.HEART}",
                f"Remove 1{constants.CONTROL}",
                hearts=6)

    def _on_reveal(self, game):
        game.locations.add_control_callback(game, self)

    def _effect(self, game):
        pass

    def control_callback(self, game, amount):
        if amount < 1:
            return
        if self._stunned:
            game.log(f"{self.name} is stunned! No penalty for added {constants.CONTROL}")
            return
        game.log(f"{self.name}: {amount}{constants.CONTROL} added, {game.heroes.active_hero.name} loses 2{constants.HEART} for each")
        for _ in range(amount):
            game.heroes.active_hero.remove_hearts(game, 2)

    def remove_callbacks(self, game):
        game.locations.remove_control_callback(game, self)

    def _reward(self, game):
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Draco Malfoy"] = Draco


class Crabbe(Villain):
    def __init__(self):
        super().__init__(
                "Crabbe & Goyle",
                f"When forced to discard, lose 1{constants.HEART}",
                "ALL heroes draw 1 card",
                hearts=5)

    def _on_reveal(self, game):
        game.heroes.add_discard_callback(game, self)

    def _effect(self, game):
        pass

    def discard_callback(self, game, hero):
        if self._stunned:
            game.log(f"{self.name} is stunned! No penalty for discard")
            return
        game.log(f"{self.name}: {hero.name} discarded, so loses 1{constants.HEART}")
        hero.remove_hearts(game, 1)

    def remove_callbacks(self, game):
        game.heroes.remove_discard_callback(game, self)

    def _reward(self, game):
        game.heroes.all_heroes.draw(game)

VILLAINS_BY_NAME["Crabbe & Goyle"] = Crabbe


class Quirrel(Villain):
    def __init__(self):
        super().__init__(
                "Quirinus Quirrell",
                f"Active hero loses 1{constants.HEART}",
                f"ALL heroes gain 1{constants.HEART} and 1{constants.INFLUENCE}",
                hearts=6)

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 1)

    def _reward(self, game):
        game.heroes.all_heroes.add(game, influence=1, hearts=1)

VILLAINS_BY_NAME["Quirinus Quirrell"] = Quirrel


game_one_villains = [
    Draco,
    Crabbe,
    Quirrel,
]


class Lucius(Villain):
    def __init__(self):
        super().__init__(
                "Lucius Malfoy",
                f"When {constants.CONTROL} is added, all villains heal 1{constants.DAMAGE}",
                f"ALL heroes gain 1{constants.INFLUENCE}, remove 1{constants.CONTROL}",
                hearts=7)

    def _on_reveal(self, game):
        game.locations.add_control_callback(game, self)

    def _effect(self, game):
        pass

    def control_callback(self, game, amount):
        if amount < 1:
            return
        if self._stunned:
            game.log(f"{self.name} is stunned! No penalty for added {constants.CONTROL}")
            return
        game.log(f"{self.name}: {amount}{constants.CONTROL} added, all Villains heal 1{constants.DAMAGE} for each")
        for _ in range(amount):
            game.villain_deck.all_villains.remove_damage(game, 1)

    def remove_callbacks(self, game):
        game.locations.remove_control_callback(game, self)

    def _reward(self, game):
        game.heroes.all_heroes.add_influence(game, 1)
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Lucius Malfoy"] = Lucius


class Basilisk(VillainCreature):
    def __init__(self):
        super().__init__(
                "Basilisk",
                "Heroes cannot draw extra cards",
                f"ALL heroes gain 1{constants.INFLUENCE}, remove 1{constants.CONTROL}",
                hearts=8)

    def _on_reveal(self, game):
        game.heroes.disallow_drawing(game)

    def _on_stun(self, game):
        game.heroes.allow_drawing(game)

    def _on_recover_from_stun(self, game):
        game.heroes.disallow_drawing(game)

    def _effect(self, game):
        pass

    def remove_callbacks(self, game):
        game.heroes.allow_drawing(game)

    def _reward(self, game):
        game.heroes.all_heroes.draw(game)
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Basilisk"] = Basilisk


class TomRiddle(Villain):
    def __init__(self):
        super().__init__(
                "Tom Riddle",
                f"For each Ally in hand, lose 2{constants.HEART} or discard a card",
                f"ALL heroes gain 2{constants.HEART} or take Ally from discard",
                hearts=6)

    def _effect(self, game):
        hero = game.heroes.active_hero
        allies = sum(1 for card in hero._hand if card.is_ally())
        if allies == 0:
            game.log(f"{hero.name} has no allies in hand, safe!")
            return
        if hero.is_stunned:
            game.log(f"{hero.name} is stunned and can't lose {constants.HEART}. No penalty for allies in hand!")
            return
        game.log(f"{hero.name} has {allies} allies in hand")
        for _ in range(allies):
            choices = ['h'] + [str(i) for i in range(len(hero._hand))]
            choice = game.input(f"Choose a card for {hero.name} to discard or (h) to lose 2{constants.HEART}: ", choices)
            if choice == 'h':
                hero.remove_hearts(game, 2)
            else:
                hero.discard(game, int(choice))

    def _reward(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        allies = [card for card in hero._discard if card.is_ally()]
        if len(allies) == 0:
            game.log(f"{hero.name} has no allies in discard, gaining 2{constants.HEART}")
            hero.add_hearts(game, 2)
            return
        game.log(f"Allies in {hero.name}'s discard:")
        for i, ally in enumerate(allies):
            game.log(f" {i}: {ally}")
        choices = ['h'] + [str(i) for i in range(len(allies))]
        choice = game.input(f"Choose an ally for {hero.name} to take or (h) to gain 2{constants.HEART}: ", choices)
        if choice == 'h':
            hero.add_hearts(game, 2)
            return
        ally = allies[int(choice)]
        hero._discard.remove(ally)
        hero._hand.append(ally)

VILLAINS_BY_NAME["Tom Riddle"] = TomRiddle


game_two_villains = [
    Lucius,
    Basilisk,
    TomRiddle,
]


class Dementor(VillainCreature):
    def __init__(self):
        super().__init__(
                "Dementy-whatsit",
                f"Active hero loses 2{constants.HEART}",
                f"ALL heroes gain 2{constants.HEART}; remove 1{constants.CONTROL}",
                hearts=8)

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 2)

    def _reward(self, game):
        game.heroes.all_heroes.add_hearts(game, 2)
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Dementor"] = Dementor


class PeterPettigrew(Villain):
    def __init__(self):
        super().__init__(
                "Peter Pettigrew",
                f"Reveal top card of deck, if costs 1{constants.INFLUENCE} or more, discard and add 1{constants.CONTROL}",
                f"ALL heroes may take Spell from discard; remove 1{constants.CONTROL}",
                hearts=7)

    def _effect(self, game):
        hero = game.heroes.active_hero
        card = hero.reveal_top_card(game)
        if card is None:
            game.log(f"{hero.name} has no cards left to reveal")
            return
        game.log(f"{hero.name} revealed {card}")
        if card.cost >= 1:
            game.heroes.active_hero.discard_top_card(game)
            game.locations.add_control(game)

    def _reward(self, game):
        game.locations.remove_control(game)
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
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

VILLAINS_BY_NAME["Peter Pettigrew"] = PeterPettigrew


game_three_villains = [
    Dementor,
    PeterPettigrew,
]

class DeathEater(Villain):
    def __init__(self):
        super().__init__(
                "Death Eater",
                f"If Morsmordre or new Villain revealed, ALL Heroes lose 1{constants.HEART}",
                f"ALL heroes gain 1{constants.HEART}; remove 1{constants.CONTROL}",
                hearts=7)

    def _effect(self, game):
        pass

    def _reward(self, game):
        game.heroes.all_heroes.add_hearts(game, 1)
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Death Eater"] = DeathEater


class BartyCrouch(Villain):
    def __init__(self):
        super().__init__(
                "Barty Crouch Jr.",
                f"Heroes cannot remove {constants.CONTROL}",
                f"Remove 2{constants.CONTROL}",
                hearts=7)

    def _on_reveal(self, game):
        game.locations.disallow_remove_control(game)

    def _on_stun(self, game):
        game.locations.allow_remove_control(game)

    def _on_recover_from_stun(self, game):
        game.locations.disallow_remove_control(game)

    def _effect(self, game):
        pass

    def remove_callbacks(self, game):
        game.locations.allow_remove_control(game)

    def _reward(self, game):
        game.locations.remove_control(game, 2)

VILLAINS_BY_NAME["Barty Crouch Jr."] = BartyCrouch


game_four_villains = [
    DeathEater,
    BartyCrouch,
]

class Umbridge(Villain):
    def __init__(self):
        super().__init__(
                "Dolores Umbridge",
                f"If acquire card with cost 4{constants.INFLUENCE} or more, lose 1{constants.HEART}",
                f"ALL heroes gain 1{constants.INFLUENCE} and 2{constants.HEART}",
                hearts=7)

    def _on_reveal(self, game):
        game.heroes.add_acquire_callback(game, self)

    def _effect(self, game):
        pass

    def acquire_callback(self, game, hero, card):
        if card.cost >= 4:
            if self._stunned:
                game.log(f"{self.name} is stunned! No penalty for acquire")
                return
            game.log(f"{self.name}: {game.heroes.active_hero.name} acquired {card.name}, so loses 1{constants.HEART}")
            hero.remove_hearts(game, 1)

    def remove_callbacks(self, game):
        game.heroes.remove_acquire_callback(game, self)

    def _reward(self, game):
        game.heroes.all_heroes.add(game, influence=1, hearts=2)

VILLAINS_BY_NAME["Dolores Umbridge"] = Umbridge

game_five_villains = [
    Umbridge,
    DeathEater,
]


class GameFiveVoldemort(Villain):
    def __init__(self):
        super().__init__(
                "Lord Voldemort",
                f"Active hero loses 1{constants.HEART} and discards a card",
                "You win!",
                hearts=10)

    def _effect(self, game):
        game.heroes.active_hero.add(game, hearts=-1, cards=-1)

    def _reward(self, game):
        pass


class BellatrixLestrange(Villain):
    def __init__(self):
        super().__init__(
                "Bellatrix Lestrange",
                "Reveal an additional Dark Arts event each turn",
                f"ALL heroes may take Item from discard; remove 2{constants.CONTROL}",
                hearts=9),

    def _effect(self, game):
        game.dark_arts_deck.play(game, 1)

    def _reward(self, game):
        game.locations.remove_control(game, 2)
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        items = [card for card in hero._discard if card.is_item()]
        if len(items) == 0:
            game.log(f"{hero.name} has no items in discard")
            return
        if len(items) == 1:
            item = items[0]
            game.log(f"{hero.name} has only one item in discard, taking {item}")
            hero._discard.remove(item)
            hero._hand.append(item)
            return
        game.log(f"Items in {hero.name}'s discard:")
        for i, item in enumerate(items):
            game.log(f" {i}: {item}")
        # TODO allow to skip?
        choice = game.input(f"Choose an item for {hero.name} to take: ", range(len(items)))
        item = items[int(choice)]
        hero._discard.remove(item)
        hero._hand.append(item)

VILLAINS_BY_NAME["Bellatrix Lestrange"] = BellatrixLestrange


class FenrirGreyback(Villain):
    def __init__(self):
        super().__init__(
                "Fenrir Greyback",
                f"Heroes cannot gain {constants.HEART}",
                f"ALL heroes gain 3{constants.HEART}, remove 2{constants.CONTROL}",
                hearts=8)

    def _on_reveal(self, game):
        game.heroes.disallow_healing(game)

    def _on_stun(self, game):
        game.heroes.allow_healing(game)

    def _on_recover_from_stun(self, game):
        game.heroes.disallow_healing(game)

    def remove_callbacks(self, game):
        game.heroes.allow_healing(game)

    def _reward(self, game):
        game.heroes.all_heroes.add_hearts(game, 3)
        game.locations.remove_control(game, 2)

VILLAINS_BY_NAME["Fenrir Greyback"] = FenrirGreyback


game_six_villains = [
    BellatrixLestrange,
    FenrirGreyback,
]


class GameSixVoldemort(Villain):
    def __init__(self):
        super().__init__(
                "Lord Voldemort",
                "Roll the Slytherin die",
                "You win!",
                hearts=15)

    def _effect(self, game):
        faces = [constants.DAMAGE, constants.DAMAGE, constants.DAMAGE, constants.INFLUENCE, constants.HEART, constants.CARD]
        die_result = random.choice(faces)
        if game.heroes.active_hero._proficiency.can_reroll_house_dice and game.input(f"Rolled {die_result}, (a)ccept or (r)eroll? ", "ar") == "r":
            die_result = random.choice(faces)
        if die_result == constants.DAMAGE:
            game.log(f"Rolled {constants.DAMAGE}, ALL heroes lose 1{constants.HEART}")
            game.heroes.all_heroes.remove_hearts(game, 1)
        elif die_result == constants.INFLUENCE:
            game.log(f"Rolled {constants.INFLUENCE}, adding 1{constants.CONTROL} to the location")
            game.locations.add_control(game)
        elif die_result == constants.HEART:
            game.log(f"Rolled {constants.HEART}, ALL Villains heal 1{constants.DAMAGE}")
            game.villain_deck.all_villains.remove_damage(game, 1)
        elif die_result == constants.CARD:
            game.log(f"Rolled {constants.CARD}, ALL heroes discard a card")
            game.heroes.all_heroes.choose_and_discard(game)

    def _reward(self, game):
        pass

game_seven_villains = [
]

class GameSevenVoldemort(Villain):
    def __init__(self):
        super().__init__(
                "Lord Voldemort",
                f"Add 1{constants.CONTROL}; each time {constants.CONTROL} is removed, ALL heroes lose 1{constants.HEART}",
                "You win!",
                hearts=20)

    def _on_reveal(self, game):
        game.locations.add_control_callback(game, self)

    def _effect(self, game):
        game.locations.add_control(game)

    def control_callback(self, game, amount):
        if amount > -1:
            return
        if self._stunned:
            game.log(f"{self.name} is stunned! No penalty for removed {constants.CONTROL}")
            return
        game.log(f"{self.name}: {constants.CONTROL} removed, ALL heroes lose 1{constants.HEART} for each")
        for _ in range(-amount):
            game.heroes.all_heroes.remove_hearts(game, 1)

    def remove_callbacks(self, game):
        game.locations.remove_control_callback(game, self)

    def _reward(self, game):
        pass


BASE_VILLAINS = [
    game_one_villains,
    game_two_villains,
    game_three_villains,
    game_four_villains,
    game_five_villains,
    game_six_villains,
    game_seven_villains,
]


class CornishPixies(Creature):
    def __init__(self):
        super().__init__(
                "Cornish Pixies",
                f"For each card in hand with EVEN {constants.INFLUENCE} cost, lose 2{constants.HEART}",
                f"ALL heroes gain 2{constants.HEART} and 1{constants.INFLUENCE}",
                hearts=6)

    def _effect(self, game):
        hero = game.heroes.active_hero
        evens = sum(1 for card in hero._hand if card.even_cost)
        if evens == 0:
            game.log(f"{hero.name} has no cards with EVEN {constants.INFLUENCE} cost in hand, safe!")
            return
        game.log(f"{hero.name} has {evens} cards with EVEN {constants.INFLUENCE} cost in hand")
        hero.remove_hearts(game, 2 * evens)

    def _reward(self, game):
        game.heroes.all_heroes.add(game, hearts=2, influence=1)

VILLAINS_BY_NAME["Cornish Pixies"] = CornishPixies


class Norbert(Creature):
    def __init__(self):
        super().__init__(
                "Norbert",
                f"Active hero loses 1{constants.HEART} plus 1{constants.HEART} for each Detention! in hand",
                f"ALL heroes may banish a card from hand or discard",
                hearts=6)

    def _effect(self, game):
        hero = game.heroes.active_hero
        detentions = sum(1 for card in hero._hand if card.name == "Detention!")
        game.log(f"{hero.name} has {detentions} Detention! in hand")
        hero.remove_hearts(game, 1 + detentions)

    def _reward(self, game):
        game.heroes.all_heroes.choose_and_banish(game)

VILLAINS_BY_NAME["Norbert"] = Norbert


class Troll(Creature):
    def __init__(self):
        super().__init__(
                "Troll",
                f"Choose: lose 2{constants.HEART} or add Detention! to discard",
                f"ALL heroes gain 1{constants.HEART} and may banish an Item from hand or discard",
                hearts=7)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.is_stunned:
            game.log(f"{hero.name} is stunned and can't lose {constants.HEART}. No penalty for {self.name}!")
            return
        choice = game.input(f"Choose: (h) lose 2{constants.HEART} or (d) add Detention!: ", "hd")
        if choice == 'h':
            hero.remove_hearts(game, 2)
        elif choice == 'd':
            hero.add_detention(game)
        else:
            raise Exception("Invalid choice")

    def _reward(self, game):
        game.heroes.all_heroes.effect(game, self.__reward_per_hero)

    def __reward_per_hero(self, game, hero):
        hero.add_hearts(game, 1)
        hero.choose_and_banish(game, desc="item", filter=lambda card: card.is_item())

VILLAINS_BY_NAME["Troll"] = Troll


class Fluffy(Creature):
    def __init__(self):
        super().__init__(
                "Fluffy",
                f"For each Item in hand, lose 1{constants.HEART} or discard a card",
                f"ALL heroes gain 1{constants.HEART} and draw a card",
                hearts=8)

    def _effect(self, game):
        hero = game.heroes.active_hero
        items = sum(1 for card in hero._hand if card.is_item())
        if items == 0:
            game.log(f"{hero.name} has no Items in hand, safe!")
            return
        if hero.is_stunned:
            game.log(f"{hero.name} is stunned and can't lose {constants.HEART}. No penalty for Items in hand!")
            return
        game.log(f"{hero.name} has {items} Items in hand")
        for _ in range(items):
            choices = ['h'] + [str(i) for i in range(len(hero._hand))]
            choice = game.input(f"Choose a card for {hero.name} to discard or (h) to lose 1{constants.HEART}: ", choices)
            if choice == 'h':
                hero.remove_hearts(game, 1)
            else:
                hero.discard(game, int(choice))

    def _reward(self, game):
        game.heroes.all_heroes.add(game, hearts=1, cards=1)

VILLAINS_BY_NAME["Fluffy"] = Fluffy


class Boggart(Creature):
    def __init__(self):
        super().__init__(
                "Boggart",
                "Roll the Creature die",
                "Roll the Creature die",
                hearts=5, cost=3)

    def _effect(self, game):
        faces = [constants.HEART, constants.HEART + constants.HEART, constants.CARD, constants.CARD + constants.CARD, constants.DAMAGE, constants.CONTROL]
        die_result = random.choice(faces)
        if die_result == constants.HEART:
            game.log(f"Rolled {constants.HEART}, ALL Creatures heal 1{constants.DAMAGE} and/or {constants.INFLUENCE}")
            game.villain_deck.all_creatures.remove_damage(game, 1)
            game.villain_deck.all_creatures.remove_influence(game, 1)
        elif die_result == constants.HEART + constants.HEART:
            game.log(f"Rolled {constants.HEART}{constants.HEART}, ALL foes heal 1{constants.DAMAGE} and/or {constants.INFLUENCE}")
            game.villain_deck.all.remove_damage(game, 1)
            game.villain_deck.all.remove_influence(game, 1)
        elif die_result == constants.CONTROL:
            game.log(f"Rolled {constants.CONTROL}, add 1{constants.CONTROL}")
            game.locations.add_control(game)
        elif die_result == constants.DAMAGE:
            game.log(f"Rolled {constants.DAMAGE}, ALL heroes lose 1{constants.HEART}")
            game.heroes.all_heroes.remove_hearts(game, 1)
        elif die_result == constants.CARD:
            game.log(f"Rolled {constants.CARD}, ALL heroes discard a card")
            game.heroes.all_heroes.choose_and_discard(game)
        elif die_result == constants.CARD + constants.CARD:
            game.log(f"Rolled {constants.CARD}{constants.CARD}, active hero discards 2 cards")
            game.heroes.active_hero.choose_and_discard(game, 2)

    def _reward(self, game):
        game.roll_creature_die()

VILLAINS_BY_NAME["Boggart"] = Boggart


class Werewolf(Creature):
    def __init__(self):
        super().__init__(
                "Werewolf",
                f"If active hero loses 4{constants.HEART}, add 1{constants.CONTROL}",
                f"ALL heroes gain 1{constants.INFLUENCE} or 2{constants.HEART}; remove 1{constants.CONTROL}",
                hearts=5, cost=4)
        self._hero_damage_taken = 0
        self._used_ability = False

    def _on_reveal(self, game):
        game.heroes.add_hearts_callback(game, self)

    def _effect(self, game):
        pass

    def end_turn(self, game):
        super().end_turn(game)
        self._hero_damage_taken = 0
        self._used_ability = False

    def hearts_callback(self, game, hero, amount, source):
        if hero != game.heroes.active_hero:
            return
        if amount >= 0:
            return
        self._hero_damage_taken -= amount
        if self._hero_damage_taken >= 4 and not self._used_ability:
            self._used_ability = True
            if self._stunned:
                game.log(f"{self.name} is stunned! No penalty for lost {constants.HEART}")
                return
            game.log(f"{self.name}: {hero.name} lost {self._hero_damage_taken}{constants.HEART} this turn, adding 1{constants.CONTROL}")
            game.locations.add_control(game)

    def remove_callbacks(self, game):
        game.heroes.remove_hearts_callback(game, self)

    def _reward(self, game):
        game.locations.remove_control(game)
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        if not hero.healing_allowed:
            game.log(f"{hero.name} can't heal, gaining 1{constants.INFLUENCE}")
            choice = 'i'
        elif not hero.gaining_tokens_allowed(game):
            game.log(f"{hero.name} not allowed to gain tokens, gaining 2{constants.HEART}")
            choice = 'h'
        else:
            choice = game.input(f"Choose {hero.name} gains (i) 1{constants.INFLUENCE} or (h) 2{constants.HEART}: ", "ih")
        if choice == 'i':
            hero.add_influence(game, 1)
        elif choice == 'h':
            hero.add_hearts(game, 2)

VILLAINS_BY_NAME["Werewolf"] = Werewolf


class Scabbers(VillainCreature):
    def __init__(self):
        super().__init__(
                "Scabbers",
                f"Reveal top card of deck, if costs 1{constants.INFLUENCE} or more, discard and lose 2{constants.HEART}",
                f"ALL heroes may take card with cost <= 3{constants.INFLUENCE} from discard; remove 1{constants.CONTROL}",
                hearts=7)

    def _effect(self, game):
        hero = game.heroes.active_hero
        card = hero.reveal_top_card(game)
        if card is None:
            game.log(f"{hero.name} has no cards left to reveal")
            return
        game.log(f"{hero.name} revealed {card}")
        if card.cost >= 1:
            hero.discard_top_card(game)
            hero.remove_hearts(game, 2)

    def _reward(self, game):
        game.locations.remove_control(game)
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        cards = [card for card in hero._discard if card.cost <= 3]
        if len(cards) == 0:
            game.log(f"{hero.name} has no cheap cards in discard")
            return
        if len(cards) == 1:
            card = cards[0]
            game.log(f"{hero.name} has only one cheap card in discard, taking {card}")
            hero._discard.remove(card)
            hero._hand.append(card)
            return
        game.log(f"Cheap cards in {hero.name}'s discard:")
        for i, card in enumerate(cards):
            game.log(f" {i}: {card}")
        # TODO allow to skip?
        choice = game.input(f"Choose a card for {hero.name} to take: ", range(len(cards)))
        card = cards[int(choice)]
        hero._discard.remove(card)
        hero._hand.append(card)

VILLAINS_BY_NAME["Scabbers"] = Scabbers


# Plus voldemort!
VILLAIN_DECK_SIZE = {
    "m1": 11,
    "m2": 11,
    "m3": 12,
    "m4": 14,
    "p1": 0,
    "p2": 0,
    "p3": 0,
    "p4": 0,
}
# game 1: voldemort 5
# game 2: voldemort 6
# game 3: voldemort 7
# game 4: voldemort special
