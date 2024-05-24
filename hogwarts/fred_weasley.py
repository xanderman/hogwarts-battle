from . import CARDS_BY_NAME
from .base import _WeasleyTwin
import constants


class FredWeasley(_WeasleyTwin):
    def __init__(self):
        super().__init__("Fred Weasley", f"Gain 1{constants.DAMAGE}; if another hero has a Weasley, ALL heroes gain 1{constants.INFLUENCE}; roll the Gryffindor die", 4, rolls_house_die=True)

    def _weasley_bonus(self, game, hero, card):
        game.log(f"{hero.name} has {card.name}, ALL heroes gain 1{constants.INFLUENCE}")
        game.heroes.all_heroes.add_influence(game, 1)

CARDS_BY_NAME['Fred Weasley'] = FredWeasley
