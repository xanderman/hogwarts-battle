from . import VILLAINS_BY_NAME, Creature
import constants


class Centaur(Creature):
    def __init__(self):
        super().__init__(
                "Centaur",
                f"Active heroe discards a spell or loses 2{constants.HEART}",
                f"ALL heroes may take a Spell from discard; remove 1{constants.CONTROL}",
                cost=7)

    def _effect(self, game):
        hero = game.heroes.active_hero
        spells = sum(1 for card in hero._hand if card.is_spell())
        if hero.is_stunned:
            game.log(f"{hero.name} is stunned and can't lose {constants.HEART}. Ignoring {self.name}!")
            return
        if spells == 0:
            game.log(f"{hero.name} has no spells to discard, losing 2{constants.HEART}")
            hero.remove_hearts(game, 2)
            return
        while True:
            choices = ['h'] + [str(i) for i in range(len(hero._hand))]
            choice = game.input(f"Choose a spell for {hero.name} to discard or (h) to lose 2{constants.HEART}: ", choices)
            if choice == 'h':
                hero.remove_hearts(game, 2)
                break
            choice = int(choice)
            card = hero._hand[choice]
            if not card.is_spell():
                game.log(f"{card.name} is not a spell!")
                continue
            hero.discard(game, choice)
            break

    def _reward(self, game):
        game.locations.remove_control(game)
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        cards = hero.choices_in_discard(game, card_filter=lambda card: card.is_spell())
        if len(cards) == 0:
            game.log(f"{hero.name} has no Spells in discard")
            return
        choices = ['c']
        choices.extend(cards.keys())
        choice = game.input(f"Choose a card for {hero.name} to take or (c)ancel: ", choices)
        if choice == 'c':
            return
        card = cards[choice]
        hero._discard.remove(card)
        hero._hand.append(card)

VILLAINS_BY_NAME["Centaur"] = Centaur
