from . import CARDS_BY_NAME, Item
import constants


class Gillyweed(Item):
    def __init__(self):
        super().__init__(
            "Gillyweed",
            f"Gain 1{constants.HEART}, for each Ally played one Hero gains 1{constants.HEART}",
            1)

    def _effect(self, game):
        game.heroes.active_hero.add_hearts(game)
        if not game.heroes.healing_allowed:
            game.log("Healing not allowed, ignoring Ally bonus")
        else:
            for card in game.heroes.active_hero._play_area:
                if card.is_ally():
                    game.log(f"Ally {card.name} already played, gillyweed grants {constants.HEART}")
                    game.heroes.choose_hero(game, prompt=f"Choose hero to gain 1{constants.HEART}: ").add_hearts(game)
        game.heroes.active_hero.add_extra_card_effect(game, self.__add_heart_if_ally)

    def __add_heart_if_ally(self, game, card):
        if not card.is_ally():
            return
        if not game.heroes.healing_allowed:
            game.log("Gillyweed: Healing not allowed, ignoring Ally bonus")
            return
        game.log(f"Ally {card.name} played, gillyweed grants {constants.HEART}")
        game.heroes.choose_hero(game, prompt=f"Choose hero to gain 1{constants.HEART}: ").add_hearts(game)

CARDS_BY_NAME['Gillyweed'] = Gillyweed
