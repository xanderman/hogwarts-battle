from . import CARDS_BY_NAME, DarkArtsCard
import constants


class HeWhoMustNotBeNamed(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "He Who Must Not Be Named",
            f"Add 1{constants.CONTROL} to the location")

    def _effect(self, game):
        game.locations.add_control(game)

CARDS_BY_NAME['He Who Must Not Be Named'] = HeWhoMustNotBeNamed
