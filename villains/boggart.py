import random

from . import VILLAINS_BY_NAME, Creature
import constants


class Boggart(Creature):
    def __init__(self):
        super().__init__(
                "Boggart",
                "Roll the Creature die",
                "Roll the Creature die",
                hearts=5, cost=3)

    def _effect(self, game):
        faces = [constants.HEART, constants.HEART + constants.HEART, constants.CARD, constants.CARD + constants.CARD, constants.DAMAGE, constants.CONTROL]
        die_result = random.choice(faces)
        if game.heroes.active_hero.can_reroll_die(house_die=False) and game.input(f"Rolled {die_result}, (a)ccept or (r)eroll? ", "ar") == "r":
            die_result = random.choice(faces)
        if die_result == constants.HEART:
            game.log(f"Rolled {constants.HEART}, ALL Creatures heal 1{constants.DAMAGE} and/or {constants.INFLUENCE}")
            game.villain_deck.all_creatures.remove_damage(game, 1)
            game.villain_deck.all_creatures.remove_influence(game, 1)
        elif die_result == constants.HEART + constants.HEART:
            game.log(f"Rolled {constants.HEART}{constants.HEART}, ALL foes heal 1{constants.DAMAGE} and/or {constants.INFLUENCE}")
            game.villain_deck.all.remove_damage(game, 1)
            game.villain_deck.all.remove_influence(game, 1)
        elif die_result == constants.CONTROL:
            game.log(f"Rolled {constants.CONTROL}, add 1{constants.CONTROL}")
            game.locations.add_control(game)
        elif die_result == constants.DAMAGE:
            game.log(f"Rolled {constants.DAMAGE}, ALL heroes lose 1{constants.HEART}")
            game.heroes.all_heroes.remove_hearts(game, 1)
        elif die_result == constants.CARD:
            game.log(f"Rolled {constants.CARD}, ALL heroes discard a card")
            game.heroes.all_heroes.choose_and_discard(game)
        elif die_result == constants.CARD + constants.CARD:
            game.log(f"Rolled {constants.CARD}{constants.CARD}, active hero discards 2 cards")
            game.heroes.active_hero.choose_and_discard(game, 2)

    def _reward(self, game):
        game.roll_creature_die()

VILLAINS_BY_NAME["Boggart"] = Boggart
