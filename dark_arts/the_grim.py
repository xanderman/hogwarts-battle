from . import CARDS_BY_NAME, DarkArtsCard
import constants


class TheGrim(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "The Grim",
            f"Active hero discards a card; add 1{constants.CONTROL}")

    def _effect(self, game):
        game.heroes.active_hero.choose_and_discard(game)
        game.locations.add_control(game)

CARDS_BY_NAME['The Grim'] = TheGrim
