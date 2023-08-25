import curses
import random

class HogwartsDeck(object):
    def __init__(self, window, market_size=6):
        self._window = window
        self._deck = game_one_cards
        self._max = market_size

        random.shuffle(self._deck)
        self._market = []

    def display_state(self):
        self._window.erase()
        self._window.box()
        self._window.addstr(0, 1, "Market")
        for i, card in enumerate(self._market):
            card.display_state(self._window, 2*i+1, i)
        self._window.refresh()

    def refill_market(self):
        while len(self._market) < self._max:
            card = self._deck.pop()
            self._market.append(card)


class HogwartsCard(object):
    def __init__(self, name, description, cost, effect=lambda game: None, discard_effect=lambda game, hero: None):
        self.name = name
        self.description = description
        self.cost = cost
        self.effect = effect
        self.discard_effect = discard_effect

    def display_state(self, window, row, i):
        window.addstr(row  , 1, f"{i}: {self.name} ({self.cost})", curses.A_BOLD)
        window.addstr(row+1, 1, f"     {self.description}")

    def __str__(self):
        return f"{self.name} ({self.cost}): {self.description}"

    def play(self, game):
        game.log(f"Playing {self.name}")
        self.effect(game)

    def is_ally(self):
        return False

    def is_item(self):
        return False

    def is_spell(self):
        return False


class Ally(HogwartsCard):
    def is_ally(self):
        return True


class Item(HogwartsCard):
    def is_item(self):
        return True


class Spell(HogwartsCard):
    def is_spell(self):
        return True


def hagrid_effect(game):
    game.active_hero.add_damage(game)
    game.all_heroes(lambda game, hero: hero.add_health(game))

def sorting_hat_effect(game):
    game.active_hero.add_influence(game, 2)
    game.active_hero.can_put_allies_in_deck(game)

def wingardium_effect(game):
    game.active_hero.add_influence(game)
    game.active_hero.can_put_items_in_deck(game)

def reparo_effect(game):
    while True:
        if not game.active_hero._drawing_allowed:
            game.log("Drawing not allowed, gaining 2💰")
            choice = "i"
        else:
            choice = game.input("Choose effect: (i)💰, (d)raw: ")
        if choice == "i":
            game.active_hero.add_influence(game, 2)
            break
        elif choice == "d":
            game.active_hero.draw(game)
            break
        else:
            game.log("Invalid choice!")

def oliver_effect(game):
    game.active_hero.add_damage(game)
    game.active_hero.add_extra_villain_reward(game, choose_and_heal)

def choose_and_heal(game):
    game.log("Choose hero to gain 2💜:")
    game.choose_hero().add_health(game, 2)

