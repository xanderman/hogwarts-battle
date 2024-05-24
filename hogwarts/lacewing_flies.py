from . import CARDS_BY_NAME, Item
import constants


class LacewingFlies(Item):
    def __init__(self):
        super().__init__(
            "Lacewing Flies",
            f"One hero draws a card. If discarded, gain 1{constants.DAMAGE}",
            2)

    def _effect(self, game):
        if not game.heroes.drawing_allowed:
            game.log("Drawing not allowed, skipping draw effect")
            return
        game.heroes.choose_hero(game, prompt=f"Choose hero to draw a card: ").draw(game)

    def discard_effect(self, game, hero):
        hero.add_damage(game)

CARDS_BY_NAME['Lacewing Flies'] = LacewingFlies
