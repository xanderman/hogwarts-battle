from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Regeneration(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Regeneration",
            f"Remove 2{constants.DAMAGE} from ALL Villains")

    def _effect(self, game):
        game.villain_deck.all_villains.remove_damage(game, 2)

CARDS_BY_NAME['Regeneration'] = Regeneration