game_one_cards = [
    Spell("Wingardium Leviosa", "Gain 1💰, may put acquired Items on top of deck", 2, wingardium_effect),
    Spell("Wingardium Leviosa", "Gain 1💰, may put acquired Items on top of deck", 2, wingardium_effect),
    Spell("Wingardium Leviosa", "Gain 1💰, may put acquired Items on top of deck", 2, wingardium_effect),
    Spell("Reparo", "Gain 2💰 or draw a card", 3, reparo_effect),
    Spell("Reparo", "Gain 2💰 or draw a card", 3, reparo_effect),
    Spell("Reparo", "Gain 2💰 or draw a card", 3, reparo_effect),
    Spell("Reparo", "Gain 2💰 or draw a card", 3, reparo_effect),
    Spell("Reparo", "Gain 2💰 or draw a card", 3, reparo_effect),
    Spell("Reparo", "Gain 2💰 or draw a card", 3, reparo_effect),
    Spell("Lumos", "ALL heroes daw a card", 4, lambda game: game.all_heroes(lambda game, hero: hero.draw(game))),
    Spell("Lumos", "ALL heroes daw a card", 4, lambda game: game.all_heroes(lambda game, hero: hero.draw(game))),
    Spell("Incendio", "Gain 1↯ and draw a card", 4, lambda game: game.active_hero.add(game, damage=1, cards=1)),
    Spell("Incendio", "Gain 1↯ and draw a card", 4, lambda game: game.active_hero.add(game, damage=1, cards=1)),
    Spell("Incendio", "Gain 1↯ and draw a card", 4, lambda game: game.active_hero.add(game, damage=1, cards=1)),
    Spell("Incendio", "Gain 1↯ and draw a card", 4, lambda game: game.active_hero.add(game, damage=1, cards=1)),
    Spell("Descendo", "Gain 2↯", 5, lambda game: game.active_hero.add_damage(game, 2)),
    Spell("Descendo", "Gain 2↯", 5, lambda game: game.active_hero.add_damage(game, 2)),
    Item("Essence of Dittany", "Any hero gains 2💜", 2, lambda game: game.choose_hero().add_health(game, 2)),
    Item("Essence of Dittany", "Any hero gains 2💜", 2, lambda game: game.choose_hero().add_health(game, 2)),
    Item("Essence of Dittany", "Any hero gains 2💜", 2, lambda game: game.choose_hero().add_health(game, 2)),
    Item("Essence of Dittany", "Any hero gains 2💜", 2, lambda game: game.choose_hero().add_health(game, 2)),
    Item("Quidditch Gear", "Gain 1↯ and 1💜", 3, lambda game: game.active_hero.add(game, damage=1, hearts=1)),
    Item("Quidditch Gear", "Gain 1↯ and 1💜", 3, lambda game: game.active_hero.add(game, damage=1, hearts=1)),
    Item("Quidditch Gear", "Gain 1↯ and 1💜", 3, lambda game: game.active_hero.add(game, damage=1, hearts=1)),
    Item("Quidditch Gear", "Gain 1↯ and 1💜", 3, lambda game: game.active_hero.add(game, damage=1, hearts=1)),
    Item("Sorting Hat", "Gain 2💰, may put acquired Allies on top of deck", 4, sorting_hat_effect),
    Item("Golden Snitch", "Gain 2💰 and draw a card", 5, lambda game: game.active_hero.add(game, influence=2, cards=1)),
    Ally("Oliver Wood", "Gain 1↯, if you defeat a Villain anyone gains 2💜", 3, oliver_effect),
    Ally("Rebeus Hagrid", "Gain 1↯; ALL heroes gain 1💜", 4, hagrid_effect),
    Ally("Albus Dumbledore", "ALL heroes gain 1↯, 1💰, 1💜, and draw a card", 8, lambda game: game.all_heroes(lambda game, hero: hero.add(game, damage=1, influence=1, hearts=1, cards=1))),
]

game_two_cards = [
    Spell("Finite", "Remove 1💀", 3, lambda game: game.locations.current.remove_control(game)),
    Spell("Finite", "Remove 1💀", 3, lambda game: game.locations.current.remove_control(game)),
    Spell("Expelliarmus", "Gain 2↯ and draw a card", 6, lambda game: game.active_hero.add(game, damage=2, cards=1)),
    Spell("Expelliarmus", "Gain 2↯ and draw a card", 6, lambda game: game.active_hero.add(game, damage=2, cards=1)),
    Item("Polyjuice potion", "Choose a played ally and gain its effect", 3),
    Item("Polyjuice potion", "Choose a played ally and gain its effect", 3),
    Item("Nimbus 2001", "Gain 2↯; if you defeat a villain, gain 2💰", 5),
    Item("Nimbus 2001", "Gain 2↯; if you defeat a villain, gain 2💰", 5),
    Ally("Fawkes", "Gain 2↯ or ALL heroes gain 2💜", 5),
    Ally("Molly Weasley", "ALL heroes gain 1💰 and 2💜", 6),
    Ally("Dobby", "Remove 1💀 and draw a card", 4),
    Ally("Arthur Weasly", "ALL heroes gain 2💰", 6),
    Ally("Gilderoy Lockhart", "Draw a card, then discard a card; if discarded, draw a card", 2),
    Ally("Ginny Weasly", "Gain 1↯ and 1💰", 4),
]

