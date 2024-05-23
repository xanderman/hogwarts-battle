from collections import defaultdict
from functools import reduce

import curses
import itertools
import operator
import random

import constants

class HogwartsDeck(object):
    def __init__(self, window, chosen_cards):
        self._window = window
        self._init_window()
        self._pad = curses.newpad(100, 100)
        self._deck = [CARDS_BY_NAME[card_name]() for card_name in chosen_cards]
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


CARDS_BY_NAME = {}


class HogwartsCard(object):
    def __init__(self, name, description, cost, rolls_house_die=False):
        self.name = name
        self.description = description
        self.cost = cost
        self.rolls_house_die = rolls_house_die

    def display_state(self, window, i, count):
        window.addstr(f"{i}: ", curses.A_BOLD)
        self.display_name(window, curses.A_BOLD)
        window.addstr(f" x{count}\n", curses.color_pair(1) | curses.A_BOLD)
        window.addstr(f"     {self.description}\n")

    def display_name(self, window, attr=0):
        window.addstr(self.name, self.color | attr)
        window.addstr(f" ({self.cost}{constants.INFLUENCE})", attr)

    def __str__(self):
        return f"{self.name} ({self.cost}{constants.INFLUENCE}): {self.description}"

    def play(self, game):
        game.log(f"Playing {self}")
        self._effect(game)

    def _effect(self, game):
        raise NotImplementedError("Programmer Error! {self.name} effect not implemented!")

    def discard_effect(self, game, hero):
        pass

    def is_ally(self):
        return False

    def is_item(self):
        return False

    def is_spell(self):
        return False

    @property
    def even_cost(self):
        return self.cost != 0 and self.cost % 2 == 0

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


class WingardiumLeviosa(Spell):
    def __init__(self):
        super().__init__(
                "Wingardium Leviosa",
                f"Gain 1{constants.INFLUENCE}, may put acquired Items on top of deck",
                2)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game)
        game.heroes.active_hero.can_put_items_in_deck(game)

CARDS_BY_NAME['Wingardium Leviosa'] = WingardiumLeviosa


class Reparo(Spell):
    def __init__(self):
        super().__init__("Reparo", f"Gain 2{constants.INFLUENCE} or draw a card", 3)

    def _effect(self, game):
        if not game.heroes.active_hero.drawing_allowed:
            game.log(f"Drawing not allowed, gaining 2{constants.INFLUENCE}")
            game.heroes.active_hero.add_influence(game, 2)
            return
        choice = game.input(f"Choose effect: (i){constants.INFLUENCE}, (d)raw: ", "id")
        if choice == "i":
            game.heroes.active_hero.add_influence(game, 2)
        elif choice == "d":
            game.heroes.active_hero.draw(game)

CARDS_BY_NAME['Reparo'] = Reparo


class Lumos(Spell):
    def __init__(self):
        super().__init__("Lumos", "ALL heroes draw a card", 4)

    def _effect(self, game):
        game.heroes.all_heroes.draw(game)

CARDS_BY_NAME['Lumos'] = Lumos


class Incendio(Spell):
    def __init__(self):
        super().__init__("Incendio", f"Gain 1{constants.DAMAGE} and draw a card", 4)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=1, cards=1)

CARDS_BY_NAME['Incendio'] = Incendio


class Descendo(Spell):
    def __init__(self):
        super().__init__("Descendo", f"Gain 2{constants.DAMAGE}", 5)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game, 2)

CARDS_BY_NAME['Descendo'] = Descendo


class EssenceOfDittany(Item):
    def __init__(self):
        super().__init__("Essence of Dittany", f"Any hero gains 2{constants.HEART}", 2)

    def _effect(self, game):
        if not game.heroes.healing_allowed:
            game.log("Healing not allowed, ignoring Essence of Dittany effect")
            return
        while True:
            choice = int(game.input(f"Choose hero to gain 2{constants.HEART}: ", range(len(game.heroes))))
            hero = game.heroes[choice]
            if not hero.healing_allowed:
                game.log(f"{hero.name} cannot heal, choose another hero!")
                continue
            hero.add_hearts(game, 2)
            break

CARDS_BY_NAME['Essence of Dittany'] = EssenceOfDittany


class QuidditchGear(Item):
    def __init__(self):
        super().__init__("Quidditch Gear", f"Gain 1{constants.DAMAGE} and 1{constants.HEART}", 3)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=1, hearts=1)

CARDS_BY_NAME['Quidditch Gear'] = QuidditchGear


class SortingHat(Item):
    def __init__(self):
        super().__init__("Sorting Hat", f"Gain 2{constants.INFLUENCE}, may put acquired Allies on top of deck", 4)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game, 2)
        game.heroes.active_hero.can_put_allies_in_deck(game)

CARDS_BY_NAME['Sorting Hat'] = SortingHat


class GoldenSnitch(Item):
    def __init__(self):
        super().__init__("Golden Snitch", f"Gain 2{constants.INFLUENCE} and draw a card", 5)

    def _effect(self, game):
        game.heroes.active_hero.add(game, influence=2, cards=1)

CARDS_BY_NAME['Golden Snitch'] = GoldenSnitch


class OliverWood(Ally):
    def __init__(self):
        super().__init__("Oliver Wood", f"Gain 1{constants.DAMAGE}, if you defeat a Villain one hero gains 2{constants.HEART}", 3)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        game.heroes.active_hero.add_extra_villain_reward(game, self.__extra_villain_reward)

    def __extra_villain_reward(self, game):
        if not game.heroes.healing_allowed:
            game.log("Oliver Wood: Villain deafeted, but healing not allowed!")
            return
        game.heroes.choose_hero(game, prompt=f"Oliver Wood: Villain defeated! Choose hero to gain 2{constants.HEART}: ").add_hearts(game, 2)

CARDS_BY_NAME['Oliver Wood'] = OliverWood


class RubeusHagrid(Ally):
    def __init__(self):
        super().__init__("Rubeus Hagrid", f"Gain 1{constants.DAMAGE}; ALL heroes gain 1{constants.HEART}", 4)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        game.heroes.all_heroes.add_hearts(game)

