import curses

from . import ENCOUNTERS_BY_NAME, Encounter
import constants


class UnregisteredAnimagus(Encounter):
    def __init__(self):
        super().__init__(
            "Unregistered Animagus",
            f"If there are >= 2{constants.CONTROL}, lose 1{constants.HEART}",
            f"1/game: discard this; roll the Creature die twice",
            ["Scabbers", "Peter Pettigrew"])
        self._damage_assigned = 0

    def _display_to_complete(self, window):
        window.addstr(f"Assign 5{constants.DAMAGE} in one turn")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" {self._damage_assigned}/5", curses.A_BOLD)

    def effect(self, game):
        self._damage_assigned = 0
        game.heroes.active_hero.add_extra_damage_effect(game, self.__extra_effect)
        if game.locations.current._control >= 2:
            game.log(f"{self.name}: {game.locations.current._control}{constants.CONTROL} on location! {game.heroes.active_hero.name} loses 1{constants.HEART}")
            game.heroes.active_hero.remove_hearts(game)

    def __extra_effect(self, game, creature, amount):
        if self.completed:
            return
        self._damage_assigned += amount
        if self._damage_assigned >= 5:
            self.completed = True

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'U', "(U)nregistered Anumagus", self.__reward_action)

    def __reward_action(self, game):
        game.log(f"{self.name} discarded to roll Creature die twice")
        game.heroes.active_hero._encounters.remove(self)
        game.heroes.active_hero.remove_action(game, 'U')
        game.roll_creature_die()
        game.roll_creature_die()

ENCOUNTERS_BY_NAME['Unregistered Animagus'] = UnregisteredAnimagus


class FullMoonRises(Encounter):
    def __init__(self):
        super().__init__(
            "Full Moon Rises",
            f"Each time {constants.CONTROL} is added active Hero adds a Detention! to hand",
            f"1/game: discard this; ALL heroes gain 3{constants.HEART} and may banish a card in hand or discard",
            ["Werewolf", "Fenrir Greyback"])
        self._foes_defeated = 0

    def _display_to_complete(self, window):
        window.addstr(f"Defeat 3 foes in one turn")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" {self._foes_defeated}/3", curses.A_BOLD)

    def on_reveal(self, game):
        game.locations.add_control_callback(game, self)

    def control_callback(self, game, amount):
        if self.completed or amount < 1:
            return
        game.log(f"{self.name}: {amount}{constants.CONTROL} added, {game.heroes.active_hero.name} adds a Detention! to hand for each")
        for _ in range(amount):
            game.heroes.active_hero.add_detention(game, to_hand=True)

    def effect(self, game):
        self._foes_defeated = 0
        game.heroes.active_hero.add_extra_damage_effect(game, self.__extra_effect)
        game.heroes.active_hero.add_extra_influence_effect(game, self.__extra_effect)

    def __extra_effect(self, game, foe, amount):
        if self.completed:
            return
        if foe._defeated:
            self._foes_defeated += 1
        if self._foes_defeated >= 3:
            self.completed = True
            game.locations.remove_control_callback(game, self)

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'F', "(F)ull Moon Rises", self.__reward_action)

    def __reward_action(self, game):
        game.log(f"{self.name} discarded; ALL heroes gain 3{constants.HEART} and may banish a card in hand or discard")
        game.heroes.active_hero._encounters.remove(self)
        game.heroes.active_hero.remove_action(game, 'F')
        game.heroes.all_heroes.add_hearts(game, 3)
        game.heroes.all_heroes.choose_and_banish(game)

ENCOUNTERS_BY_NAME['Full Moon Rises'] = FullMoonRises


class DefensiveTraining(Encounter):
    def __init__(self):
        super().__init__(
            "Defensive Training",
            f"Heroes cannot remove {constants.CONTROL}",
            f"1/game: discard this; ALL heroes gain 2{constants.INFLUENCE} and 2{constants.HEART}",
            ["Boggart"])
        self._got_damage = 0

    def _display_to_complete(self, window):
        window.addstr(f"roll 3{constants.DAMAGE}")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" {self._got_damage}/3", curses.A_BOLD)

    def die_roll_applies(self, game, result):
        return result == constants.DAMAGE and self._got_damage < 3

    def apply_die_roll(self, game, result):
        if result == constants.DAMAGE:
            self._got_damage += 1
        else:
            raise ValueError(f"Programmer Error! Defensive Training only applies to {constants.DAMAGE}")
        if self._got_damage >= 3:
            self.completed = True
            game.locations.allow_remove_control(game)

    def on_reveal(self, game):
        game.locations.disallow_remove_control(game)

    def effect(self, game):
        pass

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'D', "(D)efensive Training", self.__reward_action)

    def __reward_action(self, game):
        game.log(f"{self.name} discarded; ALL heroes gain 2{constants.INFLUENCE} and 2{constants.HEART}")
        game.heroes.active_hero._encounters.remove(self)
        game.heroes.active_hero.remove_action(game, 'D')
        game.heroes.all_heroes.add(game, influence=2, hearts=2)

ENCOUNTERS_BY_NAME['Defensive Training'] = DefensiveTraining
