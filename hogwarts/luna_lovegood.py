from . import CARDS_BY_NAME, Ally
import constants


class LunaLovegood(Ally):
    def __init__(self):
        super().__init__("Luna Lovegood", f"Gain 1{constants.INFLUENCE}; if you play an item, gain 1{constants.DAMAGE}; roll the Ravenclaw die", 5, rolls_house_die=True)
        self._used_ability = False

    def _effect(self, game):
        self._used_ability = False
        game.heroes.active_hero.add_influence(game, 1)
        game.roll_ravenclaw_die()
        for card in game.heroes.active_hero._play_area:
            if card.is_item() and card != self:
                game.log(f"Item {card.name} already played, {self.name} adds 1{constants.DAMAGE}")
                game.heroes.active_hero.add_damage(game, 1)
                return
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if card.is_item() and not self._used_ability:
            game.log(f"Item {card.name} played, {self.name} adds 1{constants.DAMAGE}")
            game.heroes.active_hero.add_damage(game, 1)
            self._used_ability = True

CARDS_BY_NAME['Luna Lovegood'] = LunaLovegood
