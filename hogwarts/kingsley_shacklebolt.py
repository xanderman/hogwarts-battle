from . import CARDS_BY_NAME, Ally
import constants


class KingsleyShacklebolt(Ally):
    def __init__(self):
        super().__init__("Kingsley Shacklebolt", f"Gain 2{constants.DAMAGE} and 1{constants.HEART}; remove 1{constants.CONTROL}", 7)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=2, hearts=1)
        game.locations.remove_control(game)

CARDS_BY_NAME['Kingsley Shacklebolt'] = KingsleyShacklebolt
