import constants
import hogwarts

from .base import Hero, Alohomora, StarterAlly, StarterBroom


class EveryFlavourBeans(hogwarts.Item):
    def __init__(self):
        super().__init__("Every Flavour Beans", f"Gain 1{constants.INFLUENCE}; for each Ally played, gain 1{constants.DAMAGE}", 0)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game)
        for card in game.heroes.active_hero._play_area:
            if card.is_ally():
                game.log(f"Ally {card.name} already played, beans add damage")
                game.heroes.active_hero.add_damage(game)
        game.heroes.active_hero.add_extra_card_effect(game, self.__add_damage_if_ally)

    def __add_damage_if_ally(self, game, card):
        if card.is_ally():
            game.log(f"Ally {card.name} played, beans add damage")
            game.heroes.active_hero.add_damage(game)


class Ron(Hero):
    def __init__(self, ability, proficiency):
        super().__init__("Ron", ability, [
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            StarterAlly("Pigwidgeon"),
            EveryFlavourBeans(),
            StarterBroom("Cleansweep 11"),
        ], proficiency)
        self._damage_assigned = 0
        self._used_ability = False

    @property
    def ability_description(self):
        if self._ability < 3:
            return None
        if self._ability < 7:
            return f"If you assign 3 or more {constants.DAMAGE}, one hero gains 2{constants.HEART}"
        return f"If you assign 3 or more {constants.DAMAGE}, ALL heroes gain 2{constants.HEART}"

    def assign_damage(self, game):
        villain = super().assign_damage(game)
        if villain is None:
            return
        self._damage_assigned += 1
        if self._damage_assigned != 3 or self._used_ability:
            return
        self._used_ability = True
        if self._ability >= 7:
            self._game_seven_ability(game)
            return
        if self._ability >= 3:
            self._game_three_ability(game)

    def play_turn(self, game):
        self._damage_assigned = 0
        self._used_ability = False
        super().play_turn(game)

    def _game_three_ability(self, game):
        if not game.heroes.healing_allowed:
            game.log(f"Nobody can heal, ignoring {self.name}'s ability")
            return
        game.heroes.choose_hero(game, prompt=f"{self.name} assigned 3 or more {constants.DAMAGE}, choose hero to gain 2{constants.HEART}: ").add_hearts(game, 2)

    def _game_seven_ability(self, game):
        game.log(f"{self.name} assigned 3 or more {constants.DAMAGE}, all heroes gain 2{constants.HEART}")
        game.heroes.all_heroes.add_hearts(game, 2)

    def _monster_box_one_ability(self, game):
        game.log(f"{self.name} assigned 3 or more {constants.DAMAGE}/{constants.INFLUENCE}, all heroes gain 1{constants.HEART}")
        game.heroes.all_heroes.add_hearts(game, 1)
