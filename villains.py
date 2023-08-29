from functools import reduce

import operator
import random

class VillainDeck(object):
    def __init__(self, window, game_num):
        self._window = window
        self._deck = reduce(operator.add, VILLAINS[:game_num])
        self._max = MAX_VILLAINS[game_num]

        random.shuffle(self._deck)
        self.current = []

    def display_state(self):
        self._window.clear()
        self._window.box()
        self._window.addstr(0, 1, f"Villains ({len(self._deck)} left)")
        for i, villain in enumerate(self.current):
            villain.display_state(self._window, 3*i+1, i)
        self._window.refresh()

    def play_turn(self, game):
        game.log("-----Villain phase-----")
        for villain in self.current:
            game.log(f"Villain: {villain}")
            villain.effect(game)

    def reveal(self, game):
        for villain in self.current:
            villain.took_damage = False
        while len(self.current) < self._max and len(self._deck) > 0:
            villain = self._deck.pop()
            self.current.append(villain)
            villain.on_reveal(game)

    def choose_villain(self, game, prompt="Choose a villain: "):
        if len(self.current) == 1:
            return self.current[0]

        choice = int(game.input(prompt, range(len(self.current))))
        return self.current[choice]

    def all_villains(self, game, effect):
        for villain in self.current:
            effect(game, villain)


class Villain(object):
    def __init__(self, name, description, reward_desc, health, effect=lambda game: None, on_reveal=lambda game: None, reward=lambda game: None):
        self.name = name
        self.description = description
        self.reward_desc = reward_desc
        self._health = health
        self.effect = effect
        self.on_reveal = on_reveal
        self._reward = reward

        self._damage = 0
        self.took_damage = False

    def display_state(self, window, row, i):
        window.addstr(row  , 1, f"{i}: {self.name} ({self._damage}↯/{self._health}💜)")
        window.addstr(row+1, 1, f"     {self.description}")
        window.addstr(row+2, 1, f"     Reward: {self.reward_desc}")

    def __str__(self):
        return f"{self.name} ({self._damage}/{self._health}), {self.description}"

    def add_damage(self, game, amount=1):
        self.took_damage = True
        self._damage += amount
        if self._damage >= self._health:
            self.reward(game)
            game.villain_deck.current.remove(self)
            return True
        return False

    def remove_damage(self, game, amount=1):
        self._damage -= amount
        if self._damage < 0:
            self._damage = 0

    def reward(self, game):
        game.log(f"{self.name} defeated!")
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
        game.log(f"{self.name}: 💀 added, {game.heroes.active_hero.name} loses 2💜 for each")
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
        game.log(f"{self.name}: {hero.name} discarded, so loses 1💜")
        hero.remove_health(game, 1)

    def __reward(self, game):
        game.heroes.remove_discard_callback(game, self)
        game.heroes.all_heroes(game, lambda game, hero: hero.draw(game))


game_one_villains = [
    Draco(),
    Crabbe(),
    Villain("Quirinus Quirrell", "Active hero loses 1💜",
            "ALL heroes gain 1💜 and 1💰", 6,
            effect=lambda game: game.heroes.active_hero.remove_health(game),
            reward=lambda game: game.heroes.all_heroes(game, lambda game, hero: hero.add(game, influence=1, hearts=1))),
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
        game.log(f"{self.name}: 💀 added, all Villains heal 1↯ for each")
        for _ in range(amount):
            game.villain_deck.all_villains(game, lambda game, villain: villain.remove_damage(game, 1))

    def __reward(self, game):
        game.locations.remove_control_callback(game, self)
        game.heroes.all_heroes(game, lambda game, hero: hero.add_influence(game, 1))
        game.locations.remove_control(game)

def basilisk_reward(game):
    # TODO solve problem of petrification and basilisk together
    game.heroes.basilisk_defeated(game)
    game.heroes.all_heroes(game, lambda game, hero: hero.draw(game))
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
            break
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
            # TODO solve disallowed drawing as a result of forced discard
            on_reveal=lambda game: game.heroes.basilisk_revealed(game),
            reward=basilisk_reward),
    Villain("Tom Riddle", "For each Ally in hand, lose 2💜 or discard",
            "ALL heroes gain 2💜 or take Ally from discard", 6,
            effect=riddle_effect, reward=lambda game: game.heroes.all_heroes(game, riddle_reward)),
]

