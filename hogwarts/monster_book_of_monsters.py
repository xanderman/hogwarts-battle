from . import CARDS_BY_NAME, Item
import constants


class MonsterBookOfMonster(Item):
    def __init__(self):
        super().__init__(
            "Monster Book of Monsters",
            f"Gain 1{constants.DAMAGE}; roll the Creature die",
            5)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game, 1)
        game.roll_creature_die()

CARDS_BY_NAME['Monster Book of Monsters'] = MonsterBookOfMonster
