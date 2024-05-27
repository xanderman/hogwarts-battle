from . import CARDS_BY_NAME, DarkArtsCard
import constants


class IngquisitorialSquad(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Inquisitorial Squad",
            f"Active hero adds Detention to hand; ALL heroes lose 1{constants.HEART} for each Detention! in hand")

    def _effect(self, game):
        game.heroes.active_hero.add_detention(game, to_hand=True)
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        total = sum(1 for card in hero._hand if card.name == "Detention!")
        game.log(f"Inquisitorial Squad: {hero.name} has {total} Detention! cards")
        hero.remove_hearts(game, total)

CARDS_BY_NAME['Inquisitorial Squad'] = IngquisitorialSquad
