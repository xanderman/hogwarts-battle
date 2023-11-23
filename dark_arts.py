from functools import reduce

import curses
import operator
import random

import constants

class DarkArtsDeck(object):
    def __init__(self, window, game_num):
        self._window = window
        self._init_window()
        self._pad = curses.newpad(100, 100)

        if isinstance(game_num, int):
            self._deck = reduce(operator.add, CARDS[:game_num])
        elif game_num[0] == 'm':
            self._deck = reduce(operator.add, CARDS)
            self._deck.extend(reduce(operator.add, MONSTER_BOX_CARDS[:int(game_num[1])]))
        random.shuffle(self._deck)
        self._discard = []
        self._played = []

    def _init_window(self):
        self._window.box()
        self._window.addstr(0, 1, "Dark Arts Deck")
        self._window.noutrefresh()
        beg = self._window.getbegyx()
        self._pad_start_line = beg[0] + 1
        self._pad_start_col = beg[1] + 1
        end = self._window.getmaxyx()
        self._pad_end_line = self._pad_start_line + end[0] - 3
        self._pad_end_col = self._pad_start_col + end[1] - 3

    def display_state(self, resize=False, size=None):
        if resize:
            self._window.resize(*size)
            self._window.clear()
            self._init_window()
        self._pad.clear()
        for i, card in enumerate(self._played):
            self._pad.addstr(f"{card.name}: {card.description}\n")
        self._pad.noutrefresh(0,0, self._pad_start_line,self._pad_start_col, self._pad_end_line,self._pad_end_col)

    def play_turn(self, game):
        game.log("-----Dark Arts phase-----")
        count = game.locations.current.dark_arts_count
        self._only_one_card = any(card.name == "Finite Incantatem" for card in game.heroes.active_hero._hand)
        game.log(f"Playing {count} dark arts cards")
        self.play(game, count)

    def play(self, game, count):
        if self._only_one_card:
            if len(self._played) == 0:
                game.log("Finite Incantatem: Only one dark arts card can be played!")
                count = 1
            else:
                game.log("Finite Incantatem: No more dark arts cards can be played!")
                return
        for i in range(count):
            card = self._draw()
            self._discard.append(card)
            self._played.append(card)
            card.play(game)

    def _draw(self):
        if not self._deck:
            self._deck = self._discard
            random.shuffle(self._deck)
            self._discard = []
        return self._deck.pop()

    def reveal(self):
        card = self._draw()
        self._deck.append(card)
        return card

    def discard(self):
        self._discard.append(self._draw())

    def end_turn(self):
        self._played = []


class DarkArtsCard(object):
    def __init__(self, name, description, effect):
        self.name = name
        self.description = description
        self.effect = effect

    def play(self, game):
        game.log(f"Playing {self.name} dark arts card: {self.description}")
        self.effect(game)


def petrification_effect(game, hero):
    hero.remove_hearts(game)
    hero.disallow_drawing(game)

game_one_cards = [
    DarkArtsCard("Petrification", f"ALL heroes lose 1{constants.HEART}; no drawing cards", lambda game: game.heroes.all_heroes.effect(game, petrification_effect)),
    DarkArtsCard("Petrification", f"ALL heroes lose 1{constants.HEART}; no drawing cards", lambda game: game.heroes.all_heroes.effect(game, petrification_effect)),
    DarkArtsCard("Expulso", f"Active hero loses 2{constants.HEART}", lambda game: game.heroes.active_hero.remove_hearts(game, 2)),
    DarkArtsCard("Expulso", f"Active hero loses 2{constants.HEART}", lambda game: game.heroes.active_hero.remove_hearts(game, 2)),
    DarkArtsCard("Expulso", f"Active hero loses 2{constants.HEART}", lambda game: game.heroes.active_hero.remove_hearts(game, 2)),
    DarkArtsCard("He Who Must Not Be Named", f"Add 1{constants.CONTROL} to the location", lambda game: game.locations.add_control(game)),
    DarkArtsCard("He Who Must Not Be Named", f"Add 1{constants.CONTROL} to the location", lambda game: game.locations.add_control(game)),
    DarkArtsCard("He Who Must Not Be Named", f"Add 1{constants.CONTROL} to the location", lambda game: game.locations.add_control(game)),
    DarkArtsCard("Flipendo", f"Active hero loses 1{constants.HEART} and discards a card", lambda game: game.heroes.active_hero.add(game, hearts=-1, cards=-1)),
    DarkArtsCard("Flipendo", f"Active hero loses 1{constants.HEART} and discards a card", lambda game: game.heroes.active_hero.add(game, hearts=-1, cards=-1)),
]

def hand_of_glory_effect(game):
    game.heroes.active_hero.remove_hearts(game, 1)
    game.locations.add_control(game)

