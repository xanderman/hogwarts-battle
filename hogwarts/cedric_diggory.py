from . import CARDS_BY_NAME, Ally
import constants


class CedricDiggory(Ally):
    def __init__(self):
        super().__init__("Cedric Diggory", f"Gain 1{constants.DAMAGE}; roll the Hufflepuff die", 4, rolls_house_die=True)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        game.roll_hufflepuff_die()

CARDS_BY_NAME['Cedric Diggory'] = CedricDiggory
