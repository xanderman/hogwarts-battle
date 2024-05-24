from . import CARDS_BY_NAME, Spell
import constants


class Stupefy(Spell):
    def __init__(self):
        super().__init__("Stupefy", f"Gain 1{constants.DAMAGE}; remove 1{constants.CONTROL}; draw a card", 6)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=1, cards=1)
        game.locations.remove_control(game)

CARDS_BY_NAME['Stupefy'] = Stupefy
