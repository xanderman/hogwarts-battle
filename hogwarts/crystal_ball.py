from . import CARDS_BY_NAME, Item
import constants


class CrystalBall(Item):
    def __init__(self):
        super().__init__("Crystal Ball", "Draw two cards; discard one card", 3)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.drawing_allowed:
            hero.draw(game, 2)
        elif game.input("Drawing not allowed, still discard? (y/n): ", "yn") == 'n':
            return
        hero.choose_and_discard(game, with_callbacks=False)

CARDS_BY_NAME['Crystal Ball'] = CrystalBall
