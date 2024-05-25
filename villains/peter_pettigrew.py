from . import VILLAINS_BY_NAME, Villain
import constants


class PeterPettigrew(Villain):
    def __init__(self):
        super().__init__(
                "Peter Pettigrew",
                f"Reveal top card of deck, if costs 1{constants.INFLUENCE} or more, discard and add 1{constants.CONTROL}",
                f"ALL heroes may take Spell from discard; remove 1{constants.CONTROL}",
                hearts=7)

    def _effect(self, game):
        hero = game.heroes.active_hero
        card = hero.reveal_top_card(game)
        if card is None:
            game.log(f"{hero.name} has no cards left to reveal")
            return
        game.log(f"{hero.name} revealed {card}")
        if card.cost >= 1:
            game.heroes.active_hero.discard_top_card(game)
            game.locations.add_control(game)

    def _reward(self, game):
        game.locations.remove_control(game)
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        spells = hero.choices_in_discard(game, card_filter=lambda card: card.is_spell())
        if len(spells) == 0:
            game.log(f"{hero.name} has no spells in discard")
            return
        choices = ['c']
        choices.extend(spells.keys())
        choice = game.input(f"Choose a Spell for {hero.name} to take or (c)ancel: ", choices)
        if choice == 'c':
            return
        spell = spells[choice]
        hero._discard.remove(spell)
        hero._hand.append(spell)

VILLAINS_BY_NAME["Peter Pettigrew"] = PeterPettigrew
