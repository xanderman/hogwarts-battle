from . import CARDS_BY_NAME, Ally
import constants


class ViktorKrum(Ally):
    def __init__(self):
        super().__init__("Viktor Krum", f"Gain 2{constants.DAMAGE}, if you defeat a Villain gain 1{constants.INFLUENCE} and 1{constants.HEART}", 5)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game, 2)
        game.heroes.active_hero.add_extra_villain_reward(game, self.__villain_reward)

    def __villain_reward(self, game):
        game.heroes.active_hero.add(game, influence=1, hearts=1)

CARDS_BY_NAME['Viktor Krum'] = ViktorKrum
