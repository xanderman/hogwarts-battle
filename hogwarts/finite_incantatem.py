from . import CARDS_BY_NAME, Spell
import constants


class FiniteIncantatem(Spell):
    def __init__(self):
        super().__init__(
            "Finite Incantatem",
            f"Remove 1{constants.CONTROL}; if in hand, reveal only 1 Dark Arts event",
            6)

    def _effect(self, game):
        game.locations.remove_control(game)

CARDS_BY_NAME['Finite Incantatem'] = FiniteIncantatem
