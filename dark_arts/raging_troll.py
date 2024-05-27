from . import CARDS_BY_NAME, DarkArtsCard
import constants


class RagingTroll(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Raging Troll",
            f"Next hero loses 2{constants.HEART}; add 1{constants.CONTROL}")

    def _effect(self, game):
        game.heroes.next_hero.remove_hearts(game, 2)
        game.locations.add_control(game)

CARDS_BY_NAME['Raging Troll'] = RagingTroll
