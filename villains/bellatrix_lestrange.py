from . import VILLAINS_BY_NAME, Villain
import constants


class BellatrixLestrange(Villain):
    def __init__(self):
        super().__init__(
                "Bellatrix Lestrange",
                "Reveal an additional Dark Arts event each turn",
                f"ALL heroes may take Item from discard; remove 2{constants.CONTROL}",
                hearts=9),

    def _effect(self, game):
        game.dark_arts_deck.play(game, 1)

    def _reward(self, game):
        game.locations.remove_control(game, 2)
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        items = hero.choices_in_discard(game, card_filter=lambda card: card.is_item())
        if len(items) == 0:
            game.log(f"{hero.name} has no items in discard")
            return
        choices = ['c']
        choices.extend(items.keys())
        choice = game.input(f"Choose an Item for {hero.name} to take or (c)ancel: ", choices)
        if choice == 'c':
            return
        item = items[choice]
        hero._discard.remove(item)
        hero._hand.append(item)

VILLAINS_BY_NAME["Bellatrix Lestrange"] = BellatrixLestrange
