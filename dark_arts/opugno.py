from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Opugno(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Opugno",
            f"ALL heroes reveal top card, if it costs 1{constants.INFLUENCE} or more discard it and lose 2{constants.HEART}")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        card = hero.reveal_top_card(game)
        if card is None:
            game.log(f"{hero.name} has no cards left to reveal")
            return
        game.log(f"{hero.name} revealed {card}")
        if card.cost >= 1:
            hero.discard_top_card(game)
            hero.remove_hearts(game, 2)

CARDS_BY_NAME['Opugno'] = Opugno
