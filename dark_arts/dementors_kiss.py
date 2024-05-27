from . import CARDS_BY_NAME, DarkArtsCard
import constants


class DementorsKiss(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Dementor's Kiss",
            f"Active hero loses 2{constants.HEART}, others lose 1{constants.HEART}")

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 2)
        game.heroes.all_heroes_except_active.remove_hearts(game, 1)

CARDS_BY_NAME["Dementor's Kiss"] = DementorsKiss
