from . import CARDS_BY_NAME, DarkArtsCard
import constants


class MenacingGrowl(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Menacing Growl",
            f"ALL heroes lose 1{constants.HEART} for each card in hand with cost of 3{constants.INFLUENCE}")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        total = sum(1 for card in hero._hand if card.cost == 3)
        game.log(f"Menacing Growl: {hero.name} has {total} cards with cost 3{constants.INFLUENCE}")
        hero.remove_hearts(game, total)

CARDS_BY_NAME['Menacing Growl'] = MenacingGrowl
