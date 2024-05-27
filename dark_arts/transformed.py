from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Transformed(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Transformed",
            "Active hero discards a card then adds Detention! to hand")

    def _effect(self, game):
        game.heroes.active_hero.choose_and_discard(game)
        game.heroes.active_hero.add_detention(game, to_hand=True)

CARDS_BY_NAME['Transformed'] = Transformed
