from . import VILLAINS_BY_NAME, Villain
import constants


class CrabbeAndGoyle(Villain):
    def __init__(self):
        super().__init__(
                "Crabbe & Goyle",
                f"When forced to discard, lose 1{constants.HEART}",
                f"ALL heroes draw 1{constants.CARD}",
                hearts=5)

    def _on_reveal(self, game):
        game.heroes.add_discard_callback(game, self)

    def _effect(self, game):
        pass

    def discard_callback(self, game, hero):
        if self._stunned:
            game.log(f"{self.name} is stunned! No penalty for discard")
            return
        game.log(f"{self.name}: {hero.name} discarded, so loses 1{constants.HEART}")
        hero.remove_hearts(game, 1)

    def remove_callbacks(self, game):
        game.heroes.remove_discard_callback(game, self)

    def _reward(self, game):
        game.heroes.all_heroes.draw(game)

VILLAINS_BY_NAME["Crabbe & Goyle"] = CrabbeAndGoyle
