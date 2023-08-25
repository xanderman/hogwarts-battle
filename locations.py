import curses

class Locations(object):
    def __init__(self, window):
        self._window = window
        self._locations = game_one_locations
        self._current = 0

    @property
    def current(self):
        return self._locations[self._current]

    def advance(self, game):
        callbacks = self.current._control_callbacks
        self._current = self._current + 1
        if self._current < len(self._locations):
            self.current._control_callbacks = callbacks
            self.current.reveal(game)
        return self._current < len(self._locations)

    def display_state(self):
        self._window.erase()
        for i in range(len(self._locations)):
            attr = curses.A_BOLD | curses.color_pair(1) if i == self._current else curses.A_NORMAL
            self._window.addstr(i+1, 1, f"{self._locations[i]}", attr)
        self._window.box()
        self._window.addstr(0, 1, "Locations")
        self._window.refresh()


class Location(object):
    def __init__(self, name, dark_arts_count, control_max, reveal_effect=lambda game: None):
        self.name = name
        self.dark_arts_count = dark_arts_count
        self._control_max = control_max
        self._reveal_effect = reveal_effect

        self._control = 0
        self._control_callbacks = []

    def __str__(self):
        return f"{self.name} ({self._control}/{self._control_max}💀), {self.dark_arts_count} dark arts"

    def reveal(self, game):
        self._reveal_effect(game)

    def add_control_callback(self, game, callback):
        self._control_callbacks.append(callback)

    def remove_control_callback(self, game, callback):
        self._control_callbacks.remove(callback)

    def add_control(self, game, amount=1):
        control_start = self._control
        self._control += amount
        if self._control > self._control_max:
            self._control = self._control_max
        if self._control < 0:
            self._control = 0
        if self._control != control_start:
            for callback in self._control_callbacks:
                callback.control_callback(game, self._control - control_start)

    def remove_control(self, game, amount=1):
        self.add_control(game, -amount)

    def is_controlled(self, game):
        return self._control == self._control_max


game_one_locations = [
    Location("Diagon Alley", 1, 4),
    Location("Mirror of Erised", 1, 4),
]
