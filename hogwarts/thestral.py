from . import CARDS_BY_NAME, Ally
import constants


class Thestral(Ally):
    def __init__(self):
        super().__init__(
            "Thestral",
            f"ALL heroes choose to gain 1{constants.INFLUENCE} or 2{constants.HEART}",
            4)

    def _effect(self, game):
        for hero in game.heroes.all_heroes:
            if not hero.healing_allowed:
                game.log(f"{hero.name} can't heal, gaining 1{constants.INFLUENCE}")
                hero.add_influence(game, 1)
                continue
            if not hero.gaining_tokens_allowed(game):
                game.log(f"{hero.name} not allowed to gain tokens, gaining 2{constants.HEART}")
                hero.add_hearts(game, 2)
                continue
            choice = game.input(f"Choose {hero.name} gains (i) 1{constants.INFLUENCE} or (h) 2{constants.HEART}: ", "ih")
            if choice == 'i':
                hero.add_influence(game, 1)
            elif choice == 'h':
                hero.add_hearts(game, 2)

CARDS_BY_NAME['Thestral'] = Thestral