CARDS_BY_NAME['Rubeus Hagrid'] = RubeusHagrid


class AlbusDumbledore(Ally):
    def __init__(self):
        super().__init__("Albus Dumbledore", f"ALL heroes gain 1{constants.DAMAGE}, 1{constants.INFLUENCE}, 1{constants.HEART}, and draw a card", 8)

    def _effect(self, game):
        game.heroes.all_heroes.add(game, damage=1, influence=1, hearts=1, cards=1)

CARDS_BY_NAME['Albus Dumbledore'] = AlbusDumbledore


class Finite(Spell):
    def __init__(self):
        super().__init__("Finite", f"Remove 1{constants.CONTROL}", 3)

    def _effect(self, game):
        game.locations.remove_control(game)

CARDS_BY_NAME['Finite'] = Finite


class Expelliarmus(Spell):
    def __init__(self):
        super().__init__("Expelliarmus", f"Gain 2{constants.DAMAGE} and draw a card", 6)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=2, cards=1)

CARDS_BY_NAME['Expelliarmus'] = Expelliarmus


class PolyjuicePotion(Item):
    def __init__(self):
        super().__init__("Polyjuice Potion", "Choose a played Ally and gain its effect", 3)

    def _effect(self, game):
        played_allies = [card for card in game.heroes.active_hero._play_area if card.is_ally()]
        if len(played_allies) == 0:
            game.log("You haven't played any allies, polyjuice wasted!")
            return
        if len(played_allies) == 1:
            game.log(f"Only one ally played, copying {played_allies[0].name}")
            played_allies[0]._effect(game)
            return
        while True:
            choice = int(game.input("Choose played ally to polyjuice: ", range(len(game.heroes.active_hero._play_area))))
            card = game.heroes.active_hero._play_area[choice]
            if not card.is_ally():
                game.log("{card.name} is not an ally!")
                continue
            game.log(f"Copying {card.name}")
            card._effect(game)
            break

CARDS_BY_NAME['Polyjuice Potion'] = PolyjuicePotion


class Nimbus2001(Item):
    def __init__(self):
        super().__init__("Nimbus 2001", f"Gain 2{constants.DAMAGE}; if you defeat a Villain, gain 2{constants.INFLUENCE}", 5)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=2)
        game.heroes.active_hero.add_extra_villain_reward(game, self.__villain_reward)

    def __villain_reward(self, game):
        game.heroes.active_hero.add_influence(game, 2)

CARDS_BY_NAME['Nimbus 2001'] = Nimbus2001


class Fawkes(Ally):
    def __init__(self):
        super().__init__("Fawkes", f"Gain 2{constants.DAMAGE} or ALL heroes gain 2{constants.HEART}", 5)

    def _effect(self, game):
        if not game.heroes.healing_allowed:
            game.log(f"Healing not allowed, gaining 2{constants.DAMAGE}")
            game.heroes.active_hero.add_damage(game, 2)
            return
        choice = game.input(f"Choose effect: (d){constants.DAMAGE}, (h){constants.HEART}: ", "dh")
        if choice == "d":
            game.heroes.active_hero.add_damage(game, 2)
        elif choice == "h":
            game.heroes.all_heroes.add_hearts(game, 2)

CARDS_BY_NAME['Fawkes'] = Fawkes


class MollyWeasley(Ally):
    def __init__(self):
        super().__init__("Molly Weasley", f"ALL heroes gain 1{constants.INFLUENCE} and 2{constants.HEART}", 6)

    def _effect(self, game):
        game.heroes.all_heroes.add(game, influence=1, hearts=2)

CARDS_BY_NAME['Molly Weasley'] = MollyWeasley


class Dobby(Ally):
    def __init__(self):
        super().__init__("Dobby", f"Remove 1{constants.CONTROL} and draw a card", 4)

    def _effect(self, game):
        game.locations.remove_control(game)
        game.heroes.active_hero.draw(game)

CARDS_BY_NAME['Dobby'] = Dobby


class ArthurWeasley(Ally):
    def __init__(self):
        super().__init__("Arthur Weasley", f"ALL heroes gain 2{constants.INFLUENCE}", 6)

    def _effect(self, game):
        game.heroes.all_heroes.add_influence(game, 2)

CARDS_BY_NAME['Arthur Weasley'] = ArthurWeasley


class GilderyLockhart(Ally):
    def __init__(self):
        super().__init__("Gilderoy Lockhart", f"Draw a card, then discard a card; if discarded, draw a card", 2)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.drawing_allowed:
            hero.draw(game)
        elif game.input("Drawing not allowed, still discard? (y/n): ", "yn") == 'n':
            return
        hero.choose_and_discard(game, with_callbacks=False)

    def discard_effect(self, game, hero):
        hero.draw(game)

CARDS_BY_NAME['Gilderoy Lockhart'] = GilderyLockhart


class GinnyWeasley(Ally):
    def __init__(self):
        super().__init__("Ginny Weasley", f"Gain 1{constants.DAMAGE} and 1{constants.INFLUENCE}", 4)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=1, influence=1)

CARDS_BY_NAME['Ginny Weasley'] = GinnyWeasley


class ExpectoPatronum(Spell):
    def __init__(self):
        super().__init__("Expecto Patronum", f"Gain 1{constants.DAMAGE}; remove 1{constants.CONTROL}", 5)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        game.locations.remove_control(game)

CARDS_BY_NAME['Expecto Patronum'] = ExpectoPatronum


class PetrificusTotalus(Spell):
    def __init__(self):
        super().__init__("Petrificus Totalus", f"Gain 1{constants.DAMAGE}; stun a Villain", 6)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        choices = game.villain_deck.villain_choices
        if len(choices) == 0:
            game.log("No villains to stun!")
            return
        choice = game.input("Choose villain to stun ('c' to cancel): ", ['c'] + choices)
        if choice == 'c':
            return
        game.villain_deck[choice].stun(game)

