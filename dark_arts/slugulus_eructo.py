from . import CARDS_BY_NAME, DarkArtsCard
import constants


class SlugulusEructo(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Slugulus Eructo",
            f"ALL heroes lose 1{constants.HEART} for each Creature in play")

    def _effect(self, game):
        total = sum(1 for card in game.villain_deck.current if card.is_creature)
        game.log(f"Slugulus Eructo: {total} Creatures in play")
        game.heroes.all_heroes.remove_hearts(game, total)

CARDS_BY_NAME['Slugulus Eructo'] = SlugulusEructo
