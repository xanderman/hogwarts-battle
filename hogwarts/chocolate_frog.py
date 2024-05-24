from . import CARDS_BY_NAME, Item
import constants


class ChocolateFrog(Item):
    def __init__(self):
        super().__init__("Chocolate Frog", f"One hero gains 1{constants.INFLUENCE} and 1{constants.HEART}; if discarded, gain 1{constants.INFLUENCE} and 1{constants.HEART}", 2)

    def _effect(self, game):
        game.heroes.choose_hero(game, prompt=f"Choose a hero to gain 1{constants.INFLUENCE} and 1{constants.HEART}: ").add(game, influence=1, hearts=1)

    def discard_effect(self, game, hero):
        hero.add(game, influence=1, hearts=1)

CARDS_BY_NAME['Chocolate Frog'] = ChocolateFrog