CARDS_BY_NAME['Petrificus Totalus'] = PetrificusTotalus


class ChocolateFrog(Item):
    def __init__(self):
        super().__init__("Chocolate Frog", f"One hero gains 1{constants.INFLUENCE} and 1{constants.HEART}; if discarded, gain 1{constants.INFLUENCE} and 1{constants.HEART}", 2)

    def _effect(self, game):
        game.heroes.choose_hero(game, prompt=f"Choose a hero to gain 1{constants.INFLUENCE} and 1{constants.HEART}: ").add(game, influence=1, hearts=1)

    def discard_effect(self, game, hero):
        hero.add(game, influence=1, hearts=1)

CARDS_BY_NAME['Chocolate Frog'] = ChocolateFrog


class Butterbeer(Item):
    def __init__(self):
        super().__init__("Butterbeer", f"Two heroes gain 1{constants.INFLUENCE} and 1{constants.HEART}", 3)

    def _effect(self, game):
        game.heroes.choose_two_heroes(game, prompt=f"to gain 1{constants.INFLUENCE} and 1{constants.HEART}: ").add(game, influence=1, hearts=1)

CARDS_BY_NAME['Butterbeer'] = Butterbeer


class CrystalBall(Item):
    def __init__(self):
        super().__init__("Crystal Ball", "Draw two cards; discard one card", 3)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.drawing_allowed:
            hero.draw(game, 2)
        elif game.input("Drawing not allowed, still discard? (y/n): ", "yn") == 'n':
            return
        hero.choose_and_discard(game, with_callbacks=False)

CARDS_BY_NAME['Crystal Ball'] = CrystalBall


class MaraudersMap(Item):
    def __init__(self):
        super().__init__("Marauder's Map", "Draw two cards; if discarded, ALL heroes draw a card", 5)

    def _effect(self, game):
        game.heroes.active_hero.draw(game, 2)

    def discard_effect(self, game, hero):
        game.heroes.all_heroes.draw(game)

CARDS_BY_NAME["Marauder's Map"] = MaraudersMap


class RemusLupin(Ally):
    def __init__(self):
        super().__init__("Remus Lupin", f"Gain 1{constants.DAMAGE}, any hero gains 3{constants.HEART}", 4)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        if not game.heroes.healing_allowed:
            game.log(f"Healing not allowed, ignoring Lupin's healing effect")
            return
        game.heroes.choose_hero(game, prompt=f"Choose hero to gain 3{constants.HEART}: ").add_hearts(game, 3)

CARDS_BY_NAME['Remus Lupin'] = RemusLupin


class SiriusBlack(Ally):
    def __init__(self):
        super().__init__("Sirius Black", f"Gain 2{constants.DAMAGE} and 1{constants.INFLUENCE}", 6)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=2, influence=1)

CARDS_BY_NAME['Sirius Black'] = SiriusBlack


class SybillTrelawney(Ally):
    def __init__(self):
        super().__init__(
            "Sybill Trelawney",
            f"Draw 2 cards; discard one card. If you discard a Spell, gain 2{constants.INFLUENCE}",
            4)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.drawing_allowed:
            hero.draw(game, 2)
        elif game.input("Drawing not allowed, still discard? (y/n): ", "yn") == 'n':
            return
        discarded = hero.choose_and_discard(game, with_callbacks=False)[0]
        if discarded.is_spell():
            game.log(f"Discarded spell, gaining 2{constants.INFLUENCE}")
            hero.add_influence(game, 2)

CARDS_BY_NAME['Sybill Trelawney'] = SybillTrelawney


class Accio(Spell):
    def __init__(self):
        super().__init__("Accio", f"Gain 2{constants.INFLUENCE} or take Item from discard", 4)

    def _effect(self, game):
        hero = game.heroes.active_hero
        items = hero.choices_in_discard(game, card_filter=lambda card: card.is_item())
        if len(items) == 0:
            game.log(f"{hero.name} has no items in discard, gaining 2{constants.INFLUENCE}")
            hero.add_influence(game, 2)
            return
        choices = ['i']
        choices.extend(items.keys())
        choice = game.input(f"Choose an item for {hero.name} to take, or (i) to gain 2{constants.INFLUENCE}: ", choices)
        if choice == 'i':
            hero.add_influence(game, 2)
            return
        item = items[choice]
        hero._discard.remove(item)
        hero._hand.append(item)

CARDS_BY_NAME['Accio'] = Accio


class Protego(Spell):
    def __init__(self):
        super().__init__("Protego", f"Gain 1{constants.DAMAGE} and 1{constants.HEART}; if discarded, gain 1{constants.DAMAGE} and 1{constants.HEART}", 5)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=1, hearts=1)

    def discard_effect(self, game, hero):
        hero.add(game, damage=1, hearts=1)

CARDS_BY_NAME['Protego'] = Protego


class HogwartsAHistory(Item):
    def __init__(self):
        super().__init__("Hogwarts: A History", "Roll any house die", 4, rolls_house_die=True)

    def _effect(self, game):
        choice = game.input(f"Choose house die to roll, (g)ryffindor, (h)ufflepuff, (r)avenclaw, (s)lytherin: ", "ghrs")
        if choice == "g":
            game.roll_gryffindor_die()
        elif choice == "h":
            game.roll_hufflepuff_die()
        elif choice == "r":
            game.roll_ravenclaw_die()
        elif choice == "s":
            game.roll_slytherin_die()

CARDS_BY_NAME['Hogwarts: A History'] = HogwartsAHistory


class Pensieve(Item):
    def __init__(self):
        super().__init__("Pensieve", f"Two heroes gain 1{constants.INFLUENCE} and draw a card", 5)

    def _effect(self, game):
        game.heroes.choose_two_heroes(game, prompt=f"to gain 1{constants.INFLUENCE} and draw a card: ").add(game, influence=1, cards=1)

CARDS_BY_NAME['Pensieve'] = Pensieve


