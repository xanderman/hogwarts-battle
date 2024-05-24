from . import CARDS_BY_NAME, Item
import constants


class SortingHat(Item):
    def __init__(self):
        super().__init__("Sorting Hat", f"Gain 2{constants.INFLUENCE}, may put acquired Allies on top of deck", 4)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game, 2)
        game.heroes.active_hero.can_put_allies_in_deck(game)

CARDS_BY_NAME['Sorting Hat'] = SortingHat
