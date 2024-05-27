import constants
import hogwarts

from .base import Hero, Alohomora, StarterAlly


class Remembrall(hogwarts.Item):
    def __init__(self):
        super().__init__("Remembrall", f"Gain 1{constants.INFLUENCE}; if discarded, gain 2{constants.INFLUENCE}", 0)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game)

    def discard_effect(self, game, hero):
        hero.add_influence(game, 2)


class Mandrake(hogwarts.Item):
    def __init__(self):
        super().__init__("Mandrake", f"Gain 1{constants.DAMAGE}, or one hero gains 2{constants.HEART}", 0)

    def _effect(self, game):
        if not game.heroes.healing_allowed:
            game.log(f"Nobody can heal, gaining 1{constants.DAMAGE}")
            game.heroes.active_hero.add_damage(game, 1)
            return
        choices = ['d'] + [str(i) for i in range(len(game.heroes))]
        while True:
            choice = game.input(f"Choose hero to gain 2{constants.HEART} or (d){constants.DAMAGE}: ", choices)
            if choice == "d":
                game.heroes.active_hero.add_damage(game)
                break
            hero = game.heroes[int(choice)]
            if not hero.healing_allowed:
                game.log(f"{hero.name} can't heal, choose another hero!")
                continue
            game.heroes[int(choice)].add_hearts(game, 2)
            break


class Neville(Hero):
    def __init__(self, ability, proficiency):
        super().__init__("Neville", ability, [
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            StarterAlly("Trevor"),
            Remembrall(),
            Mandrake(),
        ], proficiency)
        self._healed_heroes = set()

    @property
    def ability_description(self):
        if self._ability < 3:
            return None
        if self._ability < 7:
            return f"The first time a hero gains {constants.HEART} on your turn, that hero gains +1{constants.HEART}"
        return f"Each time a hero gains {constants.HEART} on your turn, that hero gains +1{constants.HEART}"

    def hearts_callback(self, game, hero, amount, source):
        if source == self:
            return
        if self._ability >= 7:
            self._game_seven_ability_healing_callback(game, hero, amount)
            return
        if self._ability >= 3:
            self._game_three_ability_healing_callback(game, hero, amount)

    def _game_three_ability_healing_callback(self, game, hero, amount):
        if hero in self._healed_heroes:
            return
        if amount < 1:
            return
        self._healed_heroes.add(hero)
        game.log(f"First time {self.name} healed {hero.name} this turn, {hero.name} gets an extra {constants.HEART}")
        hero.add_hearts(game, 1, source=self)

    def _game_seven_ability_healing_callback(self, game, hero, amount):
        if amount < 1:
            return
        game.log(f"{self.name} healed {hero.name}, {hero.name} gets an extra {constants.HEART}")
        hero.add_hearts(game, 1, source=self)

    def _monster_box_one_ability_healing_callback(self, game, hero, amount):
        if hero in self._healed_heroes:
            return
        if amount < 1:
            return
        game.log(f"First time {self.name} healed {hero.name} this turn, {hero.name} gets an extra {constants.HEART} or {constants.INFLUENCE}")
        if not hero.healing_allowed:
            game.log(f"{hero.name} can't heal, {hero.name} gains 1{constants.INFLUENCE}")
            hero.add_influence(game, 1)
            return
        if not hero.gaining_tokens_allowed(game):
            game.log(f"{hero.name} can't gain tokens, {hero.name} gains 1{constants.HEART}")
            hero.add_hearts(game, 1)
            return
        self._healed_heroes.add(hero)
        choice = game.input(f"Choose effect: (h){constants.HEART}, (i){constants.INFLUENCE}: ", "hi")
        if choice == "h":
            hero.add_hearts(game, 1)
        elif choice == "i":
            hero.add_influence(game, 1)

    def play_turn(self, game):
        self._healed_heroes = set()
        game.heroes.add_hearts_callback(game, self)
        super().play_turn(game)
        game.heroes.remove_hearts_callback(game, self)
