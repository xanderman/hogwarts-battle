from . import CARDS_BY_NAME, DarkArtsCard
import constants


class Poison(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Poison",
            f"ALL heroes discard an ally or lose 2{constants.HEART}")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        allies = sum(1 for card in hero._hand if card.is_ally())
        if hero.is_stunned:
            game.log(f"{hero.name} is stunned and can't lose {constants.HEART}. Ignoring poison!")
            return
        if allies == 0:
            game.log(f"{hero.name} has no allies to discard, losing 2{constants.HEART}")
            hero.remove_hearts(game, 2)
            return
        while True:
            choices = ['h'] + [str(i) for i in range(len(hero._hand))]
            choice = game.input(f"Choose an ally for {hero.name} to discard or (h) to lose 2{constants.HEART}: ", choices)
            if choice == 'h':
                hero.remove_hearts(game, 2)
                break
            choice = int(choice)
            card = hero._hand[choice]
            if not card.is_ally():
                game.log(f"{card.name} is not an ally!")
                continue
            hero.discard(game, choice)
            break

CARDS_BY_NAME['Poison'] = Poison
