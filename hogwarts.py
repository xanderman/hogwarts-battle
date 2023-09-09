from collections import defaultdict
from functools import reduce

import curses
import itertools
import operator
import random

class HogwartsDeck(object):
    def __init__(self, window, game_num):
        self._window = window
        self._init_window()
        self._pad = curses.newpad(100, 100)
        self._deck = reduce(operator.add, CARDS[:game_num])
        self._max = 6
        random.shuffle(self._deck)
        self._market = defaultdict(list)

    def _init_window(self):
        self._window.box()
        self._window.addstr(0, 1, "Market")
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
        self._pad.clear()
        for i, name in enumerate(self._market):
            card = self._market[name][0]
            count = len(self._market[name])
            card.display_state(self._pad, i, count)
        self._pad.noutrefresh(0,0, self._pad_start_line,self._pad_start_col, self._pad_end_line,self._pad_end_col)

    def refill_market(self, game):
        while len(self._market) < self._max:
            if len(self._deck) == 0:
                break
            card = self._deck.pop()
            game.log(f"Adding {card.name} to market")
            self._market[card.name].append(card)

    def empty_market(self, game):
        for card in itertools.chain.from_iterable(self._market.values()):
            self._deck.insert(0, card)
        self._market.clear()

    def empty_market_slot(self, game, slot):
        for card in self._market[slot]:
            self._deck.insert(0, card)
        del self._market[slot]

    def __getitem__(self, pos):
        if pos not in range(len(self._market)):
            raise ValueError("Programmer Error! Invalid position!")
        name = list(self._market.keys())[pos]
        return self._market[name][0]

    def remove(self, name):
        if name not in self._market:
            raise ValueError("Programmer Error! Card not in market!")
        card = self._market[name].pop()
        if len(self._market[name]) == 0:
            del self._market[name]
        return card


class HogwartsCard(object):
    def __init__(self, name, description, cost, effect=lambda game: None, discard_effect=lambda game, hero: None, rolls_house_die=False):
        self.name = name
        self.description = description
        self.cost = cost
        self.effect = effect
        self.discard_effect = discard_effect
        self.rolls_house_die = rolls_house_die

    def display_state(self, window, i, count):
        window.addstr(f"{i}: ", curses.A_BOLD)
        self.display_name(window, curses.A_BOLD)
        window.addstr(f" x{count}\n", curses.color_pair(1) | curses.A_BOLD)
        window.addstr(f"     {self.description}\n")

    def display_name(self, window, attr=0):
        window.addstr(self.name, self.color | attr)
        window.addstr(f" ({self.cost}💰)", attr)

    def __str__(self):
        return f"{self.name} ({self.cost}💰): {self.description}"

    def play(self, game):
        game.log(f"Playing {self}")
        self.effect(game)

    def is_ally(self):
        return False

    def is_item(self):
        return False

    def is_spell(self):
        return False

    @property
    def color(self):
        return 0


class Ally(HogwartsCard):
    def is_ally(self):
        return True

    @property
    def color(self):
        return curses.color_pair(3)


class Item(HogwartsCard):
    def is_item(self):
        return True

    @property
    def color(self):
        return curses.color_pair(4)


class Spell(HogwartsCard):
    def is_spell(self):
        return True

    @property
    def color(self):
        return curses.color_pair(2)


def hagrid_effect(game):
    game.heroes.active_hero.add_damage(game)
    game.heroes.all_heroes.add_health(game)

def sorting_hat_effect(game):
    game.heroes.active_hero.add_influence(game, 2)
    game.heroes.active_hero.can_put_allies_in_deck(game)

def wingardium_effect(game):
    game.heroes.active_hero.add_influence(game)
    game.heroes.active_hero.can_put_items_in_deck(game)

def reparo_effect(game):
    if not game.heroes.active_hero.drawing_allowed:
        game.log("Drawing not allowed, gaining 2💰")
        choice = "i"
    else:
        choice = game.input("Choose effect: (i)💰, (d)raw: ", "id")

    if choice == "i":
        game.heroes.active_hero.add_influence(game, 2)
    elif choice == "d":
        game.heroes.active_hero.draw(game)

def dittany_effect(game):
    if not game.heroes.healing_allowed:
        game.log("Healing not allowed, ignoring Essence of Dittany effect")
        return
    while True:
        choice = int(game.input("Choose hero to gain 2💜: ", range(len(game.heroes))))
        hero = game.heroes[choice]
        if not hero.healing_allowed:
            game.log(f"{hero.name} cannot heal, choose another hero!")
            continue
        hero.add_health(game, 2)
        break

