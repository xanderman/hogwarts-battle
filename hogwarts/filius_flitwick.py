from . import CARDS_BY_NAME, Ally
import constants


class FiliusFlitwick(Ally):
    def __init__(self):
        super().__init__("Filius Flitwick", f"Gain 1{constants.INFLUENCE} and draw a card; roll the Ravenclaw die", 6, rolls_house_die=True)

    def _effect(self, game):
        game.heroes.active_hero.add(game, influence=1, cards=1)
        game.roll_ravenclaw_die()

CARDS_BY_NAME['Filius Flitwick'] = FiliusFlitwick
