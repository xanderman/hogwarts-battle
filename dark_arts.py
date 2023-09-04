from functools import reduce

import curses
import operator
import random

class DarkArtsDeck(object):
    def __init__(self, window, game_num):
        self._window = window
        self._window.box()
        self._window.addstr(0, 1, "Dark Arts Deck")
        self._window.noutrefresh()
        beg = self._window.getbegyx()
        self._pad_start_line = beg[0] + 1
        self._pad_start_col = beg[1] + 1
        end = self._window.getmaxyx()
        self._pad_end_line = self._pad_start_line + end[0] - 3
        self._pad_end_col = self._pad_start_col + end[1] - 3
        self._pad = curses.newpad(100, 100)

        self._deck = reduce(operator.add, CARDS[:game_num])
        random.shuffle(self._deck)
        self._discard = []
        self._played = []

    def display_state(self):
        self._pad.clear()
        for i, card in enumerate(self._played):
            self._pad.addstr(f"{card.name}: {card.description}\n")
        self._pad.noutrefresh(0,0, self._pad_start_line,self._pad_start_col, self._pad_end_line,self._pad_end_col)

    def play_turn(self, game):
        game.log("-----Dark Arts phase-----")
        count = game.locations.current.dark_arts_count
        game.log(f"Playing {count} dark arts cards")
        self.play(game, count)

    def play(self, game, count):
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
    hero.remove_health(game)
    hero.disallow_drawing(game)

game_one_cards = [
    DarkArtsCard("Petrification", "ALL heroes lose 1💜; no drawing cards", lambda game: game.heroes.all_heroes.effect(game, petrification_effect)),
    DarkArtsCard("Petrification", "ALL heroes lose 1💜; no drawing cards", lambda game: game.heroes.all_heroes.effect(game, petrification_effect)),
    DarkArtsCard("Expulso", "Active hero loses 2💜", lambda game: game.heroes.active_hero.remove_health(game, 2)),
    DarkArtsCard("Expulso", "Active hero loses 2💜", lambda game: game.heroes.active_hero.remove_health(game, 2)),
    DarkArtsCard("Expulso", "Active hero loses 2💜", lambda game: game.heroes.active_hero.remove_health(game, 2)),
    DarkArtsCard("He Who Must Not Be Named", "Add 1💀 to the location", lambda game: game.locations.add_control(game)),
    DarkArtsCard("He Who Must Not Be Named", "Add 1💀 to the location", lambda game: game.locations.add_control(game)),
    DarkArtsCard("He Who Must Not Be Named", "Add 1💀 to the location", lambda game: game.locations.add_control(game)),
    DarkArtsCard("Flipendo", "Active hero loses 1💜 and discards a card", lambda game: game.heroes.active_hero.add(game, hearts=-1, cards=-1)),
    DarkArtsCard("Flipendo", "Active hero loses 1💜 and discards a card", lambda game: game.heroes.active_hero.add(game, hearts=-1, cards=-1)),
]

def hand_of_glory_effect(game):
    game.heroes.active_hero.remove_health(game, 1)
    game.locations.add_control(game)

def relashio_effect(game, hero):
    items = sum(1 for card in hero._hand if card.is_item())
    if items == 0:
        game.log(f"{hero.name} has no items to discard, losing 2💜")
        hero.remove_health(game, 2)
        return
    while True:
        choices = ['h'] + [str(i) for i in range(len(hero._hand))]
        choice = game.input(f"Choose an item for {hero.name} to discard or (h) to lose 2💜: ", choices)
        if choice == 'h':
            hero.remove_health(game, 2)
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
    if allies == 0:
        game.log(f"{hero.name} has no allies to discard, losing 2💜")
        hero.remove_health(game, 2)
        return
    while True:
        choices = ['h'] + [str(i) for i in range(len(hero._hand))]
        choice = game.input(f"Choose an ally for {hero.name} to discard or (h) to lose 2💜: ", choices)
        if choice == 'h':
            hero.remove_health(game, 2)
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
    if spells == 0:
        game.log(f"{hero.name} has no spells to discard, losing 2💜")
        hero.remove_health(game, 2)
        return
    while True:
        choices = ['h'] + [str(i) for i in range(len(hero._hand))]
        choice = game.input(f"Choose a spell for {hero.name} to discard or (h) to lose 2💜: ", choices)
        if choice == 'h':
            hero.remove_health(game, 2)
            break
        choice = int(choice)
        card = hero._hand[choice]
        if not card.is_spell():
            game.log(f"{card.name} is not a spell!")
            continue
        hero.discard(game, choice)
        break

