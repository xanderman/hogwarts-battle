from . import CARDS_BY_NAME, Spell
import constants


class Descendo(Spell):
    def __init__(self):
        super().__init__("Descendo", f"Gain 2{constants.DAMAGE}", 5)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game, 2)

CARDS_BY_NAME['Descendo'] = Descendo
