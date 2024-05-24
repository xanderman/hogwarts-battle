from collections import defaultdict
from functools import reduce

import curses
import itertools
import operator
import random

import constants


CARDS_BY_NAME = {}


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


class _HogwartsCard(object):
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


class Ally(_HogwartsCard):
    def is_ally(self):
        return True

    @property
    def color(self):
        return curses.color_pair(3)


class Item(_HogwartsCard):
    def is_item(self):
        return True

    @property
    def color(self):
        return curses.color_pair(4)


class Spell(_HogwartsCard):
    def is_spell(self):
        return True

    @property
    def color(self):
        return curses.color_pair(2)


class _WeasleyTwin(Ally):
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
