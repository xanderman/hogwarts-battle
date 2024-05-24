from . import CARDS_BY_NAME, Ally
import constants


class PomonaSprout(Ally):
    def __init__(self):
        super().__init__("Pomona Sprout", f"Gain 1{constants.INFLUENCE}; anyone gains 2{constants.HEART}; roll the Hufflepuff die", 6, rolls_house_die=True)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game)
        if not game.heroes.healing_allowed:
            game.log("Healing not allowed, skipping healing effect")
        else:
            game.heroes.choose_hero(game, prompt=f"Choose hero to gain 2{constants.HEART}: ").add_hearts(game, 2)
        game.roll_hufflepuff_die()

CARDS_BY_NAME['Pomona Sprout'] = PomonaSprout
