from collections import namedtuple

import curses
import random

import hogwarts

class QuitGame(Exception):
    pass


Action = namedtuple("Action", ["key", "description", "action"])


class Heroes(object):
    def __init__(self, window, game_num, chosen_heroes):
        self._window = window
        self._heroes = chosen_heroes
        self._hero_rows = 2 if len(self._heroes) > 2 else 1
        self._harry = next((hero for hero in self._heroes if hero.name == "Harry"), None)
        self._current = 0

        self._init_window()
        self._pads = [curses.newpad(100,100) for _ in self._heroes]

    def _init_window(self):
        self._window.box()
        self._window.addstr(0, 1, "Heroes")
        beg = self._window.getbegyx()
        self._pad_start_line = beg[0] + 1
        self._pad_start_col = beg[1] + 1
        end = self._window.getmaxyx()
        self._pad_lines = end[0] - 1
        self._pad_cols = end[1]
        self._window.vline(1, self._pad_cols//2, curses.ACS_VLINE, self._pad_lines - 1)
        if self._hero_rows == 2:
            self._window.hline(self._pad_lines//2, 1, curses.ACS_HLINE, self._pad_cols - 2)
        self._window.noutrefresh()

    def display_state(self, resize=False, size=None):
        if resize:
            self._window.resize(*size)
            self._window.clear()
            self._init_window()
        for i, hero in enumerate(self._heroes):
            attr = curses.A_BOLD | curses.color_pair(1) if i == self._current else curses.A_NORMAL
            hero.display_state(self._pads[i], i, attr)
            first_line = self._pad_start_line + (i//2)*(self._pad_lines//2)
            first_col = self._pad_start_col + (i%2)*(self._pad_cols//2)
            last_line = first_line + self._pad_lines//self._hero_rows - 2
            last_col = first_col + self._pad_cols//2 - 3
            self._pads[i].noutrefresh(0,0, first_line,first_col, last_line,last_col)

    def __len__(self):
        return len(self._heroes)

    def __getitem__(self, pos):
        return self._heroes[pos]

    def __iter__(self):
        return iter(self._heroes)

    def play_turn(self, game):
        if self._harry:
            self._harry._used_ability = False
        self.active_hero.play_turn(game)

    @property
    def active_hero(self):
        return self._heroes[self._current]

    @property
    def next_hero(self):
        return self._heroes[(self._current + 1) % len(self._heroes)]

    @property
    def previous_hero(self):
        return self._heroes[(self._current - 1) % len(self._heroes)]

    def choose_hero(self, game, prompt="Choose a hero: ", disallow=None, disallow_msg="{} cannot be chosen!"):
        if len(self._heroes) == 1:
            return self._heroes[0]

        while True:
            chosen = self._heroes[int(game.input(prompt, range(len(self._heroes))))]
            if chosen == disallow:
                game.log(disallow_msg.format(disallow.name))
                continue
            return chosen

    def choose_two_heroes(self, game, prompt="to eat pizza", disallow=None, disallow_msg="{} cannot be chosen!"):
        if len(self._heroes) <= 2:
            return self.all_heroes

        while True:
            first = self._heroes[int(game.input(f"Choose first hero {prompt}: ", range(len(self._heroes))))]
            if first == disallow:
                game.log(disallow_msg.format(disallow.name))
                continue
            break
        while True:
            second = self._heroes[int(game.input(f"Choose second hero {prompt}: ", range(len(self._heroes))))]
            if second == disallow:
                game.log(disallow_msg.format(disallow.name))
                continue
            if second == first:
                game.log("Cannot choose the same hero twice!")
                continue
            break
        return HeroList(first, second)

    @property
    def all_heroes(self):
        return HeroList(*self._heroes)

    @property
    def all_heroes_except_active(self):
        return HeroList(*[hero for hero in self._heroes if hero != self.active_hero])

    def next(self):
        self._current = (self._current + 1) % len(self._heroes)

    def disallow_drawing(self, game):
        for hero in self._heroes:
            hero.disallow_drawing(game)

    def allow_drawing(self, game):
        for hero in self._heroes:
            hero.allow_drawing(game)

    def basilisk_revealed(self, game):
        for hero in self._heroes:
            hero._basilisk_present = True

    def basilisk_defeated(self, game):
        for hero in self._heroes:
            hero._basilisk_present = False

    @property
    def drawing_allowed(self):
        return any(hero.drawing_allowed for hero in self._heroes)

    def disallow_healing(self, game):
        for hero in self._heroes:
            hero.disallow_healing(game)

    def allow_healing(self, game):
        for hero in self._heroes:
            hero.allow_healing(game)

    def greyback_revealed(self, game):
        for hero in self._heroes:
            hero._greyback_present = True

    def greyback_defeated(self, game):
        for hero in self._heroes:
            hero._greyback_present = False

    @property
    def healing_allowed(self):
        return any(hero.healing_allowed for hero in self._heroes)

    def add_acquire_callback(self, game, callback):
        for hero in self._heroes:
            hero.add_acquire_callback(game, callback)

    def remove_acquire_callback(self, game, callback):
        for hero in self._heroes:
            hero.remove_acquire_callback(game, callback)

    def add_discard_callback(self, game, callback):
        for hero in self._heroes:
            hero.add_discard_callback(game, callback)

    def remove_discard_callback(self, game, callback):
        for hero in self._heroes:
            hero.remove_discard_callback(game, callback)

    def add_health_callback(self, game, callback):
        for hero in self._heroes:
            hero.add_health_callback(game, callback)

    def remove_health_callback(self, game, callback):
        for hero in self._heroes:
            hero.remove_health_callback(game, callback)


class HeroList(list):
    def __init__(self, *args):
        super().__init__(args)

    def __getattr__(self, attr):
        def f(game, *args, **kwargs):
            for hero in self:
                getattr(hero, attr)(game, *args, **kwargs)
        return f

    def effect(self, game, effect=lambda game, hero: None):
        for hero in self:
            effect(game, hero)


class Hero(object):
    def __init__(self, name, game_num, starting_deck, proficiency):
        self.name = name
        self._game_num = game_num
        self._max_health = 10
        self._health = 10
        self._deck = []
        self._hand = []
        self._play_area = []
        self._discard = starting_deck
        self._proficiency = proficiency
        self._damage_tokens = 0
        self._influence_tokens = 0
        self._cards_acquired = 0
        self._acquire_callbacks = []
        self._discard_callbacks = []
        self._health_callbacks = []
        self._drawing_allowed = True
        self._healing_allowed = True
        self._gaining_out_of_turn_allowed = True
        self._basilisk_present = False
        self._greyback_present = False
        self._can_put_allies_in_deck = False
        self._can_put_items_in_deck = False
        self._can_put_spells_in_deck = False
        self._only_one_damage = False
        self._extra_villain_rewards = []
        self._extra_card_effects = []
        self._extra_damage_effects = []
        self._encounters = []
        self._extra_actions = {}
        self._proficiency.start_game(self)

    def display_state(self, window, i, attr):
        window.clear()
        window.addstr(f"{i}: {self.name} ({self._health}💜 {self._damage_tokens}ϟ {self._influence_tokens}💰) -- Deck: {len(self._deck)}, Discard: {len(self._discard)}\n", attr)
        if self.ability_description is not None:
            window.addstr(f"{self.ability_description}\n")
        self._proficiency.display_state(window)
        for encounter in self._encounters:
            window.addstr(f"{encounter}\n")
        window.addstr(f"  Hand ({len(self._hand)} cards):\n")
        for i, card in enumerate(self._hand):
            window.addstr(f"    {i}: ", curses.A_BOLD)
            card.display_name(window, curses.A_BOLD)
            window.addstr(f"\n        {card.description}\n")
        if len(self._play_area) != 0:
            window.addstr(f"  Play area ({len(self._play_area)} cards):\n")
            for i, card in enumerate(self._play_area):
                window.addstr(f"    {i}: ", curses.A_BOLD)
                card.display_name(window, curses.A_BOLD)
                window.addstr(f"\n        {card.description}\n")

    @property
    def ability_description(self):
        return None

    def is_stunned(self, game):
        return self._health == 0

    def recover_from_stun(self, game):
        if not self.is_stunned(game):
            return
        game.log(f"{self.name} recovers from stun!")
        self._health = self._max_health

    def add_health(self, game, amount=1, source=None):
        if amount == 0:
            return
        if self.is_stunned(game):
            game.log(f"{self.name} is stunned and cannot gain/lose health!")
            return
        if amount > 0 and self._health == self._max_health:
            game.log(f"{self.name} is already at max health!")
            return
        if amount > 0 and not self.healing_allowed:
            game.log(f"{self.name}: healing not allowed!")
            return
        if amount < -1 and any(card.name == "Invisibility cloak" for card in self._hand):
            game.log(f"Invisibility cloak prevents {-1 - amount}↯!")
            amount = -1
        if amount < 0:
            game.log(f"{self.name} loses {-amount} health!")
        else:
            game.log(f"{self.name} gains {amount} health!")
        health_start = self._health
        self._health += amount
        if self._health > self._max_health:
            self._health = self._max_health
        if self._health < 0:
            self._health = 0
        if self.is_stunned(game):
            game.log(f"{self.name} has been stunned!")
            game.locations.add_control(game)
            self._damage_tokens = 0
            self._influence_tokens = 0
            self.choose_and_discard(game, len(self._hand) // 2)
        if health_start != self._health:
            health_gained = self._health - health_start
            for callback in self._health_callbacks:
                callback.health_callback(game, self, health_gained, source)

    def remove_health(self, game, amount=1):
        self.add_health(game, -amount)

    def disallow_drawing(self, game):
        self._drawing_allowed = False

    def allow_drawing(self, game):
        self._drawing_allowed = True

    @property
    def drawing_allowed(self):
        return self._drawing_allowed and not self._basilisk_present

    def disallow_healing(self, game):
        self._healing_allowed = False

    def allow_healing(self, game):
        self._healing_allowed = True

    @property
    def healing_allowed(self):
        return self._healing_allowed and not self._greyback_present and not self.is_stunned(None) and not self._health == self._max_health

    def disallow_gaining_tokens_out_of_turn(self, game):
        self._gaining_out_of_turn_allowed = False

    def allow_gaining_tokens_out_of_turn(self, game):
        self._gaining_out_of_turn_allowed = True

    def gaining_tokens_allowed(self, game):
        if self == game.heroes.active_hero:
            return True
        return self._gaining_out_of_turn_allowed

    def draw(self, game, count=1, end_of_turn=False):
        if not end_of_turn and not self.drawing_allowed:
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

    def discard_top_card(self, game, with_callbacks=True):
        card = self._deck.pop()
        self._discard_card(game, card, with_callbacks)
        return card

    def discard(self, game, which, with_callbacks=True):
        card = self._hand.pop(which)
        self._discard_card(game, card, with_callbacks)
        return card

    def _discard_card(self, game, card, with_callbacks=True):
        self._discard.append(card)
        game.log(f"{self.name} discarded {card}")
        card.discard_effect(game, self)
        if not with_callbacks:
            return
        for callback in self._discard_callbacks:
            callback.discard_callback(game, self)

    def choose_and_discard(self, game, count=1, with_callbacks=True):
        discarded = []
        for i in range(count):
            if len(self._hand) == 0:
                game.log(f"{self.name} has no cards to discard!")
                return
            choice = int(game.input(f"Choose card for {self.name} to discard: ", range(len(self._hand))))
            discarded.append(self.discard(game, choice, with_callbacks))
        return discarded

    def add_acquire_callback(self, game, callback):
        self._acquire_callbacks.append(callback)

    def remove_acquire_callback(self, game, callback):
        self._acquire_callbacks.remove(callback)

    def add_discard_callback(self, game, callback):
        self._discard_callbacks.append(callback)

    def remove_discard_callback(self, game, callback):
        self._discard_callbacks.remove(callback)

    def add_health_callback(self, game, callback):
        self._health_callbacks.append(callback)

    def remove_health_callback(self, game, callback):
        self._health_callbacks.remove(callback)

    def can_put_allies_in_deck(self, game):
        self._can_put_allies_in_deck = True

    def can_put_items_in_deck(self, game):
        self._can_put_items_in_deck = True

    def can_put_spells_in_deck(self, game):
        self._can_put_spells_in_deck = True

    def allow_only_one_damage(self, game):
        self._only_one_damage = True

    def _acquire(self, game, card, top_of_deck=False):
        self._cards_acquired += 1
        if top_of_deck:
            self._deck.append(card)
        else:
            self._discard.append(card)
        for callback in self._acquire_callbacks:
            callback.acquire_callback(game, self, card)

    def buy_card(self, game):
        if self._influence_tokens == 0:
            game.log("No 💰 to spend!")
            return
        if len(game.hogwarts_deck._market) == 0:
            game.log("No cards to buy!")
            return
        choices = ['c'] + [str(i) for i in range(len(game.hogwarts_deck._market))]
        choice = game.input("Choose card to buy ('c' to cancel): ", choices)
        if choice == "c":
            return
        choice = game.hogwarts_deck[int(choice)]
        game.log(f"Buying {choice.name} ({choice.cost}💰; {choice.description})")
        cost = choice.cost
        cost += self._proficiency.cost_modifier(game, choice)
        if self._influence_tokens < cost:
            game.log("Not enough 💰!")
            return
        self._influence_tokens -= cost
        card = game.hogwarts_deck.remove(choice.name)
        top_of_deck = False
        if (card.is_ally() and self._can_put_allies_in_deck) or (card.is_item() and self._can_put_items_in_deck) or (card.is_spell() and self._can_put_spells_in_deck):
            if game.input(f"Put {card} on top of deck? (y/n): ", "yn") == "y":
                top_of_deck = True
        self._acquire(game, card, top_of_deck)

    def add_extra_card_effect(self, game, effect):
        self._extra_card_effects.append(effect)

    def add_extra_damage_effect(self, game, effect):
        self._extra_damage_effects.append(effect)

    def play_card(self, game, which):
        card = self._hand.pop(which)
        card.play(game)
        for effect in self._extra_card_effects:
            effect(game, card)
        self._play_area.append(card)

    def choose_and_play(self, game):
        if len(self._hand) == 0:
            game.log(f"{self.name} has no cards to play!")
            return
        choices = ['a', 'c'] + [str(i) for i in range(len(self._hand))]
        choice = game.input("Choose card to play ('a' for all, 'c' to cancel): ", choices)
        if choice == "c":
            return
        if choice == "a":
            # Get length first, so we don't play cards that get added to hand
            num_to_play = len(self._hand)
            for _ in range(num_to_play):
                self.play_card(game, 0)
        else:
            self.play_card(game, int(choice))

    def add_damage(self, game, amount=1):
        if amount > 0 and game.heroes.active_hero != self and not self.gaining_tokens_allowed(game):
            game.log(f"{self.name}: gaining ↯ on other heroes' turns not allowed!")
            return
        self._damage_tokens += amount
        if self._damage_tokens < 0:
            self._damage_tokens = 0

    def remove_damage(self, game, amount=1):
        self.add_damage(game, -amount)

    def assign_damage(self, game):
        if self._damage_tokens == 0:
            game.log("No ↯ to assign!")
            return
        if len(game.villain_deck.choices) == 0:
            game.log("No villains to assign ↯ to!")
            return None
        choices = ['c'] + game.villain_deck.choices
        choice = game.input("Choose villain to assign ↯ to ('c' to cancel): ", choices)
        if choice == 'c':
            return None
        if choice == 'v' and not game.villain_deck.voldemort_vulnerable(game):
            game.log("Voldemort is not vulnerable!")
            return None
        villain = game.villain_deck[choice]
        if self._only_one_damage and villain.took_damage:
            game.log(f"{villain.name} has already been assigned damage!")
            return None
        self.remove_damage(game)
        if villain.add_damage(game):
            for reward in self._extra_villain_rewards:
                reward(game)
            # Extra rewards only apply once
            self._extra_villain_rewards = []
        for effect in self._extra_damage_effects:
            effect(game, villain, 1)
        return villain

    def add_influence(self, game, amount=1):
        if amount > 0 and game.heroes.active_hero != self and not self.gaining_tokens_allowed(game):
            game.log(f"{self.name}: gaining 💰 on other heroes' turns not allowed!")
            return
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

    def add_encounter(self, game, encounter):
        self._encounters.append(encounter)

    def add_action(self, game, key, description, action):
        self._extra_actions[key] = (description, action)

    def play_turn(self, game):
        game.log(f"-----{self.name}'s turn-----")
        self._proficiency.start_turn(game)
        for encounter in self._encounters:
            encounter.reward_effect(game)
        if game.locations.current.action is not None:
            self.add_action(game, *game.locations.current.action)
        while True:
            game.display_state()
            actions = ["p", "a", "b", "e", "q"]
            prompt = "Select (p)lay card, (a)ssign ↯, (b)uy card"
            for key, (description, _) in self._extra_actions.items():
                actions.append(key)
                prompt += f", {description}"
            prompt += ", (e)nd turn, or (q)uit: "

            action = game.input(prompt, actions)
            if action == "p":
                self.choose_and_play(game)
                continue
            if action == "a":
                self.assign_damage(game)
                continue
            if action == "b":
                self.buy_card(game)
                continue
            if action == "e":
                return
            if action == "q":
                raise QuitGame()
            if action in self._extra_actions:
                self._extra_actions[action][1](game)
                continue
            raise ValueError("Programmer Error! Invalid choice!")

    def end_turn(self, game):
        if self._cards_acquired == 0 and len(game.hogwarts_deck._market) >= 0:
            choices = ['a', 'c'] + [str(i) for i in range(len(game.hogwarts_deck._market))]
            choice = game.input(f"{self.name} didn't acquire any cards, choose market slot to empty, (a)ll, or (c)ancel: ", choices)
            if choice == "c":
                pass
            elif choice == "a":
                game.log("Recycling entire market")
                game.hogwarts_deck.empty_market(game)
            else:
                choice = game.hogwarts_deck[int(choice)]
                game.log(f"Recycling {choice}")
                game.hogwarts_deck.empty_market_slot(game, choice.name)
        self._discard += self._hand + self._play_area
        self._hand = []
        self._play_area = []
        self._damage_tokens = 0
        self._influence_tokens = 0
        self._cards_acquired = 0
        game.heroes.allow_drawing(game)
        game.heroes.allow_healing(game)
        self._can_put_allies_in_deck = False
        self._can_put_items_in_deck = False
        self._can_put_spells_in_deck = False
        self._only_one_damage = False
        self._extra_villain_rewards = []
        self._extra_card_effects = []
        self._extra_damage_effects = []
        self._extra_actions = {}
        self.draw(game, 5, True)
        self._proficiency.end_turn(game)


def base_ally_effect(game):
    hero = game.heroes.active_hero
    if hero._health == hero._max_health:
        game.log(f"{hero.name} is already at max health, gaining 1↯")
        hero.add_damage(game, 1)
        return
    if not hero.healing_allowed:
        game.log(f"{hero.name} can't heal, gaining 1↯")
        hero.add_damage(game, 1)
        return
    choice = game.input("Choose effect: (d)↯, (h)💜: ", "dh")
    if choice == "d":
        hero.add_damage(game, 1)
    elif choice == "h":
        hero.add_health(game, 2)

def beedle_effect(game):
    if len(game.heroes) == 1:
        game.log("Only one hero, gaining 2💰")
        choice = "y"
    else:
        choice = game.input("Choose effect: (y)ou get 2💰, (a)ll get 1💰: ", "ya")

    if choice == "y":
        game.heroes.active_hero.add_influence(game, 2)
    elif choice == "a":
        game.heroes.all_heroes.add_influence(game, 1)

def time_turner_effect(game):
    game.heroes.active_hero.add_influence(game)
    game.heroes.active_hero.can_put_spells_in_deck(game)

def broom_effect(game):
    game.heroes.active_hero.add_damage(game)
    game.heroes.active_hero.add_extra_villain_reward(game, lambda game: game.heroes.active_hero.add_influence(game))

def add_damage_if_ally(game, card):
    if card.is_ally():
        game.log(f"Ally {card.name} played, beans add damage")
        game.heroes.active_hero.add_damage(game)

def beans_effect(game):
    game.heroes.active_hero.add_influence(game)
    for card in game.heroes.active_hero._play_area:
        if card.is_ally():
            game.log(f"Ally {card.name} already played, beans add damage")
            game.heroes.active_hero.add_damage(game)
    game.heroes.active_hero.add_extra_card_effect(game, add_damage_if_ally)

def mandrake_effect(game):
    if not game.heroes.healing_allowed:
        game.log(f"Healing not allowed, gaining 1↯")
        game.heroes.active_hero.add_damage(game, 1)
        return
    choices = ['d'] + [str(i) for i in range(len(game.heroes))]
    while True:
        choice = game.input("Choose hero to gain 2💜 or (d)↯: ", choices)
        if choice == "d":
            game.heroes.active_hero.add_damage(game)
            break
        hero = game.heroes[int(choice)]
        if not hero.healing_allowed:
            game.log(f"{hero.name} can't heal, choose another hero!")
            continue
        game.heroes[int(choice)].add_health(game, 2)
        break

def bat_bogey_effect(game):
    choice =  game.input("Choose effect: (d)↯, (h) ALL heroes get 1💜: ", "dh")
    if choice == "d":
        game.heroes.active_hero.add_damage(game)
    elif choice == "h":
        game.heroes.all_heroes.add_health(game, 1)

def spectrespecs_effect(game):
    game.heroes.active_hero.add_influence(game)
    if game.input("Reveal top Dark Arts event? (y/n): ", "yn") == "y":
        card = game.dark_arts_deck.reveal()
        game.log(f"Revealed {card.name}: {card.description}")
        if game.input("Discard? (y/n): ", "yn") == "y":
            game.dark_arts_deck.discard()

broom_cards = ["Quidditch Gear", "Cleansweep 11", "Firebolt", "Nimbus 2000", "Nimbus 2001"]
def lion_hat_effect(game):
    game.heroes.active_hero.add_influence(game)
    for hero in game.heroes:
        if hero == game.heroes.active_hero:
            continue
        for card in hero._hand:
            if card.name in broom_cards:
                game.log(f"{hero.name} has {card.name}, {game.heroes.active_hero.name} gains 1↯")
                game.heroes.active_hero.add_damage(game)
                return


class Hermione(Hero):
    def __init__(self, game_num, proficiency):
        super().__init__("Hermione", game_num, [
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Ally("Crookshanks", "Gain 1↯ or 2💜", 0, base_ally_effect),
            hogwarts.Item("Time-Turner", "Gain 1💰, may put acquired Spells on top of deck", 0, time_turner_effect),
            hogwarts.Item("The Tales of Beedle the Bard", "Gain 2💰, or ALL heroes gain 1💰", 0, beedle_effect),
        ], proficiency)
        self._spells_played = 0
        self._used_ability = False

    @property
    def ability_description(self):
        if self._game_num < 3:
            return None
        if self._game_num < 7:
            return "If you play 4 or more spells, one hero gains 1💰"
        return "If you play 4 or more spells, ALL heroes gain 1💰"

    def play_turn(self, game):
        self._spells_played = 0
        self._used_ability = False
        super().play_turn(game)

    def play_card(self, game, which):
        if self._hand[which].is_spell():
            self._spells_played += 1
        super().play_card(game, which)
        if self._spells_played != 4 or self._used_ability:
            return
        self._used_ability = True
        if self._game_num >= 7:
            self._game_seven_ability(game)
            return
        if self._game_num >= 3:
            self._game_three_ability(game)

    def _game_three_ability(self, game):
        game.heroes.choose_hero(game, prompt=f"{self.name} played 4 Spells, choose hero to gain 1💰: ").add_influence(game, 1)

    def _game_seven_ability(self, game):
        game.log(f"{self.name} played 4 Spells, ALL heroes gain 1💰: ")
        game.heroes.all_heroes.add_influence(game, 1)

    def _monster_box_one_ability(self, game):
        game.log(f"{self.name} played 4 spells. Two heroes gain 1↯")
        game.heroes.choose_two_heroes(game, prompt="to gain 1↯").add_damage(game, 1)


class Ron(Hero):
    def __init__(self, game_num, proficiency):
        super().__init__("Ron", game_num, [
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Ally("Pigwidgeon", "Gain 1↯ or 2💜", 0, base_ally_effect),
            hogwarts.Item("Every-flavour Beans", "Gain 1💰; for each Ally played, gain 1↯", 0, beans_effect),
            hogwarts.Item("Cleansweep 11", "Gain 1↯; if you defeat a Villain, gain 1💰", 0, broom_effect),
        ], proficiency)
        self._damage_assigned = 0
        self._used_ability = False

    @property
    def ability_description(self):
        if self._game_num < 3:
            return None
        if self._game_num < 7:
            return "If you assign 3 or more ↯, one hero gains 2💜"
        return "If you assign 3 or more ↯, ALL heroes gain 2💜"

    def assign_damage(self, game):
        villain = super().assign_damage(game)
        if villain is None:
            return
        self._damage_assigned += 1
        if self._damage_assigned != 3 or self._used_ability:
            return
        self._used_ability = True
        if self._game_num >= 7:
            self._game_seven_ability(game)
            return
        if self._game_num >= 3:
            self._game_three_ability(game)

    def play_turn(self, game):
        self._damage_assigned = 0
        self._used_ability = False
        super().play_turn(game)

    def _game_three_ability(self, game):
        game.heroes.choose_hero(game, prompt=f"{self.name} assigned 3 or more ↯, choose hero to gain 2💜: ").add_health(game, 2)

    def _game_seven_ability(self, game):
        game.log(f"{self.name} assigned 3 or more ↯, all heroes gain 2💜")
        game.heroes.all_heroes.add_health(game, 2)

    def _monster_box_one_ability(self, game):
        game.log(f"{self.name} assigned 3 or more ↯/💰, all heroes gain 1💜")
        game.heroes.all_heroes.add_health(game, 1)


class Harry(Hero):
    def __init__(self, game_num, proficiency):
        super().__init__("Harry", game_num, [
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Ally("Hedwig", "Gain 1↯ or 2💜", 0, base_ally_effect),
            hogwarts.Item("Invisibility cloak", "Gain 1💰; if in hand, take only 1↯ from each Villain or Dark Arts", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Item("Firebolt", "Gain 1↯; if you defeat a Villain, gain 1💰", 0, broom_effect),
        ], proficiency)
        self._used_ability = False

    @property
    def ability_description(self):
        if self._game_num < 3:
            return None
        if self._game_num < 7:
            return "The first time 💀 is removed on any turn, one hero gains 1↯"
        return "The first time 💀 is removed on any turn, two heroes gain 1↯"

    def control_callback(self, game, amount):
        if amount > -1:
            return
        if self._game_num >= 7:
            self._game_seven_ability_control_callback(game, amount)
            return
        if self._game_num >= 3:
            self._game_three_ability_control_callback(game, amount)
        self._used_ability = True

    def _game_three_ability_control_callback(self, game, amount):
        if self._used_ability:
            return
        game.heroes.choose_hero(game, prompt=f"{self.name}: first 💀 removed this turn, choose hero to gain 1↯: ").add_damage(game, 1)

    def _game_seven_ability_control_callback(self, game, amount):
        if self._used_ability:
            return
        game.log(f"{self.name}: first 💀 removed this turn, two heroes gain 1↯")
        game.heroes.choose_two_heroes(game, prompt="to gain 1↯").add_damage(game, 1)

    def _monster_box_one_ability_control_callback(self, game, amount):
        game.log(f"{self.name}: 💀 removed, ALL heroes gain 1💜 for each")
        for _ in range(amount):
            game.heroes.all_heroes.add_health(game, 1)


class Neville(Hero):
    def __init__(self, game_num, proficiency):
        super().__init__("Neville", game_num, [
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Ally("Trevor", "Gain 1↯ or 2💜", 0, base_ally_effect),
            hogwarts.Item("Remembrall", "Gain 1💰; if discarded, gain 2💰", 0, lambda game: game.heroes.active_hero.add_influence(game), discard_effect=lambda game, hero: hero.add_influence(game, 2)),
            hogwarts.Item("Mandrake", "Gain 1↯, or one hero gains 2💜", 0, mandrake_effect),
        ], proficiency)
        self._healed_heroes = set()

    @property
    def ability_description(self):
        if self._game_num < 3:
            return None
        if self._game_num < 7:
            return "The first time a hero gains 💜 on your turn, that hero gains +1💜"
        return "Each time a hero gains 💜 on your turn, that hero gains +1💜"

    def health_callback(self, game, hero, amount, source):
        if source == self:
            return
        if self._game_num >= 7:
            self._game_seven_ability_healing_callback(game, hero, amount)
            return
        if self._game_num >= 3:
            self._game_three_ability_healing_callback(game, hero, amount)

    def _game_three_ability_healing_callback(self, game, hero, amount):
        if hero in self._healed_heroes:
            return
        if amount < 1:
            return
        self._healed_heroes.add(hero)
        game.log(f"First time {self.name} healed {hero.name} this turn, {hero.name} gets an extra 💜")
        hero.add_health(game, 1, source=self)

    def _game_seven_ability_healing_callback(self, game, hero, amount):
        if amount < 1:
            return
        game.log(f"{self.name} healed {hero.name}, {hero.name} gets an extra 💜")
        hero.add_health(game, 1, source=self)

    def _monster_box_one_ability_healing_callback(self, game, hero, amount):
        if hero in self._healed_heroes:
            return
        if amount < 1:
            return
        self._healed_heroes.add(hero)
        game.log(f"First time {self.name} healed {hero.name} this turn, {hero.name} gets an extra 💜 or 💰")
        choice = game.input("Choose effect: (h)💜, (i)💰: ", "hi")
        if choice == "h":
            hero.add_health(game, 1)
        elif choice == "i":
            hero.add_influence(game, 1)

    def play_turn(self, game):
        self._healed_heroes = set()
        game.heroes.add_health_callback(game, self)
        super().play_turn(game)
        game.heroes.remove_health_callback(game, self)


class Ginny(Hero):
    def __init__(self, game_num, proficiency):
        super().__init__("Ginny", game_num, [
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Ally("Arnold", "Gain 1↯ or 2💜", 0, base_ally_effect),
            hogwarts.Item("Nimbus 2000", "Gain 1↯; if you defeat a Villian, gain 1💰", 0, broom_effect),
            hogwarts.Spell("Bat Bogey Hex", "Gain 1↯, or ALL heroes gain 1💜", 0, bat_bogey_effect),
        ], proficiency)
        self._villains_damaged = set()
        self._used_ability = False

    @property
    def ability_description(self):
        if self._game_num < 3:
            return None
        return "If you assign ↯ to 2 or more villains, ALL heroes gain 1💰"

    def assign_damage(self, game):
        villain = super().assign_damage(game)
        if villain is None:
            return
        self._villains_damaged.add(villain)
        if self._game_num < 3 or len(self._villains_damaged) != 2 or self._used_ability:
            return
        self._used_ability = True
        game.log(f"{self.name} assigned ↯/💰 to 2 or more villains, ALL heroes gain 1💰")
        game.heroes.all_heroes.add_influence(game, 1)

    def play_turn(self, game):
        self._villains_damaged = set()
        self._used_ability = False
        super().play_turn(game)


class Luna(Hero):
    def __init__(self, game_num, proficiency):
        super().__init__("Luna", game_num, [
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Spell("Alohomora", "Gain 1💰", 0, lambda game: game.heroes.active_hero.add_influence(game)),
            hogwarts.Ally("Crumple-horned Snorkack", "Gain 1↯ or 2💜", 0, base_ally_effect),
            hogwarts.Item("Spectrespecs", "Gain 1💰; you may reveal the top Dark Arts and choose to discard it", 0, spectrespecs_effect),
            hogwarts.Item("Lion Hat", "Gain 1💰; if another hero has broom or quidditch gear, gain 1↯", 0, lion_hat_effect),
        ], proficiency)
        self._used_ability = False

    @property
    def ability_description(self):
        if self._game_num < 3:
            return None
        return "If you draw at least one extra card, one hero gains 2💜"

    def draw(self, game, count=1, end_of_turn=False):
        cards_before = len(self._hand)
        super().draw(game, count, end_of_turn)
        if not end_of_turn and self._game_num >= 3 and len(self._hand) > cards_before and not self._used_ability:
            game.heroes.choose_hero(game, prompt=f"{self.name} drew first extra card, choose hero to gain 2💜: ").add_health(game, 2)
            self._used_ability = True

    def play_turn(self, game):
        self._used_ability = False
        super().play_turn(game)


HEROES = {
    "Hermione": Hermione,
    "Ron": Ron,
    "Harry": Harry,
    "Neville": Neville,
    "Ginny": Ginny,
    "Luna": Luna,
}
