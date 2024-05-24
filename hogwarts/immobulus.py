from . import CARDS_BY_NAME, Spell
import constants


class Immobulus(Spell):
    def __init__(self):
        super().__init__(
            "Immobulus",
            f"Gain 1{constants.DAMAGE}; if you defeat a Creature, remove 1{constants.CONTROL}",
            3)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        game.heroes.active_hero.add_extra_creature_reward(game, self.__reward)

    def __reward(self, game):
        game.log(f"Defeated creature, {self.name} removes 1{constants.CONTROL}")
        game.locations.remove_control(game)

CARDS_BY_NAME['Immobulus'] = Immobulus
