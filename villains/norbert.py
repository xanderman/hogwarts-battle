from . import VILLAINS_BY_NAME, Creature
import constants


class Norbert(Creature):
    def __init__(self):
        super().__init__(
                "Norbert",
                f"Active hero loses 1{constants.HEART} plus 1{constants.HEART} for each Detention! in hand",
                f"ALL heroes may banish a card from hand or discard",
                hearts=6)

    def _effect(self, game):
        hero = game.heroes.active_hero
        detentions = sum(1 for card in hero._hand if card.name == "Detention!")
        game.log(f"{hero.name} has {detentions} Detention! in hand")
        hero.remove_hearts(game, 1 + detentions)

    def _reward(self, game):
        game.heroes.all_heroes.choose_and_banish(game)

VILLAINS_BY_NAME["Norbert"] = Norbert
