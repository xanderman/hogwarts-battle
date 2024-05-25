from . import VILLAINS_BY_NAME, Villain
import constants

class DracoMalfoy(Villain):
    def __init__(self):
        super().__init__(
                "Draco Malfoy",
                f"When {constants.CONTROL} is added, active hero loses 2{constants.HEART}",
                f"Remove 1{constants.CONTROL}",
                hearts=6)

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
        game.log(f"{self.name}: {amount}{constants.CONTROL} added, {game.heroes.active_hero.name} loses 2{constants.HEART} for each")
        for _ in range(amount):
            game.heroes.active_hero.remove_hearts(game, 2)

    def remove_callbacks(self, game):
        game.locations.remove_control_callback(game, self)

    def _reward(self, game):
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Draco Malfoy"] = DracoMalfoy
