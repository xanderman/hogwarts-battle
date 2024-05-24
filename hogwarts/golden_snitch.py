from . import CARDS_BY_NAME, Item
import constants


class GoldenSnitch(Item):
    def __init__(self):
        super().__init__("Golden Snitch", f"Gain 2{constants.INFLUENCE} and draw a card", 5)

    def _effect(self, game):
        game.heroes.active_hero.add(game, influence=2, cards=1)

CARDS_BY_NAME['Golden Snitch'] = GoldenSnitch
