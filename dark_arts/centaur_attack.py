from . import CARDS_BY_NAME, DarkArtsCard
import constants


class CentaurAttack(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Centaur Attack",
            f"ALL heroes with >=3 Spells lose 1{constants.HEART}")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        spells = sum(1 for card in hero._hand if card.is_spell())
        game.log(f"Centaur Attack: {hero.name} has {spells} Spells")
        if spells >= 3:
            hero.remove_hearts(game, 1)

CARDS_BY_NAME['Centaur Attack'] = CentaurAttack
