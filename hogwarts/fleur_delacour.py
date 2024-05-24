from . import CARDS_BY_NAME, Ally
import constants


class FleurDelacour(Ally):
    def __init__(self):
        super().__init__("Fleur Delacour", f"Gain 2{constants.INFLUENCE}; if you play another ally, gain 2{constants.HEART}", 4)
        self._used_ability = False

    def _effect(self, game):
        self._used_ability = False
        game.heroes.active_hero.add_influence(game, 2)
        for card in game.heroes.active_hero._play_area:
            if card.is_ally() and card != self:
                game.log(f"Ally {card.name} already played, {self.name} adds 2{constants.HEART}")
                game.heroes.active_hero.add_hearts(game, 2)
                return
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if card.is_ally() and card != self and not self._used_ability:
            game.log(f"Ally {card.name} played, {self.name} adds 2{constants.HEART}")
            game.heroes.active_hero.add_hearts(game, 2)
            self._used_ability = True

CARDS_BY_NAME['Fleur Delacour'] = FleurDelacour
