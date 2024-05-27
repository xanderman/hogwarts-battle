from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Fiendfyre(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Fiendfyre",
            f"ALL heroes lose 3{constants.HEART}")

    def _effect(self, game):
        game.heroes.all_heroes.remove_hearts(game, 3)

CARDS_BY_NAME['Fiendfyre'] = Fiendfyre
