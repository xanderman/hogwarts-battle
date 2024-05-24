from . import CARDS_BY_NAME, Spell
import constants


class WingardiumLeviosa(Spell):
    def __init__(self):
        super().__init__(
                "Wingardium Leviosa",
                f"Gain 1{constants.INFLUENCE}, may put acquired Items on top of deck",
                2)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game)
        game.heroes.active_hero.can_put_items_in_deck(game)

CARDS_BY_NAME['Wingardium Leviosa'] = WingardiumLeviosa
