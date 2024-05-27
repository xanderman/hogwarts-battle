import constants
import hogwarts

from .base import Hero, Alohomora, StarterAlly


class Spectrespecs(hogwarts.Item):
    def __init__(self):
        super().__init__("Spectrespecs", f"Gain 1{constants.INFLUENCE}; you may reveal the top Dark Arts and choose to discard it", 0)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game)
        if game.input("Reveal top Dark Arts event? (y/n): ", "yn") == "y":
            card = game.dark_arts_deck.reveal()
            game.log(f"Revealed {card.name}: {card.description}")
            if game.input("Discard? (y/n): ", "yn") == "y":
                game.dark_arts_deck.discard()


class LionHat(hogwarts.Item):
    def __init__(self):
        super().__init__("Lion Hat", f"Gain 1{constants.INFLUENCE}; if another hero has broom or quidditch gear, gain 1{constants.DAMAGE}", 0)

    def _effect(self, game):
        broom_cards = ["Quidditch Gear", "Cleansweep 11", "Firebolt", "Nimbus 2000", "Nimbus 2001"]
        game.heroes.active_hero.add_influence(game)
        for hero in game.heroes:
            if hero == game.heroes.active_hero:
                continue
            for card in hero._hand:
                if card.name in broom_cards:
                    game.log(f"{hero.name} has {card.name}, {game.heroes.active_hero.name} gains 1{constants.DAMAGE}")
                    game.heroes.active_hero.add_damage(game)
                    return


class Luna(Hero):
    def __init__(self, ability, proficiency):
        super().__init__("Luna", ability, [
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            Alohomora(),
            StarterAlly("Crumple-horned Snorkack"),
            Spectrespecs(),
            LionHat(),
        ], proficiency)
        self._used_ability = False

    @property
    def ability_description(self):
        if self._ability < 3:
            return None
        return f"If you draw at least one extra card, one hero gains 2{constants.HEART}"

    def draw(self, game, count=1, end_of_turn=False):
        cards_before = len(self._hand)
        super().draw(game, count, end_of_turn)
        if not end_of_turn and self._ability >= 3 and len(self._hand) > cards_before and not self._used_ability:
            game.heroes.choose_hero(game, prompt=f"{self.name} drew first extra card, choose hero to gain 2{constants.HEART}: ").add_hearts(game, 2)
            self._used_ability = True

    def play_turn(self, game):
        self._used_ability = False
        super().play_turn(game)
