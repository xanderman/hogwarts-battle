from . import CARDS_BY_NAME, Ally
import constants


class AlbusDumbledore(Ally):
    def __init__(self):
        super().__init__("Albus Dumbledore", f"ALL heroes gain 1{constants.DAMAGE}, 1{constants.INFLUENCE}, 1{constants.HEART}, and draw a card", 8)

    def _effect(self, game):
        game.heroes.all_heroes.add(game, damage=1, influence=1, hearts=1, cards=1)

CARDS_BY_NAME['Albus Dumbledore'] = AlbusDumbledore
