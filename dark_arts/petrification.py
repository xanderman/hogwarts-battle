from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Petrification(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Petrification",
            f"ALL heroes lose 1{constants.HEART}; no drawing cards")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        hero.remove_hearts(game, 1)
        hero.disallow_drawing(game)

    def _end_turn(self, game):
        game.heroes.allow_drawing(game)

CARDS_BY_NAME['Petrification'] = Petrification