def oliver_effect(game):
    game.heroes.active_hero.add_damage(game)
    game.heroes.active_hero.add_extra_villain_reward(game, lambda game: game.heroes.choose_hero(game, prompt="Oliver Wood: Villain defeated! Choose hero to gain 2💜: ").add_health(game, 2))

game_one_cards = [
    Spell("Wingardium Leviosa", "Gain 1💰, may put acquired Items on top of deck", 2, wingardium_effect),
    Spell("Wingardium Leviosa", "Gain 1💰, may put acquired Items on top of deck", 2, wingardium_effect),
    Spell("Wingardium Leviosa", "Gain 1💰, may put acquired Items on top of deck", 2, wingardium_effect),
    Spell("Reparo", "Gain 2💰 or draw a card", 3, reparo_effect),
    Spell("Reparo", "Gain 2💰 or draw a card", 3, reparo_effect),
    Spell("Reparo", "Gain 2💰 or draw a card", 3, reparo_effect),
    Spell("Reparo", "Gain 2💰 or draw a card", 3, reparo_effect),
    Spell("Reparo", "Gain 2💰 or draw a card", 3, reparo_effect),
    Spell("Reparo", "Gain 2💰 or draw a card", 3, reparo_effect),
    Spell("Lumos", "ALL heroes daw a card", 4, lambda game: game.heroes.all_heroes.draw(game)),
    Spell("Lumos", "ALL heroes daw a card", 4, lambda game: game.heroes.all_heroes.draw(game)),
    Spell("Incendio", "Gain 1↯ and draw a card", 4, lambda game: game.heroes.active_hero.add(game, damage=1, cards=1)),
    Spell("Incendio", "Gain 1↯ and draw a card", 4, lambda game: game.heroes.active_hero.add(game, damage=1, cards=1)),
    Spell("Incendio", "Gain 1↯ and draw a card", 4, lambda game: game.heroes.active_hero.add(game, damage=1, cards=1)),
    Spell("Incendio", "Gain 1↯ and draw a card", 4, lambda game: game.heroes.active_hero.add(game, damage=1, cards=1)),
    Spell("Descendo", "Gain 2↯", 5, lambda game: game.heroes.active_hero.add_damage(game, 2)),
    Spell("Descendo", "Gain 2↯", 5, lambda game: game.heroes.active_hero.add_damage(game, 2)),
    Item("Essence of Dittany", "Any hero gains 2💜", 2, dittany_effect),
    Item("Essence of Dittany", "Any hero gains 2💜", 2, dittany_effect),
    Item("Essence of Dittany", "Any hero gains 2💜", 2, dittany_effect),
    Item("Essence of Dittany", "Any hero gains 2💜", 2, dittany_effect),
    Item("Quidditch Gear", "Gain 1↯ and 1💜", 3, lambda game: game.heroes.active_hero.add(game, damage=1, hearts=1)),
    Item("Quidditch Gear", "Gain 1↯ and 1💜", 3, lambda game: game.heroes.active_hero.add(game, damage=1, hearts=1)),
    Item("Quidditch Gear", "Gain 1↯ and 1💜", 3, lambda game: game.heroes.active_hero.add(game, damage=1, hearts=1)),
    Item("Quidditch Gear", "Gain 1↯ and 1💜", 3, lambda game: game.heroes.active_hero.add(game, damage=1, hearts=1)),
    Item("Sorting Hat", "Gain 2💰, may put acquired Allies on top of deck", 4, sorting_hat_effect),
    Item("Golden Snitch", "Gain 2💰 and draw a card", 5, lambda game: game.heroes.active_hero.add(game, influence=2, cards=1)),
    Ally("Oliver Wood", "Gain 1↯, if you defeat a Villain anyone gains 2💜", 3, oliver_effect),
    Ally("Rubeus Hagrid", "Gain 1↯; ALL heroes gain 1💜", 4, hagrid_effect),
    Ally("Albus Dumbledore", "ALL heroes gain 1↯, 1💰, 1💜, and draw a card", 8, lambda game: game.heroes.all_heroes.add(game, damage=1, influence=1, hearts=1, cards=1)),
]

