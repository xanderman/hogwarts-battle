from . import CARDS_BY_NAME, Item
import constants


class HogwartsAHistory(Item):
    def __init__(self):
        super().__init__("Hogwarts: A History", "Roll any house die", 4, rolls_house_die=True)

    def _effect(self, game):
        choice = game.input(f"Choose house die to roll, (g)ryffindor, (h)ufflepuff, (r)avenclaw, (s)lytherin: ", "ghrs")
        if choice == "g":
            game.roll_gryffindor_die()
        elif choice == "h":
            game.roll_hufflepuff_die()
        elif choice == "r":
            game.roll_ravenclaw_die()
        elif choice == "s":
            game.roll_slytherin_die()

CARDS_BY_NAME['Hogwarts: A History'] = HogwartsAHistory
