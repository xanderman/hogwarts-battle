from . import CARDS_BY_NAME, Ally
import constants


class Griphook(Ally):
    def __init__(self):
        super().__init__(
            "Griphook",
            f"Draw 3 cards; discard two. For each Item discarded, gain 2{constants.INFLUENCE}",
            6)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.drawing_allowed:
            hero.draw(game, 3)
        elif game.input("Drawing not allowed, still discard? (y/n): ", "yn") == 'n':
            return
        discarded = hero.choose_and_discard(game, 2, with_callbacks=False)
        for card in discarded:
            if card.is_item():
                game.log(f"Discarded item {card.name}, gaining 2{constants.INFLUENCE}")
                hero.add_influence(game, 2)

CARDS_BY_NAME['Griphook'] = Griphook
