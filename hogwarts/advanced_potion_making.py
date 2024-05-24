from . import CARDS_BY_NAME, Item
import constants


class AdvancedPotionMaking(Item):
    def __init__(self):
        super().__init__("Advanced Potion-Making", f"ALL heroes gain 2{constants.HEART}; each hero at max gains 1{constants.DAMAGE} and draws a card", 6)

    def _effect(self, game):
        game.heroes.all_heroes.add_hearts(game, 2)
        for hero in game.heroes:
            if hero._hearts == hero._max_hearts:
                game.log(f"{hero.name} at max hearts, gaining 1{constants.DAMAGE} and drawing a card")
                hero.add(game, damage=1, cards=1)

CARDS_BY_NAME['Advanced Potion-Making'] = AdvancedPotionMaking
