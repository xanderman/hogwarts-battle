from . import CARDS_BY_NAME, DarkArtsCard
import constants


class EducationalDecree(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Educational Decree",
            f"Active hero loses 1{constants.HEART} for each card with cost 4{constants.INFLUENCE} or more in hand")

    def _effect(self, game):
        total = sum(1 for card in game.heroes.active_hero._hand if card.cost >= 4)
        game.heroes.active_hero.remove_hearts(game, total)

CARDS_BY_NAME['Educational Decree'] = EducationalDecree
