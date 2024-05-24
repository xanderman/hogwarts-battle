from . import CARDS_BY_NAME, Ally
import constants


class SybillTrelawney(Ally):
    def __init__(self):
        super().__init__(
            "Sybill Trelawney",
            f"Draw 2 cards; discard one card. If you discard a Spell, gain 2{constants.INFLUENCE}",
            4)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.drawing_allowed:
            hero.draw(game, 2)
        elif game.input("Drawing not allowed, still discard? (y/n): ", "yn") == 'n':
            return
        discarded = hero.choose_and_discard(game, with_callbacks=False)[0]
        if discarded.is_spell():
            game.log(f"Discarded spell, gaining 2{constants.INFLUENCE}")
            hero.add_influence(game, 2)

CARDS_BY_NAME['Sybill Trelawney'] = SybillTrelawney