def polyjuice_effect(game):
    played_allies = [card for card in game.heroes.active_hero._play_area if card.is_ally()]
    if len(played_allies) == 0:
        game.log("You haven't played any allies, polyjuice wasted!")
        return
    if len(played_allies) == 1:
        game.log(f"Only one ally played, copying {played_allies[0].name}")
        played_allies[0].effect(game)
        return
    while True:
        choice = int(game.input("Choose played ally to polyjuice: ", range(len(game.heroes.active_hero._play_area))))
        card = game.heroes.active_hero._play_area[choice]
        if not card.is_ally():
            game.log("{card.name} is not an ally!")
            continue
        game.log(f"Copying {card.name}")
        card.effect(game)
        break

def level_two_broom_effect(game):
    game.heroes.active_hero.add_damage(game, 2)
    game.heroes.active_hero.add_extra_villain_reward(game, lambda game: game.heroes.active_hero.add_influence(game, 2))

def fawkes_effect(game):
    if not game.heroes.healing_allowed:
        game.log("Healing not allowed, gaining 2↯")
        game.heroes.active_hero.add_damage(game, 2)
        return
    choice = game.input("Choose effect: (d)↯, (h)💜: ", "dh")
    if choice == "d":
        game.heroes.active_hero.add_damage(game, 2)
    elif choice == "h":
        game.heroes.all_heroes.add_health(game, 2)

def dobby_effect(game):
    game.locations.remove_control(game)
    game.heroes.active_hero.draw(game)

def lockhart_effect(game):
    if not game.heroes.active_hero.drawing_allowed:
        game.log("Drawing not allowed, ignoring Lockhart effect")
        return
    game.heroes.active_hero.draw(game)
    game.heroes.active_hero.choose_and_discard(game, with_callbacks=False)

game_two_cards = [
    Spell("Finite", "Remove 1💀", 3, lambda game: game.locations.remove_control(game)),
    Spell("Finite", "Remove 1💀", 3, lambda game: game.locations.remove_control(game)),
    Spell("Expelliarmus", "Gain 2↯ and draw a card", 6, lambda game: game.heroes.active_hero.add(game, damage=2, cards=1)),
    Spell("Expelliarmus", "Gain 2↯ and draw a card", 6, lambda game: game.heroes.active_hero.add(game, damage=2, cards=1)),
    Item("Polyjuice potion", "Choose a played ally and gain its effect", 3, polyjuice_effect),
    Item("Polyjuice potion", "Choose a played ally and gain its effect", 3, polyjuice_effect),
    Item("Nimbus 2001", "Gain 2↯; if you defeat a villain, gain 2💰", 5, level_two_broom_effect),
    Item("Nimbus 2001", "Gain 2↯; if you defeat a villain, gain 2💰", 5, level_two_broom_effect),
    Ally("Fawkes", "Gain 2↯ or ALL heroes gain 2💜", 5, fawkes_effect),
    Ally("Molly Weasley", "ALL heroes gain 1💰 and 2💜", 6, lambda game: game.heroes.all_heroes.add(game, influence=1, hearts=2)),
    Ally("Dobby", "Remove 1💀 and draw a card", 4, dobby_effect),
    Ally("Arthur Weasley", "ALL heroes gain 2💰", 6, lambda game: game.heroes.all_heroes.add_influence(game, 2)),
    Ally("Gilderoy Lockhart", "Draw a card, then discard a card; if discarded, draw a card", 2, lockhart_effect, discard_effect=lambda game, hero: hero.draw(game)),
    Ally("Ginny Weasley", "Gain 1↯ and 1💰", 4, lambda game: game.heroes.active_hero.add(game, damage=1, influence=1)),
]

def patronum_effect(game):
    game.heroes.active_hero.add_damage(game)
    game.locations.remove_control(game)

def petrificus_effect(game):
    game.heroes.active_hero.add_damage(game)
    if len(game.villain_deck.choices) == 0:
        game.log("No villains to stun!")
        return
    choices = ['c'] + game.villain_deck.choices
    choice = game.input("Choose villain to stun ('c' to cancel): ", choices)
    if choice == 'c':
        return
    game.villain_deck[choice].stun(game)

def crystal_ball_effect(game):
    hero = game.heroes.active_hero
    if not hero.drawing_allowed:
        game.log("Drawing not allowed, ignoring Crystal Ball effect")
        return
    hero.draw(game, 2)
    hero.choose_and_discard(game, with_callbacks=False)

