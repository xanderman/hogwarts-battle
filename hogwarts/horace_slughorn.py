from . import CARDS_BY_NAME, Ally
import constants


class HoraceSlughorn(Ally):
    def __init__(self):
        super().__init__("Horace Slughorn", f"ALL heroes gain 1{constants.INFLUENCE} or 1{constants.HEART}; roll the Slytherin die", 6, rolls_house_die=True)

    def _effect(self, game):
        for hero in game.heroes.all_heroes:
            if not hero.healing_allowed:
                game.log(f"{hero.name} can't heal, gaining 1{constants.INFLUENCE}")
                hero.add_influence(game, 1)
                continue
            if not hero.gaining_tokens_allowed(game):
                game.log(f"{hero.name} not allowed to gain tokens, gaining 1{constants.HEART}")
                hero.add_hearts(game, 1)
                continue
            choice = game.input(f"Choose {hero.name} gains (i) 1{constants.INFLUENCE} or (h) 1{constants.HEART}: ", "ih")
            if choice == 'i':
                hero.add_influence(game, 1)
            elif choice == 'h':
                hero.add_hearts(game, 1)
        game.roll_slytherin_die()

CARDS_BY_NAME['Horace Slughorn'] = HoraceSlughorn
