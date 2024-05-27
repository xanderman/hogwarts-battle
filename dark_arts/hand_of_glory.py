from . import CARDS_BY_NAME, DarkArtsCard
import constants


class HandOfGlory(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Hand of Glory",
            f"Active hero loses 1{constants.HEART}, add 1{constants.CONTROL}")

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 1)
        game.locations.add_control(game)

CARDS_BY_NAME['Hand of Glory'] = HandOfGlory
