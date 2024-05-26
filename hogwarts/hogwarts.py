from . import CARDS_BY_NAME, Spell, Item, Ally

import constants



class Scourgify(Spell):
    def __init__(self):
        super().__init__(
            "Scourgify",
            f"Gain 1{constants.HEART}; you may banish a card in hand or discard",
            2)

    def _effect(self, game):
        game.heroes.active_hero.add_hearts(game)
        game.heroes.active_hero.choose_and_banish(game)

CARDS_BY_NAME['Scourgify'] = Scourgify


class Locomotor(Spell):
    def __init__(self):
        super().__init__(
            "Locomotor",
            f"You and neighbors gain 1{constants.INFLUENCE}; you may move a card from your discard to another Hero's hand",
            3)

    def _effect(self, game):
        hero = game.heroes.active_hero
        hero.add_influence(game)
        hero.neighbors(game).add_influence(game)

        cards = hero.choices_in_discard(game)
        if len(cards) == 0:
            game.log(f"{hero.name} has no cards in discard")
            return
        choices = ['c']
        choices.extend(items.keys())
        choice = game.input(f"Choose a card to give away, or (c)ancel: ", choices)
        if choice == 'c':
            return
        card = cards[choice]
        target = game.heroes.choose_hero(
            game, prompt=f"Choose hero to give {card.name} to, or (c)ancel: ", optional=True, disallow=hero)
        if target is None:
            return
        hero._discard.remove(card)
        target._hand.append(card)

CARDS_BY_NAME['Locomotor'] = Locomotor


class ArrestoMomentum(Spell):
    def __init__(self):
        super().__init__(
            "Arresto Momentum",
            f"Remove 1{constants.CONTROL}; you may banish a card in discard; if discarded banish the top Dark Arts event",
            4)

    def _effect(self, game):
        game.locations.remove_control(game)
        game.heroes.active_hero.choose_and_banish(game, discard_only=True)

    def discard_effect(self, game, hero):
        game.dark_arts_deck.banish_top_card(game)

CARDS_BY_NAME['Arresto Momentum'] = ArrestoMomentum
