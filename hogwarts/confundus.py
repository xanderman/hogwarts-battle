from . import CARDS_BY_NAME, Spell
import constants


class Confundus(Spell):
    def __init__(self):
        super().__init__("Confundus", f"Gain 1{constants.DAMAGE}; if you damage each Villian, remove 1{constants.CONTROL}", 3)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        if all([villain.took_damage for villain in game.villain_deck.all_villains]):
            game.log(f"Already damaged all villains, {self.name} removes 1{constants.CONTROL}")
            game.locations.remove_control(game)
            return
        self._used_ability = False
        game.heroes.active_hero.add_extra_damage_effect(game, self.__extra_effect)

    def __extra_effect(self, game, villain, damage):
        if all([villain.took_damage for villain in game.villain_deck.all_villains]) and not self._used_ability:
            game.log(f"Damaged all villains, {self.name} removes 1{constants.CONTROL}")
            game.locations.remove_control(game)
            self._used_ability = True

CARDS_BY_NAME['Confundus'] = Confundus
