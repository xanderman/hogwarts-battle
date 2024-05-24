from . import CARDS_BY_NAME, Item
import constants


class MaraudersMap(Item):
    def __init__(self):
        super().__init__("Marauder's Map", "Draw two cards; if discarded, ALL heroes draw a card", 5)

    def _effect(self, game):
        game.heroes.active_hero.draw(game, 2)

    def discard_effect(self, game, hero):
        game.heroes.all_heroes.draw(game)

CARDS_BY_NAME["Marauder's Map"] = MaraudersMap
