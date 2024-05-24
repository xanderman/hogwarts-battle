from . import CARDS_BY_NAME, Item
import constants


class SwordOfGryffindor(Item):
    def __init__(self):
        super().__init__("Sword of Gryffindor", f"Gain 2{constants.DAMAGE}; Roll the Gryffindor die twice", 7, rolls_house_die=True)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game, 2)
        game.roll_gryffindor_die()
        game.roll_gryffindor_die()

CARDS_BY_NAME['Sword of Gryffindor'] = SwordOfGryffindor