def dementor_reward(game):
    game.heroes.all_heroes(game, lambda game, hero: hero.add_health(game, 2))
    game.locations.remove_control(game)

def pettigrew_effect(game):
    pass

def pettigrew_reward(game):
    game.locations.remove_control(game)
    game.heroes.all_heroes(game, pettigrew_per_hero)

def pettigrew_per_hero(game, hero):
    spells = [card for card in hero._discard if card.is_spell()]
    if len(spells) == 0:
        game.log(f"{hero.name} has no spells in discard")
        return
    game.log(f"Spells in {hero.name}'s discard: {spells_str}")
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
    game.heroes.all_heroes(game, lambda game, hero: hero.add_health(game, 1))
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
            reward=crouch_reward),
]

class Umbridge(Villain):
    def __init__(self):
        super().__init__("Dolores Umbridge", "If acquire card with cost 4💰 or more, lose 1💜",
                         "ALL heroes gain 1💰 and 2💜", 7,
                         on_reveal=lambda game: game.heroes.add_acquire_callback(game, self),
                         reward=self.__reward),

    def acquire_callback(self, game, hero, card):
        if card.cost >= 4:
            game.log(f"{self.name}: {game.heroes.active_hero.name} acquired {card}, so loses 1💜")
            hero.remove_health(game, 1)

    def __reward(self, game):
        game.heroes.remove_acquire_callback(game, self)
        game.heroes.all_heroes(game, lambda game, hero: hero.add(game, influence=1, hearts=2))

game_five_villains = [
    # TODO villain revealed callback
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
    game.heroes.all_heroes(game, bellatrix_per_hero)

def bellatrix_per_hero(game, hero):
    items = [card for card in hero._discard if card.is_item()]
    if len(items) == 0:
        game.log(f"{hero.name} has no items in discard")
        return
    game.log(f"Items in {hero.name}'s discard: {items_str}")
    for i, item in enumerate(items):
        game.log(f" {i}: {item}")
    # TODO allow to skip?
    choice = game.input(f"Choose an item for {hero.name} to take: ", range(len(items)))
    item = items[int(choice)]
    hero._discard.remove(item)
    hero._hand.append(item)

def greyback_reward(game):
    game.heroes.greyback_defeated(game)
    game.heroes.all_heroes(game, lambda game, hero: hero.add_health(game, 3))
    game.locations.remove_control(game, 2)

game_six_villains = [
    Villain("Bellatrix Lestrange", "Reveal an additional Dark Arts event each turn",
            "ALL heroes may take Item from discard; remove 2💀", 9,
            effect=lambda game: game.dark_arts_deck.play(game, 1),
            reward=bellatrix_reward),
    Villain("Fenrir Greyback", "Heroes cannot gain 💜", "ALL heroes gain 3💜, remove 2💀", 8,
            on_reveal=lambda game: game.heroes.greyback_revealed(game),
            reward=greyback_reward),
]

class GameSixVoldemort(Villain):
    def __init__(self):
        super().__init__("Lord Voldemort", "Active hero loses 1💜 and discards a card",
                         "You win!", 15, effect=self.__effect)

    def __effect(self, game):
        die_result = random.choice("↯↯↯💰💜🃏")
        if die_result == "↯":
            game.log("Rolled ↯, ALL heroes lose 1💜")
            game.heroes.all_heroes(game, lambda game, hero: hero.remove_health(game, 1))
        elif die_result == "💰":
            game.log("Rolled 💰, adding 1💀 to the location")
            game.locations.add_control(game)
        elif die_result == "💜":
            game.log("Rolled 💜, ALL Villains heal 1↯")
            game.villain_deck.all_villains(lambda game, villain: villain.remove_damage(game, 1))
        elif die_result == "🃏":
            game.log("Rolled 🃏, ALL heroes discard a card")
            game.heroes.all_heroes(game, lambda game, hero: hero.choose_and_discard(game))

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
        game.log(f"{self.name}: 💀 removed, ALL heroes lose 1💜 for each")
        for _ in range(-amount):
            game.heroes.all_heroes(game, lambda game, hero: hero.remove_health(game, 1))

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