def relashio_effect(game, hero):
    items = sum(1 for card in hero._hand if card.is_item())
    if hero.is_stunned:
        game.log(f"{hero.name} is stunned and can't lose {constants.HEART}. Ignoring relashio!")
        return
    if items == 0:
        game.log(f"{hero.name} has no items to discard, losing 2{constants.HEART}")
        hero.remove_hearts(game, 2)
        return
    while True:
        choices = ['h'] + [str(i) for i in range(len(hero._hand))]
        choice = game.input(f"Choose an item for {hero.name} to discard or (h) to lose 2{constants.HEART}: ", choices)
        if choice == 'h':
            hero.remove_hearts(game, 2)
            break
        choice = int(choice)
        card = hero._hand[choice]
        if not card.is_item():
            game.log(f"{card.name} is not an item!")
            continue
        hero.discard(game, choice)
        break

def poison_effect(game, hero):
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

def obliviate_effect(game, hero):
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

game_two_cards = [
    DarkArtsCard("Hand of Glory", f"Active hero loses 1{constants.HEART}, add 1{constants.CONTROL}", hand_of_glory_effect),
    DarkArtsCard("Hand of Glory", f"Active hero loses 1{constants.HEART}, add 1{constants.CONTROL}", hand_of_glory_effect),
    DarkArtsCard("Relashio", f"ALL heroes discard an item or lose 2{constants.HEART}", lambda game: game.heroes.all_heroes.effect(game, relashio_effect)),
    DarkArtsCard("Poison", f"ALL heroes discard an ally or lose 2{constants.HEART}", lambda game: game.heroes.all_heroes.effect(game, poison_effect)),
    DarkArtsCard("Obliviate", f"ALL heroes discard a spell or lose 2{constants.HEART}", lambda game: game.heroes.all_heroes.effect(game, obliviate_effect)),
]

def kiss_effect(game):
    game.heroes.active_hero.remove_hearts(game, 2)
    game.heroes.all_heroes_except_active.remove_hearts(game, 1)

def opugno_effect(game, hero):
    card = hero.reveal_top_card(game)
    if card is None:
        game.log(f"{hero.name} has no cards left to reveal")
        return
    game.log(f"{hero.name} revealed {card}")
    if card.cost >= 1:
        hero.discard_top_card(game)
        hero.remove_hearts(game, 2)

def tarantallegra_effect(game):
    hero = game.heroes.active_hero
    hero.remove_hearts(game, 1)
    hero.allow_only_one_damage(game)

game_three_cards = [
    DarkArtsCard("Dementor's Kiss", f"Active hero loses 2{constants.HEART}, others lose 1{constants.HEART}", kiss_effect),
    DarkArtsCard("Dementor's Kiss", f"Active hero loses 2{constants.HEART}, others lose 1{constants.HEART}", kiss_effect),
    DarkArtsCard("Opugno", f"ALL heroes reveal top card, if it costs 1{constants.INFLUENCE} or more discard it and lose 2{constants.HEART}", lambda game: game.heroes.all_heroes.effect(game, opugno_effect)),
    DarkArtsCard("Tarantallegra", f"Active hero loses 1{constants.HEART} and cannot assign more than 1{constants.DAMAGE} to each Villain", tarantallegra_effect),
]

def morsmordre_effect(game):
    death_eaters = sum(1 for v in game.villain_deck.current if v.name == "Death Eater" and not v._stunned)
    if death_eaters > 0:
        game.log(f"Damage increased to {death_eaters+1}{constants.HEART} by Death Eater(s)")
    game.heroes.all_heroes.remove_hearts(game, 1 + death_eaters)
    game.locations.add_control(game)

def imperio_effect(game):
    game.heroes.choose_hero(game, prompt=f"Choose hero to lose 2{constants.HEART}: ", disallow=game.heroes.active_hero,
                            disallow_msg="Active hero cannot be chosen!").remove_hearts(game, 2)
    game.dark_arts_deck.play(game, 1)

def avada_kedavra_effect(game):
    was_stunned = game.heroes.active_hero.is_stunned
    game.heroes.active_hero.remove_hearts(game, 3)
    if not was_stunned and game.heroes.active_hero.is_stunned:
        game.log(f"Stunned by Avada Kedavra! Adding another {constants.CONTROL}")
        game.locations.add_control(game)
    game.dark_arts_deck.play(game, 1)

