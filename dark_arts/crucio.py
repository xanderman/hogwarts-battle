from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Crucio(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Crucio",
            f"Active hero loses 1{constants.HEART}; reveal another card")

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 1)
        game.dark_arts_deck.play(game, 1)

CARDS_BY_NAME['Crucio'] = Crucio
