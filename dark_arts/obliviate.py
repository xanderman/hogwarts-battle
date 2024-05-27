from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Obliviate(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Obliviate",
            f"ALL heroes discard a spell or lose 2{constants.HEART}")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        spells = sum(1 for card in hero._hand if card.is_spell())
        if hero.is_stunned:
            game.log(f"{hero.name} is stunned and can't lose {constants.HEART}. Ignoring obliviate!")
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

CARDS_BY_NAME['Obliviate'] = Obliviate
