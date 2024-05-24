from . import CARDS_BY_NAME, Ally
import constants


class RemusLupin(Ally):
    def __init__(self):
        super().__init__("Remus Lupin", f"Gain 1{constants.DAMAGE}, any hero gains 3{constants.HEART}", 4)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        if not game.heroes.healing_allowed:
            game.log(f"Healing not allowed, ignoring Lupin's healing effect")
            return
        game.heroes.choose_hero(game, prompt=f"Choose hero to gain 3{constants.HEART}: ").add_hearts(game, 3)

CARDS_BY_NAME['Remus Lupin'] = RemusLupin
