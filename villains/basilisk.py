from . import VILLAINS_BY_NAME, VillainCreature
import constants


class Basilisk(VillainCreature):
    def __init__(self):
        super().__init__(
                "Basilisk",
                "Heroes cannot draw extra cards",
                f"ALL heroes draw 1{constants.CARD}, remove 1{constants.CONTROL}",
                hearts=8)

    def _on_reveal(self, game):
        game.heroes.disallow_drawing(game)

    def _on_stun(self, game):
        game.heroes.allow_drawing(game)

    def _on_recover_from_stun(self, game):
        game.heroes.disallow_drawing(game)

    def _effect(self, game):
        pass

    def remove_callbacks(self, game):
        game.heroes.allow_drawing(game)

    def _reward(self, game):
        game.heroes.all_heroes.draw(game)
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Basilisk"] = Basilisk