game_three_cards = [
    Spell("Expecto Patronum", "Gain 1↯; remove 1💀", 5),
    Spell("Expecto Patronum", "Gain 1↯; remove 1💀", 5),
    Spell("Petrificus Totalus", "Gain 1↯; stun a Villain", 6),
    Spell("Petrificus Totalus", "Gain 1↯; stun a Villain", 6),
    Item("Chocolate Frog", "One hero gains 1💰 and 1💜; if discarded, gain 1💰 and 1💜", 2, lambda game: game.choose_hero().add(game, influence=1, hearts=1), discard_effect=lambda game, hero: hero.add(game, influence=1, hearts=1)),
    Item("Chocolate Frog", "One hero gains 1💰 and 1💜; if discarded, gain 1💰 and 1💜", 2, lambda game: game.choose_hero().add(game, influence=1, hearts=1), discard_effect=lambda game, hero: hero.add(game, influence=1, hearts=1)),
    Item("Chocolate Frog", "One hero gains 1💰 and 1💜; if discarded, gain 1💰 and 1💜", 2, lambda game: game.choose_hero().add(game, influence=1, hearts=1), discard_effect=lambda game, hero: hero.add(game, influence=1, hearts=1)),
    Item("Butterbeer", "Two heroes gain 1💰 and 1💜", 3),
    Item("Butterbeer", "Two heroes gain 1💰 and 1💜", 3),
    Item("Butterbeer", "Two heroes gain 1💰 and 1💜", 3),
    Item("Crystal Ball", "Draw two cards; discard one card", 3),
    Item("Crystal Ball", "Draw two cards; discard one card", 3),
    Item("Marauder's Map", "Draw two cards; if discarded, ALL heroes draw a card", 5),
    Ally("Remus Lupin", "Gain 1↯, any hero gains 3💜", 4),
    Ally("Sirius Black", "Gain 2↯ and 1💰", 6, lambda game: game.active_hero.add(game, damage=2, influence=1)),
    Ally("Sybill Trelawney", "Draw 2 cards; discard one card. If you discard a Spell, gain 2💰", 4),
]

game_four_cards = [
    Spell("Accio", "Gain 2↯ or draw Item from discard", 4),
    Spell("Accio", "Gain 2↯ or draw Item from discard", 4),
    Spell("Protego", "Gain 1↯ and 1💜; if discarded, gain 1↯ and 1💜", 5, lambda game: game.active_hero.add(game, damage=1, hearts=1), discard_effect=lambda game, hero: hero.add(game, damage=1, hearts=1)),
    Spell("Protego", "Gain 1↯ and 1💜; if discarded, gain 1↯ and 1💜", 5, lambda game: game.active_hero.add(game, damage=1, hearts=1), discard_effect=lambda game, hero: hero.add(game, damage=1, hearts=1)),
    Spell("Protego", "Gain 1↯ and 1💜; if discarded, gain 1↯ and 1💜", 5, lambda game: game.active_hero.add(game, damage=1, hearts=1), discard_effect=lambda game, hero: hero.add(game, damage=1, hearts=1)),
    Item("Hogwarts: A History", "Roll any house die", 4),
    Item("Hogwarts: A History", "Roll any house die", 4),
    Item("Hogwarts: A History", "Roll any house die", 4),
    Item("Hogwarts: A History", "Roll any house die", 4),
    Item("Hogwarts: A History", "Roll any house die", 4),
    Item("Hogwarts: A History", "Roll any house die", 4),
    Item("Pensieve", "Two heroes gain 1💰 and draw a card", 5),
    Item("Triwizard Cup", "Gain 1↯, 1💰, and 1💜", 5, lambda game: game.active_hero.add(game, damage=1, influence=1, hearts=1)),
    Ally("Severus Snape", "Gain 1↯ and 2💜; roll the Slytherin die", 6),
    Ally("Fleur Delacour", "Gane 2💰; if you play another ally, gain 2💜", 4),
    Ally("Filius Flitwick", "Gain 1💰 and draw a card; roll the Ravenclaw die", 6),
    Ally("Cedric Diggory", "Gain 1↯; roll the Hufflepuff die", 4),
    Ally("Viktor Krum", "Gain 2↯, if you defeat a Villain gain 1💰 and 1💜", 5),
    Ally("Mad-eye Moody", "Gain 2💰, remove 1💀", 6),
    Ally("Minerva McGonagall", "Gain 1💰 and 1↯; roll the Gryffindor die", 6),
    Ally("Pomona Sprout", "Gain 1💰; anyone gains 2💜; roll the Hufflepuff die", 6),
]

