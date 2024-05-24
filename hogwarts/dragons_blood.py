from . import CARDS_BY_NAME, Item
import constants


class DragonsBlood(Item):
    def __init__(self):
        super().__init__(
            "Dragon's Blood",
            f"ALL Heroes gain 3{constants.HEART}; You may assign 1 additional {constants.INFLUENCE} to Creatures this turn",
            5)

    def _effect(self, game):
        game.heroes.all_heroes.add_hearts(game, 3)
        for creature in game.villain_deck.all_creatures:
            creature._max_influence_per_turn += 1

CARDS_BY_NAME["Dragon's Blood"] = DragonsBlood
