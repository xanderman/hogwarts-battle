from . import CARDS_BY_NAME, Ally
import constants


class NymphadoraTonks(Ally):
    def __init__(self):
        super().__init__("Nymphadora Tonks", f"Gain 3{constants.INFLUENCE} or 2{constants.DAMAGE}, or remove 1{constants.CONTROL}", 5)

    def _effect(self, game):
        if game.locations.can_remove_control:
            choice = game.input(f"Choose to (i) gain 3{constants.INFLUENCE}, (d) gain 2{constants.DAMAGE}, or (c) remove 1{constants.CONTROL}: ", "idc")
        elif game.locations.current._control == 0:
            choice = game.input(f"No {constants.CONTROL} to remove! Choose to (i) gain 3{constants.INFLUENCE}, (d) gain 2{constants.DAMAGE}: ", "id")
        else:
            choice = game.input(f"Removing {constants.CONTROL} not allowed! Choose to (i) gain 3{constants.INFLUENCE}, (d) gain 2{constants.DAMAGE}: ", "id")

        if choice == "i":
            game.heroes.active_hero.add_influence(game, 3)
        elif choice == "d":
            game.heroes.active_hero.add_damage(game, 2)
        elif choice == "c":
            game.locations.remove_control(game)

CARDS_BY_NAME['Nymphadora Tonks'] = NymphadoraTonks
