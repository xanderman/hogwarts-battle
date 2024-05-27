from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Expulso(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Expulso",
            f"Active hero loses 2{constants.HEART}")

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 2)

CARDS_BY_NAME['Expulso'] = Expulso
