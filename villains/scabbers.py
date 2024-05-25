from . import VILLAINS_BY_NAME, VillainCreature
import constants


class Scabbers(VillainCreature):
    def __init__(self):
        super().__init__(
                "Scabbers",
                f"Reveal top card of deck, if costs 1{constants.INFLUENCE} or more, discard and lose 2{constants.HEART}",
                f"ALL heroes may take card with cost <= 3{constants.INFLUENCE} from discard; remove 1{constants.CONTROL}",
                hearts=7)

    def _effect(self, game):
        hero = game.heroes.active_hero
        card = hero.reveal_top_card(game)
        if card is None:
            game.log(f"{hero.name} has no cards left to reveal")
            return
        game.log(f"{hero.name} revealed {card}")
        if card.cost >= 1:
            hero.discard_top_card(game)
            hero.remove_hearts(game, 2)

    def _reward(self, game):
        game.locations.remove_control(game)
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        cards = hero.choices_in_discard(game, card_filter=lambda card: card.cost <= 3)
        if len(cards) == 0:
            game.log(f"{hero.name} has no cheap cards in discard")
            return
        choices = ['c']
        choices.extend(cards.keys())
        choice = game.input(f"Choose a card for {hero.name} to take or (c)ancel: ", choices)
        if choice == 'c':
            return
        card = cards[choice]
        hero._discard.remove(card)
        hero._hand.append(card)

VILLAINS_BY_NAME["Scabbers"] = Scabbers
