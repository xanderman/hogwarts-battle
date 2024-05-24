from . import CARDS_BY_NAME, Ally
import constants


class Fawkes(Ally):
    def __init__(self):
        super().__init__("Fawkes", f"Gain 2{constants.DAMAGE} or ALL heroes gain 2{constants.HEART}", 5)

    def _effect(self, game):
        if not game.heroes.healing_allowed:
            game.log(f"Healing not allowed, gaining 2{constants.DAMAGE}")
            game.heroes.active_hero.add_damage(game, 2)
            return
        choice = game.input(f"Choose effect: (d){constants.DAMAGE}, (h){constants.HEART}: ", "dh")
        if choice == "d":
            game.heroes.active_hero.add_damage(game, 2)
        elif choice == "h":
            game.heroes.all_heroes.add_hearts(game, 2)

CARDS_BY_NAME['Fawkes'] = Fawkes
