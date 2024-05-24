from . import CARDS_BY_NAME, Item
import constants


class Butterbeer(Item):
    def __init__(self):
        super().__init__("Butterbeer", f"Two heroes gain 1{constants.INFLUENCE} and 1{constants.HEART}", 3)

    def _effect(self, game):
        game.heroes.choose_two_heroes(game, prompt=f"to gain 1{constants.INFLUENCE} and 1{constants.HEART}: ").add(game, influence=1, hearts=1)

CARDS_BY_NAME['Butterbeer'] = Butterbeer
