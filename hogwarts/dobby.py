from . import CARDS_BY_NAME, Ally
import constants


class Dobby(Ally):
    def __init__(self):
        super().__init__("Dobby", f"Remove 1{constants.CONTROL} and draw a card", 4)

    def _effect(self, game):
        game.locations.remove_control(game)
        game.heroes.active_hero.draw(game)

CARDS_BY_NAME['Dobby'] = Dobby
