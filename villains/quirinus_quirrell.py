from . import VILLAINS_BY_NAME, Villain
import constants


class QuirinusQuirrell(Villain):
    def __init__(self):
        super().__init__(
                "Quirinus Quirrell",
                f"Active hero loses 1{constants.HEART}",
                f"ALL heroes gain 1{constants.HEART} and 1{constants.INFLUENCE}",
                hearts=6)

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 1)

    def _reward(self, game):
        game.heroes.all_heroes.add(game, influence=1, hearts=1)

VILLAINS_BY_NAME["Quirinus Quirrell"] = QuirinusQuirrell
