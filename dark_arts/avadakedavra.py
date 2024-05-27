from . import CARDS_BY_NAME, DarkArtsCard
import constants


class AvadaKedavra(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Avada Kedavra",
            f"Active hero loses 3{constants.HEART}, if this stuns add +1{constants.CONTROL}; reveal another card")

    def _effect(self, game):
        hero = game.heroes.active_hero
        was_stunned = hero.is_stunned
        hero.remove_hearts(game, 3)
        if not was_stunned and hero.is_stunned:
            game.log(f"Stunned by Avada Kedavra! Adding another {constants.CONTROL}")
            game.locations.add_control(game)
        game.dark_arts_deck.play(game, 1)

CARDS_BY_NAME['Avada Kedavra'] = AvadaKedavra