def lupin_effect(game):
    game.heroes.active_hero.add_damage(game)
    game.heroes.choose_hero(game, prompt="Choose hero to gain 3💜: ").add_health(game, 3)

def trelawny_effect(game):
    hero = game.heroes.active_hero
    if not hero.drawing_allowed:
        game.log("Drawing not allowed, ignoring Trelawny effect")
        return
    hero.draw(game, 2)
    discarded = hero.choose_and_discard(game, with_callbacks=False)[0]
    if discarded.is_spell():
        game.log("Discarded spell, gaining 2💰")
        hero.add_influence(game, 2)

game_three_cards = [
    Spell("Expecto Patronum", "Gain 1↯; remove 1💀", 5, patronum_effect),
    Spell("Expecto Patronum", "Gain 1↯; remove 1💀", 5, patronum_effect),
    Spell("Petrificus Totalus", "Gain 1↯; stun a Villain", 6, petrificus_effect),
    Spell("Petrificus Totalus", "Gain 1↯; stun a Villain", 6, petrificus_effect),
    Item("Chocolate Frog", "One hero gains 1💰 and 1💜; if discarded, gain 1💰 and 1💜", 2, lambda game: game.heroes.choose_hero(game, prompt="Choose a hero to gain 1💰 and 1💜: ").add(game, influence=1, hearts=1), discard_effect=lambda game, hero: hero.add(game, influence=1, hearts=1)),
    Item("Chocolate Frog", "One hero gains 1💰 and 1💜; if discarded, gain 1💰 and 1💜", 2, lambda game: game.heroes.choose_hero(game, prompt="Choose a hero to gain 1💰 and 1💜: ").add(game, influence=1, hearts=1), discard_effect=lambda game, hero: hero.add(game, influence=1, hearts=1)),
    Item("Chocolate Frog", "One hero gains 1💰 and 1💜; if discarded, gain 1💰 and 1💜", 2, lambda game: game.heroes.choose_hero(game, prompt="Choose a hero to gain 1💰 and 1💜: ").add(game, influence=1, hearts=1), discard_effect=lambda game, hero: hero.add(game, influence=1, hearts=1)),
    Item("Butterbeer", "Two heroes gain 1💰 and 1💜", 3, lambda game: game.heroes.choose_two_heroes(game, prompt="to gain 1💰 and 1💜").add(game, influence=1, hearts=1)),
    Item("Butterbeer", "Two heroes gain 1💰 and 1💜", 3, lambda game: game.heroes.choose_two_heroes(game, prompt="to gain 1💰 and 1💜").add(game, influence=1, hearts=1)),
    Item("Butterbeer", "Two heroes gain 1💰 and 1💜", 3, lambda game: game.heroes.choose_two_heroes(game, prompt="to gain 1💰 and 1💜").add(game, influence=1, hearts=1)),
    Item("Crystal Ball", "Draw two cards; discard one card", 3, crystal_ball_effect),
    Item("Crystal Ball", "Draw two cards; discard one card", 3, crystal_ball_effect),
    Item("Marauder's Map", "Draw two cards; if discarded, ALL heroes draw a card", 5, lambda game: game.heroes.active_hero.draw(game, 2), discard_effect=lambda game, hero: game.heroes.all_heroes.draw(game)),
    Ally("Remus Lupin", "Gain 1↯, any hero gains 3💜", 4, lupin_effect),
    Ally("Sirius Black", "Gain 2↯ and 1💰", 6, lambda game: game.heroes.active_hero.add(game, damage=2, influence=1)),
    Ally("Sybill Trelawney", "Draw 2 cards; discard one card. If you discard a Spell, gain 2💰", 4, trelawny_effect),
]

def accio_effect(game):
    hero = game.heroes.active_hero
    items = [card for card in hero._discard if card.is_item()]
    if len(items) == 0:
        game.log(f"{hero.name} has no items in discard, gaining 2💰")
        hero.add_influence(game, 2)
        return
    game.log(f"Items in {hero.name}'s discard: ")
    for i, item in enumerate(items):
        game.log(f" {i}: {item}")
    choices = ['i'] + [str(i) for i in range(len(items))]
    choice = game.input(f"Choose an item for {hero.name} to take, or (i) to gain 2💰: ", choices)
    if choice == 'i':
        hero.add_influence(game, 2)
        return
    item = items[int(choice)]
    hero._discard.remove(item)
    hero._hand.append(item)

