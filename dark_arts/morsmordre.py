from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Morsmordre(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Morsmordre",
            f"ALL heroes lose 1{constants.HEART}, add 1{constants.CONTROL}")

    def _effect(self, game):
        # Bit of a hack. Maybe import and do type check?
        death_eaters = sum(1 for v in game.villain_deck.current if v.name == "Death Eater" and not v._stunned)
        if death_eaters > 0:
            game.log(f"Damage increased to {death_eaters+1}{constants.HEART} by Death Eater(s)")
        game.heroes.all_heroes.remove_hearts(game, 1 + death_eaters)
        game.locations.add_control(game)

CARDS_BY_NAME['Morsmordre'] = Morsmordre
