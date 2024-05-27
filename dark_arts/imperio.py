from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Imperio(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Imperio",
            f"Choose another hero to lose 2{constants.HEART}; reveal another card")

    def _effect(self, game):
        game.heroes.choose_hero(game, prompt=f"Choose hero to lose 2{constants.HEART}: ",
                                disallow=game.heroes.active_hero).remove_hearts(game, 2)
        game.dark_arts_deck.play(game, 1)

CARDS_BY_NAME['Imperio'] = Imperio