class TriwizardCup(Item):
    def __init__(self):
        super().__init__("Triwizard Cup", f"Gain 1{constants.DAMAGE}, 1{constants.INFLUENCE}, and 1{constants.HEART}", 5)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=1, influence=1, hearts=1)

CARDS_BY_NAME['Triwizard Cup'] = TriwizardCup


class SeverusSnape(Ally):
    def __init__(self):
        super().__init__("Severus Snape", f"Gain 1{constants.DAMAGE} and 2{constants.HEART}; roll the Slytherin die", 6, rolls_house_die=True)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=1, hearts=2)
        game.roll_slytherin_die()

CARDS_BY_NAME['Severus Snape'] = SeverusSnape


class FleurDelacour(Ally):
    def __init__(self):
        super().__init__("Fleur Delacour", f"Gain 2{constants.INFLUENCE}; if you play another ally, gain 2{constants.HEART}", 4)
        self._used_ability = False

    def _effect(self, game):
        self._used_ability = False
        game.heroes.active_hero.add_influence(game, 2)
        for card in game.heroes.active_hero._play_area:
            if card.is_ally() and card != self:
                game.log(f"Ally {card.name} already played, {self.name} adds 2{constants.HEART}")
                game.heroes.active_hero.add_hearts(game, 2)
                return
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if card.is_ally() and card != self and not self._used_ability:
            game.log(f"Ally {card.name} played, {self.name} adds 2{constants.HEART}")
            game.heroes.active_hero.add_hearts(game, 2)
            self._used_ability = True

CARDS_BY_NAME['Fleur Delacour'] = FleurDelacour


class FiliusFlitwick(Ally):
    def __init__(self):
        super().__init__("Filius Flitwick", f"Gain 1{constants.INFLUENCE} and draw a card; roll the Ravenclaw die", 6, rolls_house_die=True)

    def _effect(self, game):
        game.heroes.active_hero.add(game, influence=1, cards=1)
        game.roll_ravenclaw_die()

CARDS_BY_NAME['Filius Flitwick'] = FiliusFlitwick


class CedricDiggory(Ally):
    def __init__(self):
        super().__init__("Cedric Diggory", f"Gain 1{constants.DAMAGE}; roll the Hufflepuff die", 4, rolls_house_die=True)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        game.roll_hufflepuff_die()

CARDS_BY_NAME['Cedric Diggory'] = CedricDiggory


class ViktorKrum(Ally):
    def __init__(self):
        super().__init__("Viktor Krum", f"Gain 2{constants.DAMAGE}, if you defeat a Villain gain 1{constants.INFLUENCE} and 1{constants.HEART}", 5)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game, 2)
        game.heroes.active_hero.add_extra_villain_reward(game, self.__villain_reward)

    def __villain_reward(self, game):
        game.heroes.active_hero.add(game, influence=1, hearts=1)

CARDS_BY_NAME['Viktor Krum'] = ViktorKrum


class MadEyeMoody(Ally):
    def __init__(self):
        super().__init__("Mad-eye Moody", f"Gain 2{constants.INFLUENCE}, remove 1{constants.CONTROL}", 6)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game, 2)
        game.locations.remove_control(game)

CARDS_BY_NAME['Mad-eye Moody'] = MadEyeMoody


class MinervaMcGonagall(Ally):
    def __init__(self):
        super().__init__("Minerva McGonagall", f"Gain 1{constants.INFLUENCE} and 1{constants.DAMAGE}; roll the Gryffindor die", 6, rolls_house_die=True)

    def _effect(self, game):
        game.heroes.active_hero.add(game, influence=1, damage=1)
        game.roll_gryffindor_die()

CARDS_BY_NAME['Minerva McGonagall'] = MinervaMcGonagall


class PomonaSprout(Ally):
    def __init__(self):
        super().__init__("Pomona Sprout", f"Gain 1{constants.INFLUENCE}; anyone gains 2{constants.HEART}; roll the Hufflepuff die", 6, rolls_house_die=True)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game)
        if not game.heroes.healing_allowed:
            game.log("Healing not allowed, skipping healing effect")
        else:
            game.heroes.choose_hero(game, prompt=f"Choose hero to gain 2{constants.HEART}: ").add_hearts(game, 2)
        game.roll_hufflepuff_die()

CARDS_BY_NAME['Pomona Sprout'] = PomonaSprout


class Stupefy(Spell):
    def __init__(self):
        super().__init__("Stupefy", f"Gain 1{constants.DAMAGE}; remove 1{constants.CONTROL}; draw a card", 6)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=1, cards=1)
        game.locations.remove_control(game)

CARDS_BY_NAME['Stupefy'] = Stupefy


class Owls(Item):
    def __init__(self):
        super().__init__("O.W.L.S.", f"Gain 2{constants.INFLUENCE}; if you play 2 spells, gain 1{constants.DAMAGE} and 1{constants.HEART}", 4)
        self._used_ability = False
        self._spells_played = 0

    def _effect(self, game):
        self._used_ability = False
        game.heroes.active_hero.add_influence(game, 2)
        self._spells_played = sum([1 for card in game.heroes.active_hero._play_area if card.is_spell()])
        if self._spells_played >= 2:
            game.log(f"Already played {self._spells_played} spells, gaining 1{constants.DAMAGE} and 1{constants.HEART}")
            game.heroes.active_hero.add(game, damage=1, hearts=1)
            return
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if card.is_spell():
            self._spells_played += 1
        if self._spells_played >= 2 and not self._used_ability:
            game.log(f"Second spell played, {self.name} adds 1{constants.DAMAGE} and 1{constants.HEART}")
            game.heroes.active_hero.add(game, damage=1, hearts=1)
            self._used_ability = True

CARDS_BY_NAME['O.W.L.S.'] = Owls


