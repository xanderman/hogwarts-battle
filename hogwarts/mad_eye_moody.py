from . import CARDS_BY_NAME, Ally
import constants


class MadEyeMoody(Ally):
    def __init__(self):
        super().__init__("Mad-eye Moody", f"Gain 2{constants.INFLUENCE}, remove 1{constants.CONTROL}", 6)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game, 2)
        game.locations.remove_control(game)

CARDS_BY_NAME['Mad-eye Moody'] = MadEyeMoody
