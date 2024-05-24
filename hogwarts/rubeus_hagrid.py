from . import CARDS_BY_NAME, Ally
import constants


class RubeusHagrid(Ally):
    def __init__(self):
        super().__init__("Rubeus Hagrid", f"Gain 1{constants.DAMAGE}; ALL heroes gain 1{constants.HEART}", 4)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        game.heroes.all_heroes.add_hearts(game)

CARDS_BY_NAME['Rubeus Hagrid'] = RubeusHagrid
