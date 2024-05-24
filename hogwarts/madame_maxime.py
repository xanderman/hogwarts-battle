from . import CARDS_BY_NAME, Ally
import constants


class MadameMaxime(Ally):
    def __init__(self):
        super().__init__(
            "Madame Maxime",
            f"Gain 2{constants.DAMAGE}; ALL Heroes gain 2{constants.HEART}",
            7)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game, 2)
        game.heroes.all_heroes.add_hearts(game, 2)

CARDS_BY_NAME['Madame Maxime'] = MadameMaxime
