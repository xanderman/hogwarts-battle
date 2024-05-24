from . import CARDS_BY_NAME, Item
import constants


class GoldenEgg(Item):
    def __init__(self):
        super().__init__(
            "Golden Egg",
            f"Gain 2{constants.DAMAGE}, 1{constants.INFLUENCE}, and 1{constants.CARD}",
            7)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=2, influence=1, cards=1)

CARDS_BY_NAME['Golden Egg'] = GoldenEgg
