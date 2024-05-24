from . import CARDS_BY_NAME, Ally
import constants


class GilderyLockhart(Ally):
    def __init__(self):
        super().__init__("Gilderoy Lockhart", f"Draw a card, then discard a card; if discarded, draw a card", 2)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.drawing_allowed:
            hero.draw(game)
        elif game.input("Drawing not allowed, still discard? (y/n): ", "yn") == 'n':
            return
        hero.choose_and_discard(game, with_callbacks=False)

    def discard_effect(self, game, hero):
        hero.draw(game)

CARDS_BY_NAME['Gilderoy Lockhart'] = GilderyLockhart
