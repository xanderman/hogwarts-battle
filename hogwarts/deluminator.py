from . import CARDS_BY_NAME, Item
import constants


class Deluminator(Item):
    def __init__(self):
        super().__init__("Deluminator", f"Remove 2{constants.CONTROL}", 6)

    def _effect(self, game):
        game.locations.remove_control(game, 2)

CARDS_BY_NAME['Deluminator'] = Deluminator
