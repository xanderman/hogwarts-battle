from . import VILLAINS_BY_NAME, Creature
import constants


class Mermaid(Creature):
    def __init__(self):
        super().__init__(
                "Mermaid",
                f"Heroes cannot gain {constants.DAMAGE} or {constants.INFLUENCE} from Allies",
                f"ALL heroes may take Ally from discard; remove 1{constants.CONTROL}",
                cost=5)

    def _on_reveal(self, game):
        game.heroes.all_heroes.disallow_gaining_tokens_from_allies(game)

    def _on_stun(self, game):
        game.heroes.all_heroes.allow_gaining_tokens_from_allies(game)

    def _on_recover_from_stun(self, game):
        game.heroes.all_heroes.disallow_gaining_tokens_from_allies(game)

    def _effect(self, game):
        pass

    def remove_callbacks(self, game):
        game.heroes.all_heroes.allow_gaining_tokens_from_allies(game)

    def _reward(self, game):
        game.locations.remove_control(game)
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        allies = hero.choices_in_discard(game, card_filter=lambda card: card.is_ally())
        if len(allies) == 0:
            game.log(f"{hero.name} has no allies in discard")
            return
        choices = ['c']
        choices.extend(allies.keys())
        choice = game.input(f"Choose an ally for {hero.name} to take or (c)ancel: ", choices)
        if choice == 'c':
            return
        ally = allies[choice]
        hero._discard.remove(ally)
        hero._hand.append(ally)

VILLAINS_BY_NAME["Mermaid"] = Mermaid
