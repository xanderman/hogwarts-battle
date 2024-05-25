from . import VILLAINS_BY_NAME, Creature
import constants


class ChineseFireball(Creature):
    def __init__(self):
        super().__init__(
                "Chinese Fireball",
                "Reveal an additional Dark Arts event each turn",
                f"Roll the creature die; remove 1{constants.CONTROL}",
                cost=6)

    def _effect(self, game):
        game.dark_arts_deck.play(game, 1)

    def _reward(self, game):
        game.roll_creature_die()
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Chinese Fireball"] = ChineseFireball
