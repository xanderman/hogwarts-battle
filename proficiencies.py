from collections import Counter

import random

import constants
import hogwarts

class Proficiency(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self._used_ability = False

    def __str__(self):
        return f"{self.name}: {self.description}"

    def display_state(self, window):
        window.addstr(f"{self}\n")

    def cost_modifier(self, game, card):
        return 0

    @property
    def can_reroll_house_dice(self):
        return False

    def start_game(self, hero):
        pass

    def start_turn(self, game):
        pass

    def end_turn(self, game):
        self._used_ability = False


class NullProficiency(Proficiency):
    def __init__(self):
        super().__init__("None", "No proficiency")

    def display_state(self, window):
        pass


class FlyingLessons(Proficiency):
    def __init__(self):
        super().__init__("Flying Lessons", f"1/turn: pay 5{constants.INFLUENCE} to remove 1{constants.CONTROL}")

    def start_turn(self, game):
        game.heroes.active_hero.add_action(game, 'f', "(f)lying lessons", self._use_ability)

    def _use_ability(self, game):
        if self._used_ability:
            game.log("Flying Lessons already used this turn")
            return
        if game.locations.current._control == 0:
            game.log(f"No {constants.CONTROL} to remove with Flying Lessons")
            return
        if game.heroes.active_hero._influence_tokens < 5:
            game.log(f"Not enough {constants.INFLUENCE} to use Flying Lessons")
            return
        game.log(f"Flying Lessons used to remove 1{constants.CONTROL}")
        game.heroes.active_hero.remove_influence(game, 5)
        game.locations.remove_control(game)
        self._used_ability = True


class Charms(Proficiency):
    def __init__(self):
        super().__init__("Charms", f"1/turn: discard 2 spells; ALL heroes gain 1{constants.INFLUENCE} and draw a card")

    def start_turn(self, game):
        game.heroes.active_hero.add_action(game, 'c', "(c)harms", self._use_ability)

    def _use_ability(self, game):
        if self._used_ability:
            game.log("Charms already used this turn")
            return

        hero = game.heroes.active_hero
        spells = sum(1 for card in hero._hand if card.is_spell())
        if spells < 2:
            game.log("Not enough spells in hand to use Charms")
            return

        choices = ['c'] + [str(i) for i in range(len(hero._hand))]
        while True:
            first = game.input(f"Choose first spell for {hero.name} to discard or (c)ancel: ", choices)
            if first == 'c':
                return
            first = int(first)
            card = hero._hand[first]
            if not card.is_spell():
                game.log(f"{card.name} is not a spell!")
                continue
            break
        while True:
            second = game.input(f"Choose second spell for {hero.name} to discard or (c)ancel: ", choices)
            if second == 'c':
                return
            second = int(second)
            if second == first:
                game.log("Cannot discard the same card twice")
                continue
            card = hero._hand[second]
            if not card.is_spell():
                game.log(f"{card.name} is not a spell!")
                continue
            break
        if second > first:
            # Account for hand shrinking after first discard
            second -= 1
        hero.discard(game, first)
        hero.discard(game, second)
        game.heroes.all_heroes.add(game, influence=1, cards=1)
        self._used_ability = True


class Transfiguration(Proficiency):
    def __init__(self):
        super().__init__("Transfiguration", f"1/turn: discard an item to take card with cost 5{constants.INFLUENCE} or less from deck")

    def start_turn(self, game):
        game.heroes.active_hero.add_action(game, 't', "(t)ransfiguration", self._use_ability)

    def _use_ability(self, game):
        if self._used_ability:
            game.log("Transfiguration already used this turn")
            return

        hero = game.heroes.active_hero
        items = sum(1 for card in hero._hand if card.is_item())
        if items == 0:
            game.log("No items for Transfiguration")
            return
        available_cards = [card for card in hero._deck if card.cost <= 5]
        if len(available_cards) == 0:
            game.log("No cards in deck available for Transfiguration")
            return

        while True:
            choices = ['c'] + [str(i) for i in range(len(hero._hand))]
            choice = game.input(f"Choose an item for {hero.name} to discard or (c)ancel: ", choices)
            if choice == 'c':
                return
            choice = int(choice)
            card = hero._hand[choice]
            if not card.is_item():
                game.log(f"{card.name} is not an item!")
                continue
            hero.discard(game, choice)
            break
        game.log(f"Cards in {hero.name}'s deck:")
        for i, card in enumerate(available_cards):
            game.log(f" {i}: {card}")
        choice = int(game.input(f"Choose a card to take from the deck: ", range(len(available_cards))))
        card = available_cards[choice]
        hero._deck.remove(card)
        hero._hand.append(card)
        random.shuffle(hero._deck)
        self._used_ability = True


class Herbology(Proficiency):
    def __init__(self):
        super().__init__("Herbology", f"If a Hero gains 3 or more {constants.HEART} on your turn, that Hero draws a card")
        self._healing = Counter()
        self._used_ability = set()

    def start_turn(self, game):
        self._healing = Counter()
        self._used_ability = set()
        game.heroes.add_hearts_callback(game, self)

    def end_turn(self, game):
        game.heroes.remove_hearts_callback(game, self)

    def hearts_callback(self, game, hero, amount, source):
        if amount < 1:
            return
        self._healing[hero] += amount
        if self._healing[hero] >= 3 and hero not in self._used_ability:
            game.log(f"{self.name}: {hero.name} gained {self._healing[hero]}{constants.HEART} this turn, drawing a card")
            self._used_ability.add(hero)
            hero.draw(game, 1)


class DefenseAgainstTheDarkArts(Proficiency):
    def __init__(self):
        super().__init__("Defense Against the Dark Arts", f"If forced to discard, gain 1{constants.DAMAGE} and 1{constants.HEART}")

    def start_game(self, hero):
        hero.add_discard_callback(None, self)

    def discard_callback(self, game, hero):
        game.log(f"{self.name}: {hero.name} discarded a card, gaining 1{constants.DAMAGE} and 1{constants.HEART}")
        hero.add(game, damage=1, hearts=1)


class Arithmancy(Proficiency):
    def __init__(self):
        super().__init__("Arithmancy", f"Cards that roll a house die cost 1{constants.INFLUENCE} less; you can reroll house dice once")

    def cost_modifier(self, game, card):
        if not card.rolls_house_die:
            return 0
        game.log(f"{self.name}: {card.name} costs 1{constants.INFLUENCE} less")
        return -1

    @property
    def can_reroll_house_dice(self):
        return True


class Potions(Proficiency):
    def __init__(self):
        super().__init__("Potions", f"If you play at least one ally, item, and spell, one hero gains 1{constants.DAMAGE} and 1{constants.HEART}")
        self._types_played = set()
        self._wanted_types = set([hogwarts.Ally, hogwarts.Item, hogwarts.Spell])

    def start_turn(self, game):
        self._types_played = set()
        game.heroes.active_hero.add_extra_card_effect(game, self._extra_card_effect)

    def _extra_card_effect(self, game, card):
        self._types_played.add(type(card))
        if self._types_played.issuperset(self._wanted_types) and not self._used_ability:
            self._used_ability = True
            game.heroes.choose_hero(game, prompt=f"{self.name}: played at least one ally, item, and spell. Choose hero to gain 1{constants.DAMAGE} and 1{constants.HEART}: ").add(game, damage=1, hearts=1)


class HistoryOfMagic(Proficiency):
    def __init__(self):
        super().__init__("History of Magic", f"Each time you acquire a spell, one hero gains 1{constants.INFLUENCE}")

    def start_game(self, hero):
        hero.add_acquire_callback(None, self)

    def acquire_callback(self, game, hero, card):
        if card.is_spell():
            game.heroes.choose_hero(game, prompt=f"{self.name}: {hero.name} acquired a spell. Choose hero to gain 1{constants.INFLUENCE}: ").add_influence(game, 1)


class Divination(Proficiency):
    def __init__(self):
        super().__init__("Divination", "Each time you play an item, look at top card of deck and choose to discard or keep")

    def start_turn(self, game):
        game.heroes.active_hero.add_extra_card_effect(game, self._extra_card_effect)

    def _extra_card_effect(self, game, card):
        if not card.is_item():
            return
        card = game.heroes.active_hero.reveal_top_card(game)
        if card is None:
            game.log(f"{self.name}: {hero.name} played an item, but has no cards left to reveal")
            return
        game.log(f"{self.name}: {game.heroes.active_hero.name} played an item, top of deck is {card}")
        if game.input(f"Select (k)eep or (d)iscard {card.name}: ", 'kd') == 'd':
            game.heroes.active_hero.discard_top_card(game, with_callbacks=False)


# TODO: this only applies when playing with creatures
class CareOfMagicalCreatures(Proficiency):
    def __init__(self):
        super().__init__("Care of Magical Creatures", f"The first time you assign {constants.DAMAGE}/{constants.INFLUENCE} to a Creature, one hero gains 2{constants.HEART}; if you defeat a Creature, remove 1{constants.CONTROL}")


PROFICIENCIES = {
    "None": NullProficiency,
    "Flying": FlyingLessons,
    "Charms": Charms,
    "Transfiguration": Transfiguration,
    "Herbology": Herbology,
    "Defense": DefenseAgainstTheDarkArts,
    "Arithmancy": Arithmancy,
    "Potions": Potions,
    "History": HistoryOfMagic,
    "Divination": Divination,
}