class NymphadoraTonks(Ally):
    def __init__(self):
        super().__init__("Nymphadora Tonks", f"Gain 3{constants.INFLUENCE} or 2{constants.DAMAGE}, or remove 1{constants.CONTROL}", 5)

    def _effect(self, game):
        if game.locations.can_remove_control:
            choice = game.input(f"Choose to (i) gain 3{constants.INFLUENCE}, (d) gain 2{constants.DAMAGE}, or (c) remove 1{constants.CONTROL}: ", "idc")
        elif game.locations.current._control == 0:
            choice = game.input(f"No {constants.CONTROL} to remove! Choose to (i) gain 3{constants.INFLUENCE}, (d) gain 2{constants.DAMAGE}: ", "id")
        else:
            choice = game.input(f"Removing {constants.CONTROL} not allowed! Choose to (i) gain 3{constants.INFLUENCE}, (d) gain 2{constants.DAMAGE}: ", "id")

        if choice == "i":
            game.heroes.active_hero.add_influence(game, 3)
        elif choice == "d":
            game.heroes.active_hero.add_damage(game, 2)
        elif choice == "c":
            game.locations.remove_control(game)

CARDS_BY_NAME['Nymphadora Tonks'] = NymphadoraTonks


class WeasleyTwin(Ally):
    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        game.roll_gryffindor_die()
        for hero in game.heroes:
            if hero == game.heroes.active_hero:
                continue
            for card in hero._hand:
                if 'Weasley' in card.name:
                    self._weasley_bonus(game, hero, card)

    def _weasley_bonus(self, game, hero, card):
        raise NotImplementedError("Programmer Error! {self.name} bonus not implemented!")


class FredWeasley(WeasleyTwin):
    def __init__(self):
        super().__init__("Fred Weasley", f"Gain 1{constants.DAMAGE}; if another hero has a Weasley, ALL heroes gain 1{constants.INFLUENCE}; roll the Gryffindor die", 4, rolls_house_die=True)

    def _weasley_bonus(self, game, hero, card):
        game.log(f"{hero.name} has {card.name}, ALL heroes gain 1{constants.INFLUENCE}")
        game.heroes.all_heroes.add_influence(game, 1)

CARDS_BY_NAME['Fred Weasley'] = FredWeasley


class GeorgeWeasley(WeasleyTwin):
    def __init__(self):
        super().__init__("George Weasley", f"Gain 1{constants.DAMAGE}; if another hero has a Weasley, ALL heroes gain 1{constants.HEART}; roll the Gryffindor die", 4, rolls_house_die=True)

    def _weasley_bonus(self, game, hero, card):
        game.log(f"{hero.name} has {card.name}, ALL heroes gain 1{constants.HEART}")
        game.heroes.all_heroes.add_hearts(game, 1)

CARDS_BY_NAME['George Weasley'] = GeorgeWeasley


class ChoChang(Ally):
    def __init__(self):
        super().__init__("Cho Chang", "Draw three cards, discard two; roll the Ravenclaw die", 4, rolls_house_die=True)

    def _effect(self, game):
        game.roll_ravenclaw_die()
        hero = game.heroes.active_hero
        if hero.drawing_allowed:
            hero.draw(game, 3)
        elif game.input("Drawing not allowed, still discard? (y/n): ", "yn") == 'n':
            return
        hero.choose_and_discard(game, 2, with_callbacks=False)

CARDS_BY_NAME['Cho Chang'] = ChoChang


class LunaAlly(Ally):
    def __init__(self):
        super().__init__("Luna Lovegood", f"Gain 1{constants.INFLUENCE}; if you play an item, gain 1{constants.DAMAGE}; roll the Ravenclaw die", 5, rolls_house_die=True)
        self._used_ability = False

    def _effect(self, game):
        self._used_ability = False
        game.heroes.active_hero.add_influence(game, 1)
        game.roll_ravenclaw_die()
        for card in game.heroes.active_hero._play_area:
            if card.is_item() and card != self:
                game.log(f"Item {card.name} already played, {self.name} adds 1{constants.DAMAGE}")
                game.heroes.active_hero.add_damage(game, 1)
                return
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if card.is_item() and not self._used_ability:
            game.log(f"Item {card.name} played, {self.name} adds 1{constants.DAMAGE}")
            game.heroes.active_hero.add_damage(game, 1)
            self._used_ability = True

CARDS_BY_NAME['Luna Lovegood'] = LunaAlly


class KingsleyShacklebolt(Ally):
    def __init__(self):
        super().__init__("Kingsley Shacklebolt", f"Gain 2{constants.DAMAGE} and 1{constants.HEART}; remove 1{constants.CONTROL}", 7)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=2, hearts=1)
        game.locations.remove_control(game)

CARDS_BY_NAME['Kingsley Shacklebolt'] = KingsleyShacklebolt


class Confundus(Spell):
    def __init__(self):
        super().__init__("Confundus", f"Gain 1{constants.DAMAGE}; if you damage each Villian, remove 1{constants.CONTROL}", 3)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        if all([villain.took_damage for villain in game.villain_deck.all_villains]):
            game.log(f"Already damaged all villains, {self.name} removes 1{constants.CONTROL}")
            game.locations.remove_control(game)
            return
        self._used_ability = False
        game.heroes.active_hero.add_extra_damage_effect(game, self.__extra_effect)

    def __extra_effect(self, game, villain, damage):
        if all([villain.took_damage for villain in game.villain_deck.all_villains]) and not self._used_ability:
            game.log(f"Damaged all villains, {self.name} removes 1{constants.CONTROL}")
            game.locations.remove_control(game)
            self._used_ability = True

CARDS_BY_NAME['Confundus'] = Confundus


class Bezoar(Item):
    def __init__(self):
        super().__init__("Bezoar", f"One hero gains 3{constants.HEART}; draw a card", 4)

    def _effect(self, game):
        if not game.heroes.healing_allowed:
            game.log("Healing not allowed!")
        else:
            game.heroes.choose_hero(game, prompt=f"Choose hero to gain 3{constants.HEART}: ").add_hearts(game, 3)
        game.heroes.active_hero.draw(game)

CARDS_BY_NAME['Bezoar'] = Bezoar


class Deluminator(Item):
    def __init__(self):
        super().__init__("Deluminator", f"Remove 2{constants.CONTROL}", 6)

    def _effect(self, game):
        game.locations.remove_control(game, 2)

