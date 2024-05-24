from . import CARDS_BY_NAME, Item
import constants


class Pensieve(Item):
    def __init__(self):
        super().__init__("Pensieve", f"Two heroes gain 1{constants.INFLUENCE} and draw a card", 5)

    def _effect(self, game):
        game.heroes.choose_two_heroes(game, prompt=f"to gain 1{constants.INFLUENCE} and draw a card: ").add(game, influence=1, cards=1)

CARDS_BY_NAME['Pensieve'] = Pensieve
