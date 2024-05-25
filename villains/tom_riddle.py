from . import VILLAINS_BY_NAME, Villain
import constants


class TomRiddle(Villain):
    def __init__(self):
        super().__init__(
                "Tom Riddle",
                f"For each Ally in hand, lose 2{constants.HEART} or discard a card",
                f"ALL heroes gain 2{constants.HEART} or take Ally from discard",
                hearts=6)

    def _effect(self, game):
        hero = game.heroes.active_hero
        allies = sum(1 for card in hero._hand if card.is_ally())
        if allies == 0:
            game.log(f"{hero.name} has no allies in hand, safe!")
            return
        if hero.is_stunned:
            game.log(f"{hero.name} is stunned and can't lose {constants.HEART}. No penalty for allies in hand!")
            return
        game.log(f"{hero.name} has {allies} allies in hand")
        for _ in range(allies):
            choices = ['h'] + [str(i) for i in range(len(hero._hand))]
            choice = game.input(f"Choose a card for {hero.name} to discard or (h) to lose 2{constants.HEART}: ", choices)
            if choice == 'h':
                hero.remove_hearts(game, 2)
            else:
                hero.discard(game, int(choice))

    def _reward(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        allies = hero.choices_in_discard(game, card_filter=lambda card: card.is_ally())
        if len(allies) == 0:
            game.log(f"{hero.name} has no allies in discard, gaining 2{constants.HEART}")
            hero.add_hearts(game, 2)
            return
        choices = ['h']
        choices.extend(allies.keys())
        choice = game.input(f"Choose an ally for {hero.name} to take or (h) to gain 2{constants.HEART}: ", choices)
        if choice == 'h':
            hero.add_hearts(game, 2)
            return
        ally = allies[choice]
        hero._discard.remove(ally)
        hero._hand.append(ally)

VILLAINS_BY_NAME["Tom Riddle"] = TomRiddle
