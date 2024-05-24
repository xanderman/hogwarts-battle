from . import CARDS_BY_NAME, Ally
import constants


class ArgusFilch(Ally):
    def __init__(self):
        super().__init__(
            "Argus Filch & Mrs Norris",
            f"Draw two cards, then either discard or banish a card in hand",
            4)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero.drawing_allowed:
            hero.draw(game, 2)
        elif game.input("Drawing not allowed, still discard/banish? (y/n): ", "yn") == 'n':
            return
        choice = game.input("Choose to (d)iscard or (b)anish a card: ", "db")
        if choice == 'd':
            game.heroes.active_hero.choose_and_discard(game)
        elif choice == 'b':
            game.heroes.active_hero.choose_and_banish(game, hand_only=True, optional=False)

CARDS_BY_NAME['Argus Filch & Mrs Norris'] = ArgusFilch
