from . import VILLAINS_BY_NAME, Creature
import constants


class Grindylow(Creature):
    def __init__(self):
        super().__init__(
                "Grindylow",
                f"If active Hero has >=2 Allies, add {constants.CONTROL}",
                f"Remove 1{constants.CONTROL}",
                hearts=6)

    def _effect(self, game):
        hero = game.heroes.active_hero
        allies = sum(1 for card in hero._hand if card.is_ally())
        game.log(f"{hero.name} has {allies} Allies in hand")
        if allies >= 2:
            game.locations.add_control(game)

    def _reward(self, game):
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Grindylow"] = Grindylow
