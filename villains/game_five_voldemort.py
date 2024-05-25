from . import VOLDEMORTS_BY_NAME, Villain
import constants


class GameFiveVoldemort(Villain):
    def __init__(self):
        super().__init__(
                "Lord Voldemort",
                f"Active hero loses 1{constants.HEART} and discards a card",
                "You win!",
                hearts=10)

    def _effect(self, game):
        game.heroes.active_hero.add(game, hearts=-1, cards=-1)

    def _reward(self, game):
        pass

VOLDEMORTS_BY_NAME["Game Five Voldemort"] = GameFiveVoldemort
