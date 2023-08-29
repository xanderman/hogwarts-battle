import curses

class Locations(object):
    def __init__(self, window, game_num):
        self._window = window
        self._locations = LOCATIONS[game_num]
        self._current = 0
        self._control_callbacks = []
        self._control_remove_allowed = True

    @property
    def current(self):
        return self._locations[self._current]

    def advance(self, game):
        self._current = self._current + 1
        if self._current < len(self._locations):
            self.current._reveal(game)
        return self._current < len(self._locations)

    def display_state(self):
        self._window.clear()
        row = 1
        for i, location in enumerate(self._locations):
            attr = curses.A_BOLD | curses.color_pair(1) if i == self._current else curses.A_NORMAL
            self._window.addstr(row, 1, str(location), attr)
            row += 1
            if location.desc:
                self._window.addstr(row, 1, f"  Reveal: {location.desc}", attr)
                row += 1
        self._window.box()
        self._window.addstr(0, 1, "Locations")
        self._window.refresh()

    def add_control_callback(self, game, callback):
        self._control_callbacks.append(callback)

    def remove_control_callback(self, game, callback):
        self._control_callbacks.remove(callback)

    def allow_remove_control(self, game):
        self._control_remove_allowed = True

    def disallow_remove_control(self, game):
        self._control_remove_allowed = False

    def add_control(self, game, amount=1):
        if amount < 0 and not self._control_remove_allowed:
            game.log("💀 cannot be removed!")
            return
        self.current._add_control(game, amount, self._control_callbacks)

    def remove_control(self, game, amount=1):
        self.add_control(game, -amount)

    def is_controlled(self, game):
        return self.current._is_controlled()


class Location(object):
    def __init__(self, name, dark_arts_count, control_max, desc=None, reveal_effect=lambda game: None):
        self.name = name
        self.dark_arts_count = dark_arts_count
        self._control_max = control_max
        self.desc = desc
        self._reveal_effect = reveal_effect

        self._control = 0

    def __str__(self):
        return f"{self.name} ({self._control}/{self._control_max}💀), {self.dark_arts_count} dark arts"

    def _reveal(self, game):
        self._reveal_effect(game)

    def _add_control(self, game, amount, callbacks):
        control_start = self._control
        self._control += amount
        if self._control > self._control_max:
            self._control = self._control_max
        if self._control < 0:
            self._control = 0
        if self._control != control_start:
            for callback in callbacks:
                callback.control_callback(game, self._control - control_start)

    def _is_controlled(self):
        return self._control == self._control_max


game_one_locations = [
    Location("Diagon Alley", 1, 4),
    Location("Mirror of Erised", 1, 4),
]

game_two_locations = [
    Location("Forbidden Forest", 1, 4),
    Location("Quidditch Pitch", 1, 4),
    Location("Chamber of Secrets", 2, 5),
]

game_three_locations = [
    Location("Hogwarts Express", 1, 5),
    Location("Hogsmeade Village", 2, 6),
    Location("Shrieking Shack", 2, 6),
]

def graveyard_effect(game):
    pass

game_four_locations = [
    Location("Quidditch World Cup", 1, 6),
    Location("Triwizard Tournament", 2, 6),
    Location("Graveyard", 2, 7, "ALL heroes discard an ally", graveyard_effect),
]

def ministry_effect(game):
    pass

game_five_locations = [
    Location("Azkaban", 1, 7),
    Location("Hall of Prophecy", 2, 7),
    Location("Ministry of Magic", 2, 7, "ALL heroes discard a spell", ministry_effect),
]

def tower_effect(game):
    pass

game_six_locations = [
    Location("Knockturn Alley", 1, 7),
    Location("The Burrow", 2, 7),
    Location("Astronomy Tower", 3, 8, "ALL heroes discard an item", tower_effect),
]

def castle_effect(game):
    pass

game_seven_locations = [
    Location("Godric's Hollow", 1, 6),
    Location("Gringotts", 2, 6),
    Location("Room of Requirement", 2, 7),
    Location("Hogwarts Castle", 3, 8, "ALL heroes lose 2💜, may spend 5↯ to remove 1💀", castle_effect),
]

LOCATIONS = [
    -1,
    game_one_locations,
    game_two_locations,
    game_three_locations,
    game_four_locations,
    game_five_locations,
    game_six_locations,
    game_seven_locations,
]
