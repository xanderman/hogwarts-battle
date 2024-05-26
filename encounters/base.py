from functools import reduce

import curses
import operator

import constants


ENCOUNTERS_BY_NAME = {}


# In game 7 these are Horcurxes, but in the expansions the concept is generalized into Encounters.
class EncountersDeck(object):
    def __init__(self, window, config):
        self._title = config['title']
        self._null_encounter = NullEncounter(self._title, config['complete'])
        self._window = window
        self._init_window()
        self._pad = curses.newpad(100, 100)

        self._deck = [ENCOUNTERS_BY_NAME[name]() for name in config['deck']]
        self._current = self._deck.pop(0)

    def _init_window(self):
        self._window.box()
        self._window.addstr(0, 1, self._title)
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
        self._window.addstr(0, 1, f"{self._title} ({len(self._deck)} left)")
        self._window.noutrefresh()
        self._pad.clear()
        self.current.display_state(self._pad)
        self._pad.noutrefresh(0,0, self._pad_start_line,self._pad_start_col, self._pad_end_line,self._pad_end_col)

    def required_villains(self):
        return reduce(operator.add, [encounter.required_villains for encounter in self._deck])

    @property
    def current(self):
        return self._current

    @property
    def all_complete(self):
        if len(self._deck) > 0:
            return False
        return self._current == self._null_encounter or self._current.completed

    def play_turn(self, game):
        game.log(f"-----{self._title} phase-----")
        game.log(str(self._current))
        self._current.effect(game)

    def check_completion(self, game):
        self._current.end_turn(game)
        if not self._current.completed:
            return
        game.heroes.active_hero.add_encounter(game, self._current)
        self._current = self._deck.pop(0) if len(self._deck) > 0 else self._null_encounter
        self._current.on_reveal(game)


class Encounter(object):
    def __init__(self, name, description, reward_str, required_villains):
        self.name = name
        self.description = description
        self.required_villains = required_villains
        self.reward_str = reward_str
        self.completed = False
        self._complete_str = "complete"

    def __str__(self):
        if self.completed:
            return f"{self.name}: {self.reward_str}"
        return f"{self.name}: {self.description}"

    def display_state(self, window):
        window.addstr(f"{self.name}", curses.A_BOLD | curses.color_pair(1))
        if self.completed:
            window.addstr(f" ({constants.DISALLOW}!)", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f"\n{self.description}\n")
        window.addstr(f"To {self._complete_str}: ")
        self._display_to_complete(window)
        window.addstr(f"\nReward: {self.reward_str}\n")

    def _display_to_complete(self, window):
        raise ValueError(f"Programmer Error! Forgot to implement _display_to_complete for {self.name}")

    def die_roll_applies(self, game, result):
        return False

    def apply_die_roll(self, game, result):
        raise ValueError(f"Programmer Error! Die roll should not apply to {self.name}")

    def on_reveal(self, game):
        pass

    def effect(self, game):
        raise ValueError(f"Programmer Error! Forgot to implement effect for {self.name}")

    def end_turn(self, game):
        pass

    def reward_effect(self, game):
        raise ValueError(f"Programmer Error! Forgot to implement reward_effect for {self.name}")


class NullEncounter(Encounter):
    def __init__(self, title, complete_str):
        super().__init__("NullEncounter", "No encounter", "No reward", [])
        self._title = title
        self._complete_str = complete_str
        self.completed = False

    def __str__(self):
        return "Nothing to see here"

    def display_state(self, window):
        window.addstr(f"All {self._title} {self._complete_str}!\n", curses.A_BOLD | curses.color_pair(1))

    def effect(self, game):
        pass