def hogwarts_history_effect(game):
    choice = game.input(f"Choose house die to roll, (g)ryffindor, (h)ufflepuff, (r)avenclaw, (s)lytherin: ", "ghrs")
    if choice == "g":
        game.roll_gryffindor_die()
    elif choice == "h":
        game.roll_hufflepuff_die()
    elif choice == "r":
        game.roll_ravenclaw_die()
    elif choice == "s":
        game.roll_slytherin_die()

def snape_effect(game):
    game.heroes.active_hero.add(game, damage=1, hearts=2)
    game.roll_slytherin_die()

def add_health_if_ally_once(card, game):
    if card.is_ally():
        game.log("Ally {card.name} played, beans add damage")
        game.heroes.active_hero.add_damage(game)

class FleurDelacour(Ally):
    def __init__(self):
        super().__init__("Fleur Delacour", "Gain 2💰; if you play another ally, gain 2💜", 4, self.__effect)
        self._used_ability = False

    def __effect(self, game):
        self._used_ability = False
        game.heroes.active_hero.add_influence(game, 2)
        for card in game.heroes.active_hero._play_area:
            if card.is_ally() and card != self:
                game.log(f"Ally {card.name} already played, {self.name} adds 2💜")
                game.heroes.active_hero.add_health(game, 2)
                return
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if card.is_ally() and card != self and not self._used_ability:
            game.log(f"Ally {card.name} played, {self.name} adds 2💜")
            game.heroes.active_hero.add_health(game, 2)
            self._used_ability = True

def flitwick_effect(game):
    game.heroes.active_hero.add(game, influence=1, cards=1)
    game.roll_ravenclaw_die()

def diggory_effect(game):
    game.heroes.active_hero.add_damage(game)
    game.roll_hufflepuff_die()

def krum_effect(game):
    game.heroes.active_hero.add_damage(game, 2)
    game.heroes.active_hero.add_extra_villain_reward(game, lambda game: game.heroes.active_hero.add(game, influence=1, hearts=1))

def moody_effect(game):
    game.heroes.active_hero.add_influence(game, 2)
    game.locations.remove_control(game)

def mcgonagall_effect(game):
    game.heroes.active_hero.add(game, influence=1, damage=1)
    game.roll_gryffindor_die()

def sprout_effect(game):
    game.heroes.active_hero.add_influence(game)
    game.heroes.choose_hero(game, prompt="Choose hero to gain 2💜: ").add_health(game, 2)
    game.roll_hufflepuff_die()

game_four_cards = [
    Spell("Accio", "Gain 2💰 or take Item from discard", 4, accio_effect),
    Spell("Accio", "Gain 2💰 or take Item from discard", 4, accio_effect),
    Spell("Protego", "Gain 1↯ and 1💜; if discarded, gain 1↯ and 1💜", 5, lambda game: game.heroes.active_hero.add(game, damage=1, hearts=1), discard_effect=lambda game, hero: hero.add(game, damage=1, hearts=1)),
    Spell("Protego", "Gain 1↯ and 1💜; if discarded, gain 1↯ and 1💜", 5, lambda game: game.heroes.active_hero.add(game, damage=1, hearts=1), discard_effect=lambda game, hero: hero.add(game, damage=1, hearts=1)),
    Spell("Protego", "Gain 1↯ and 1💜; if discarded, gain 1↯ and 1💜", 5, lambda game: game.heroes.active_hero.add(game, damage=1, hearts=1), discard_effect=lambda game, hero: hero.add(game, damage=1, hearts=1)),
    Item("Hogwarts: A History", "Roll any house die", 4, hogwarts_history_effect, rolls_house_die=True),
    Item("Hogwarts: A History", "Roll any house die", 4, hogwarts_history_effect, rolls_house_die=True),
    Item("Hogwarts: A History", "Roll any house die", 4, hogwarts_history_effect, rolls_house_die=True),
    Item("Hogwarts: A History", "Roll any house die", 4, hogwarts_history_effect, rolls_house_die=True),
    Item("Hogwarts: A History", "Roll any house die", 4, hogwarts_history_effect, rolls_house_die=True),
    Item("Hogwarts: A History", "Roll any house die", 4, hogwarts_history_effect, rolls_house_die=True),
    Item("Pensieve", "Two heroes gain 1💰 and draw a card", 5, lambda game: game.heroes.choose_two_heroes(game, prompt="to gain 1💰 and draw a card").add(game, influence=1, cards=1)),
    Item("Triwizard Cup", "Gain 1↯, 1💰, and 1💜", 5, lambda game: game.heroes.active_hero.add(game, damage=1, influence=1, hearts=1)),
    Ally("Severus Snape", "Gain 1↯ and 2💜; roll the Slytherin die", 6, snape_effect, rolls_house_die=True),
    FleurDelacour(),
    Ally("Filius Flitwick", "Gain 1💰 and draw a card; roll the Ravenclaw die", 6, flitwick_effect, rolls_house_die=True),
    Ally("Cedric Diggory", "Gain 1↯; roll the Hufflepuff die", 4, diggory_effect, rolls_house_die=True),
    Ally("Viktor Krum", "Gain 2↯, if you defeat a Villain gain 1💰 and 1💜", 5, krum_effect),
    Ally("Mad-eye Moody", "Gain 2💰, remove 1💀", 6, moody_effect),
    Ally("Minerva McGonagall", "Gain 1💰 and 1↯; roll the Gryffindor die", 6, mcgonagall_effect, rolls_house_die=True),
    Ally("Pomona Sprout", "Gain 1💰; anyone gains 2💜; roll the Hufflepuff die", 6, sprout_effect, rolls_house_die=True),
]

