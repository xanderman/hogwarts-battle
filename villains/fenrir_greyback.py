from . import VILLAINS_BY_NAME, Villain
import constants


class FenrirGreyback(Villain):
    def __init__(self):
        super().__init__(
                "Fenrir Greyback",
                f"Heroes cannot gain {constants.HEART}",
                f"ALL heroes gain 3{constants.HEART}, remove 2{constants.CONTROL}",
                hearts=8)

    def _on_reveal(self, game):
        game.heroes.disallow_healing(game)

    def _on_stun(self, game):
        game.heroes.allow_healing(game)

    def _on_recover_from_stun(self, game):
        game.heroes.disallow_healing(game)

    def _effect(self, game):
        pass

    def remove_callbacks(self, game):
        game.heroes.allow_healing(game)

    def _reward(self, game):
        game.heroes.all_heroes.add_hearts(game, 3)
        game.locations.remove_control(game, 2)

VILLAINS_BY_NAME["Fenrir Greyback"] = FenrirGreyback
