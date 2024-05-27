import constants
import hogwarts

from .base import Hero, Alohomora, StarterAlly


class TimeTurner(hogwarts.Item):
    def __init__(self):
        super().__init__("Time-Turner", f"Gain 1{constants.INFLUENCE}, may put acquired Spells on top of deck", 0)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game)
        game.heroes.active_hero.can_put_spells_in_deck(game)


class TalesOfBeedleTheBard(hogwarts.Item):
    def __init__(self):
        super().__init__("The Tales of Beedle the Bard", f"Gain 2{constants.INFLUENCE}, or ALL heroes gain 1{constants.INFLUENCE}", 0)

    def _effect(self, game):
        if len(game.heroes) == 1:
            game.log(f"Only one hero, gaining 2{constants.INFLUENCE}")
            choice = "y"
        else:
            choice = game.input(f"Choose effect: (y)ou get 2{constants.INFLUENCE}, (a)ll get 1{constants.INFLUENCE}: ", "ya")

        if choice == "y":
            game.heroes.active_hero.add_influence(game, 2)
        elif choice == "a":
            game.heroes.all_heroes.add_influence(game, 1)


class Hermione(Hero):
    def __init__(self, ability, proficiency):
        super().__init__("Hermione", ability, [
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            StarterAlly("Crookshanks"),
            TimeTurner(),
            TalesOfBeedleTheBard(),
        ], proficiency)
        self._spells_played = 0
        self._used_ability = False

    @property
    def ability_description(self):
        if self._ability < 3:
            return None
        if self._ability < 7:
            return f"If you play 4 or more spells, one hero gains 1{constants.INFLUENCE}"
        return f"If you play 4 or more spells, ALL heroes gain 1{constants.INFLUENCE}"

    def play_turn(self, game):
        self._spells_played = 0
        self._used_ability = False
        super().play_turn(game)

    def play_card(self, game, which):
        if self._hand[which].is_spell():
            self._spells_played += 1
        super().play_card(game, which)
        if self._spells_played != 4 or self._used_ability:
            return
        self._used_ability = True
        if self._ability >= 7:
            self._game_seven_ability(game)
            return
        if self._ability >= 3:
            self._game_three_ability(game)

    def _game_three_ability(self, game):
        game.heroes.choose_hero(game, prompt=f"{self.name} played 4 Spells, choose hero to gain 1{constants.INFLUENCE}: ").add_influence(game, 1)

    def _game_seven_ability(self, game):
        game.log(f"{self.name} played 4 Spells, ALL heroes gain 1{constants.INFLUENCE}: ")
        game.heroes.all_heroes.add_influence(game, 1)

    def _monster_box_one_ability(self, game):
        game.log(f"{self.name} played 4 spells. Two heroes gain 1{constants.DAMAGE}")
        game.heroes.choose_two_heroes(game, prompt=f"to gain 1{constants.DAMAGE}").add_damage(game, 1)
