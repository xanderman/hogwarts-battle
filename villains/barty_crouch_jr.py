from . import VILLAINS_BY_NAME, Villain
import constants


class BartyCrouchJr(Villain):
    def __init__(self):
        super().__init__(
                "Barty Crouch Jr.",
                f"Heroes cannot remove {constants.CONTROL}",
                f"Remove 2{constants.CONTROL}",
                hearts=7)

    def _on_reveal(self, game):
        game.locations.disallow_remove_control(game)

    def _on_stun(self, game):
        game.locations.allow_remove_control(game)

    def _on_recover_from_stun(self, game):
        game.locations.disallow_remove_control(game)

    def _effect(self, game):
        pass

    def remove_callbacks(self, game):
        game.locations.allow_remove_control(game)

    def _reward(self, game):
        game.locations.remove_control(game, 2)

VILLAINS_BY_NAME["Barty Crouch Jr."] = BartyCrouchJr
