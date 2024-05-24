import curses

import constants

class Locations(object):
    # def __init__(self, window, game_num):
    def __init__(self, window, game_locations, num_heroes):
        self._window = window
        self._init_window()
        self._pad = curses.newpad(100, 100)

        self._locations = [LOCATIONS_BY_NAME[l](num_heroes) for l in game_locations]
        self._current = 0
        self._control_callbacks = []
        # simple ref counter of reasons why control cannot be removed
        self._control_remove_disallowed = 0

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

    @property
    def can_remove_control(self):
        return self._control_remove_disallowed == 0 and self.current._control > 0

    def allow_remove_control(self, game):
        self._control_remove_disallowed = max(0, self._control_remove_disallowed - 1)

    def disallow_remove_control(self, game):
        self._control_remove_disallowed += 1

    def add_control(self, game, amount=1):
        if amount < 0 and not self.can_remove_control:
            game.log(f"{constants.CONTROL} cannot be removed!")
            return
        self.current._add_control(game, amount, self._control_callbacks)

    def remove_control(self, game, amount=1):
        self.add_control(game, -amount)

    def is_controlled(self, game):
        return self.current._is_controlled()


class Location(object):
    def __init__(self, name, dark_arts_count, control_max, desc="", action=None):
        self.name = name
        self.dark_arts_count = dark_arts_count
        self._control_max = control_max
        self.desc = desc
        self.action = action

        self._control = 0

    def __str__(self):
        return f"{self.name} ({self._control}/{self._control_max}{constants.CONTROL}), {self.dark_arts_count} dark arts"

    def _reveal(self, game):
        game.log(f"Moving to location {self.name}! {self.desc}")
        self._reveal_effect(game)

    def _reveal_effect(self, game):
        pass

    def _add_control(self, game, amount, callbacks):
        control_start = self._control
        self._control += amount
        action = "added" if amount > 0 else "removed"
        if self._control > self._control_max:
            self._control = self._control_max
            game.log(f"{self.name} is full of {constants.CONTROL}! Only {action} {self._control - control_start}{constants.CONTROL}")
        if self._control < 0:
            self._control = 0
            game.log(f"{self.name} is empty of {constants.CONTROL}! Only {action} {abs(self._control - control_start)}{constants.CONTROL}")
        control_added = self._control - control_start
        if self._control != control_start:
            for callback in callbacks:
                callback.control_callback(game, control_added)

    def _is_controlled(self):
        return self._control == self._control_max


LOCATIONS_BY_NAME = {}


class DiagonAlley(Location):
    def __init__(self, _):
        super().__init__("Diagon Alley", 1, 4)

LOCATIONS_BY_NAME["Diagon Alley"] = DiagonAlley


class MirrorOfErised(Location):
    def __init__(self, _):
        super().__init__("Mirror of Erised", 1, 4)

LOCATIONS_BY_NAME["Mirror of Erised"] = MirrorOfErised


class ForbiddenForest(Location):
    def __init__(self, _):
        super().__init__("Forbidden Forest", 1, 4)

LOCATIONS_BY_NAME["Forbidden Forest"] = ForbiddenForest


class QuidditchPitch(Location):
    def __init__(self, _):
        super().__init__("Quidditch Pitch", 1, 4)

LOCATIONS_BY_NAME["Quidditch Pitch"] = QuidditchPitch


class ChamberOfSecrets(Location):
    def __init__(self, _):
        super().__init__("Chamber of Secrets", 2, 5)

LOCATIONS_BY_NAME["Chamber of Secrets"] = ChamberOfSecrets


class HogwartsExpress(Location):
    def __init__(self, _):
        super().__init__("Hogwarts Express", 1, 5)

LOCATIONS_BY_NAME["Hogwarts Express"] = HogwartsExpress


class HogsmeadeVillage(Location):
    def __init__(self, _):
        super().__init__("Hogsmeade Village", 2, 6)

LOCATIONS_BY_NAME["Hogsmeade Village"] = HogsmeadeVillage


class ShriekingShack(Location):
    def __init__(self, _):
        super().__init__("Shrieking Shack", 2, 6)

LOCATIONS_BY_NAME["Shrieking Shack"] = ShriekingShack


class QuidditchWorldCup(Location):
    def __init__(self, _):
        super().__init__("Quidditch World Cup", 1, 6)

LOCATIONS_BY_NAME["Quidditch World Cup"] = QuidditchWorldCup


