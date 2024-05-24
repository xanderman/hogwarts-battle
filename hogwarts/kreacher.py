from . import CARDS_BY_NAME, Ally
import constants


class Kreacher(Ally):
    def __init__(self):
        super().__init__(
            "Kreacher",
            f"Roll the Creature die. One hero may banish a card in hand or discard",
            5)

    def _effect(self, game):
        game.roll_creature_die()
        hero = game.heroes.choose_hero(game, prompt=f"Choose hero to banish a card (c to cancel): ", optional=True)
        if hero is not None:
          hero.choose_and_banish(game)

CARDS_BY_NAME['Kreacher'] = Kreacher
