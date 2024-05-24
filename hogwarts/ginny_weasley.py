from . import CARDS_BY_NAME, Ally
import constants


class GinnyWeasley(Ally):
    def __init__(self):
        super().__init__("Ginny Weasley", f"Gain 1{constants.DAMAGE} and 1{constants.INFLUENCE}", 4)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=1, influence=1)

CARDS_BY_NAME['Ginny Weasley'] = GinnyWeasley