game_two_cards = [
    DarkArtsCard("Hand of Glory", "Active hero loses 1💜, add 1💀", hand_of_glory_effect),
    DarkArtsCard("Hand of Glory", "Active hero loses 1💜, add 1💀", hand_of_glory_effect),
    DarkArtsCard("Relashio", "ALL heroes discard an item or lose 2💜", lambda game: game.heroes.all_heroes.effect(game, relashio_effect)),
    DarkArtsCard("Poison", "ALL heroes discard an ally or lose 2💜", lambda game: game.heroes.all_heroes.effect(game, poison_effect)),
    DarkArtsCard("Obliviate", "ALL heroes discard a spell or lose 2💜", lambda game: game.heroes.all_heroes.effect(game, obliviate_effect)),
]

def kiss_effect(game):
    game.heroes.active_hero.remove_health(game, 2)
    game.heroes.all_heroes_except_active.remove_health(game, 1)

def opugno_effect(game, hero):
    card = hero.reveal_top_card(game)
    if card is None:
        game.log(f"{hero.name} has no cards left to reveal")
        return
    game.log(f"{hero.name} revealed {card}")
    if card.cost >= 1:
        hero.discard_top_card(game)
        hero.remove_health(game, 2)

def tarantallegra_effect(game):
    hero = game.heroes.active_hero
    hero.remove_health(game, 1)
    hero.allow_only_one_damage(game)

game_three_cards = [
    DarkArtsCard("Dementor's Kiss", "Active hero loses 2💜, others lose 1💜", kiss_effect),
    DarkArtsCard("Dementor's Kiss", "Active hero loses 2💜, others lose 1💜", kiss_effect),
    DarkArtsCard("Opugno", "ALL heroes reveal top card, if it costs 1💰 or more discard it and lose 2💜", lambda game: game.heroes.all_heroes.effect(game, opugno_effect)),
    DarkArtsCard("Tarantallegra", "Active hero loses 1💜 and cannot assign more than 1↯ to each Villain", tarantallegra_effect),
]

def morsmordre_effect(game):
    death_eaters = sum(1 for v in game.villain_deck.current if v.name == "Death Eater")
    if death_eaters > 0:
        game.log(f"Damage increased to {death_eaters+1}💜 by Death Eater(s)")
    game.heroes.all_heroes.remove_health(game, 1 + death_eaters)
    game.locations.add_control(game)

def imperio_effect(game):
    game.heroes.choose_hero(game, prompt="Choose hero to lose 2💜: ", disallow=game.heroes.active_hero,
                            disallow_msg="Active hero cannot be chosen!").remove_health(game, 2)
    game.dark_arts_deck.play(game, 1)

def avada_kedavra_effect(game):
    was_stunned = game.heroes.active_hero.is_stunned(game)
    game.heroes.active_hero.remove_health(game, 3)
    if not was_stunned and game.heroes.active_hero.is_stunned(game):
        game.log("Stunned by Avada Kedavra! Adding another 💀")
        game.locations.add_control(game)
    game.dark_arts_deck.play(game, 1)

def heir_of_slytherin_effect(game):
    die_result = random.choice("↯↯↯💰💜🃏")
    if die_result == "↯":
        game.log("Rolled ↯, ALL heroes lose 1💜")
        game.heroes.all_heroes.remove_health(game, 1)
    elif die_result == "💰":
        game.log("Rolled 💰, adding 1💀 to the location")
        game.locations.add_control(game)
    elif die_result == "💜":
        game.log("Rolled 💜, ALL Villains remove one ↯")
        game.villain_deck.all_villains(game, lambda game, villain: villain.remove_damage(game, 1))
    elif die_result == "🃏":
        game.log("Rolled 🃏, ALL heroes discard a card")
        game.heroes.all_heroes.choose_and_discard(game)

def crucio_effect(game):
    game.heroes.active_hero.remove_health(game)
    game.dark_arts_deck.play(game, 1)

game_four_cards = [
    DarkArtsCard("Morsmordre", "ALL heroes lose 1💜, add 1💀", morsmordre_effect),
    DarkArtsCard("Morsmordre", "ALL heroes lose 1💜, add 1💀", morsmordre_effect),
    DarkArtsCard("Regeneration", "Remove 2↯ from ALL Villains", lambda game: game.villain_deck.all_villains(game, lambda game, villain: villain.remove_damage(game, 2))),
    DarkArtsCard("Imperio", "Choose another hero to lose 2💜; reveal another card", imperio_effect),
    DarkArtsCard("Avada Kedavra", "Active hero loses 3💜, if stun add +1💀; reveal another card", avada_kedavra_effect),
    DarkArtsCard("Heir of Slytherin", "Roll the Slytherin die", heir_of_slytherin_effect),
    DarkArtsCard("Heir of Slytherin", "Roll the Slytherin die", heir_of_slytherin_effect),
    DarkArtsCard("Crucio", "Active hero loses 1💜; reveal another card", crucio_effect),
]

