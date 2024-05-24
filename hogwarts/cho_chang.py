from . import CARDS_BY_NAME, Ally
import constants


class ChoChang(Ally):
    def __init__(self):
        super().__init__("Cho Chang", "Draw three cards, discard two; roll the Ravenclaw die", 4, rolls_house_die=True)

    def _effect(self, game):
        game.roll_ravenclaw_die()
        hero = game.heroes.active_hero
        if hero.drawing_allowed:
            hero.draw(game, 3)
        elif game.input("Drawing not allowed, still discard? (y/n): ", "yn") == 'n':
            return
        hero.choose_and_discard(game, 2, with_callbacks=False)

CARDS_BY_NAME['Cho Chang'] = ChoChang
