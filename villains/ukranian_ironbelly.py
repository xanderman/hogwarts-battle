from . import VILLAINS_BY_NAME, Creature
import constants


class UkrainianIronbelly(Creature):
    def __init__(self):
        super().__init__(
                "Ukrainian Ironbelly",
                f"If active hero has an Ally and an Item, loses 3{constants.HEART}",
                f"ALL heroes gain 2{constants.HEART}; remove 1{constants.CONTROL}",
                hearts=8)

    def _effect(self, game):
        hero = game.heroes.active_hero
        allies = sum(1 for card in hero._hand if card.is_ally())
        items = sum(1 for card in hero._hand if card.is_item())
        if hero.is_stunned:
            game.log(f"{hero.name} is stunned and can't lose {constants.HEART}. Ignoring {self.name}!")
            return
        game.log(f"{hero.name} has {allies} Allies and {items} Items in hand")
        if allies >= 1 and items >= 1:
            hero.remove_hearts(game, 3)

    def _reward(self, game):
        game.heroes.all_heroes.add(game, hearts=2)
        game.locations.remove_control(game)

VILLAINS_BY_NAME["Ukrainian Ironbelly"] = UkrainianIronbelly
