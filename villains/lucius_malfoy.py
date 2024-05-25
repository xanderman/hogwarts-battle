from . import VILLAINS_BY_NAME, Villain
import constants


class LuciusMalfoy(Villain):
    def __init__(self):
        super().__init__(
                "Lucius Malfoy",
                f"When {constants.CONTROL} is added, all villains heal 1{constants.DAMAGE}",
                f"ALL heroes gain 1{constants.INFLUENCE}, remove 1{constants.CONTROL}",
                hearts=7)

    def _on_reveal(self, game):
        game.locations.add_control_callback(game, self)

    def _effect(self, game):
        pass

    def control_callback(self, game, amount):
        if amount < 1:
            return
        if self._stunned:
            game.log(f"{self.name} is stunned! No penalty for added {constants.CONTROL}")
            return
        game.log(f"{self.name}: {amount}{constants.CONTROL} added, all Villains heal 1{constants.DAMAGE} for each")
        for _ in range(amount):
            game.villain_deck.all_villains.remove_damage(game, 1)

    def remove_callbacks(self, game):
        game.locations.remove_control_callback(game, self)

    def _reward(self, game):
        game.heroes.all_heroes.add_influence(game, 1)
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Lucius Malfoy"] = LuciusMalfoy
