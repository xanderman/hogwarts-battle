from . import CARDS_BY_NAME, Item
import constants


class ErumpentHorn(Item):
    def __init__(self):
        super().__init__(
            "Erumpent Horn",
            f"Lose 2{constants.HEART}; Gain 3{constants.DAMAGE}",
            5)

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 2)
        game.heroes.active_hero.add_damage(game, 3)

CARDS_BY_NAME['Erumpent Horn'] = ErumpentHorn
