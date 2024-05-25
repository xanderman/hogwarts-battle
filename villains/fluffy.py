from . import VILLAINS_BY_NAME, Creature
import constants


class Fluffy(Creature):
    def __init__(self):
        super().__init__(
                "Fluffy",
                f"For each Item in hand, lose 1{constants.HEART} or discard a card",
                f"ALL heroes gain 1{constants.HEART} and draw a card",
                hearts=8)

    def _effect(self, game):
        hero = game.heroes.active_hero
        items = sum(1 for card in hero._hand if card.is_item())
        if items == 0:
            game.log(f"{hero.name} has no Items in hand, safe!")
            return
        if hero.is_stunned:
            game.log(f"{hero.name} is stunned and can't lose {constants.HEART}. No penalty for Items in hand!")
            return
        game.log(f"{hero.name} has {items} Items in hand")
        for _ in range(items):
            choices = ['h'] + [str(i) for i in range(len(hero._hand))]
            choice = game.input(f"Choose a card for {hero.name} to discard or (h) to lose 1{constants.HEART}: ", choices)
            if choice == 'h':
                hero.remove_hearts(game, 1)
            else:
                hero.discard(game, int(choice))

    def _reward(self, game):
        game.heroes.all_heroes.add(game, hearts=1, cards=1)

VILLAINS_BY_NAME["Fluffy"] = Fluffy