def stupefy_effect(game):
    game.heroes.active_hero.add(game, damage=1, cards=1)
    game.locations.remove_control(game)

class Owls(Item):
    def __init__(self):
        super().__init__("O.W.L.S.", "Gain 2💰; if you play 2 spells, gain 1↯ and 1💜", 4, self.__effect)
        self._used_ability = False
        self._spells_played = 0

    def __effect(self, game):
        self._used_ability = False
        game.heroes.active_hero.add_influence(game, 2)
        self._spells_played = sum([1 for card in game.heroes.active_hero._play_area if card.is_spell()])
        if self._spells_played >= 2:
            game.log(f"Already played {self._spells_played} spells, gaining 1↯ and 1💜")
            game.heroes.active_hero.add(game, damage=1, hearts=1)
            return
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if card.is_spell():
            self._spells_played += 1
        if self._spells_played >= 2 and not self._used_ability:
            game.log(f"Second spell played, {self.name} adds 1↯ and 1💜")
            game.heroes.active_hero.add(game, damage=1, hearts=1)
            self._used_ability = True

def tonks_effect(game):
    if game.locations._control_remove_allowed:
        choice = game.input("Choose to (i) gain 3💰, (d) gain 2↯, or (c) remove 1💀: ", "idc")
    else:
        choice = game.input("Rmoving 💀 not allowed! Choose to (i) gain 3💰, (d) gain 2↯: ", "id")

    if choice == "i":
        game.heroes.active_hero.add_influence(game, 3)
    elif choice == "d":
        game.heroes.active_hero.add_damage(game, 2)
    elif choice == "c":
        game.locations.remove_control(game)

def weasley_twin_effect(bonus):
    def effect(game):
        game.heroes.active_hero.add_damage(game)
        game.roll_gryffindor_die()
        for hero in game.heroes:
            if hero == game.heroes.active_hero:
                continue
            for card in hero._hand:
                if 'Weasley' in card.name:
                    game.log(f"{hero.name} has {card.name}, ALL heroes gain 1{bonus}")
                    if bonus == "💰":
                        game.heroes.all_heroes.add_influence(game, 1)
                    elif bonus == "💜":
                        game.heroes.all_heroes.add_health(game, 1)
                    return
    return effect

def cho_effect(game):
    game.roll_ravenclaw_die()
    hero = game.heroes.active_hero
    if not hero.drawing_allowed:
        game.log("Drawing not allowed, ignoring Cho's draw effect")
        return
    hero.draw(game, 3)
    hero.choose_and_discard(game, 2, with_callbacks=False)

class LunaAlly(Ally):
    def __init__(self):
        super().__init__("Luna Lovegood", "Gain 1💰; if you play an item, gain 1↯; roll the Ravenclaw die", 5, self.__effect)
        self._used_ability = False

    def __effect(self, game):
        self._used_ability = False
        game.heroes.active_hero.add_influence(game, 1)
        game.roll_ravenclaw_die()
        for card in game.heroes.active_hero._play_area:
            if card.is_item() and card != self:
                game.log(f"Item {card.name} already played, {self.name} adds 1↯")
                game.heroes.active_hero.add_damage(game, 1)
                return
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if card.is_item() and not self._used_ability:
            game.log(f"Item {card.name} played, {self.name} adds 1↯")
            game.heroes.active_hero.add_damage(game, 1)
            self._used_ability = True

