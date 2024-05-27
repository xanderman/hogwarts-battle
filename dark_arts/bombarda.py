from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Bombarda(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Bombarda!",
            f"ALL heroes add a Detention! to their discard")

    def _effect(self, game):
        game.heroes.all_heroes.add_detention(game)

CARDS_BY_NAME['Bombarda!'] = Bombarda
