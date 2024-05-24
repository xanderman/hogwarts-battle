from . import CARDS_BY_NAME, Spell
import constants


class ExpectoPatronum(Spell):
    def __init__(self):
        super().__init__("Expecto Patronum", f"Gain 1{constants.DAMAGE}; remove 1{constants.CONTROL}", 5)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        game.locations.remove_control(game)

CARDS_BY_NAME['Expecto Patronum'] = ExpectoPatronum
