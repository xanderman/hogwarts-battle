from . import VILLAINS_BY_NAME, Creature
import constants


class Troll(Creature):
    def __init__(self):
        super().__init__(
                "Troll",
                f"Choose: lose 2{constants.HEART} or add Detention! to discard",
                f"ALL heroes gain 1{constants.HEART} and may banish an Item from hand or discard",
                hearts=7)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.is_stunned:
            game.log(f"{hero.name} is stunned and can't lose {constants.HEART}. No penalty for {self.name}!")
            return
        choice = game.input(f"Choose: (h) lose 2{constants.HEART} or (d) add Detention!: ", "hd")
        if choice == 'h':
            hero.remove_hearts(game, 2)
        elif choice == 'd':
            hero.add_detention(game)
        else:
            raise Exception("Invalid choice")

    def _reward(self, game):
        game.heroes.all_heroes.effect(game, self.__reward_per_hero)

    def __reward_per_hero(self, game, hero):
        hero.add_hearts(game, 1)
        hero.choose_and_banish(game, desc="item", card_filter=lambda card: card.is_item())

VILLAINS_BY_NAME["Troll"] = Troll
