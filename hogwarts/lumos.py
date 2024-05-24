from . import CARDS_BY_NAME, Spell
import constants


class Lumos(Spell):
    def __init__(self):
        super().__init__("Lumos", "ALL heroes draw a card", 4)

    def _effect(self, game):
        game.heroes.all_heroes.draw(game)

CARDS_BY_NAME['Lumos'] = Lumos
