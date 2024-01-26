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

    def end_turn(self, game):
        for card in self._played:
            card._end_turn(game)
        self._played = []


class DarkArtsCard(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def play(self, game):
        game.log(f"Playing {self.name} dark arts card: {self.description}")
        self._effect(game)

    def _effect(self, game):
        raise ValueError(f"Programmer Error! Forgot to implement effect for {self.name}")

    def _end_turn(self, game):
        pass


class Petrification(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Petrification",
            f"ALL heroes lose 1{constants.HEART}; no drawing cards")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        hero.remove_hearts(game, 1)
        hero.disallow_drawing(game)

    def _end_turn(self, game):
        game.heroes.allow_drawing(game)


class Expulso(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Expulso",
            f"Active hero loses 2{constants.HEART}")

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 2)


class HeWhoMustNotBeNamed(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "He Who Must Not Be Named",
            f"Add 1{constants.CONTROL} to the location")

    def _effect(self, game):
        game.locations.add_control(game)


class Flipendo(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Flipendo",
            f"Active hero loses 1{constants.HEART} and discards a card")

    def _effect(self, game):
        game.heroes.active_hero.add(game, hearts=-1, cards=-1)


game_one_cards = [
    Petrification(),
    Petrification(),
    Expulso(),
    Expulso(),
    Expulso(),
    HeWhoMustNotBeNamed(),
    HeWhoMustNotBeNamed(),
    HeWhoMustNotBeNamed(),
    Flipendo(),
    Flipendo(),
]

class HandOfGlory(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Hand of Glory",
            f"Active hero loses 1{constants.HEART}, add 1{constants.CONTROL}")

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 1)
        game.locations.add_control(game)


class Relashio(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Relashio",
            f"ALL heroes discard an item or lose 2{constants.HEART}")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
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


game_two_cards = [
    HandOfGlory(),
    HandOfGlory(),
    Relashio(),
    Poison(),
    Obliviate(),
]


class DementorsKiss(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Dementor's Kiss",
            f"Active hero loses 2{constants.HEART}, others lose 1{constants.HEART}")

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 2)
        game.heroes.all_heroes_except_active.remove_hearts(game, 1)


class Opugno(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Opugno",
            f"ALL heroes reveal top card, if it costs 1{constants.INFLUENCE} or more discard it and lose 2{constants.HEART}")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        card = hero.reveal_top_card(game)
        if card is None:
            game.log(f"{hero.name} has no cards left to reveal")
            return
        game.log(f"{hero.name} revealed {card}")
        if card.cost >= 1:
            hero.discard_top_card(game)
            hero.remove_hearts(game, 2)


class Tarantallegra(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Tarantallegra",
            f"Active hero loses 1{constants.HEART} and cannot assign more than 1{constants.DAMAGE} to each Villain")

    def _effect(self, game):
        hero = game.heroes.active_hero
        hero.remove_hearts(game, 1)
        hero.allow_only_one_damage_per_villain(game)


game_three_cards = [
    DementorsKiss(),
    DementorsKiss(),
    Opugno(),
    Tarantallegra(),
]


class Morsmordre(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Morsmordre",
            f"ALL heroes lose 1{constants.HEART}, add 1{constants.CONTROL}")

    def _effect(self, game):
        death_eaters = sum(1 for v in game.villain_deck.current if v.name == "Death Eater" and not v._stunned)
        if death_eaters > 0:
            game.log(f"Damage increased to {death_eaters+1}{constants.HEART} by Death Eater(s)")
        game.heroes.all_heroes.remove_hearts(game, 1 + death_eaters)
        game.locations.add_control(game)


class Regeneration(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Regeneration",
            f"Remove 2{constants.DAMAGE} from ALL Villains")

    def _effect(self, game):
        game.villain_deck.all_villains.remove_damage(game, 2)


class Imperio(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Imperio",
            f"Choose another hero to lose 2{constants.HEART}; reveal another card")

    def _effect(self, game):
        game.heroes.choose_hero(game, prompt=f"Choose hero to lose 2{constants.HEART}: ",
                                disallow=game.heroes.active_hero).remove_hearts(game, 2)
        game.dark_arts_deck.play(game, 1)


