from . import CARDS_BY_NAME, Spell
import constants


class Accio(Spell):
    def __init__(self):
        super().__init__("Accio", f"Gain 2{constants.INFLUENCE} or take Item from discard", 4)

    def _effect(self, game):
        hero = game.heroes.active_hero
        items = hero.choices_in_discard(game, card_filter=lambda card: card.is_item())
        if len(items) == 0:
            game.log(f"{hero.name} has no items in discard, gaining 2{constants.INFLUENCE}")
            hero.add_influence(game, 2)
            return
        choices = ['i']
        choices.extend(items.keys())
        choice = game.input(f"Choose an item for {hero.name} to take, or (i) to gain 2{constants.INFLUENCE}: ", choices)
        if choice == 'i':
            hero.add_influence(game, 2)
            return
        item = items[choice]
        hero._discard.remove(item)
        hero._hand.append(item)

CARDS_BY_NAME['Accio'] = Accio
