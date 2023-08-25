import curses
import random

import hogwarts

class QuitGame(Exception):
    pass


class Heroes(object):
    def __init__(self, window, num_heroes=3):
        self._window = window
        self._heroes = [Hermione(), Ginny(), Neville(), Luna()]
        self._pads = [curses.newpad(100,100) for _ in self._heroes]
        # self._heroes = [Hermione(), Harry(), Ron()]
        self._max = num_heroes
        self._current = 0

    def display_state(self):
        beg_line, beg_col = self._window.getbegyx()
        lines, cols = self._window.getmaxyx()
        self._window.erase()
        self._window.box()
        self._window.addstr(0, 1, "Heroes")
        self._window.vline(1, cols//2, curses.ACS_VLINE, lines - 2)
        lines -= 1
        self._window.hline(lines//2, 1, curses.ACS_HLINE, curses.COLS - 2)
        self._window.refresh()
        for i, hero in enumerate(self._heroes):
            attr = curses.A_BOLD | curses.color_pair(1) if i == self._current else curses.A_NORMAL
            hero.display_state(self._pads[i], i, attr)
            first_line = beg_line + 1 + (i//2)*(lines//2)
            first_col = beg_col + 1 + (i%2)*(cols//2)
            last_line = first_line + lines//2 - 2
            last_col = first_col + cols//2 - 3
            self._pads[i].refresh(0,0, first_line,first_col, last_line,last_col)

    @property
    def active_hero(self):
        return self._heroes[self._current]

    def choose_hero(self, game):
        if len(self._heroes) == 1:
            return self._heroes[0]

        while True:
            try:
                choice = int(game.input("Choose a hero: "))
                if choice < 0 or choice >= len(self._heroes):
                    raise ValueError()
                return self._heroes[choice]
            except ValueError:
                self.log("Invalid hero!")

    def all_heroes(self, game, effect):
        for hero in self._heroes:
            effect(game, hero)

    def next(self):
        self._current = (self._current + 1) % len(self._heroes)

    def add_discard_callback(self, game, callback):
        for hero in self._heroes:
            hero.add_discard_callback(game, callback)

    def remove_discard_callback(self, game, callback):
        for hero in self._heroes:
            hero.remove_discard_callback(game, callback)


class Hero(object):
    def __init__(self, name, starting_deck, starting_health=10):
        self.name = name
        self._max_health = starting_health
        self._health = starting_health
        self._deck = []
        self._hand = []
        self._play_area = []
        self._discard = starting_deck
        self._damage_tokens = 0
        self._influence_tokens = 0
        self._discard_callbacks = []
        self._drawing_allowed = True
        self._can_put_allies_in_deck = False
        self._can_put_items_in_deck = False
        self._can_put_spells_in_deck = False
        self._extra_villain_rewards = []
        self._extra_card_effects = []

    def display_state(self, window, i, attr):
        window.erase()
        window.addstr(0,0, f" {i}: {self.name} ({self._health}/{self._max_health}💜)", attr)
        window.addstr(1,0, f"     {self._damage_tokens}↯, {self._influence_tokens}💰")
        window.addstr(2,0, f"     Hand:")
        row = 3
        for i, card in enumerate(self._hand):
            window.addstr(row,0, f"       {i}: {card.name} ({card.cost})")
            window.addstr(row+1,0, f"         {card.description}")
            row += 2
        if len(self._play_area) != 0:
            window.addstr(row,0, "     Play area:")
            row += 1
            for i, card in enumerate(self._play_area):
                window.addstr(row,0, f"       {i}: {card.name} ({card.cost})")
                window.addstr(row+1,0, f"         {card.description}")
                row += 2

    def _is_stunned(self, game):
        return self._health == 0

    def recover_from_stun(self, game):
        if not self._is_stunned(game):
            return
        game.log(f"{self.name} recovers from stun!")
        self._health = self._max_health

    def add_health(self, game, amount=1):
        if amount == 0:
            return
        if self._is_stunned(game):
            game.log(f"{self.name} is stunned and cannot gain/lose health!")
            return
        if amount > 0 and self._health == self._max_health:
            game.log(f"{self.name} is already at max health!")
            return
        if amount < -1 and any(card.name == "Invisibility cloak" for card in self._hand):
            game.log("Invisibility cloak prevents {-1 - amount}↯!")
            amount = -1
        if amount < 0:
            game.log(f"{self.name} loses {-amount} health!")
        else:
            game.log(f"{self.name} gains {amount} health!")
        self._health += amount
        if self._health > self._max_health:
            self._health = self._max_health
        if self._health < 0:
            self._health = 0
        if self._is_stunned(game):
            game.log(f"{self.name} has been stunned!")
            game.locations.current.add_control(game)
            self._damage_tokens = 0
            self._influence_tokens = 0
            self.choose_and_discard(game, len(self._hand) // 2)

    def remove_health(self, game, amount=1):
        self.add_health(game, -amount)

    def disallow_drawing(self, game):
        self._drawing_allowed = False

    def allow_drawing(self, game):
        self._drawing_allowed = True

    def draw(self, game, count=1):
        if not self._drawing_allowed:
            game.log("Drawing not allowed!")
            return
        game.log(f"{self.name} draws {count} cards")
        for i in range(count):
            if len(self._deck) == 0:
                if len(self._discard) == 0:
                    # We've already shuffled the discard into the deck, so if the
                    # deck is empty now, we're out of cards
                    break
                self._deck = self._discard
                self._discard = []
                random.shuffle(self._deck)
            self._hand.append(self._deck.pop())

    def reveal_top_card(self, game):
        if len(self._deck) == 0:
            self._deck = self._discard
            self._discard = []
            random.shuffle(self._deck)
        if len(self._deck) == 0:
            return None
        return self._deck[-1]

    def discard(self, game, which):
        card = self._hand.pop(which)
        self._discard.append(card)
        game.log(f"{self.name} discarded {card}")
        card.discard_effect(game, self)
        for callback in self._discard_callbacks:
            callback.discard_callback(game, self)

    def choose_and_discard(self, game, count=1):
        for i in range(count):
            while True:
                try:
                    choice = int(game.input(f"Choose card for {self.name} to discard: "))
                    if choice < 0 or choice >= len(self._hand):
                        raise ValueError()
                    break
                except ValueError:
                    game.log("Invalid choice!")
            self.discard(game, choice)

    def add_discard_callback(self, game, callback):
        self._discard_callbacks.append(callback)

    def remove_discard_callback(self, game, callback):
        self._discard_callbacks.remove(callback)

    def can_put_allies_in_deck(self, game):
        self._can_put_allies_in_deck = True

    def can_put_items_in_deck(self, game):
        self._can_put_items_in_deck = True

    def can_put_spells_in_deck(self, game):
        self._can_put_spells_in_deck = True

    def _acquire(self, card, top_of_deck=False):
        if top_of_deck:
            self._deck.append(card)
        else:
            self._discard.append(card)

    def add_extra_card_effect(self, game, effect):
        self._extra_card_effects.append(effect)

    def play_card(self, game, which):
        card = self._hand.pop(which)
        card.play(game)
        for effect in self._extra_card_effects:
            effect(card, game)
        self._play_area.append(card)

    def add_damage(self, game, amount=1):
        self._damage_tokens += amount
        if self._damage_tokens < 0:
            self._damage_tokens = 0

    def remove_damage(self, game, amount=1):
        self.add_damage(game, -amount)

    def add_influence(self, game, amount=1):
        self._influence_tokens += amount
        if self._influence_tokens < 0:
            self._influence_tokens = 0

    def remove_influence(self, game, amount=1):
        self.add_influence(game, -amount)

    def add(self, game, damage=0, influence=0, hearts=0, cards=0):
        self.add_damage(game, damage)
        self.add_influence(game, influence)
        if cards > 0:
            self.draw(game, cards)
        elif cards < 0:
            self.choose_and_discard(game, -cards)
        # health last so that if we're stunned, it applies last
        self.add_health(game, hearts)

    def add_extra_villain_reward(self, game, reward):
        self._extra_villain_rewards.append(reward)

    def play_turn(self, game):
        game.log(f"-----{self.name}'s turn-----")
        while True:
            game.display_state()
            action = game.input("Select (p)lay card, (a)ssign ↯, (b)uy card, (e)nd turn, or (q)uit: ")
            if action == "p":
                if len(self._hand) == 0:
                    game.log("No cards to play!")
                    continue
                choice = game.input("Choose card to play ('a' for all): ")
                if choice == "a":
                    while len(self._hand) > 0:
                        self.play_card(game, 0)
                else:
                    try:
                        choice = int(choice)
                        if choice < 0 or choice >= len(self._hand):
                            raise ValueError()
                    except ValueError:
                        game.log("Invalid choice!")
                        continue
                    self.play_card(game, choice)
            elif action == "a":
                if self._damage_tokens == 0:
                    game.log("No ↯ to assign!")
                    continue
                if len(game.villain_deck.current) == 0:
                    game.log("No villains to assign ↯ to!")
                    continue
                try:
                    choice = int(game.input("Choose villain to assign ↯ to: "))
                    if choice < 0 or choice >= len(game.villain_deck.current):
                        raise ValueError()
                except ValueError:
                    game.log("Invalid choice!")
                    continue
                if game.villain_deck.current[choice].add_damage(game):
                    for reward in self._extra_villain_rewards:
                        reward(game)
                self.remove_damage(game)
            elif action == "b":
                if self._influence_tokens == 0:
                    game.log("No 💰 to spend!")
                    continue
                if len(game.hogwarts_deck._market) == 0:
                    game.log("No cards to buy!")
                    continue
                try:
                    choice = int(game.input("Choose card to buy: "))
                    if choice < 0 or choice >= len(game.hogwarts_deck._market):
                        raise ValueError()
                except ValueError:
                    game.log("Invalid choice!")
                    continue
                cost = game.hogwarts_deck._market[choice].cost
                if self._influence_tokens < cost:
                    game.log("Not enough 💰!")
                    continue
                self._influence_tokens -= cost
                card = game.hogwarts_deck._market.pop(choice)
                top_of_deck = False
                if (card.is_ally() and self._can_put_allies_in_deck) or (card.is_item() and self._can_put_items_in_deck) or (card.is_spell() and self._can_put_spells_in_deck):
                    while True:
                        choice = game.input(f"Put {card} on top of deck? (y/n): ")
                        if choice == "y":
                            top_of_deck = True
                            break
                        elif choice == "n":
                            break
                        else:
                            game.log("Invalid choice!")
                self._acquire(card, top_of_deck)
            elif action == "e":
                self.end_turn(game)
                break
            elif action == "q":
                raise QuitGame()
            elif action == "debug":
                self.display_state()
                game.log("Discard:")
                for card in self._discard:
                    game.log(f"\t{card}")
                game.log("Deck:")
                for card in self._deck:
                    game.log(f"\t{card}")
            else:
                game.log("Invalid action!")

    def end_turn(self, game):
        self._discard += self._hand + self._play_area
        self._hand = []
        self._play_area = []
        self._damage_tokens = 0
        self._influence_tokens = 0
        game.all_heroes(lambda game, hero: hero.allow_drawing(game))
        self._can_put_allies_in_deck = False
        self._can_put_items_in_deck = False
        self._can_put_spells_in_deck = False
        self._extra_villain_rewards = []
        self._extra_card_effects = []
        self.draw(game, 5)


def base_ally_effect(game):
    while True:
        choice = game.input("Choose effect: (d)↯, (h)💜: ")
        if choice == "d":
            game.active_hero.add_damage(game, 1)
            break
        elif choice == "h":
            game.active_hero.add_health(game, 2)
            break
        else:
            game.log("Invalid choice!")

def beedle_effect(game):
    while True:
        if len(game.heroes._heroes) == 1:
            game.log("Only one hero, gaining 2💰")
            choice = "y"
        else:
            choice = game.input("Choose effect: (y)ou get 2💰, (a)ll get 1💰: ")
        if choice == "y":
            game.active_hero.add_influence(game, 2)
            break
        elif choice == "a":
            game.all_heroes(lambda game, hero: hero.add_influence(game, 1))
            break
        else:
            game.log("Invalid choice!")

def time_turner_effect(game):
    game.active_hero.add_influence(game)
    game.active_hero.can_put_spells_in_deck(game)

def broom_effect(game):
    game.active_hero.add_damage(game)
    game.active_hero.add_extra_villain_reward(game, lambda game: game.active_hero.add_influence(game))

def add_damage_if_ally(card, game):
    if card.is_ally():
        game.log("Ally {card.name} played, beans add damage")
        game.active_hero.add_damage(game)

def beans_effect(game):
    game.active_hero.add_influence(game)
    for card in game.active_hero._play_area:
        if card.is_ally():
            game.active_hero.add_damage(game)
    game.active_hero.add_extra_card_effect(game, add_damage_if_ally)

def mandrake_effect(game):
    while True:
        choice = game.input("Choose effect: (d)↯, (h) one heroes get 2💜: ")
        if choice == "d":
            game.active_hero.add_damage(game)
            break
        elif choice == "h":
            game.choose_hero().add_health(game, 2)
            break
        else:
            game.log("Invalid choice!")

def bat_bogey_effect(game):
    while True:
        choice = game.input("Choose effect: (d)↯, (h) ALL heroes get 1💜: ")
        if choice == "d":
            game.active_hero.add_damage(game)
            break
        elif choice == "h":
            game.all_heroes(lambda game, hero: hero.add_health(game, 1))
            break
        else:
            game.log("Invalid choice!")

def spectrespecs_effect(game):
    game.active_hero.add_influence(game)
    while True:
        choice = game.input("Reveal top Dark Arts event? (y/n): ")
        if choice == "y":
            card = game.dark_arts_deck.reveal()
            game.log(f"Revealed {card.name}: {card.description}")
            while True:
                choice = game.input("Discard? (y/n): ")
                if choice == "y":
                    game.dark_arts_deck.discard()
                    return
                elif choice == "n":
                    return
                else:
                    game.log("Invalid choice!")
        elif choice == "n":
            break
        else:
            game.log("Invalid choice!")

broom_cards = ["Quidditch Gear", "Cleansweep 11", "Firebolt", "Nimbus 2000"]
def lion_hat_effect(game):
    game.active_hero.add_influence(game)
    all_cards = []
    for hero in game.heroes._heroes:
        if hero == game.active_hero:
            continue
        all_cards += hero._hand
    if any(card.name in broom_cards for card in all_cards):
        game.active_hero.add_damage(game)
    pass


class Hermione(Hero):
    def __init__(self):
        super().__init__("Hermione", [
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Ally("Crookshanks", "Gain 1↯ or 2💜", 0, base_ally_effect),
            hogwarts.Item("Time-Turner", "Gain 1💰, may put acquired Spells on top of deck", 0, time_turner_effect),
            hogwarts.Item("The Tales of Beedle the Bard", "Gain 2💰, or ALL heroes gain 1💰", 0, beedle_effect),
        ])


class Ron(Hero):
    def __init__(self):
        super().__init__("Ron", [
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Ally("Pigwidgeon", "Gain 1↯ or 2💜", 0, base_ally_effect),
            hogwarts.Item("Every-flavour Beans", "Gain 1💰; for each Ally played, gain 1↯", 0, beans_effect),
            hogwarts.Item("Cleansweep 11", "Gain 1↯; if you defeat a Villain, gain 1💰", 0, broom_effect),
        ])


class Harry(Hero):
    def __init__(self):
        super().__init__("Harry", [
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Ally("Hedwig", "Gain 1↯ or 2💜", 0, base_ally_effect),
            hogwarts.Item("Invisibility cloak", "Gain 1💰; if in hand, take only 1↯ from each Villain or Dark Arts", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Item("Firebolt", "Gain 1↯; if you defeat a Villain, gain 1💰", 0, broom_effect),
        ])


class Neville(Hero):
    def __init__(self):
        super().__init__("Neville", [
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Ally("Trevor", "Gain 1↯ or 2💜", 0, base_ally_effect),
            hogwarts.Item("Remembrall", "Gain 1💰; if discarded, gain 2💰", 0, lambda game: game.active_hero.add_influence(game), discard_effect=lambda game, hero: hero.add_influence(game, 2)),
            hogwarts.Item("Mandrake", "Gain 1↯, or one hero gains 2💜", 0, mandrake_effect),
        ])


class Ginny(Hero):
    def __init__(self):
        super().__init__("Ginny", [
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Ally("Arnold", "Gain 1↯ or 2💜", 0, base_ally_effect),
            hogwarts.Item("Nimbus 2000", "Gain 1↯; if you defeat a Villian, gain 1💰", 0, broom_effect),
            hogwarts.Spell("Bat Bogey Hex", "Gain 1↯, or ALL heroes gain 1💜", 0, bat_bogey_effect),
        ])


class Luna(Hero):
    def __init__(self):
        super().__init__("Luna", [
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.active_hero.add_influence(game)),
            hogwarts.Ally("Crumple-horned Snorkack", "Gain 1↯ or 2💜", 0, base_ally_effect),
            hogwarts.Item("Spectrespecs", "Gain 1💰; you may reveal the top Dark Arts and choose to discard it", 0, spectrespecs_effect),
            hogwarts.Item("Lion Hat", "Gain 1💰; if another hero has broom or quidditch gear, gain 1↯", 0, lion_hat_effect),
        ])