class AvadaKedavra(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Avada Kedavra",
            f"Active hero loses 3{constants.HEART}, if stun add +1{constants.CONTROL}; reveal another card")

    def _effect(self, game):
        hero = game.heroes.active_hero
        was_stunned = hero.is_stunned
        hero.remove_hearts(game, 3)
        if not was_stunned and hero.is_stunned:
            game.log(f"Stunned by Avada Kedavra! Adding another {constants.CONTROL}")
            game.locations.add_control(game)
        game.dark_arts_deck.play(game, 1)


class HeirOfSlytherin(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Heir of Slytherin",
            "Roll the Slytherin die")

    def _effect(self, game):
        faces = [constants.DAMAGE, constants.DAMAGE, constants.DAMAGE, constants.INFLUENCE, constants.HEART, constants.CARD]
        die_result = random.choice(faces)
        if game.heroes.active_hero.can_reroll_die(house_die=True) and game.input(f"Rolled {die_result}, (a)ccept or (r)eroll? ", "ar") == "r":
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


class Crucio(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Crucio",
            f"Active hero loses 1{constants.HEART}; reveal another card")

    def _effect(self, game):
        game.heroes.active_hero.remove_hearts(game, 1)
        game.dark_arts_deck.play(game, 1)


game_four_cards = [
    Morsmordre(),
    Morsmordre(),
    Regeneration(),
    Imperio(),
    AvadaKedavra(),
    HeirOfSlytherin(),
    HeirOfSlytherin(),
    Crucio(),
]


class EducationalDecree(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Educational Decree",
            f"Active hero loses 1{constants.HEART} for each card with cost 4{constants.INFLUENCE} or more in hand")

    def _effect(self, game):
        total = sum(1 for card in game.heroes.active_hero._hand if card.cost >= 4)
        game.heroes.active_hero.remove_hearts(game, total)


class Legilimency(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Legilimency",
            f"ALL heroes reveal top card of deck, if spell discard it and lose 2{constants.HEART}")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        card = hero.reveal_top_card(game)
        if card is None:
            game.log(f"{hero.name} has no cards left to reveal")
            return
        game.log(f"{hero.name} revealed {card}")
        if card.is_spell():
            hero.discard_top_card(game)
            hero.remove_hearts(game, 2)


game_five_cards = [
    EducationalDecree(),
    EducationalDecree(),
    Legilimency(),
    Morsmordre(),
    Imperio(),
    AvadaKedavra(),
    Crucio(),
]


class Sectumsempra(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Sectumsempra",
            f"ALL heroes lose 2{constants.HEART} and cannot gain {constants.HEART} this turn")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        hero.remove_hearts(game, 2)
        hero.disallow_healing(game)

    def _end_turn(self, game):
        game.heroes.allow_healing(game)


game_six_cards = [
    Sectumsempra(),
    Sectumsempra(),
    Morsmordre(),
]


class Fiendfyre(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Fiendfyre",
            f"ALL heroes lose 3{constants.HEART}")

    def _effect(self, game):
        game.heroes.all_heroes.remove_hearts(game, 3)


game_seven_cards = [
    Fiendfyre(),
    Imperio(),
    AvadaKedavra(),
    Crucio(),
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
            f"ALL heroes lose 1{constants.HEART} for each card in hand with cost of 3{constants.INFLUENCE}")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        total = sum(1 for card in hero._hand if card.cost == 3)
        game.log(f"Menacing Growl: {hero.name} has {total} cards with cost 3{constants.INFLUENCE}")
        hero.remove_hearts(game, total)


class IngquisitorialSquad(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Inquisitorial Squad",
            f"Active hero adds Detention to hand; ALL heroes lose 1{constants.HEART} for each Detention! in hand")

    def _effect(self, game):
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
            f"Next hero loses 2{constants.HEART}; add 1{constants.CONTROL}")

    def _effect(self, game):
        game.heroes.next_hero.remove_hearts(game, 2)
        game.locations.add_control(game)


class SlugulusEructo(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Slugulus Eructo",
            f"ALL heroes lose 1{constants.HEART} for each Creature in play")

    def _effect(self, game):
        total = sum(1 for card in game.villain_deck.current if card.is_creature)
        game.log(f"Slugulus Eructo: {total} Creatures in play")
        game.heroes.all_heroes.remove_hearts(game, total)