CARDS_BY_NAME['Deluminator'] = Deluminator


class AdvancedPotionMaking(Item):
    def __init__(self):
        super().__init__("Advanced Potion-Making", f"ALL heroes gain 2{constants.HEART}; each hero at max gains 1{constants.DAMAGE} and draws a card", 6)

    def _effect(self, game):
        game.heroes.all_heroes.add_hearts(game, 2)
        for hero in game.heroes:
            if hero._hearts == hero._max_hearts:
                game.log(f"{hero.name} at max hearts, gaining 1{constants.DAMAGE} and drawing a card")
                hero.add(game, damage=1, cards=1)

CARDS_BY_NAME['Advanced Potion-Making'] = AdvancedPotionMaking


class FelixFelicis(Item):
    def __init__(self):
        super().__init__(
            "Felix Felicis",
            f"Choose 2: gain 2{constants.DAMAGE}, 2{constants.INFLUENCE}, 2{constants.HEART}, draw two cards",
            7)

    def _effect(self, game):
        choices = {'d': f"2{constants.DAMAGE}", 'i': f"2{constants.INFLUENCE}", 'h': f"2{constants.HEART}", 'c': "draw 2 cards"}
        if not game.heroes.active_hero.healing_allowed:
            game.log("Healing not allowed, removing hearts option")
            del(choices['h'])
        if not game.heroes.active_hero.drawing_allowed:
            game.log("Drawing not allowed, removing draw option")
            del(choices['c'])
        if len(choices) == 2:
            game.log(f"Only two options left, gaining 2{constants.DAMAGE} and 2{constants.INFLUENCE}")
            game.heroes.active_hero.add_damage(game, 2)
            game.heroes.active_hero.add_influence(game, 2)
            return
        for i in range(2):
            choice_str = ", ".join(f"({key}) {value}" for key, value in choices.items())
            choice = game.input(f"Choose {['first', 'second'][i]} {choice_str}: ", choices.keys())
            del(choices[choice])
            if choice == 'd':
                game.heroes.active_hero.add_damage(game, 2)
            elif choice == 'i':
                game.heroes.active_hero.add_influence(game, 2)
            elif choice == 'h':
                game.heroes.active_hero.add_hearts(game, 2)
            elif choice == 'c':
                game.heroes.active_hero.draw(game, 2)

CARDS_BY_NAME['Felix Felicis'] = FelixFelicis


class ElderWand(Item):
    def __init__(self):
        super().__init__("Elder Wand", f"For each Spell played gain 1{constants.DAMAGE} and 1{constants.HEART}", 7)

    def _effect(self, game):
        for card in game.heroes.active_hero._play_area:
            if card.is_spell():
                game.log(f"Spell {card.name} already played, elder wand adds 1{constants.DAMAGE} and 1{constants.HEART}")
                game.heroes.active_hero.add(game, damage=1, hearts=1)
        game.heroes.active_hero.add_extra_card_effect(game, self.__add_if_spell)

    def __add_if_spell(self, game, card):
        if card.is_spell():
            game.log(f"Spell {card.name} played, elder wand adds 1{constants.DAMAGE} and 1{constants.HEART}")
            game.heroes.active_hero.add(game, damage=1, hearts=1)

CARDS_BY_NAME['Elder Wand'] = ElderWand


class HoraceSlughorn(Ally):
    def __init__(self):
        super().__init__("Horace Slughorn", f"ALL heroes gain 1{constants.INFLUENCE} or 1{constants.HEART}; roll the Slytherin die", 6, rolls_house_die=True)

    def _effect(self, game):
        for hero in game.heroes.all_heroes:
            if not hero.healing_allowed:
                game.log(f"{hero.name} can't heal, gaining 1{constants.INFLUENCE}")
                hero.add_influence(game, 1)
                continue
            if not hero.gaining_tokens_allowed(game):
                game.log(f"{hero.name} not allowed to gain tokens, gaining 1{constants.HEART}")
                hero.add_hearts(game, 1)
                continue
            choice = game.input(f"Choose {hero.name} gains (i) 1{constants.INFLUENCE} or (h) 1{constants.HEART}: ", "ih")
            if choice == 'i':
                hero.add_influence(game, 1)
            elif choice == 'h':
                hero.add_hearts(game, 1)
        game.roll_slytherin_die()

CARDS_BY_NAME['Horace Slughorn'] = HoraceSlughorn


class SwordOfGryffindor(Item):
    def __init__(self):
        super().__init__("Sword of Gryffindor", f"Gain 2{constants.DAMAGE}; Roll the Gryffindor die twice", 7, rolls_house_die=True)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game, 2)
        game.roll_gryffindor_die()
        game.roll_gryffindor_die()

CARDS_BY_NAME['Sword of Gryffindor'] = SwordOfGryffindor


class Detention(Item):
    def __init__(self):
        super().__init__("Detention!", f"If you discard this, lose 2{constants.HEART}", 0)

    def _effect(self, game):
        pass

    def discard_effect(self, game, hero):
        hero.remove_hearts(game, 2)


class Tergeo(Spell):
    def __init__(self):
        super().__init__(
            "Tergeo",
            f"Gain 1{constants.INFLUENCE}; you may banish a card in hand, if an Item, draw a card",
            2)

    def _effect(self, game):
        hero = game.heroes.active_hero
        hero.add_influence(game, 1)
        if len(game.heroes.active_hero._hand) == 0:
            game.log("No cards in hand, skipping banish effect")
            return
        banished = hero.choose_and_banish(game, hand_only=True)
        if banished is not None and banished.is_item():
            hero.draw(game)

CARDS_BY_NAME['Tergeo'] = Tergeo


class FiniteIncantatem(Spell):
    def __init__(self):
        super().__init__(
            "Finite Incantatem",
            f"Remove 1{constants.CONTROL}; if in hand, reveal only 1 Dark Arts event",
            6)

    def _effect(self, game):
        game.locations.remove_control(game)

CARDS_BY_NAME['Finite Incantatem'] = FiniteIncantatem


