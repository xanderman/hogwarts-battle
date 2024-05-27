from . import CARDS_BY_NAME, DarkArtsCard
import constants


class LeprechaunGold(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Leprechaun Gold",
            f"ALL Heroes discard any {constants.DAMAGE} and {constants.INFLUENCE}")

    def _effect(self, game):
        game.heroes.all_heroes.remove_all_damage(game)
        game.heroes.all_heroes.remove_all_influence(game)

CARDS_BY_NAME['Leprechaun Gold'] = LeprechaunGold
