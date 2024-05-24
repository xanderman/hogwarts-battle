from . import CARDS_BY_NAME, Ally
import constants


class Buckbeak(Ally):
    def __init__(self):
        super().__init__(
            "Buckbeak",
            f"Draw 2 cards; discard one card. If you discard an Ally, gain 2{constants.DAMAGE}",
            4)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.drawing_allowed:
            hero.draw(game, 2)
        elif game.input("Drawing not allowed, still discard? (y/n): ", "yn") == 'n':
            return
        discarded = hero.choose_and_discard(game, with_callbacks=False)[0]
        if discarded.is_ally():
            game.log(f"Discarded ally, gaining 2{constants.DAMAGE}")
            hero.add_damage(game, 2)

CARDS_BY_NAME['Buckbeak'] = Buckbeak
