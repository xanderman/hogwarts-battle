from . import VILLAINS_BY_NAME, Villain
import constants


class DoloresUmbridge(Villain):
    def __init__(self):
        super().__init__(
                "Dolores Umbridge",
                f"If acquire card with cost 4{constants.INFLUENCE} or more, lose 1{constants.HEART}",
                f"ALL heroes gain 1{constants.INFLUENCE} and 2{constants.HEART}",
                hearts=7)

    def _on_reveal(self, game):
        game.heroes.add_acquire_callback(game, self)

    def _effect(self, game):
        pass

    def acquire_callback(self, game, hero, card):
        if card.cost >= 4:
            if self._stunned:
                game.log(f"{self.name} is stunned! No penalty for acquire")
                return
            game.log(f"{self.name}: {game.heroes.active_hero.name} acquired {card.name}, so loses 1{constants.HEART}")
            hero.remove_hearts(game, 1)

    def remove_callbacks(self, game):
        game.heroes.remove_acquire_callback(game, self)

    def _reward(self, game):
        game.heroes.all_heroes.add(game, influence=1, hearts=2)

VILLAINS_BY_NAME["Dolores Umbridge"] = DoloresUmbridge
