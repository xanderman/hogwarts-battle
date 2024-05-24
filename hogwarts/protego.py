from . import CARDS_BY_NAME, Spell
import constants


class Protego(Spell):
    def __init__(self):
        super().__init__("Protego", f"Gain 1{constants.DAMAGE} and 1{constants.HEART}; if discarded, gain 1{constants.DAMAGE} and 1{constants.HEART}", 5)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=1, hearts=1)

    def discard_effect(self, game, hero):
        hero.add(game, damage=1, hearts=1)

CARDS_BY_NAME['Protego'] = Protego
