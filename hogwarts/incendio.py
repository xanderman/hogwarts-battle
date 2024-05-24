from . import CARDS_BY_NAME, Spell
import constants


class Incendio(Spell):
    def __init__(self):
        super().__init__("Incendio", f"Gain 1{constants.DAMAGE} and draw a card", 4)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=1, cards=1)

CARDS_BY_NAME['Incendio'] = Incendio
