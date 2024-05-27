from . import CARDS_BY_NAME, DarkArtsCard
import constants


class BlastEnded(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Blast-ended",
            f"Previous hero loses 1{constants.HEART} and discards a card")

    def _effect(self, game):
        game.heroes.previous_hero.add(game, hearts=-1, cards=-1)

CARDS_BY_NAME['Blast-ended'] = BlastEnded
