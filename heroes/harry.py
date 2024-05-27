import constants
import hogwarts

from .base import Hero, Alohomora, StarterAlly, StarterBroom


class InvisibilityCloak(hogwarts.Item):
    def __init__(self):
        super().__init__("Invisibility cloak", f"Gain 1{constants.INFLUENCE}; if in hand, take only 1{constants.DAMAGE} from each Villain or Dark Arts", 0)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game)


class Harry(Hero):
    def __init__(self, ability, proficiency):
        super().__init__("Harry", ability, [
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            StarterAlly("Hedwig"),
            InvisibilityCloak(),
            StarterBroom("Firebolt"),
        ], proficiency)
        self._used_ability = False

    @property
    def ability_description(self):
        if self._ability < 3:
            return None
        if self._ability < 7:
            return f"The first time {constants.CONTROL} is removed on any turn, one hero gains 1{constants.DAMAGE}"
        return f"The first time {constants.CONTROL} is removed on any turn, two heroes gain 1{constants.DAMAGE}"

    def control_callback(self, game, amount):
        if amount > -1:
            return
        if self._used_ability:
            return
        self._used_ability = True
        if self._ability >= 7:
            self._game_seven_ability_control_callback(game, amount)
            return
        if self._ability >= 3:
            self._game_three_ability_control_callback(game, amount)

    def _game_three_ability_control_callback(self, game, amount):
        game.heroes.choose_hero(game, prompt=f"{self.name}: first {constants.CONTROL} removed this turn, choose hero to gain 1{constants.DAMAGE}: ").add_damage(game, 1)

    def _game_seven_ability_control_callback(self, game, amount):
        game.log(f"{self.name}: first {constants.CONTROL} removed this turn, two heroes gain 1{constants.DAMAGE}")
        game.heroes.choose_two_heroes(game, prompt=f"to gain 1{constants.DAMAGE}").add_damage(game, 1)

    def _monster_box_one_ability_control_callback(self, game, amount):
        game.log(f"{self.name}: {constants.CONTROL} removed, ALL heroes gain 1{constants.HEART} for each")
        for _ in range(amount):
            game.heroes.all_heroes.add_hearts(game, 1)