game_five_cards = [
    Spell("Stupefy", "Gain 1↯; remove 1💀; draw a card", 6),
    Spell("Stupefy", "Gain 1↯; remove 1💀; draw a card", 6),
    Item("O.W.L.S.", "Gain 2💰; if you play 2 Spells, gain 1↯ and 1💜", 4),
    Item("O.W.L.S.", "Gain 2💰; if you play 2 Spells, gain 1↯ and 1💜", 4),
    Ally("Nymphadora Tonks", "Gain 3💰 or 2↯, or remove 1💀", 5),
    Ally("Fred Weasley", "Gain 1↯; if another hero has a Weasley, ALL heroes gain 1💰; roll the Gryffindor die", 4),
    Ally("George Weasley", "Gain 1↯; if another hero has a Weasley, ALL heroes gain 1💜; roll the Gryffindor die", 4),
    Ally("Cho Chang", "Draw three cards, discard two; roll the Ravenclaw die", 4),
    Ally("Luna Lovegood", "Gain 1💰; if you play an item, gain 1↯; roll the Ravenclaw die", 5),
    Ally("Kingsley Shacklebolt", "Gain 2↯ and 1💜, remove 1💀", 7),
]

game_six_cards = [
    Spell("Confundus", "Gain 1↯; if you damage each Villian, remove 1💀", 3),
    Spell("Confundus", "Gain 1↯; if you damage each Villian, remove 1💀", 3),
    Item("Bezoar", "One hero gains 3💜; draw a card", 4),
    Item("Bezoar", "One hero gains 3💜; draw a card", 4),
    Item("Deluminator", "Remove 2💀", 6, lambda game: game.locations.current.remove_control(game, 2)),
    Item("Advanced Potion-Making", "ALL heroes gain 2💜; each hero at max gains 1↯ and draws a card", 6),
    Item("Felix Felicis", "Choose 2: gain 2↯, 2💰, 2💜, draw two cards", 7),
    Item("Felix Felicis", "Choose 2: gain 2↯, 2💰, 2💜, draw two cards", 7),
    Item("Elder Wand", "For each Spell played gain 1↯ and 1💜", 7),
    Ally("Horace Slughorn", "ALL heroes gain 1💰 or 1💜; roll the Slytherin die", 6),
]

game_seven_cards = [
    Item("Sword of Gryffindor", "Gain 2↯; Roll the Gryffindor die twice", 7)
]

monster_box_one_cards = [
    Spell("Tergeo", "Gain 1💰; you may banish a card in hand, if an Item, draw a card", 2),
    Spell("Tergeo", "Gain 1💰; you may banish a card in hand, if an Item, draw a card", 2),
    Spell("Tergeo", "Gain 1💰; you may banish a card in hand, if an Item, draw a card", 2),
    Spell("Tergeo", "Gain 1💰; you may banish a card in hand, if an Item, draw a card", 2),
    Spell("Tergeo", "Gain 1💰; you may banish a card in hand, if an Item, draw a card", 2),
    Spell("Tergeo", "Gain 1💰; you may banish a card in hand, if an Item, draw a card", 2),
    Spell("Finite Incantatem", "Remove 1💀; if in hand, reveal only 1 Dark Arts event", 6),
    Spell("Finite Incantatem", "Remove 1💀; if in hand, reveal only 1 Dark Arts event", 6),
    Item("Old Sock", "Gain 1💰; if another hero has an elf, gain 2↯; if discarded, gain 2💰", 1),
    Item("Old Sock", "Gain 1💰; if another hero has an elf, gain 2↯; if discarded, gain 2💰", 1),
    Item("Harp", "Gain 1↯, stun one Creature", 6),
    Ally("Fang", "One hero gain 1💰 and 2💜", 3, lambda game: game.choose_hero().add(game, influence=1, hearts=2)),
    Ally("Argus Filch & Mrs Norris", "Draw two cards, then either discard or banish a card in hand", 4),
]