def decree_effect(game):
    total = sum(1 for card in game.heroes.active_hero._hand if card.cost >= 4)
    # game.log(f"{game.heroes.active_hero.name} has {total} cards with value 4💰 or more, loses {total}💜")
    game.heroes.active_hero.remove_health(game, total)

def legilimency_effect(game, hero):
    card = hero.reveal_top_card(game)
    if card is None:
        game.log(f"{hero.name} has no cards left to reveal")
        return
    game.log(f"{hero.name} revealed {card}")
    if card.is_spell():
        hero.discard_top_card(game)
        hero.remove_health(game, 2)

game_five_cards = [
    DarkArtsCard("Educational Decree", "Active hero loses 1💜 for each card with cost 4💰 or more in hand", decree_effect),
    DarkArtsCard("Educational Decree", "Active hero loses 1💜 for each card with cost 4💰 or more in hand", decree_effect),
    DarkArtsCard("Legilimency", "ALL heroes reveal top card of deck, if spell discard it and lose 2💜", lambda game: game.heroes.all_heroes.effect(game, legilimency_effect)),
    DarkArtsCard("Morsmordre", "ALL heroes lose 1💜, add 1💀", morsmordre_effect),
    DarkArtsCard("Imperio", "Choose another hero to lose 2💜; reveal another card", imperio_effect),
    DarkArtsCard("Avada Kedavra", "Active hero loses 3💜, if stun add +1💀; reveal another card", avada_kedavra_effect),
    DarkArtsCard("Crucio", "Active hero loses 1💜; reveal another card", crucio_effect),
]

def sectumsempra_effect(game, hero):
    hero.remove_health(game, 2)
    hero.disallow_healing(game)

game_six_cards = [
    DarkArtsCard("Sectumsempra", "ALL heroes lose 2💜 and cannot gain 💜 this turn", lambda game: game.heroes.all_heroes.effect(game, sectumsempra_effect)),
    DarkArtsCard("Sectumsempra", "ALL heroes lose 2💜 and cannot gain 💜 this turn", lambda game: game.heroes.all_heroes.effect(game, sectumsempra_effect)),
    DarkArtsCard("Morsmordre", "ALL heroes lose 1💜, add 1💀", morsmordre_effect),
]

game_seven_cards = [
    DarkArtsCard("Fiendfyre", "ALL heroes lose 3💜", lambda game: game.heroes.all_heroes.remove_health(game, 3)),
    DarkArtsCard("Imperio", "Choose another hero to lose 2💜; reveal another card", imperio_effect),
    DarkArtsCard("Avada Kedavra", "Active hero loses 3💜, if stun add +1💀; reveal another card", avada_kedavra_effect),
    DarkArtsCard("Crucio", "Active hero loses 1💜; reveal another card", crucio_effect),
]

def menacing_growl_effect(game):
    pass

def inquisitorial_squad_effect(game):
    pass

def raging_troll_effect(game):
    pass

def slugulus_eructo_effect(game):
    pass

monster_box_one_cards = [
    DarkArtsCard("Menacing Growl", "ALL heroes lose 1💜 for each card in hand with cost of 3💰", menacing_growl_effect),
    DarkArtsCard("Menacing Growl", "ALL heroes lose 1💜 for each card in hand with cost of 3💰", menacing_growl_effect),
    DarkArtsCard("Inquisitorial Squad", "Active hero adds Detention to hand; ALL heroes lose 1💜 for each Detention in hand", inquisitorial_squad_effect),
    DarkArtsCard("Inquisitorial Squad", "Active hero adds Detention to hand; ALL heroes lose 1💜 for each Detention in hand", inquisitorial_squad_effect),
    DarkArtsCard("Raging Troll", "next hero loses 2💜; add 1💀", raging_troll_effect),
    DarkArtsCard("Raging Troll", "next hero loses 2💜; add 1💀", raging_troll_effect),
    DarkArtsCard("Slugulus Eructo", "ALL heroes lose 1💜 for each Creature", slugulus_eructo_effect),
    DarkArtsCard("Blast-ended", "Previous hero loses 1💜 and discards a card", lambda game: game.heroes.previous_hero.add(game, hearts=-1, cards=-1)),
]

CARDS = [
    game_one_cards,
    game_two_cards,
    game_three_cards,
    game_four_cards,
    game_five_cards,
    game_six_cards,
    game_seven_cards,
    monster_box_one_cards,
]
