import random

from . import VILLAINS_BY_NAME, Creature
import constants


class SwedishShortSnout(Creature):
    def __init__(self):
        super().__init__(
                "Swedish Short-Snout",
                f"Roll the Hufflepuff die",
                f"Roll the Hufflepuff and Creature dice",
                cost=6)

    def _effect(self, game):
        faces = [constants.INFLUENCE, constants.HEART, constants.HEART, constants.HEART, constants.CARD, constants.DAMAGE]
        game.log("Rolling Hufflepuff die")
        die_result = random.choice(faces)
        if game.heroes.active_hero.can_reroll_die(house_die=True) and game.input(f"Rolled {die_result}, (a)ccept or (r)eroll? ", "ar") == "r":
            die_result = random.choice(faces)
        if die_result == constants.HEART:
            game.log(f"Rolled {constants.HEART}, ALL Creatures heal 1{constants.DAMAGE}")
            game.villain_deck.all_creatures.remove_damage(game, 1)
        elif die_result == constants.INFLUENCE:
            game.log(f"Rolled {constants.INFLUENCE}, ALL Creatures heal 1{constants.INFLUENCE}")
            game.villain_deck.all_creatures.remove_influence(game, 1)
        elif die_result == constants.DAMAGE:
            game.log(f"Rolled {constants.DAMAGE}, ALL heroes lose 1{constants.HEART}")
            game.heroes.all_heroes.remove_hearts(game, 1)
        elif die_result == constants.CARD:
            game.log(f"Rolled {constants.CARD}, ALL Heroes add Detention! to hand")
            game.heroes.all_heroes.add_detention(game, to_hand=True)

    def _reward(self, game):
        game.roll_hufflepuff_die()
        game.roll_creature_die()

VILLAINS_BY_NAME["Swedish Short-Snout"] = SwedishShortSnout
