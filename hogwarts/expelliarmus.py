from . import CARDS_BY_NAME, Spell
import constants


class Expelliarmus(Spell):
    def __init__(self):
        super().__init__("Expelliarmus", f"Gain 2{constants.DAMAGE} and draw a card", 6)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=2, cards=1)

CARDS_BY_NAME['Expelliarmus'] = Expelliarmus
