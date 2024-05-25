from . import VILLAINS_BY_NAME, Creature
import constants


class Werewolf(Creature):
    def __init__(self):
        super().__init__(
                "Werewolf",
                f"If active hero loses 4{constants.HEART}, add 1{constants.CONTROL}",
                f"ALL heroes gain 1{constants.INFLUENCE} or 2{constants.HEART}; remove 1{constants.CONTROL}",
                hearts=5, cost=4)
        self._hero_damage_taken = 0
        self._used_ability = False

    def _on_reveal(self, game):
        game.heroes.add_hearts_callback(game, self)

    def _effect(self, game):
        pass

    def end_turn(self, game):
        super().end_turn(game)
        self._hero_damage_taken = 0
        self._used_ability = False

    def hearts_callback(self, game, hero, amount, source):
        if hero != game.heroes.active_hero:
            return
        if amount >= 0:
            return
        self._hero_damage_taken -= amount
        if self._hero_damage_taken >= 4 and not self._used_ability:
            self._used_ability = True
            if self._stunned:
                game.log(f"{self.name} is stunned! No penalty for lost {constants.HEART}")
                return
            game.log(f"{self.name}: {hero.name} lost {self._hero_damage_taken}{constants.HEART} this turn, adding 1{constants.CONTROL}")
            game.locations.add_control(game)

    def remove_callbacks(self, game):
        game.heroes.remove_hearts_callback(game, self)

    def _reward(self, game):
        game.locations.remove_control(game)
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        if not hero.healing_allowed:
            game.log(f"{hero.name} can't heal, gaining 1{constants.INFLUENCE}")
            choice = 'i'
        elif not hero.gaining_tokens_allowed(game):
            game.log(f"{hero.name} not allowed to gain tokens, gaining 2{constants.HEART}")
            choice = 'h'
        else:
            choice = game.input(f"Choose {hero.name} gains (i) 1{constants.INFLUENCE} or (h) 2{constants.HEART}: ", "ih")
        if choice == 'i':
            hero.add_influence(game, 1)
        elif choice == 'h':
            hero.add_hearts(game, 2)

VILLAINS_BY_NAME["Werewolf"] = Werewolf
