from . import VILLAINS_BY_NAME, Creature
import constants


class Grawp(Creature):
    def __init__(self):
        super().__init__(
                "Grawp",
                f"If active hero has >=6{constants.CARD}, loses 2{constants.HEART}",
                f"ALL heroes draw 2{constants.CARD} then discard 1{constants.CARD}",
                hearts=8)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.is_stunned:
            game.log(f"{hero.name} is stunned and can't lose {constants.HEART}. Ignoring {self.name}!")
            return
        game.log(f"{hero.name} has {len(hero._hand)} cards in hand")
        if len(hero._hand) >= 6:
            hero.remove_hearts(game, 2)

    def _reward(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        if hero.drawing_allowed:
            hero.draw(game, 2)
        elif game.input("Drawing not allowed, still discard? (y/n): ", "yn") == 'n':
            return
        # No callbacks. It's technically an enemy, but it's a reward.
        hero.choose_and_discard(game, with_callbacks=False)

VILLAINS_BY_NAME["Grawp"] = Grawp
