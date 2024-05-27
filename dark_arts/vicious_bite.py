from . import CARDS_BY_NAME, DarkArtsCard
import constants


class ViciousBite(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Vicious Bite",
            f"ALL heroes with least {constants.HEART} lose 2{constants.HEART}; if this stuns anyone, add an extra {constants.CONTROL}")

    def _effect(self, game):
        min_hearts = min(hero._hearts for hero in game.heroes.all_heroes)
        any_stunned = False
        for hero in game.heroes.all_heroes:
            if hero._hearts == min_hearts:
                was_stunned = hero.is_stunned
                hero.remove_hearts(game, 2)
                if not was_stunned and hero.is_stunned:
                    any_stunned = True
        if any_stunned:
            game.log(f"Vicious Bite: Adding another {constants.CONTROL}")
            game.locations.add_control(game)

CARDS_BY_NAME['Vicious Bite'] = ViciousBite
