from . import CARDS_BY_NAME, Ally
import constants


class SiriusBlack(Ally):
    def __init__(self):
        super().__init__("Sirius Black", f"Gain 2{constants.DAMAGE} and 1{constants.INFLUENCE}", 6)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=2, influence=1)

CARDS_BY_NAME['Sirius Black'] = SiriusBlack
