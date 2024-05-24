from . import CARDS_BY_NAME, Ally
import constants


class SeverusSnape(Ally):
    def __init__(self):
        super().__init__("Severus Snape", f"Gain 1{constants.DAMAGE} and 2{constants.HEART}; roll the Slytherin die", 6, rolls_house_die=True)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=1, hearts=2)
        game.roll_slytherin_die()

CARDS_BY_NAME['Severus Snape'] = SeverusSnape
