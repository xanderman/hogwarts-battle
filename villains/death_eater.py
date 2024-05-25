from . import VILLAINS_BY_NAME, Villain
import constants


class DeathEater(Villain):
    def __init__(self):
        super().__init__(
                "Death Eater",
                f"If Morsmordre or new Villain revealed, ALL Heroes lose 1{constants.HEART}",
                f"ALL heroes gain 1{constants.HEART}; remove 1{constants.CONTROL}",
                hearts=7)

    def _effect(self, game):
        pass

    def _reward(self, game):
        game.heroes.all_heroes.add_hearts(game, 1)
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Death Eater"] = DeathEater
# This makes 2 Death Eaters available for games with random villains
VILLAINS_BY_NAME["Death Eater 2"] = DeathEater
