from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Flipendo(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Flipendo",
            f"Active hero loses 1{constants.HEART} and discards a card")

    def _effect(self, game):
        game.heroes.active_hero.add(game, hearts=-1, cards=-1)

CARDS_BY_NAME['Flipendo'] = Flipendo
