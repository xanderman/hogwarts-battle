from . import VILLAINS_BY_NAME, VillainCreature
import constants


class Dementor(VillainCreature):
    def __init__(self):
        super().__init__(
                "Dementy-whatsit",
                f"Active hero loses 2{constants.HEART}",
                f"ALL heroes gain 2{constants.HEART}; remove 1{constants.CONTROL}",
                hearts=8)

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 2)

    def _reward(self, game):
        game.heroes.all_heroes.add_hearts(game, 2)
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Dementor"] = Dementor
