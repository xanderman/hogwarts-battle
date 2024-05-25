from . import VILLAINS_BY_NAME, Creature
import constants


class CornishPixies(Creature):
    def __init__(self):
        super().__init__(
                "Cornish Pixies",
                f"For each card in hand with EVEN {constants.INFLUENCE} cost, lose 2{constants.HEART}",
                f"ALL heroes gain 2{constants.HEART} and 1{constants.INFLUENCE}",
                hearts=6)

    def _effect(self, game):
        hero = game.heroes.active_hero
        evens = sum(1 for card in hero._hand if card.even_cost)
        if evens == 0:
            game.log(f"{hero.name} has no cards with EVEN {constants.INFLUENCE} cost in hand, safe!")
            return
        game.log(f"{hero.name} has {evens} cards with EVEN {constants.INFLUENCE} cost in hand")
        hero.remove_hearts(game, 2 * evens)

    def _reward(self, game):
        game.heroes.all_heroes.add(game, hearts=2, influence=1)

VILLAINS_BY_NAME["Cornish Pixies"] = CornishPixies
