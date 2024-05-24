from . import CARDS_BY_NAME, Ally
import constants


class Fang(Ally):
    def __init__(self):
        super().__init__(
            "Fang",
            f"One hero gains 1{constants.INFLUENCE} and 2{constants.HEART}",
            3)

    def _effect(self, game):
        hero = game.heroes.choose_hero(game, prompt=f"Choose hero to gain 1{constants.INFLUENCE} and 2{constants.HEART}: ")
        hero.add(game, influence=1, hearts=2)

CARDS_BY_NAME['Fang'] = Fang
