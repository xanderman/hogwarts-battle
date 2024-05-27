from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Sectumsempra(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Sectumsempra",
            f"ALL heroes lose 2{constants.HEART} and cannot gain {constants.HEART} this turn")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        hero.remove_hearts(game, 2)
        hero.disallow_healing(game)

    def _end_turn(self, game):
        game.heroes.allow_healing(game)

CARDS_BY_NAME['Sectumsempra'] = Sectumsempra
