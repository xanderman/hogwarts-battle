from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Tarantallegra(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Tarantallegra",
            f"Active hero loses 1{constants.HEART} and cannot assign more than 1{constants.DAMAGE} to each Villain")

    def _effect(self, game):
        hero = game.heroes.active_hero
        hero.remove_hearts(game, 1)
        for villain in game.villain_deck.all_villains:
            villain._max_damage_per_turn = 1

CARDS_BY_NAME['Tarantallegra'] = Tarantallegra