def kingsley_effect(game):
    game.heroes.active_hero.add(game, damage=2, hearts=1)
    game.locations.remove_control(game)

game_five_cards = [
    Spell("Stupefy", "Gain 1↯; remove 1💀; draw a card", 6, stupefy_effect),
    Spell("Stupefy", "Gain 1↯; remove 1💀; draw a card", 6, stupefy_effect),
    Owls(),
    Owls(),
    Ally("Nymphadora Tonks", "Gain 3💰 or 2↯, or remove 1💀", 5, tonks_effect),
    Ally("Fred Weasley", "Gain 1↯; if another hero has a Weasley, ALL heroes gain 1💰; roll the Gryffindor die", 4, weasley_twin_effect("💰"), rolls_house_die=True),
    Ally("George Weasley", "Gain 1↯; if another hero has a Weasley, ALL heroes gain 1💜; roll the Gryffindor die", 4, weasley_twin_effect("💜"), rolls_house_die=True),
    Ally("Cho Chang", "Draw three cards, discard two; roll the Ravenclaw die", 4, cho_effect, rolls_house_die=True),
    LunaAlly(),
    Ally("Kingsley Shacklebolt", "Gain 2↯ and 1💜, remove 1💀", 7, kingsley_effect),
]

class Confundus(Spell):
    def __init__(self):
        super().__init__("Confundus", "Gain 1↯; if you damage each Villian, remove 1💀", 3, self.__effect)

    def __effect(self, game):
        game.heroes.active_hero.add_damage(game)
        if all([villain.took_damage for villain in game.villain_deck.all_villains]):
            game.log(f"Already damaged all villains, {self.name} removes 1💀")
            game.locations.remove_control(game)
            return
        self._used_ability = False
        game.heroes.active_hero.add_extra_damage_effect(game, self.__extra_effect)

    def __extra_effect(self, game, villain, damage):
        if all([villain.took_damage for villain in game.villain_deck.all_villains]) and not self._used_ability:
            game.log(f"Damaged all villains, {self.name} removes 1💀")
            game.locations.remove_control(game)
            self._used_ability = True

def bezoar_effect(game):
    if not game.heroes.healing_allowed:
        game.log("Healing not allowed!")
    else:
        game.heroes.choose_hero(game, prompt="Choose hero to gain 3💜: ").add_health(game, 3)
    game.heroes.active_hero.draw(game)

def advanced_potion_effect(game):
    game.heroes.all_heroes.add_health(game, 2)
    for hero in game.heroes:
        if hero._health == hero._max_health:
            game.log(f"{hero.name} at max health, gaining 1↯ and drawing a card")
            hero.add(game, damage=1, cards=1)

def felix_effect(game):
    first = game.input(f"Choose (d) 2↯, (i) 2💰, (h) 2💜, or (c) draw 2 cards: ", "dihc")
    if first == 'd':
        game.heroes.active_hero.add_damage(game, 2)
        second = game.input(f"Choose (i) 2💰, (h) 2💜, or (c) draw 2 cards: ", "ihc")
    elif first == 'i':
        game.heroes.active_hero.add_influence(game, 2)
        second = game.input(f"Choose (d) 2↯, (h) 2💜, or (c) draw 2 cards: ", "dhc")
    elif first == 'h':
        game.heroes.active_hero.add_health(game, 2)
        second = game.input(f"Choose (d) 2↯, (i) 2💰, or (c) draw 2 cards: ", "dic")
    elif first == 'c':
        game.heroes.active_hero.draw(game, 2)
        second = game.input(f"Choose (d) 2↯, (i) 2💰, (h) 2💜: ", "dih")

    if second == 'd':
        game.heroes.active_hero.add_damage(game, 2)
    elif second == 'i':
        game.heroes.active_hero.add_influence(game, 2)
    elif second == 'h':
        game.heroes.active_hero.add_health(game, 2)
    elif second == 'c':
        game.heroes.active_hero.draw(game, 2)

def add_if_spell(game, card):
    if card.is_spell():
        game.log(f"Spell {card.name} played, elder wand adds 1↯ and 1💜")
        game.heroes.active_hero.add(game, damage=1, hearts=1)