def heir_of_slytherin_effect(game):
    faces = [constants.DAMAGE, constants.DAMAGE, constants.DAMAGE, constants.INFLUENCE, constants.HEART, constants.CARD]
    die_result = random.choice(faces)
    if game.heroes.active_hero._proficiency.can_reroll_house_dice and game.input(f"Rolled {die_result}, (a)ccept or (r)eroll? ", "ar") == "r":
        die_result = random.choice(faces)
    if die_result == constants.DAMAGE:
        game.log(f"Rolled {constants.DAMAGE}, ALL heroes lose 1{constants.HEART}")
        game.heroes.all_heroes.remove_hearts(game, 1)
    elif die_result == constants.INFLUENCE:
        game.log(f"Rolled {constants.INFLUENCE}, adding 1{constants.CONTROL} to the location")
        game.locations.add_control(game)
    elif die_result == constants.HEART:
        game.log(f"Rolled {constants.HEART}, ALL Villains remove one {constants.DAMAGE}")
        game.villain_deck.all_villains.remove_damage(game, 1)
    elif die_result == constants.CARD:
        game.log(f"Rolled {constants.CARD}, ALL heroes discard a card")
        game.heroes.all_heroes.choose_and_discard(game)

def crucio_effect(game):
    game.heroes.active_hero.remove_hearts(game)
    game.dark_arts_deck.play(game, 1)

game_four_cards = [
    DarkArtsCard("Morsmordre", f"ALL heroes lose 1{constants.HEART}, add 1{constants.CONTROL}", morsmordre_effect),
    DarkArtsCard("Morsmordre", f"ALL heroes lose 1{constants.HEART}, add 1{constants.CONTROL}", morsmordre_effect),
    DarkArtsCard("Regeneration", f"Remove 2{constants.DAMAGE} from ALL Villains", lambda game: game.villain_deck.all_villains.remove_damage(game, 2)),
    DarkArtsCard("Imperio", f"Choose another hero to lose 2{constants.HEART}; reveal another card", imperio_effect),
    DarkArtsCard("Avada Kedavra", f"Active hero loses 3{constants.HEART}, if stun add +1{constants.CONTROL}; reveal another card", avada_kedavra_effect),
    DarkArtsCard("Heir of Slytherin", "Roll the Slytherin die", heir_of_slytherin_effect),
    DarkArtsCard("Heir of Slytherin", "Roll the Slytherin die", heir_of_slytherin_effect),
    DarkArtsCard("Crucio", f"Active hero loses 1{constants.HEART}; reveal another card", crucio_effect),
]

def decree_effect(game):
    total = sum(1 for card in game.heroes.active_hero._hand if card.cost >= 4)
    game.heroes.active_hero.remove_hearts(game, total)

def legilimency_effect(game, hero):
    card = hero.reveal_top_card(game)
    if card is None:
        game.log(f"{hero.name} has no cards left to reveal")
        return
    game.log(f"{hero.name} revealed {card}")
    if card.is_spell():
        hero.discard_top_card(game)
        hero.remove_hearts(game, 2)

game_five_cards = [
    DarkArtsCard("Educational Decree", f"Active hero loses 1{constants.HEART} for each card with cost 4{constants.INFLUENCE} or more in hand", decree_effect),
    DarkArtsCard("Educational Decree", f"Active hero loses 1{constants.HEART} for each card with cost 4{constants.INFLUENCE} or more in hand", decree_effect),
    DarkArtsCard("Legilimency", f"ALL heroes reveal top card of deck, if spell discard it and lose 2{constants.HEART}", lambda game: game.heroes.all_heroes.effect(game, legilimency_effect)),
    DarkArtsCard("Morsmordre", f"ALL heroes lose 1{constants.HEART}, add 1{constants.CONTROL}", morsmordre_effect),
    DarkArtsCard("Imperio", f"Choose another hero to lose 2{constants.HEART}; reveal another card", imperio_effect),
    DarkArtsCard("Avada Kedavra", f"Active hero loses 3{constants.HEART}, if stun add +1{constants.CONTROL}; reveal another card", avada_kedavra_effect),
    DarkArtsCard("Crucio", f"Active hero loses 1{constants.HEART}; reveal another card", crucio_effect),
]

def sectumsempra_effect(game, hero):
    hero.remove_hearts(game, 2)
    hero.disallow_healing(game)

game_six_cards = [
    DarkArtsCard("Sectumsempra", f"ALL heroes lose 2{constants.HEART} and cannot gain {constants.HEART} this turn", lambda game: game.heroes.all_heroes.effect(game, sectumsempra_effect)),
    DarkArtsCard("Sectumsempra", f"ALL heroes lose 2{constants.HEART} and cannot gain {constants.HEART} this turn", lambda game: game.heroes.all_heroes.effect(game, sectumsempra_effect)),
    DarkArtsCard("Morsmordre", f"ALL heroes lose 1{constants.HEART}, add 1{constants.CONTROL}", morsmordre_effect),
]

