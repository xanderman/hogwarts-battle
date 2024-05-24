from . import CARDS_BY_NAME, Item
import constants


class Harp(Item):
    def __init__(self):
        super().__init__(
            "Harp",
            f"Gain 1{constants.DAMAGE}; stun one Creature",
            6)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game, 1)
        choices = game.villain_deck.creature_choices
        if len(choices) == 0:
            game.log("No creatures to stun!")
            return
        choice = game.input("Choose creature to stun ('c' to cancel): ", ['c'] + choices)
        if choice == 'c':
            return
        game.villain_deck[choice].stun(game)

CARDS_BY_NAME['Harp'] = Harp
