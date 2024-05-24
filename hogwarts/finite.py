from . import CARDS_BY_NAME, Spell
import constants


class Finite(Spell):
    def __init__(self):
        super().__init__("Finite", f"Remove 1{constants.CONTROL}", 3)

    def _effect(self, game):
        game.locations.remove_control(game)

CARDS_BY_NAME['Finite'] = Finite
