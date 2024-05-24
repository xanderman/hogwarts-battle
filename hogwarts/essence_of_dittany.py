from . import CARDS_BY_NAME, Item
import constants


class EssenceOfDittany(Item):
    def __init__(self):
        super().__init__("Essence of Dittany", f"Any hero gains 2{constants.HEART}", 2)

    def _effect(self, game):
        if not game.heroes.healing_allowed:
            game.log("Healing not allowed, ignoring Essence of Dittany effect")
            return
        while True:
            choice = int(game.input(f"Choose hero to gain 2{constants.HEART}: ", range(len(game.heroes))))
            hero = game.heroes[choice]
            if not hero.healing_allowed:
                game.log(f"{hero.name} cannot heal, choose another hero!")
                continue
            hero.add_hearts(game, 2)
            break

CARDS_BY_NAME['Essence of Dittany'] = EssenceOfDittany
