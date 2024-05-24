from . import CARDS_BY_NAME, Spell
import constants


class Nox(Spell):
    def __init__(self):
        super().__init__(
            "Nox",
            f"Gain 1{constants.DAMAGE}; ALL heroes may banish a card in hand or discard",
            6)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game, 1)
        game.heroes.all_heroes.choose_and_banish(game)

CARDS_BY_NAME['Nox'] = Nox
