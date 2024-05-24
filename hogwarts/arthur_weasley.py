from . import CARDS_BY_NAME, Ally
import constants


class ArthurWeasley(Ally):
    def __init__(self):
        super().__init__("Arthur Weasley", f"ALL heroes gain 2{constants.INFLUENCE}", 6)

    def _effect(self, game):
        game.heroes.all_heroes.add_influence(game, 2)

CARDS_BY_NAME['Arthur Weasley'] = ArthurWeasley
