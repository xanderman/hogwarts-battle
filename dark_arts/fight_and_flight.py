from . import CARDS_BY_NAME, DarkArtsCard
import constants


class FightAndFlight(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Fight and Flight",
            f"Add 2{constants.CONTROL}")

    def _effect(self, game):
        game.locations.add_control(game, 2)

CARDS_BY_NAME['Fight and Flight'] = FightAndFlight
