from . import CARDS_BY_NAME, Item
import constants


class TriwizardCup(Item):
    def __init__(self):
        super().__init__("Triwizard Cup", f"Gain 1{constants.DAMAGE}, 1{constants.INFLUENCE}, and 1{constants.HEART}", 5)

    def _effect(self, game):
        game.heroes.active_hero.add(game, damage=1, influence=1, hearts=1)

CARDS_BY_NAME['Triwizard Cup'] = TriwizardCup
