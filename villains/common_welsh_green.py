from . import VILLAINS_BY_NAME, Creature
import constants


class CommonWelshGreen(Creature):
    def __init__(self):
        super().__init__(
                "Common Welsh Green",
                f"When a new Creature is revealed, ALL Heroes lose 2{constants.HEART}",
                f"ALL heroes gain 2{constants.INFLUENCE}",
                hearts=8)

    def _effect(self, game):
        pass

    def _reward(self, game):
        game.heroes.all_heroes.add_influence(game, 2)

VILLAINS_BY_NAME["Common Welsh Green"] = CommonWelshGreen
