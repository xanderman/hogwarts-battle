from . import CARDS_BY_NAME, Spell
import constants


class PrioriIncantatem(Spell):
    def __init__(self):
        super().__init__(
            "Priori Incantatem",
            f"Choose a played Spell and gain its effect",
            3)

    def _effect(self, game):
        played_spells = [card for card in game.heroes.active_hero._play_area if card.is_spell()]
        if len(played_spells) == 0:
            game.log("You haven't played any spells, priori incantatem wasted!")
            return
        if len(played_spells) == 1:
            game.log(f"Only one spell played, copying {played_spells[0].name}")
            played_spells[0]._effect(game)
            return
        while True:
            choice = int(game.input("Choose played spell to polyjuice: ", range(len(game.heroes.active_hero._play_area))))
            card = game.heroes.active_hero._play_area[choice]
            if not card.is_spell():
                game.log("{card.name} is not an spell!")
                continue
            game.log(f"Copying {card.name}")
            card._effect(game)
            break

CARDS_BY_NAME['Priori Incantatem'] = PrioriIncantatem
