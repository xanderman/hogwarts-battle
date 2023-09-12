#!/opt/homebrew/bin/python3

from datetime import datetime

import argparse
import curses
import random

import constants
import dark_arts
import encounters
import heroes
import hogwarts
import locations
import proficiencies
import villains

class Game(object):
    def __init__(self, window, game_num, chosen_heroes):
        self._window = window
        self._window.noutrefresh()
        if game_num < 7:
            locations_window = window.subwin(7, curses.COLS // 2, 0, 0)
            dark_arts_window = window.subwin(7, curses.COLS // 2, 0, curses.COLS // 2)
            self.encounters = None
        else:
            locations_window = window.subwin(7, curses.COLS // 3, 0, 0)
            enounters_window = window.subwin(7, curses.COLS // 3, 0, curses.COLS // 3)
            dark_arts_window = window.subwin(7, curses.COLS // 3, 0, curses.COLS * 2 // 3)
            self.encounters = encounters.EncountersDeck(enounters_window, game_num)

        self.locations = locations.Locations(locations_window, game_num)
        self.dark_arts_deck = dark_arts.DarkArtsDeck(dark_arts_window, game_num)

        villains_window = window.subwin(15, curses.COLS // 2, 7, 0)
        self.villain_deck = villains.VillainDeck(villains_window, game_num)

        hogwarts_window = window.subwin(15, curses.COLS // 2, 7, curses.COLS // 2)
        self.hogwarts_deck = hogwarts.HogwartsDeck(hogwarts_window, game_num)

        # self._heroes_height = 40 if len(chosen_heroes) > 2 else 20
        self._heroes_height = (curses.LINES - 22) // 4 * 3
        self._heroes_window = window.subwin(self._heroes_height, curses.COLS, 22, 0)
        self.heroes = heroes.Heroes(self._heroes_window, game_num, chosen_heroes)

        log_begin = 22 + self._heroes_height
        self._log_window = window.subwin(curses.LINES - log_begin, curses.COLS, log_begin, 0)
        self._init_log_window()
        self._last_log_line = 0
        self._log_pad = curses.newpad(1000, 1000)
        self._log_pad.scrollok(True)

        self.villain_deck.reveal(self)
        self.hogwarts_deck.refill_market(self)
        self._active_hero = 0
        self.heroes.all_heroes.draw(self, 5, True)

        if self.heroes._harry:
            self.locations.add_control_callback(self, self.heroes._harry)

    def _init_log_window(self):
        self._log_window.box()
        self._log_window.addstr(0, 1, "Log")
        self._log_window.noutrefresh()
        beg = self._log_window.getbegyx()
        self._log_start_line = beg[0] + 1
        self._log_start_col = beg[1] + 1
        end = self._log_window.getmaxyx()
        self._log_end_line = self._log_start_line + end[0] - 3
        self._log_end_col = self._log_start_col + end[1] - 3
        self._log_lines_to_show = self._log_end_line - self._log_start_line + 1

    def display_state(self, resize=False):
        if resize:
            curses.update_lines_cols()
            self._log_window.resize(curses.LINES - 22 - self._heroes_height, curses.COLS)
            self._init_log_window()
            self._refresh_log()

            self.hogwarts_deck._window.mvwin(7, curses.COLS // 2)
            if self.encounters is None:
                self.dark_arts_deck._window.mvwin(0, curses.COLS // 2)
            else:
                self.encounters._window.mvwin(0, curses.COLS // 3)
                self.dark_arts_deck._window.mvwin(0, curses.COLS * 2 // 3)
        if self.encounters is None:
            self.locations.display_state(resize=resize, size=(7, curses.COLS // 2))
            self.dark_arts_deck.display_state(resize=resize, size=(7, curses.COLS // 2))
        else:
            self.locations.display_state(resize=resize, size=(7, curses.COLS // 3))
            self.encounters.display_state(resize=resize, size=(7, curses.COLS // 3))
            self.dark_arts_deck.display_state(resize=resize, size=(7, curses.COLS // 3))
        self.villain_deck.display_state(self, resize=resize, size=(15, curses.COLS // 2))
        self.hogwarts_deck.display_state(resize=resize, size=(15, curses.COLS // 2))
        self.heroes.display_state(self, resize=resize, size=(self._heroes_height, curses.COLS))
        curses.doupdate()

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
                if key == "\t":
                    self.heroes.next_display_mode()
                    self.display_state()
                    continue
                if key in valid_choices:
                    break
            except curses.error:
                self.display_state(True)
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

    def play_turn(self):
        self.display_state()

        self.log("-----Turn start-----")
        self.dark_arts_deck.play_turn(self)
        if self.encounters is not None:
            self.encounters.play_turn(self)
        self.villain_deck.play_turn(self)
        self.heroes.play_turn(self)

        self.log("-----Cleanup phase-----")
        self.heroes.all_heroes.recover_from_stun(self)
        self.dark_arts_deck.end_turn()
        if self.encounters is not None:
            self.encounters.check_completion(self)
        self.villain_deck.reveal(self)
        self.heroes.active_hero.end_turn(self)
        self.hogwarts_deck.refill_market(self)

        self.log("-----Turn end-----")
        self.heroes.next()

    def roll_gryffindor_die(self, times=1):
        faces = [constants.INFLUENCE, constants.INFLUENCE, constants.INFLUENCE, constants.HEART, constants.CARD, constants.DAMAGE]
        for _ in range(times):
            self.log("Rolling Gryffindor die")
            self._roll_die(faces)

    def roll_hufflepuff_die(self, times=1):
        faces = [constants.INFLUENCE, constants.HEART, constants.HEART, constants.HEART, constants.CARD, constants.DAMAGE]
        for _ in range(times):
            self.log("Rolling Hufflepuff die")
            self._roll_die(faces)

    def roll_ravenclaw_die(self, times=1):
        faces = [constants.INFLUENCE, constants.HEART, constants.CARD, constants.CARD, constants.CARD, constants.DAMAGE]
        for _ in range(times):
            self.log("Rolling Ravenclaw die")
            self._roll_die(faces)

    def roll_slytherin_die(self, times=1):
        faces = [constants.INFLUENCE, constants.HEART, constants.CARD, constants.DAMAGE, constants.DAMAGE, constants.DAMAGE]
        for _ in range(times):
            self.log("Rolling Slytherin die")
            self._roll_die(faces)

    def _roll_die(self, options):
        die_result = random.choice(options)
        if self.heroes.active_hero._proficiency.can_reroll_house_dice and self.input(f"Rolled {die_result}, (a)ccept or (r)eroll?", "ar") == "r":
            die_result = random.choice(options)
        if (self.encounters is not None
            and self.encounters.current.die_roll_applies(self, die_result)
            and self.input(f"Rolled {die_result}, apply to {self.encounters.current.name}? (y/n): ", "yn") == "y"):
            self.encounters.current.apply_die_roll(self, die_result)
            return
        if die_result == constants.DAMAGE:
            self.log(f"Rolled {constants.DAMAGE}, ALL heroes gain 1{constants.DAMAGE}")
            self.heroes.all_heroes.add_damage(self, 1)
        elif die_result == constants.INFLUENCE:
            self.log(f"Rolled {constants.INFLUENCE}, ALL heroes gain 1{constants.INFLUENCE}")
            self.heroes.all_heroes.add_influence(self, 1)
        elif die_result == constants.HEART:
            self.log(f"Rolled {constants.HEART}, ALL heroes gain 1{constants.HEART}")
            self.heroes.all_heroes.add_hearts(self, 1)
        elif die_result == constants.CARD:
            self.log(f"Rolled {constants.CARD}, ALL heroes draw a card")
            self.heroes.all_heroes.draw(self)


def main(stdscr, game_num, chosen_heroes):
    # For active hero & location, and input prompts
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    # For spells
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    # For allies
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    # For items
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    game = Game(stdscr, game_num, chosen_heroes)
    while True:
        try:
            game.play_turn()
        except heroes.QuitGame:
            return False

        if len(game.villain_deck) == 0:
            return True

        if game.locations.is_controlled(game) and not game.locations.advance(game):
            return False

class HeroArgAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) > 4:
            parser.error("Cannot play with more than 4 heroes")
        game_num = namespace.game_num
        chosen_heroes = []
        for hero_name in values:
            parts = hero_name.split(":")
            if game_num < 6 and len(parts) > 1:
                parser.error(f"Proficiencies cannot be used in game {game_num}")
            if game_num >= 6 and len(parts) == 1:
                parser.error(f"Proficiencies must be specified in game {game_num}")
            if len(parts) > 2:
                parser.error(f"Heroes must be specified as 'NAME' or 'NAME:PROFICIENCY'")

            hero_name = parts[0]
            if hero_name not in heroes.HEROES:
                parser.error(f"Unknown hero: {hero_name}")

            if len(parts) == 2:
                proficiency_name = parts[1]
                if proficiency_name not in proficiencies.PROFICIENCIES:
                    parser.error(f"Unknown proficiency: {proficiency_name}")
                proficiency = proficiencies.PROFICIENCIES[proficiency_name]()
            else:
                proficiency = proficiencies.NullProficiency()
            chosen_heroes.append(heroes.HEROES[hero_name](game_num, proficiency))
        setattr(namespace, self.dest, chosen_heroes)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Play Harry Potter: Hogwarts Battle")
    parser.add_argument("game_num", metavar="GAME", type=int, choices=range(1, 8),
                        help="Game number to play, 1-7")
    parser.add_argument("heroes", metavar="HERO", nargs="+", action=HeroArgAction,
                        help=f"""Hero to play, min 1, max 4. For games 6 and up, specify as NAME:PROFICIENCY.
                        Valid names are {', '.join(heroes.HEROES.keys())}. Valid
                        proficiencies are {', '.join(proficiencies.PROFICIENCIES.keys())}.""")
    parser.add_argument("--seed", type=int, default=None, help="Random seed to use")
    args = parser.parse_args()

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
