from collections import Counter
import curses

from . import ENCOUNTERS_BY_NAME, Encounter
import constants


class TheFirstTask(Encounter):
    def __init__(self):
        super().__init__(
            "The First Task",
            f"If you assign 2{constants.DAMAGE} to a foe, lose 2{constants.HEART}",
            f"1/game: discard this; roll any two House dice",
            ["Chinese Fireball", "Common Welsh Green", "Hungarian Horntail", "Swedish Short-Snout"])
        self._influence_spent = 0
        self._damaged_foes = Counter()
        self._used_ability = set()

    def _display_to_complete(self, window):
        window.addstr(f"Acquire Items with total cost >= 7{constants.INFLUENCE} in one turn")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" {self._influence_spent}/7", curses.A_BOLD)

    def on_reveal(self, game):
        game.heroes.add_acquire_callback(game, self)

    def acquire_callback(self, game, hero, card):
        if card.is_item():
            self._influence_spent += card.cost
        if self._influence_spent >= 7:
            self.completed = True
            game.heroes.remove_acquire_callback(game, self)

    def effect(self, game):
        self._damaged_foes = Counter()
        self._used_ability = set()
        game.heroes.active_hero.add_extra_damage_effect(game, self.__extra_effect)
        self._influence_spent = 0

    def __extra_effect(self, game, villain, damage):
        if self.completed:
            return
        self._damaged_foes[villain] += damage
        if self._damaged_foes[villain] >= 2 and villain not in self._used_ability:
            self._used_ability.add(villain)
            game.log(f"{self.name}: {game.heroes.active_hero.name} assigned 2{constants.DAMAGE} to {villain.name}, loses 2{constants.HEART}")
            game.heroes.active_hero.remove_hearts(game, 2)

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'F', "(F)irst Task", self.__reward_action)

    def __reward_action(self, game):
        game.log(f"{self.name} discarded; roll any two House dice")
        game.heroes.active_hero._encounters.remove(self)
        game.heroes.active_hero.remove_action(game, 'F')
        choice = game.input("Choose first die to roll (Gryffindor, Hufflepuff, Ravenclaw, Slytherin): ", ["G", "H", "R", "S"])
        if choice == "G":
            game.roll_gryffindor_die()
        elif choice == "H":
            game.roll_hufflepuff_die()
        elif choice == "R":
            game.roll_ravenclaw_die()
        elif choice == "S":
            game.roll_slytherin_die()
        choice = game.input("Choose second die to roll (Gryffindor, Hufflepuff, Ravenclaw, Slytherin): ", ["G", "H", "R", "S"])
        if choice == "G":
            game.roll_gryffindor_die()
        elif choice == "H":
            game.roll_hufflepuff_die()
        elif choice == "R":
            game.roll_ravenclaw_die()
        elif choice == "S":
            game.roll_slytherin_die()

ENCOUNTERS_BY_NAME['The First Task'] = TheFirstTask


class TheSecondTask(Encounter):
    def __init__(self):
        super().__init__(
            "The Second Task",
            f"If you don't have an Ally, add 1{constants.CONTROL}",
            f"1/game: discard this; remove 1{constants.CONTROL}, ALL Heroes draw a card",
            ["Mermaid", "Grindylow"])
        self._allies_acquired = 0

    def _display_to_complete(self, window):
        window.addstr(f"Acquire 2 Allies in one turn")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" {self._allies_acquired}/2", curses.A_BOLD)

    def on_reveal(self, game):
        game.heroes.add_acquire_callback(game, self)

    def acquire_callback(self, game, hero, card):
        if card.is_ally():
            self._allies_acquired += 1
            if self._allies_acquired >= 2:
                self.completed = True
                game.heroes.remove_acquire_callback(game, self)

    def effect(self, game):
        self._allies_acquired = 0
        hero = game.heroes.active_hero
        allies = sum(1 for card in hero._hand if card.is_ally())
        if allies == 0:
            game.log(f"{self.name}: {game.heroes.active_hero.name} doesn't have an Ally, adding 1{constants.CONTROL}")
            game.locations.add_control(game)

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'S', "(S)econd Task", self.__reward_action)

    def __reward_action(self, game):
        game.log(f"{self.name} discarded; remove 1{constants.CONTROL}, ALL Heroes draw a card")
        game.heroes.active_hero._encounters.remove(self)
        game.heroes.active_hero.remove_action(game, 'S')
        game.locations.remove_control(game)
        game.heroes.all_heroes.draw(game)

ENCOUNTERS_BY_NAME['The Second Task'] = TheSecondTask


class TheThirdTask(Encounter):
    def __init__(self):
        super().__init__(
            "The Third Task",
            f"Lose 2{constants.HEART}",
            f"1/game: discard this; ALL Heroes heal to full",
            [])
        self._got_heart = 0

    def _display_to_complete(self, window):
        window.addstr(f"roll 3{constants.HEART}")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" {self._got_heart}/3", curses.A_BOLD)

    def die_roll_applies(self, game, result):
        if self.completed:
            return False
        return result == constants.HEART or result == (constants.HEART + constants.HEART)

    def apply_die_roll(self, game, result):
        if result == constants.HEART:
            self._got_heart += 1
        elif result == (constants.HEART + constants.HEART):
            self._got_heart += 2
        else:
            raise ValueError(f"Programmer Error! The Third Task only applies to {constants.HEART}")
        if self._got_heart >= 3:
            self.completed = True

    def effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 2)

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'T', "(T)hird Task", self.__reward_action)

    def __reward_action(self, game):
        game.log(f"{self.name} discarded; remove 1{constants.CONTROL}, ALL Heroes gain 2{constants.INFLUENCE}")
        game.heroes.active_hero._encounters.remove(self)
        game.heroes.active_hero.remove_action(game, 'T')
        game.locations.remove_control(game)
        game.heroes.all_heroes.add_influence(game, 2)

ENCOUNTERS_BY_NAME['The Third Task'] = TheThirdTask
