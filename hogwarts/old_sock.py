from . import CARDS_BY_NAME, Item
import constants


class OldSock(Item):
    def __init__(self):
        super().__init__(
            "Old Sock",
            f"Gain 1{constants.INFLUENCE}; if another hero has an elf, gain 2{constants.DAMAGE}; if discarded, gain 2{constants.INFLUENCE}",
            1)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game, 1)
        for hero in game.heroes:
            if hero == game.heroes.active_hero:
                continue
            for card in hero._discard:
                if card.name == "Dobby" or card.name == "Kreacher":
                    game.log(f"{hero.name} has {card.name}, {self.name} adds 2{constants.DAMAGE}")
                    game.heroes.active_hero.add_damage(game, 2)
                    return

    def discard_effect(self, game, hero):
        hero.add_influence(game, 2)

CARDS_BY_NAME['Old Sock'] = OldSock
