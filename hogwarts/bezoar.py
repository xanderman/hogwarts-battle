from . import CARDS_BY_NAME, Item
import constants


class Bezoar(Item):
    def __init__(self):
        super().__init__("Bezoar", f"One hero gains 3{constants.HEART}; draw a card", 4)

    def _effect(self, game):
        if not game.heroes.healing_allowed:
            game.log("Healing not allowed!")
        else:
            game.heroes.choose_hero(game, prompt=f"Choose hero to gain 3{constants.HEART}: ").add_hearts(game, 3)
        game.heroes.active_hero.draw(game)

CARDS_BY_NAME['Bezoar'] = Bezoar
