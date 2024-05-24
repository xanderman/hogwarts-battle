from . import CARDS_BY_NAME, Spell
import constants


class Tergeo(Spell):
    def __init__(self):
        super().__init__(
            "Tergeo",
            f"Gain 1{constants.INFLUENCE}; you may banish a card in hand, if an Item, draw a card",
            2)

    def _effect(self, game):
        hero = game.heroes.active_hero
        hero.add_influence(game, 1)
        if len(game.heroes.active_hero._hand) == 0:
            game.log("No cards in hand, skipping banish effect")
            return
        banished = hero.choose_and_banish(game, hand_only=True)
        if banished is not None and banished.is_item():
            hero.draw(game)

CARDS_BY_NAME['Tergeo'] = Tergeo
