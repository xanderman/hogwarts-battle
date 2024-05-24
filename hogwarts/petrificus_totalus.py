from . import CARDS_BY_NAME, Spell
import constants


class PetrificusTotalus(Spell):
    def __init__(self):
        super().__init__("Petrificus Totalus", f"Gain 1{constants.DAMAGE}; stun a Villain", 6)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        choices = game.villain_deck.villain_choices
        if len(choices) == 0:
            game.log("No villains to stun!")
            return
        choice = game.input("Choose villain to stun ('c' to cancel): ", ['c'] + choices)
        if choice == 'c':
            return
        game.villain_deck[choice].stun(game)

CARDS_BY_NAME['Petrificus Totalus'] = PetrificusTotalus