def elder_wand_effect(game):
    for card in game.heroes.active_hero._play_area:
        if card.is_spell():
            game.log(f"Spell {card.name} already played, elder wand adds 1↯ and 1💜")
            game.heroes.active_hero.add(game, damage=1, hearts=1)
    game.heroes.active_hero.add_extra_card_effect(game, add_if_spell)

def slughorn_effect(game):
    for hero in game.heroes.all_heroes:
        if not hero.healing_allowed:
            game.log(f"Horace Slughorn: {hero.name} can't heal, gaining 1💰")
            hero.add_influence(game, 1)
            continue
        if not hero.gaining_tokens_allowed(game):
            game.log(f"Horace Slughorn: {hero.name} not allowed to gain tokens, gaining 1💜")
            hero.add_health(game, 1)
            continue
        choice = game.input(f"Horace Slughorn: {hero.name} gains (i) 1💰 or (h) 1💜: ", "ih")
        if choice == 'i':
            hero.add_influence(game, 1)
        elif choice == 'h':
            hero.add_health(game, 1)
    game.roll_slytherin_die()

game_six_cards = [
    Confundus(),
    Confundus(),
    Item("Bezoar", "One hero gains 3💜; draw a card", 4, bezoar_effect),
    Item("Bezoar", "One hero gains 3💜; draw a card", 4, bezoar_effect),
    Item("Deluminator", "Remove 2💀", 6, lambda game: game.locations.remove_control(game, 2)),
    Item("Advanced Potion-Making", "ALL heroes gain 2💜; each hero at max gains 1↯ and draws a card", 6, advanced_potion_effect),
    Item("Felix Felicis", "Choose 2: gain 2↯, 2💰, 2💜, draw two cards", 7, felix_effect),
    Item("Felix Felicis", "Choose 2: gain 2↯, 2💰, 2💜, draw two cards", 7, felix_effect),
    Item("Elder Wand", "For each Spell played gain 1↯ and 1💜", 7, elder_wand_effect),
    Ally("Horace Slughorn", "ALL heroes gain 1💰 or 1💜; roll the Slytherin die", 6, slughorn_effect, rolls_house_die=True),
]

def sword_effect(game):
    game.heroes.active_hero.add_damage(game, 2)
    game.roll_gryffindor_die()
    game.roll_gryffindor_die()

game_seven_cards = [
    Item("Sword of Gryffindor", "Gain 2↯; Roll the Gryffindor die twice", 7, sword_effect, rolls_house_die=True)
]

monster_box_one_cards = [
    Spell("Tergeo", "Gain 1💰; you may banish a card in hand, if an Item, draw a card", 2),
    Spell("Tergeo", "Gain 1💰; you may banish a card in hand, if an Item, draw a card", 2),
    Spell("Tergeo", "Gain 1💰; you may banish a card in hand, if an Item, draw a card", 2),
    Spell("Tergeo", "Gain 1💰; you may banish a card in hand, if an Item, draw a card", 2),
    Spell("Tergeo", "Gain 1💰; you may banish a card in hand, if an Item, draw a card", 2),
    Spell("Tergeo", "Gain 1💰; you may banish a card in hand, if an Item, draw a card", 2),
    Spell("Finite Incantatem", "Remove 1💀; if in hand, reveal only 1 Dark Arts event", 6),
    Spell("Finite Incantatem", "Remove 1💀; if in hand, reveal only 1 Dark Arts event", 6),
    Item("Old Sock", "Gain 1💰; if another hero has an elf, gain 2↯; if discarded, gain 2💰", 1),
    Item("Old Sock", "Gain 1💰; if another hero has an elf, gain 2↯; if discarded, gain 2💰", 1),
    Item("Harp", "Gain 1↯, stun one Creature", 6),
    Ally("Fang", "One hero gain 1💰 and 2💜", 3, lambda game: game.heroes.choose_hero(game, prompt="Choose hero to gain 1💰 and 2💜: ").add(game, influence=1, hearts=2)),
    Ally("Argus Filch & Mrs Norris", "Draw two cards, then either discard or banish a card in hand", 4),
]

CARDS = [
    game_one_cards,
    game_two_cards,
    game_three_cards,
    game_four_cards,
    game_five_cards,
    game_six_cards,
    game_seven_cards,
    monster_box_one_cards,
]
