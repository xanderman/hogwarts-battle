from . import CARDS_BY_NAME, Item
import constants


class ElderWand(Item):
    def __init__(self):
        super().__init__("Elder Wand", f"For each Spell played gain 1{constants.DAMAGE} and 1{constants.HEART}", 7)

    def _effect(self, game):
        for card in game.heroes.active_hero._play_area:
            if card.is_spell():
                game.log(f"Spell {card.name} already played, elder wand adds 1{constants.DAMAGE} and 1{constants.HEART}")
                game.heroes.active_hero.add(game, damage=1, hearts=1)
        game.heroes.active_hero.add_extra_card_effect(game, self.__add_if_spell)

    def __add_if_spell(self, game, card):
        if card.is_spell():
            game.log(f"Spell {card.name} played, elder wand adds 1{constants.DAMAGE} and 1{constants.HEART}")
            game.heroes.active_hero.add(game, damage=1, hearts=1)

CARDS_BY_NAME['Elder Wand'] = ElderWand
