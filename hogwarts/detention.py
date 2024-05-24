from . import CARDS_BY_NAME, Item
import constants


class Detention(Item):
    def __init__(self):
        super().__init__("Detention!", f"If you discard this, lose 2{constants.HEART}", 0)

    def _effect(self, game):
        pass

    def discard_effect(self, game, hero):
        hero.remove_hearts(game, 2)

CARDS_BY_NAME['Detention!'] = Detention
