from . import CARDS_BY_NAME, Spell
import constants


class Depulso(Spell):
    def __init__(self):
        super().__init__(
            "Depulso",
            f"Gain 2{constants.INFLUENCE} or banish an Item in your hand or discard",
            3)

    def _effect(self, game):
        banished = game.heroes.active_hero.choose_and_banish(game, desc="item", card_filter=lambda card: card.is_item(), cancel_with='i', cancel_desc=f"to gain 2{constants.INFLUENCE}")
        if banished is None:
            game.heroes.active_hero.add_influence(game, 2)

CARDS_BY_NAME['Depulso'] = Depulso
