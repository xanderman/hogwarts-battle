import constants
import hogwarts

from .base import Hero, Alohomora, StarterAlly, StarterBroom


class BatBogeyHex(hogwarts.Item):
    def __init__(self):
        super().__init__("Bat Bogey Hex", f"Gain 1{constants.DAMAGE}, or ALL heroes gain 1{constants.HEART}", 0)

    def _effect(self, game):
        if not game.heroes.healing_allowed:
            game.log(f"Nobody can heal, gaining 1{constants.DAMAGE}")
            game.heroes.active_hero.add_damage(game, 1)
            return
        choice =  game.input(f"Choose effect: (d){constants.DAMAGE}, (h) ALL heroes get 1{constants.HEART}: ", "dh")
        if choice == "d":
            game.heroes.active_hero.add_damage(game)
        elif choice == "h":
            game.heroes.all_heroes.add_hearts(game, 1)


class Ginny(Hero):
    def __init__(self, ability, proficiency):
        super().__init__("Ginny", ability, [
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            StarterAlly("Arnold"),
            StarterBroom("Nimbus 2000"),
            BatBogeyHex(),
        ], proficiency)
        self._villains_damaged = set()
        self._used_ability = False

    @property
    def ability_description(self):
        if self._ability < 3:
            return None
        return f"If you assign {constants.DAMAGE} to 2 or more villains, ALL heroes gain 1{constants.INFLUENCE}"

    def assign_damage(self, game):
        villain = super().assign_damage(game)
        if villain is None:
            return
        self._villains_damaged.add(villain)
        if self._ability < 3 or len(self._villains_damaged) != 2 or self._used_ability:
            return
        self._used_ability = True
        game.log(f"{self.name} assigned {constants.DAMAGE}/{constants.INFLUENCE} to 2 or more villains, ALL heroes gain 1{constants.INFLUENCE}")
        game.heroes.all_heroes.add_influence(game, 1)

    def play_turn(self, game):
        self._villains_damaged = set()
        self._used_ability = False
        super().play_turn(game)