class TriwizardTournament(Location):
    def __init__(self, _):
        super().__init__("Triwizard Tournament", 2, 6)

LOCATIONS_BY_NAME["Triwizard Tournament"] = TriwizardTournament


class Graveyard(Location):
    def __init__(self, _):
        super().__init__("Graveyard", 2, 7, "ALL heroes discard an ally")

    def _reveal_effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
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

LOCATIONS_BY_NAME["Graveyard"] = Graveyard


class Azkaban(Location):
    def __init__(self, _):
        super().__init__("Azkaban", 1, 7)

LOCATIONS_BY_NAME["Azkaban"] = Azkaban


class HallOfProphecy(Location):
    def __init__(self, _):
        super().__init__("Hall of Prophecy", 2, 7)

LOCATIONS_BY_NAME["Hall of Prophecy"] = HallOfProphecy


class MinistryOfMagic(Location):
    def __init__(self, _):
        super().__init__("Ministry of Magic", 2, 7, "ALL heroes discard a spell")

    def _reveal_effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
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

LOCATIONS_BY_NAME["Ministry of Magic"] = MinistryOfMagic


class KnockturnAlley(Location):
    def __init__(self, _):
        super().__init__("Knockturn Alley", 1, 7)

LOCATIONS_BY_NAME["Knockturn Alley"] = KnockturnAlley


class TheBurrow(Location):
    def __init__(self, _):
        super().__init__("The Burrow", 2, 7)

LOCATIONS_BY_NAME["The Burrow"] = TheBurrow


class AstronomyTower(Location):
    def __init__(self, _):
        super().__init__("Astronomy Tower", 3, 8, "ALL heroes discard an item")

    def _reveal_effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
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

LOCATIONS_BY_NAME["Astronomy Tower"] = AstronomyTower


class GodricsHollow(Location):
    def __init__(self, _):
        super().__init__("Godric's Hollow", 1, 6)

LOCATIONS_BY_NAME["Godric's Hollow"] = GodricsHollow


class Gringotts(Location):
    def __init__(self, _):
        super().__init__("Gringotts", 2, 6)

LOCATIONS_BY_NAME["Gringotts"] = Gringotts


class RoomOfRequirement(Location):
    def __init__(self, _):
        super().__init__("Room of Requirement", 2, 7)

LOCATIONS_BY_NAME["Room of Requirement"] = RoomOfRequirement


class HogwartsCastle(Location):
    def __init__(self, _):
        super().__init__("Hogwarts Castle", 3, 8, f"ALL heroes lose 2{constants.HEART}, may spend 5{constants.DAMAGE} to remove 1{constants.CONTROL}", ('H', "(H)ogwarts Castle", self._action))

    def _reveal_effect(self, game):
        game.heroes.all_heroes.remove_hearts(game, 2)

    def _action(self, game):
        if game.heroes.active_hero._damage_tokens < 5:
            game.log(f"Not enough {constants.DAMAGE} to use Hogwarts Castle")
            return
        game.heroes.active_hero.remove_damage(game, 5)
        game.locations.remove_control(game)

LOCATIONS_BY_NAME["Hogwarts Castle"] = HogwartsCastle


class CastleGates(Location):
    def __init__(self, _):
        super().__init__("Castle Gates", 1, 5)

LOCATIONS_BY_NAME["Castle Gates"] = CastleGates


class HagridsHut(Location):
    def __init__(self, _):
        super().__init__("Hagrid's Hut", 2, 6)

LOCATIONS_BY_NAME["Hagrid's Hut"] = HagridsHut


class GreatHallM1(Location):
    def __init__(self, _):
        super().__init__("Great Hall", 3, 7)

LOCATIONS_BY_NAME["Great Hall (m1)"] = GreatHallM1


class DADAClassroom(Location):
    def __init__(self, _):
        super().__init__("D.A.D.A. Classroom", 1, 6)

LOCATIONS_BY_NAME["D.A.D.A. Classroom"] = DADAClassroom


class CastleHallways(Location):
    def __init__(self, _):
        super().__init__("Castle Hallways", 2, 6)

LOCATIONS_BY_NAME["Castle Hallways"] = CastleHallways


class WhompingWillow(Location):
    def __init__(self, _):
        super().__init__("Whomping Willow", 3, 7)

LOCATIONS_BY_NAME["Whomping Willow"] = WhompingWillow


class UnicornHollow(Location):
    def __init__(self, _):
        super().__init__("Unicorn Hollow", 1, 5)