class BlastEnded(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Blast-ended",
            f"Previous hero loses 1{constants.HEART} and discards a card")

    def _effect(self, game):
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
            f"Active hero discards a card; add 1{constants.CONTROL}")

    def _effect(self, game):
        game.heroes.active_hero.choose_and_discard(game)
        game.locations.add_control(game)


class Transformed(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Transformed",
            "Active hero discards a card then adds Detention! to hand")

    def _effect(self, game):
        game.heroes.active_hero.choose_and_discard(game)
        game.heroes.active_hero.add_detention(game, to_hand=True)


class ViciousBite(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Vicious Bite",
            f"ALL heroes with least {constants.HEART} lose 2{constants.HEART}; if anyone is stunned, add an extra {constants.CONTROL}")

    def _effect(self, game):
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
            f"ALL heroes add a Detention! to their discard")

    def _effect(self, game):
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


class CentaurAttack(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Centaur Attack",
            f"ALL heroes with >=3 Spells lose 1{constants.HEART}")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        spells = sum(1 for card in hero._hand if card.is_spell())
        game.log(f"Centaur Attack: {hero.name} has {spells} Spells")
        if spells >= 3:
            hero.remove_hearts(game, 1)


class FightAndFlight(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Fight and Flight",
            f"Add 2{constants.CONTROL}")

    def _effect(self, game):
        game.locations.add_control(game, 2)


class AcromantulaAttack(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Acromantula Attack",
            f"ALL heroes reveal top card, if it costs 0{constants.INFLUENCE} discard it and lose 1{constants.HEART}")

    def _effect(self, game):
        game.heroes.all_heroes.effect(game, self.__per_hero)

    def __per_hero(self, game, hero):
        card = hero.reveal_top_card(game)
        if card is None:
            game.log(f"{hero.name} has no cards left to reveal")
            return
        game.log(f"{hero.name} revealed {card}")
        if card.cost == 0:
            hero.discard_top_card(game)
            hero.remove_hearts(game, 1)


class SeriouslyMisunderstoodCreatures(DarkArtsCard):
    def __init__(self):
        super().__init__(
            "Seriously Misunderstood Creatures",
            f"Roll the Creature die")

    def _effect(self, game):
        faces = [constants.HEART, constants.HEART + constants.HEART, constants.CARD, constants.CARD + constants.CARD, constants.DAMAGE, constants.CONTROL]
        die_result = random.choice(faces)
        if game.heroes.active_hero.can_reroll_die(house_die=False) and game.input(f"Rolled {die_result}, (a)ccept or (r)eroll? ", "ar") == "r":
            die_result = random.choice(faces)
        if die_result == constants.HEART or die_result == constants.HEART + constants.HEART:
            game.log(f"Rolled {constants.HEART}{constants.HEART}, ALL foes heal 1{constants.DAMAGE} and/or {constants.INFLUENCE}")
            game.villain_deck.all.remove_damage(game, 1)
            game.villain_deck.all.remove_influence(game, 1)
        elif die_result == constants.CONTROL:
            game.log(f"Rolled {constants.CONTROL}, add 1{constants.CONTROL}")
            game.locations.add_control(game)
        elif die_result == constants.DAMAGE:
            game.log(f"Rolled {constants.DAMAGE}, ALL heroes lose 1{constants.HEART}")
            game.heroes.all_heroes.remove_hearts(game, 1)
        elif die_result == constants.CARD or die_result == constants.CARD + constants.CARD:
            game.log(f"Rolled {constants.CARD}, ALL heroes discard a card")
            game.heroes.all_heroes.choose_and_discard(game)


monster_box_three_cards = [
    CentaurAttack(),
    CentaurAttack(),
    FightAndFlight(),
    AcromantulaAttack(),
    AcromantulaAttack(),
    SeriouslyMisunderstoodCreatures(),
    SeriouslyMisunderstoodCreatures(),
    Bombarda(),
]

monster_box_four_cards = [
]

MONSTER_BOX_CARDS = [
    monster_box_one_cards,
    monster_box_two_cards,
    monster_box_three_cards,
    monster_box_four_cards,
]
