from . import CARDS_BY_NAME, Item
import constants


class PolyjuicePotion(Item):
    def __init__(self):
        super().__init__("Polyjuice Potion", "Choose a played Ally and gain its effect", 3)

    def _effect(self, game):
        played_allies = [card for card in game.heroes.active_hero._play_area if card.is_ally()]
        if len(played_allies) == 0:
            game.log("You haven't played any allies, polyjuice wasted!")
            return
        if len(played_allies) == 1:
            game.log(f"Only one ally played, copying {played_allies[0].name}")
            played_allies[0]._effect(game)
            return
        while True:
            choice = int(game.input("Choose played ally to polyjuice: ", range(len(game.heroes.active_hero._play_area))))
            card = game.heroes.active_hero._play_area[choice]
            if not card.is_ally():
                game.log("{card.name} is not an ally!")
                continue
            game.log(f"Copying {card.name}")
            card._effect(game)
            break

CARDS_BY_NAME['Polyjuice Potion'] = PolyjuicePotion