game_seven_cards = [
    DarkArtsCard("Fiendfyre", f"ALL heroes lose 3{constants.HEART}", lambda game: game.heroes.all_heroes.remove_hearts(game, 3)),
    DarkArtsCard("Imperio", f"Choose another hero to lose 2{constants.HEART}; reveal another card", imperio_effect),
    DarkArtsCard("Avada Kedavra", f"Active hero loses 3{constants.HEART}, if stun add +1{constants.CONTROL}; reveal another card", avada_kedavra_effect),
    DarkArtsCard("Crucio", f"Active hero loses 1{constants.HEART}; reveal another card", crucio_effect),
]

CARDS = [
    game_one_cards,
    game_two_cards,
    game_three_cards,
    game_four_cards,
    game_five_cards,
    game_six_cards,
    game_seven_cards,
]


class MenacingGrowl(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Menacing Growl",
            f"ALL heroes lose 1{constants.HEART} for each card in hand with cost of 3{constants.INFLUENCE}", self.__effect)

    def __effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        total = sum(1 for card in hero._hand if card.cost == 3)
        game.log(f"Menacing Growl: {hero.name} has {total} cards with cost 3{constants.INFLUENCE}")
        hero.remove_hearts(game, total)


class IngquisitorialSquad(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Inquisitorial Squad",
            f"Active hero adds Detention to hand; ALL heroes lose 1{constants.HEART} for each Detention! in hand", self.__effect)

    def __effect(self, game):
        game.heroes.active_hero.add_detention(game, to_hand=True)
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        total = sum(1 for card in hero._hand if card.name == "Detention!")
        game.log(f"Inquisitorial Squad: {hero.name} has {total} Detention! cards")
        hero.remove_hearts(game, total)


class RagingTroll(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Raging Troll",
            f"Next hero loses 2{constants.HEART}; add 1{constants.CONTROL}", self.__effect)

    def __effect(self, game):
        game.heroes.next_hero.remove_hearts(game, 2)
        game.locations.add_control(game)


class SlugulusEructo(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Slugulus Eructo",
            f"ALL heroes lose 1{constants.HEART} for each Creature in play", self.__effect)

    def __effect(self, game):
        total = sum(1 for card in game.villain_deck.current if card.is_creature)
        game.log(f"Slugulus Eructo: {total} Creatures in play")
        game.heroes.all_heroes.remove_hearts(game, total)


class BlastEnded(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Blast-ended",
            f"Previous hero loses 1{constants.HEART} and discards a card", self.__effect)

    def __effect(self, game):
        game.heroes.previous_hero.add(game, hearts=-1, cards=-1)


monster_box_one_cards = [
    MenacingGrowl(),
    MenacingGrowl(),
    IngquisitorialSquad(),
    IngquisitorialSquad(),
    RagingTroll(),
    RagingTroll(),
    SlugulusEructo(),
    BlastEnded(),
]


class TheGrim(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "The Grim",
            f"Active hero discards a card; add 1{constants.CONTROL}", self.__effect)

    def __effect(self, game):
        game.heroes.active_hero.choose_and_discard(game)
        game.locations.add_control(game)


class Transformed(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Transformed",
            "Active hero discards a card then adds Detention! to hand", self.__effect)

    def __effect(self, game):
        game.heroes.active_hero.choose_and_discard(game)
        game.heroes.active_hero.add_detention(game, to_hand=True)


class ViciousBite(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Vicious Bite",
            f"ALL heroes with least {constants.HEART} lose 2{constants.HEART}; if anyone is stunned, add an extra {constants.CONTROL}", self.__effect)

    def __effect(self, game):
        min_hearts = min(hero._hearts for hero in game.heroes.all_heroes)
        any_stunned = False
        for hero in game.heroes.all_heroes:
            if hero._hearts == min_hearts:
                was_stunned = hero.is_stunned
                hero.remove_hearts(game, 2)
                if not was_stunned and hero.is_stunned:
                    any_stunned = True
        if any_stunned:
            game.log(f"Vicious Bite: Adding another {constants.CONTROL}")
            game.locations.add_control(game)


class Bombarda(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Bombarda!",
            f"ALL heroes add a Detention! to their discard", self.__effect)

    def __effect(self, game):
        game.heroes.all_heroes.add_detention(game)


monster_box_two_cards = [
    TheGrim(),
    Transformed(),
    Transformed(),
    ViciousBite(),
    ViciousBite(),
    Bombarda(),
    Bombarda(),
]

monster_box_three_cards = [
]

monster_box_four_cards = [
]

MONSTER_BOX_CARDS = [
    monster_box_one_cards,
    monster_box_two_cards,
    monster_box_three_cards,
    monster_box_four_cards,
]
