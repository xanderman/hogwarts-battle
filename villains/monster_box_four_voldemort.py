from . import VOLDEMORTS_BY_NAME, Villain
import constants


class MonsterBoxFourVoldemort(Villain):
    def __init__(self):
        super().__init__(
                "Lord Voldemort",
                f"Lose 2{constants.HEART}; Add 1{constants.CONTROL}; Each time a Hero is stunned, add an extra {constants.CONTROL}",
                "You win!",
                hearts=25, cost=7)

    def _on_reveal(self, game):
        game.heroes.all_heroes.add_hearts_callback(game, self)

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 2)
        game.locations.add_control(game)

    def hearts_callback(self, game, hero, amount, source):
        if amount >= 0:
            return
        if not hero.is_stunned:
            return
        if self._stunned:
            game.log(f"{self.name} is stunned! No penalty for stunned hero")
            return
        game.log(f"{self.name}: {hero.name} is stunned, adding an extra {constants.CONTROL}")
        game.locations.add_control(game)

    def remove_callbacks(self, game):
        game.heroes.remove_hearts_callback(game, self)

    def _reward(self, game):
        pass

VOLDEMORTS_BY_NAME["Monster Box Four Voldemort"] = MonsterBoxFourVoldemort
