from . import CARDS_BY_NAME, DarkArtsCard
import constants


class DragonsBreath(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Dragon's Breath",
            f"Active Hero loses 1{constants.HEART} and discards ALL Items")

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 1)
        game.heroes.active_hero.discard_all_items(game)

CARDS_BY_NAME["Dragon's Breath"] = DragonsBreath
