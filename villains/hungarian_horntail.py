from . import VILLAINS_BY_NAME, Creature
import constants


class HungarianHorntail(Creature):
    def __init__(self):
        super().__init__(
                "Hungarian Horntail",
                f"Other Villains and Creatures may not be assigned {constants.DAMAGE}",
                f"Roll the creature die; remove 1{constants.CONTROL}",
                hearts=10)

    def _effect(self, game):
        for foe in game.villain_deck.current:
            if foe is self:
                continue
            foe._can_take_damage = False

    def _on_stun(self, game):
        for foe in game.villain_deck.current:
            if foe is self:
                continue
            foe._can_take_damage = True

    def _on_recover_from_stun(self, game):
        for foe in game.villain_deck.current:
            if foe is self:
                continue
            foe._can_take_damage = False

    def _reward(self, game):
        game.roll_creature_die()
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Hungarian Horntail"] = HungarianHorntail
