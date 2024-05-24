from . import CARDS_BY_NAME, Spell
import constants


class Reparo(Spell):
    def __init__(self):
        super().__init__("Reparo", f"Gain 2{constants.INFLUENCE} or draw a card", 3)

    def _effect(self, game):
        if not game.heroes.active_hero.drawing_allowed:
            game.log(f"Drawing not allowed, gaining 2{constants.INFLUENCE}")
            game.heroes.active_hero.add_influence(game, 2)
            return
        choice = game.input(f"Choose effect: (i){constants.INFLUENCE}, (d)raw: ", "id")
        if choice == "i":
            game.heroes.active_hero.add_influence(game, 2)
        elif choice == "d":
            game.heroes.active_hero.draw(game)

CARDS_BY_NAME['Reparo'] = Reparo
