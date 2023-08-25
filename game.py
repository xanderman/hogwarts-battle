#!/usr/bin/python3

import curses
from curses import wrapper

import locations
import dark_arts
import villains
import hogwarts
import heroes

class Game(object):
    def __init__(self, window):
        self._window = window
        locations_window = window.subwin(7, curses.COLS // 2, 0, 0)
        self.locations = locations.Locations(locations_window)

        dark_arts_window = window.subwin(7, curses.COLS // 2, 0, curses.COLS // 2)
        self.dark_arts_deck = dark_arts.DarkArtsDeck(dark_arts_window)

        villains_window = window.subwin(15, curses.COLS // 2, 7, 0)
        self.villain_deck = villains.VillainDeck(villains_window, max_villains=2)

        hogwarts_window = window.subwin(15, curses.COLS // 2, 7, curses.COLS // 2)
        hogwarts_window.box()
        self.hogwarts_deck = hogwarts.HogwartsDeck(hogwarts_window)

        self._heroes_window = window.subwin(40, curses.COLS, 22, 0)
        self._heroes_window.box()
        self._heroes_window.addstr(0, 1, "Heroes")
        self.heroes = heroes.Heroes(self._heroes_window)

        self._log_window = window.subwin(curses.LINES - 62, curses.COLS, 62, 0)
        self._log_window.box()
        self._log_window.addstr(0, 1, "Log")
        self._max_logs = curses.LINES - 64
        self._logs = []

        self.villain_deck.reveal(self)
        self.hogwarts_deck.refill_market()
        self._active_hero = 0
        self.all_heroes(lambda game, hero: hero.draw(game, 5))

    def input(self, message, valid_choices=None):
        self.display_state()
        self.log(message, curses.A_BOLD | curses.color_pair(1))
        key = self._window.getkey()
        self._logs[-1][0] += key
        return key

    def log(self, message, attr=curses.A_NORMAL):
        self._logs.append([message, attr])
        if len(self._logs) > self._max_logs:
            self._logs.pop(0)
        self._log_window.clear()
        self._log_window.box()
        self._log_window.addstr(0, 1, "Log")
        for i, (message, attr) in enumerate(self._logs):
            self._log_window.addstr(i + 1, 1, message, attr)
        self._log_window.refresh()

    def display_state(self):
        self.locations.display_state()
        self.villain_deck.display_state()
        self.hogwarts_deck.display_state()
        self.heroes.display_state()
        self._window.refresh()

    @property
    def active_hero(self):
        return self.heroes.active_hero

    def choose_hero(self):
        return self.heroes.choose_hero(self)

    def all_heroes(self, effect):
        return self.heroes.all_heroes(self, effect)

    def play_turn(self):
        self.display_state()

        self.log("-----Turn start-----")
        self.play_dark_arts()
        self.play_villains()
        self.active_hero.play_turn(self)

        self.log("-----Cleanup phase-----")
        self.hogwarts_deck.refill_market()
        self.villain_deck.reveal(self)
        self.all_heroes(lambda game, hero: hero.recover_from_stun(game))

        self.log("-----Turn end-----")
        self.heroes.next()

    def play_dark_arts(self):
        self.log("-----Dark Arts phase-----")
        self.dark_arts_deck.play(self.locations.current.dark_arts_count, self)

    def play_villains(self):
        self.log("-----Villain phase-----")
        for villain in self.villain_deck.current:
            self.log(f"Villain: {villain}")
            villain.effect(self)

    def add_control_callback(self, callback):
        self.locations.current.add_control_callback(self, callback)

    def remove_control_callback(self, callback):
        self.locations.current.remove_control_callback(self, callback)

    def add_discard_callback(self, callback):
        self.heroes.add_discard_callback(self, callback)

    def remove_discard_callback(self, callback):
        self.heroes.remove_discard_callback(self, callback)


def main(stdscr):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    game = Game(stdscr)
    while True:
        try:
            game.play_turn()
        except heroes.QuitGame:
            return False

        if len(game.villain_deck.current) == 0:
            return True

        if game.locations.current.is_controlled(game) and not game.locations.advance(game):
            return False

if __name__ == '__main__':
    if wrapper(main):
        print("You won!")
    else:
        print("You lost!")
