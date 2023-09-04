import curses

class Locations(object):
    def __init__(self, window, game_num):
        self._window = window
        self._init_window()
        self._pad = curses.newpad(100, 100)

        self._locations = LOCATIONS[game_num]
        self._current = 0
        self._control_callbacks = []
        self._control_remove_allowed = True

    def _init_window(self):
        self._window.box()
        self._window.addstr(0, 1, "Locations")
        self._window.noutrefresh()
        beg = self._window.getbegyx()
        self._pad_start_line = beg[0] + 1
        self._pad_start_col = beg[1] + 1
        end = self._window.getmaxyx()
        self._pad_end_line = self._pad_start_line + end[0] - 3
        self._pad_end_col = self._pad_start_col + end[1] - 3

    @property
    def current(self):
        return self._locations[self._current]

    def advance(self, game):
        self._current = self._current + 1
        if self._current < len(self._locations):
            self.current._reveal(game)
        return self._current < len(self._locations)

    def display_state(self, resize=False, size=None):
        if resize:
            self._window.resize(*size)
            self._window.clear()
            self._init_window()
        self._pad.clear()
        for i, location in enumerate(self._locations):
            attr = curses.A_BOLD | curses.color_pair(1) if i == self._current else curses.A_NORMAL
            self._pad.addstr(f"{location}\n", attr)
            if location.desc != "":
                self._pad.addstr(f"  Reveal: {location.desc}\n", attr)
        self._pad.noutrefresh(0,0, self._pad_start_line,self._pad_start_col, self._pad_end_line,self._pad_end_col)

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
    def __init__(self, name, dark_arts_count, control_max, desc="", reveal_effect=lambda game: None):
        self.name = name
        self.dark_arts_count = dark_arts_count
        self._control_max = control_max
        self.desc = desc
        self._reveal_effect = reveal_effect

        self._control = 0

    def __str__(self):
        return f"{self.name} ({self._control}/{self._control_max}💀), {self.dark_arts_count} dark arts"

    def _reveal(self, game):
        game.log(f"Moving to location {self.name}! {self.desc}")
        self._reveal_effect(game)

    def _add_control(self, game, amount, callbacks):
        control_start = self._control
        self._control += amount
        action = "added" if amount > 0 else "removed"
        if self._control > self._control_max:
            self._control = self._control_max
            game.log(f"{self.name} is full of 💀! Only {action} {self._control - control_start}💀")
        if self._control < 0:
            self._control = 0
            game.log(f"{self.name} is empty of 💀! Only {action} {self._control - control_start}💀")
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

def graveyard_effect(game, hero):
    allies = sum(1 for card in hero._hand if card.is_ally())
    if allies == 0:
        game.log(f"{hero.name} has no allies to discard, safe!")
        return
    while True:
        choice = int(game.input(f"Choose an ally for {hero.name} to discard: ", range(len(hero._hand))))
        card = hero._hand[choice]
        if not card.is_ally():
            game.log(f"{card.name} is not an ally!")
            continue
        hero.discard(game, choice)
        break

game_four_locations = [
    Location("Quidditch World Cup", 1, 6),
    Location("Triwizard Tournament", 2, 6),
    Location("Graveyard", 2, 7, "ALL heroes discard an ally", lambda game: game.heroes.all_heroes.effect(game, graveyard_effect)),
]

def ministry_effect(game, hero):
    spells = sum(1 for card in hero._hand if card.is_spell())
    if spells == 0:
        game.log(f"{hero.name} has no spells to discard, safe!")
        return
    while True:
        choice = int(game.input(f"Choose a spell for {hero.name} to discard: ", range(len(hero._hand))))
        card = hero._hand[choice]
        if not card.is_spell():
            game.log(f"{card.name} is not a spell!")
            continue
        hero.discard(game, choice)
        break

game_five_locations = [
    Location("Azkaban", 1, 7),
    Location("Hall of Prophecy", 2, 7),
    Location("Ministry of Magic", 2, 7, "ALL heroes discard a spell", lambda game: game.heroes.all_heroes.effect(game, ministry_effect)),
]

def tower_effect(game, hero):
    items = sum(1 for card in hero._hand if card.is_item())
    if items == 0:
        game.log(f"{hero.name} has no items to discard, safe!")
        return
    while True:
        choice = int(game.input(f"Choose an item for {hero.name} to discard: ", range(len(hero._hand))))
        card = hero._hand[choice]
        if not card.is_item():
            game.log(f"{card.name} is not an item!")
            continue
        hero.discard(game, choice)
        break

game_six_locations = [
    Location("Knockturn Alley", 1, 7),
    Location("The Burrow", 2, 7),
    Location("Astronomy Tower", 3, 8, "ALL heroes discard an item", lambda game: game.heroes.all_heroes.effect(game, tower_effect)),
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
