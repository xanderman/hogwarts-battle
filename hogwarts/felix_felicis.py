from . import CARDS_BY_NAME, Item
import constants


class FelixFelicis(Item):
    def __init__(self):
        super().__init__(
            "Felix Felicis",
            f"Choose 2: gain 2{constants.DAMAGE}, 2{constants.INFLUENCE}, 2{constants.HEART}, draw two cards",
            7)

    def _effect(self, game):
        choices = {'d': f"2{constants.DAMAGE}", 'i': f"2{constants.INFLUENCE}", 'h': f"2{constants.HEART}", 'c': "draw 2 cards"}
        if not game.heroes.active_hero.healing_allowed:
            game.log("Healing not allowed, removing hearts option")
            del(choices['h'])
        if not game.heroes.active_hero.drawing_allowed:
            game.log("Drawing not allowed, removing draw option")
            del(choices['c'])
        if len(choices) == 2:
            game.log(f"Only two options left, gaining 2{constants.DAMAGE} and 2{constants.INFLUENCE}")
            game.heroes.active_hero.add_damage(game, 2)
            game.heroes.active_hero.add_influence(game, 2)
            return
        for i in range(2):
            choice_str = ", ".join(f"({key}) {value}" for key, value in choices.items())
            choice = game.input(f"Choose {['first', 'second'][i]} {choice_str}: ", choices.keys())
            del(choices[choice])
            if choice == 'd':
                game.heroes.active_hero.add_damage(game, 2)
            elif choice == 'i':
                game.heroes.active_hero.add_influence(game, 2)
            elif choice == 'h':
                game.heroes.active_hero.add_hearts(game, 2)
            elif choice == 'c':
                game.heroes.active_hero.draw(game, 2)

CARDS_BY_NAME['Felix Felicis'] = FelixFelicis
