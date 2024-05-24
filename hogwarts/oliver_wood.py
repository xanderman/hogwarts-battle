from . import CARDS_BY_NAME, Ally
import constants


class OliverWood(Ally):
    def __init__(self):
        super().__init__("Oliver Wood", f"Gain 1{constants.DAMAGE}, if you defeat a Villain one hero gains 2{constants.HEART}", 3)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        game.heroes.active_hero.add_extra_villain_reward(game, self.__extra_villain_reward)

    def __extra_villain_reward(self, game):
        if not game.heroes.healing_allowed:
            game.log("Oliver Wood: Villain deafeted, but healing not allowed!")
            return
        game.heroes.choose_hero(game, prompt=f"Oliver Wood: Villain defeated! Choose hero to gain 2{constants.HEART}: ").add_hearts(game, 2)

CARDS_BY_NAME['Oliver Wood'] = OliverWood
