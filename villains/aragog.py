from . import VILLAINS_BY_NAME, Creature
import constants


class Aragog(Creature):
    def __init__(self):
        super().__init__(
                "Aragog",
                f"Active hero loses 1{constants.HEART} for each Creature",
                f"ALL heroes gain 1{constants.INFLUENCE} and 2{constants.HEART}; remove 1{constants.CONTROL}",
                hearts=8)

    def _effect(self, game):
        total = sum(1 for card in game.villain_deck.current if card.is_creature)
        game.log(f"Aragog: {total} Creatures in play")
        game.heroes.active_hero.remove_hearts(game, total)

    def _reward(self, game):
        game.heroes.all_heroes.add(game, influence=1, hearts=2)
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Aragog"] = Aragog
