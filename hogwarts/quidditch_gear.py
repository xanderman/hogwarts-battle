from . import CARDS_BY_NAME, Item
import constants


class QuidditchGear(Item):
    def __init__(self):
        super().__init__("Quidditch Gear", f"Gain 1{constants.DAMAGE} and 1{constants.HEART}", 3)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=1, hearts=1)

CARDS_BY_NAME['Quidditch Gear'] = QuidditchGear
