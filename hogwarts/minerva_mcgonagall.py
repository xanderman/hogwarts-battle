from . import CARDS_BY_NAME, Ally
import constants


class MinervaMcGonagall(Ally):
    def __init__(self):
        super().__init__("Minerva McGonagall", f"Gain 1{constants.INFLUENCE} and 1{constants.DAMAGE}; roll the Gryffindor die", 6, rolls_house_die=True)

    def _effect(self, game):
        game.heroes.active_hero.add(game, influence=1, damage=1)
        game.roll_gryffindor_die()

CARDS_BY_NAME['Minerva McGonagall'] = MinervaMcGonagall