class OldSock(Item):
    def __init__(self):
        super().__init__(
            "Old Sock",
            f"Gain 1{constants.INFLUENCE}; if another hero has an elf, gain 2{constants.DAMAGE}; if discarded, gain 2{constants.INFLUENCE}",
            1)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game, 1)
        for hero in game.heroes:
            if hero == game.heroes.active_hero:
                continue
            for card in hero._discard:
                if card.name == "Dobby" or card.name == "Kreacher":
                    game.log(f"{hero.name} has {card.name}, {self.name} adds 2{constants.DAMAGE}")
                    game.heroes.active_hero.add_damage(game, 2)
                    return

    def discard_effect(self, game, hero):
        hero.add_influence(game, 2)

CARDS_BY_NAME['Old Sock'] = OldSock


class Harp(Item):
    def __init__(self):
        super().__init__(
            "Harp",
            f"Gain 1{constants.DAMAGE}; stun one Creature",
            6)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game, 1)
        choices = game.villain_deck.creature_choices
        if len(choices) == 0:
            game.log("No creatures to stun!")
            return
        choice = game.input("Choose creature to stun ('c' to cancel): ", ['c'] + choices)
        if choice == 'c':
            return
        game.villain_deck[choice].stun(game)

CARDS_BY_NAME['Harp'] = Harp


class Fang(Ally):
    def __init__(self):
        super().__init__(
            "Fang",
            f"One hero gains 1{constants.INFLUENCE} and 2{constants.HEART}",
            3)

    def _effect(self, game):
        hero = game.heroes.choose_hero(game, prompt=f"Choose hero to gain 1{constants.INFLUENCE} and 2{constants.HEART}: ")
        hero.add(game, influence=1, hearts=2)

CARDS_BY_NAME['Fang'] = Fang


class Filch(Ally):
    def __init__(self):
        super().__init__(
            "Argus Filch & Mrs Norris",
            f"Draw two cards, then either discard or banish a card in hand",
            4)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.drawing_allowed:
            hero.draw(game, 2)
        elif game.input("Drawing not allowed, still discard/banish? (y/n): ", "yn") == 'n':
            return
        choice = game.input("Choose to (d)iscard or (b)anish a card: ", "db")
        if choice == 'd':
            game.heroes.active_hero.choose_and_discard(game)
        elif choice == 'b':
            game.heroes.active_hero.choose_and_banish(game, hand_only=True, optional=False)

CARDS_BY_NAME['Argus Filch & Mrs Norris'] = Filch


class Buckbeak(Ally):
    def __init__(self):
        super().__init__(
            "Buckbeak",
            f"Draw 2 cards; discard one card. If you discard an Ally, gain 2{constants.DAMAGE}",
            4)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.drawing_allowed:
            hero.draw(game, 2)
        elif game.input("Drawing not allowed, still discard? (y/n): ", "yn") == 'n':
            return
        discarded = hero.choose_and_discard(game, with_callbacks=False)[0]
        if discarded.is_ally():
            game.log(f"Discarded ally, gaining 2{constants.DAMAGE}")
            hero.add_damage(game, 2)

CARDS_BY_NAME['Buckbeak'] = Buckbeak


class MonsterBook(Item):
    def __init__(self):
        super().__init__(
            "Monster Book of Monsters",
            f"Gain 1{constants.DAMAGE}; roll the Creature die",
            5)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game, 1)
        game.roll_creature_die()

CARDS_BY_NAME['Monster Book of Monsters'] = MonsterBook


class Immobulus(Spell):
    def __init__(self):
        super().__init__(
            "Immobulus",
            f"Gain 1{constants.DAMAGE}; if you defeat a Creature, remove 1{constants.CONTROL}",
            3)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        game.heroes.active_hero.add_extra_creature_reward(game, self.__reward)

    def __reward(self, game):
        game.log(f"Defeated creature, {self.name} removes 1{constants.CONTROL}")
        game.locations.remove_control(game)

CARDS_BY_NAME['Immobulus'] = Immobulus


class Depulso(Spell):
    def __init__(self):
        super().__init__(
            "Depulso",
            f"Gain 2{constants.INFLUENCE} or banish an Item in your hand or discard",
            3)

    def _effect(self, game):
        banished = game.heroes.active_hero.choose_and_banish(game, desc="item", card_filter=lambda card: card.is_item(), cancel_with='i', cancel_desc=f"to gain 2{constants.INFLUENCE}")
        if banished is None:
            game.heroes.active_hero.add_influence(game, 2)

CARDS_BY_NAME['Depulso'] = Depulso


class Kreacher(Ally):
    def __init__(self):
        super().__init__(
            "Kreacher",
            f"Roll the Creature die. One hero may banish a card in hand or discard",
            5)

    def _effect(self, game):
        game.roll_creature_die()
        hero = game.heroes.choose_hero(game, prompt=f"Choose hero to banish a card (c to cancel): ", optional=True)
        if hero is not None:
          hero.choose_and_banish(game)

CARDS_BY_NAME['Kreacher'] = Kreacher


class Thestral(Ally):
    def __init__(self):
        super().__init__(
            "Thestral",
            f"ALL heroes choose to gain 1{constants.INFLUENCE} or 2{constants.HEART}",
            4)

    def _effect(self, game):
        for hero in game.heroes.all_heroes:
            if not hero.healing_allowed:
                game.log(f"{hero.name} can't heal, gaining 1{constants.INFLUENCE}")
                hero.add_influence(game, 1)
                continue
            if not hero.gaining_tokens_allowed(game):
                game.log(f"{hero.name} not allowed to gain tokens, gaining 2{constants.HEART}")
                hero.add_hearts(game, 2)
                continue
            choice = game.input(f"Choose {hero.name} gains (i) 1{constants.INFLUENCE} or (h) 2{constants.HEART}: ", "ih")
            if choice == 'i':
                hero.add_influence(game, 1)
            elif choice == 'h':
                hero.add_hearts(game, 2)

