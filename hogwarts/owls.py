from . import CARDS_BY_NAME, Item
import constants


class Owls(Item):
    def __init__(self):
        super().__init__("O.W.L.S.", f"Gain 2{constants.INFLUENCE}; if you play 2 spells, gain 1{constants.DAMAGE} and 1{constants.HEART}", 4)
        self._used_ability = False
        self._spells_played = 0

    def _effect(self, game):
        self._used_ability = False
        game.heroes.active_hero.add_influence(game, 2)
        self._spells_played = sum([1 for card in game.heroes.active_hero._play_area if card.is_spell()])
        if self._spells_played >= 2:
            game.log(f"Already played {self._spells_played} spells, gaining 1{constants.DAMAGE} and 1{constants.HEART}")
            game.heroes.active_hero.add(game, damage=1, hearts=1)
            return
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if card.is_spell():
            self._spells_played += 1
        if self._spells_played >= 2 and not self._used_ability:
            game.log(f"Second spell played, {self.name} adds 1{constants.DAMAGE} and 1{constants.HEART}")
            game.heroes.active_hero.add(game, damage=1, hearts=1)
            self._used_ability = True

CARDS_BY_NAME['O.W.L.S.'] = Owls
