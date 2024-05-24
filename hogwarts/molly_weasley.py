from . import CARDS_BY_NAME, Ally
import constants


class MollyWeasley(Ally):
    def __init__(self):
        super().__init__("Molly Weasley", f"ALL heroes gain 1{constants.INFLUENCE} and 2{constants.HEART}", 6)

    def _effect(self, game):
        game.heroes.all_heroes.add(game, influence=1, hearts=2)

CARDS_BY_NAME['Molly Weasley'] = MollyWeasley