LOCATIONS_BY_NAME["Unicorn Hollow"] = UnicornHollow


class AragogsLair(Location):
    def __init__(self, _):
        super().__init__("Aragog's Lair", 2, 6)

LOCATIONS_BY_NAME["Aragog's Lair"] = AragogsLair


class GiantClearing(Location):
    def __init__(self, _):
        super().__init__("Giant Clearing", 3, 7)

LOCATIONS_BY_NAME["Giant Clearing"] = GiantClearing


class SelectionOfChampions(Location):
    def __init__(self, _):
        super().__init__("Selection of Champions", 1, 5)

LOCATIONS_BY_NAME["Selection of Champions"] = SelectionOfChampions


class DragonArena(Location):
    def __init__(self, _):
        super().__init__("Dragon Arena", 2, 6)

LOCATIONS_BY_NAME["Dragon Arena"] = DragonArena


class MermaidVillage(Location):
    def __init__(self, _):
        super().__init__("Mermaid Village", 2, 6)

LOCATIONS_BY_NAME["Mermaid Village"] = MermaidVillage


class TriwizardMaze(Location):
    def __init__(self, _):
        super().__init__("Triwizard Maze", 3, 7, f"Remove 1{constants.DAMAGE} and 1{constants.INFLUENCE} from ALL Creatures")

    def _reveal_effect(game):
        game.villain_deck.all_creatures.remove_damage(game, 1)
        game.villain_deck.all_creatures.remove_influence(game, 1)

LOCATIONS_BY_NAME["Triwizard Maze"] = TriwizardMaze


class TheBlackLake(Location):
    def __init__(self, _):
        super().__init__("The Black Lake", 1, 5)

LOCATIONS_BY_NAME["The Black Lake"] = TheBlackLake


class TheHospitalWing(Location):
    def __init__(self, num_heroes):
        super().__init__("The Hospital Wing", 2, 6 if num_heroes < 4 else 7)

LOCATIONS_BY_NAME["The Hospital Wing"] = TheHospitalWing


class TheHogwartsLibrary(Location):
    def __init__(self, _):
        super().__init__("The Hogwarts Library", 3, 7)

LOCATIONS_BY_NAME["The Hogwarts Library"] = TheHogwartsLibrary


class MinistryOfMagicAtrium(Location):
    def __init__(self, num_heroes):
        super().__init__("Ministry of Magic Atrium", 1, 5 if num_heroes < 4 else 6)

LOCATIONS_BY_NAME["Ministry of Magic Atrium"] = MinistryOfMagicAtrium


class MinistryCourtroom(Location):
    def __init__(self, num_heroes):
        super().__init__("Ministry Courtroom", 2, 6 if num_heroes < 4 else 7)

LOCATIONS_BY_NAME["Ministry Courtroom"] = MinistryCourtroom


class MinistryLift(Location):
    def __init__(self, _):
        super().__init__("Ministry Lift", 3, 7)

LOCATIONS_BY_NAME["Ministry Lift"] = MinistryLift


class MalfoyManor(Location):
    def __init__(self, _):
        super().__init__("Malfoy Manor", 1, 5)

LOCATIONS_BY_NAME["Malfoy Manor"] = MalfoyManor


class Cave(Location):
    def __init__(self, num_heroes):
        super().__init__("Cave", 2, 5 if num_heroes < 4 else 6)

LOCATIONS_BY_NAME["Cave"] = Cave


class AtopTheTower(Location):
    def __init__(self, num_heroes):
        super().__init__("Atop the Tower", 3, 6 if num_heroes < 4 else 7)

LOCATIONS_BY_NAME["Atop the Tower"] = AtopTheTower


class GreatHallP4(Location):
    def __init__(self, num_heroes):
        super().__init__("Great Hall", 1, 6 if num_heroes < 4 else 7)

LOCATIONS_BY_NAME["Great Hall (p4)"] = GreatHallP4


class ForestClearing(Location):
    def __init__(self, num_heroes):
        super().__init__("Forest Clearing", 2, 6 if num_heroes < 4 else 7)

LOCATIONS_BY_NAME["Forest Clearing"] = ForestClearing


class CastleCourtyard(Location):
    def __init__(self, num_heroes):
        super().__init__("Castle Courtyard", 3, 7 if num_heroes < 4 else 8)

LOCATIONS_BY_NAME["Castle Courtyard"] = CastleCourtyard
