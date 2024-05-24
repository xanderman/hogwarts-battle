from . import CARDS_BY_NAME, Item
import constants


class Nimbus2001(Item):
    def __init__(self):
        super().__init__("Nimbus 2001", f"Gain 2{constants.DAMAGE}; if you defeat a Villain, gain 2{constants.INFLUENCE}", 5)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=2)
        game.heroes.active_hero.add_extra_villain_reward(game, self.__villain_reward)

    def __villain_reward(self, game):
        game.heroes.active_hero.add_influence(game, 2)

CARDS_BY_NAME['Nimbus 2001'] = Nimbus2001