CARDS_BY_NAME['Thestral'] = Thestral


class Griphook(Ally):
    def __init__(self):
        super().__init__(
            "Griphook",
            f"Draw 3 cards; discard two. For each Item discarded, gain 2{constants.INFLUENCE}",
            6)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.drawing_allowed:
            hero.draw(game, 3)
        elif game.input("Drawing not allowed, still discard? (y/n): ", "yn") == 'n':
            return
        discarded = hero.choose_and_discard(game, 2, with_callbacks=False)
        for card in discarded:
            if card.is_item():
                game.log(f"Discarded item {card.name}, gaining 2{constants.INFLUENCE}")
                hero.add_influence(game, 2)

CARDS_BY_NAME['Griphook'] = Griphook


class ErumpentHorn(Item):
    def __init__(self):
        super().__init__(
            "Erumpent Horn",
            f"Lose 2{constants.HEART}; Gain 3{constants.DAMAGE}",
            5)

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 2)
        game.heroes.active_hero.add_damage(game, 3)

CARDS_BY_NAME['Erumpent Horn'] = ErumpentHorn


class LacewingFlies(Item):
    def __init__(self):
        super().__init__(
            "Lacewing Flies",
            f"One hero draws a card. If discarded, gain 1{constants.DAMAGE}",
            2)

    def _effect(self, game):
        if not game.heroes.drawing_allowed:
            game.log("Drawing not allowed, skipping draw effect")
            return
        game.heroes.choose_hero(game, prompt=f"Choose hero to draw a card: ").draw(game)

    def discard_effect(self, game, hero):
        hero.add_damage(game)

CARDS_BY_NAME['Lacewing Flies'] = LacewingFlies


class Nox(Spell):
    def __init__(self):
        super().__init__(
            "Nox",
            f"Gain 1{constants.DAMAGE}; ALL heroes may banish a card in hand or discard",
            6)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game, 1)
        game.heroes.all_heroes.choose_and_banish(game)

CARDS_BY_NAME['Nox'] = Nox


class MadameMaxime(Ally):
    def __init__(self):
        super().__init__(
            "Madame Maxime",
            f"Gain 2{constants.DAMAGE}; ALL Heroes gain 2{constants.HEART}",
            7)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game, 2)
        game.heroes.all_heroes.add_hearts(game, 2)

CARDS_BY_NAME['Madame Maxime'] = MadameMaxime


class IgorKarkaroff(Ally):
    def __init__(self):
        super().__init__(
            "Igor Karkaroff",
            f"Gain 2{constants.DAMAGE}; if you defeat a Villain, gain 1{constants.DAMAGE} and 1{constants.INFLUENCE}",
            5)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=2)
        game.heroes.active_hero.add_extra_villain_reward(game, self.__villain_reward)

    def __villain_reward(self, game):
        game.heroes.active_hero.add(game, damage=1, influence=1)

CARDS_BY_NAME['Igor Karkaroff'] = IgorKarkaroff


class GoldenEgg(Item):
    def __init__(self):
        super().__init__(
            "Golden Egg",
            f"Gain 2{constants.DAMAGE}, 1{constants.INFLUENCE}, and 1{constants.CARD}",
            7)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=2, influence=1, cards=1)

CARDS_BY_NAME['Golden Egg'] = GoldenEgg


class Gillyweed(Item):
    def __init__(self):
        super().__init__(
            "Gillyweed",
            f"Gain 1{constants.HEART}, for each Ally played one Hero gains 1{constants.HEART}",
            1)

    def _effect(self, game):
        game.heroes.active_hero.add_hearts(game)
        if not game.heroes.healing_allowed:
            game.log("Healing not allowed, ignoring Ally bonus")
        else:
            for card in game.heroes.active_hero._play_area:
                if card.is_ally():
                    game.log(f"Ally {card.name} already played, gillyweed grants {constants.HEART}")
                    game.heroes.choose_hero(game, prompt=f"Choose hero to gain 1{constants.HEART}: ").add_hearts(game)
        game.heroes.active_hero.add_extra_card_effect(game, self.__add_heart_if_ally)

    def __add_heart_if_ally(self, game, card):
        if not card.is_ally():
            return
        if not game.heroes.healing_allowed:
            game.log("Gillyweed: Healing not allowed, ignoring Ally bonus")
            return
        game.log(f"Ally {card.name} played, gillyweed grants {constants.HEART}")
        game.heroes.choose_hero(game, prompt=f"Choose hero to gain 1{constants.HEART}: ").add_hearts(game)

CARDS_BY_NAME['Gillyweed'] = Gillyweed


class DragonsBlood(Item):
    def __init__(self):
        super().__init__(
            "Dragon's Blood",
            f"ALL Heroes gain 3{constants.HEART}; You may assign 1 additional {constants.INFLUENCE} to Creatures this turn",
            5)

    def _effect(self, game):
        game.heroes.all_heroes.add_hearts(game, 3)
        for creature in game.villain_deck.all_creatures:
            creature._max_influence_per_turn += 1

CARDS_BY_NAME["Dragon's Blood"] = DragonsBlood


class PrioriIncantatem(Spell):
    def __init__(self):
        super().__init__(
            "Priori Incantatem",
            f"Choose a played Spell and gain its effect",
            3)

    def _effect(self, game):
        played_spells = [card for card in game.heroes.active_hero._play_area if card.is_spell()]
        if len(played_spells) == 0:
            game.log("You haven't played any spells, priori incantatem wasted!")
            return
        if len(played_spells) == 1:
            game.log(f"Only one spell played, copying {played_spells[0].name}")
            played_spells[0]._effect(game)
            return
        while True:
            choice = int(game.input("Choose played spell to polyjuice: ", range(len(game.heroes.active_hero._play_area))))
            card = game.heroes.active_hero._play_area[choice]
            if not card.is_spell():
                game.log("{card.name} is not an spell!")
                continue
            game.log(f"Copying {card.name}")
            card._effect(game)
            break

CARDS_BY_NAME['Priori Incantatem'] = PrioriIncantatem
