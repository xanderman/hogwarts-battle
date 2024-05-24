from . import CARDS_BY_NAME, Ally
import constants


class IgorKarkaroff(Ally):
    def __init__(self):
        super().__init__(
            "Igor Karkaroff",
            f"Gain 2{constants.DAMAGE}; if you defeat a Villain, gain 1{constants.DAMAGE} and 1{constants.INFLUENCE}",
            5)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=2)
        game.heroes.active_hero.add_extra_villain_reward(game, self.__villain_reward)

    def __villain_reward(self, game):
        game.heroes.active_hero.add(game, damage=1, influence=1)

CARDS_BY_NAME['Igor Karkaroff'] = IgorKarkaroff
