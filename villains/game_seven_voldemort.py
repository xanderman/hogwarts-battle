from . import VOLDEMORTS_BY_NAME, Villain
import constants


class GameSevenVoldemort(Villain):
    def __init__(self):
        super().__init__(
                "Lord Voldemort",
                f"Add 1{constants.CONTROL}; each time {constants.CONTROL} is removed, ALL heroes lose 1{constants.HEART}",
                "You win!",
                hearts=20)

    def _on_reveal(self, game):
        game.locations.add_control_callback(game, self)

    def _effect(self, game):
        game.locations.add_control(game)

    def control_callback(self, game, amount):
        if amount > -1:
            return
        if self._stunned:
            game.log(f"{self.name} is stunned! No penalty for removed {constants.CONTROL}")
            return
        game.log(f"{self.name}: {constants.CONTROL} removed, ALL heroes lose 1{constants.HEART} for each")
        for _ in range(-amount):
            game.heroes.all_heroes.remove_hearts(game, 1)

    def remove_callbacks(self, game):
        game.locations.remove_control_callback(game, self)

    def _reward(self, game):
        pass

VOLDEMORTS_BY_NAME["Game Seven Voldemort"] = GameSevenVoldemort
