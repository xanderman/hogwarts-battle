#!/opt/homebrew/bin/python3

from datetime import datetime

import argparse
import curses
import random

import locations
import dark_arts
import villains
import hogwarts
import heroes

class Game(object):
    def __init__(self, window, game_num, hero_names):
        self._window = window
        locations_window = window.subwin(7, curses.COLS // 2, 0, 0)
        self.locations = locations.Locations(locations_window, game_num)

        dark_arts_window = window.subwin(7, curses.COLS // 2, 0, curses.COLS // 2)
        self.dark_arts_deck = dark_arts.DarkArtsDeck(dark_arts_window, game_num)

        villains_window = window.subwin(15, curses.COLS // 2, 7, 0)
        self.villain_deck = villains.VillainDeck(villains_window, game_num)

        hogwarts_window = window.subwin(15, curses.COLS // 2, 7, curses.COLS // 2)
        self.hogwarts_deck = hogwarts.HogwartsDeck(hogwarts_window, game_num)

        self._heroes_window = window.subwin(40, curses.COLS, 22, 0)
        self.heroes = heroes.Heroes(self._heroes_window, game_num, hero_names)

        self._log_window = window.subwin(curses.LINES - 62, curses.COLS, 62, 0)
        self._log_window.box()
        self._log_window.addstr(0, 1, "Log")
        beg = self._log_window.getbegyx()
        self._log_start_line = beg[0] + 1
        self._log_start_col = beg[1] + 1
        end = self._log_window.getmaxyx()
        self._log_end_line = self._log_start_line + end[0] - 3
        self._log_end_col = self._log_start_col + end[1] - 3
        self._log_lines_to_show = self._log_end_line - self._log_start_line + 1
        self._last_log_line = 0
        self._log_pad = curses.newpad(1000, 1000)
        self._log_pad.scrollok(True)

        self.villain_deck.reveal(self)
        self.hogwarts_deck.refill_market(self)
        self._active_hero = 0
        self.heroes.all_heroes(self, lambda game, hero: hero.draw(game, 5, True))

        if self.heroes._harry:
            self.locations.add_control_callback(self, self.heroes._harry)

    def input(self, message, valid_choices=None):
        if isinstance(valid_choices, range):
            valid_choices = [str(i) for i in valid_choices]
        if valid_choices is None or len(valid_choices) == 0:
            raise ValueError("Programmer Error! no valid choices")
        self.log(message, curses.A_BOLD | curses.color_pair(1))
        self.display_state()
        while True:
            try:
                key = self._window.getkey()
                if key == "KEY_UP":
                    self.scroll_log_up()
                    continue
                if key == "KEY_DOWN":
                    self.scroll_log_down()
                    continue
                if key == " ":
                    self.scroll_log_to_bottom()
                    continue
                if key in valid_choices:
                    break
            except curses.error:
                # TODO not all subwindows handle screen resizes
                self.display_state()
        self._log_pad.addstr(key)
        return key

    def log(self, message, attr=curses.A_NORMAL):
        if not self._last_log_line == 0:
            self._log_pad.addstr("\n")
        self._log_pad.addstr(message, attr)
        self._last_log_line = min(self._last_log_line + 1, 1000)
        self._last_shown_log_line = self._last_log_line
        self._refresh_log()

    def scroll_log_up(self):
        if max(self._last_shown_log_line - self._log_lines_to_show, 0) != 0:
            self._last_shown_log_line -= 1
        self._refresh_log()

    def scroll_log_down(self):
        self._last_shown_log_line = min(self._last_log_line, self._last_shown_log_line + 1)
        self._refresh_log()

    def scroll_log_to_bottom(self):
        self._last_shown_log_line = self._last_log_line
        self._refresh_log()
        self.display_state()

    def _refresh_log(self):
        self._log_pad.refresh(max(self._last_shown_log_line - self._log_lines_to_show, 0),0, self._log_start_line,self._log_start_col, self._log_end_line,self._log_end_col)

    def display_state(self):
        self.locations.display_state()
        self.dark_arts_deck.display_state()
        self.villain_deck.display_state()
        self.hogwarts_deck.display_state()
        self.heroes.display_state()
        self._window.refresh()

    def play_turn(self):
        self.display_state()

        self.log("-----Turn start-----")
        self.dark_arts_deck.play_turn(self)
        self.villain_deck.play_turn(self)
        self.heroes.play_turn(self)

        self.log("-----Cleanup phase-----")
        self.heroes.all_heroes(self, lambda game, hero: hero.recover_from_stun(game))
        self.dark_arts_deck.end_turn()
        self.villain_deck.reveal(self)
        self.heroes.active_hero.end_turn(self)
        self.hogwarts_deck.refill_market(self)

        self.log("-----Turn end-----")
        self.heroes.next()

    def roll_gryffindor_die(self, times=1):
        for _ in range(times):
            self.log("Rolling Gryffindor die")
            self._roll_die("💰💰💰💜🃏↯")

    def roll_hufflepuff_die(self, times=1):
        for _ in range(times):
            self.log("Rolling Hufflepuff die")
            self._roll_die("💰💜💜💜🃏↯")

    def roll_ravenclaw_die(self, times=1):
        for _ in range(times):
            self.log("Rolling Ravenclaw die")
            self._roll_die("💰💜🃏🃏🃏↯")

    def roll_slytherin_die(self, times=1):
        for _ in range(times):
            self.log("Rolling Slytherin die")
            self._roll_die("💰💜🃏↯↯↯")

    def _roll_die(self, options):
        die_result = random.choice(options)
        if die_result == "↯":
            self.log("Rolled ↯, ALL heroes gain 1↯")
            self.heroes.all_heroes(self, lambda game, hero: hero.add_damage(game, 1))
        elif die_result == "💰":
            self.log("Rolled 💰, ALL heroes gain 1💰")
            self.heroes.all_heroes(self, lambda game, hero: hero.add_influence(game, 1))
        elif die_result == "💜":
            self.log("Rolled 💜, ALL heroes gain 1💜")
            self.heroes.all_heroes(self, lambda game, hero: hero.add_health(game, 1))
        elif die_result == "🃏":
            self.log("Rolled 🃏, ALL heroes draw a card")
            self.heroes.all_heroes(self, lambda game, hero: hero.draw(game))


def main(stdscr, game_num, hero_names):
    # For active hero & location, and input prompts
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    # For spells
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    # For allies
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    # For items
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    game = Game(stdscr, game_num, hero_names)
    while True:
        try:
            game.play_turn()
        except heroes.QuitGame:
            return False

        if len(game.villain_deck.current) == 0:
            return True

        if game.locations.is_controlled(game) and not game.locations.advance(game):
            return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Play Harry Potter: Hogwarts Battle")
    parser.add_argument("game_num", type=int, choices=range(1, 8))
    parser.add_argument("heroes", nargs="+", choices=heroes.HEROES.keys())
    # TODO this was suggested by copilot, and looks interesting
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    if len(args.heroes) > 4:
        print("Cannot play with more than 4 heroes")
        exit(1)

    seed = args.seed
    if seed is None:
        timestamp = datetime.now()
        seed = timestamp.hour*10000 + timestamp.minute*100 + timestamp.second
    print("Seed:", seed)
    random.seed(seed)

    if curses.wrapper(main, args.game_num, args.heroes):
        print("You won!")
    else:
        print("You lost!")
