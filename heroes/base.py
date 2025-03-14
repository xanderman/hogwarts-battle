from collections import namedtuple
from enum import Enum, auto

import curses
import inspect
import random

import constants
import hogwarts


class QuitGame(Exception):
    pass


class DisplayMode(Enum):
    DEFAULT = auto()
    HAND = auto()
    PLAY_AREA = auto()
    DISCARD = auto()

DISPLAY_MODES = [DisplayMode.DEFAULT, DisplayMode.HAND, DisplayMode.PLAY_AREA, DisplayMode.DISCARD]


# Letters excluding ones used for alternates, like (c)ancel, (i)nfluence, etc
# If you have more than 50 cards to choose from, may God have mercy on your soul
ALPHA_OPTIONS = ['a', 'b', 'd', 'e', 'f', 'g', 'j', 'k', 'l', 'm',
                 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
                 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G',
                 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
                 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


class Heroes(object):
    def __init__(self, window, chosen_heroes):
        self._window = window
        self._heroes = chosen_heroes
        self._hero_rows = 2 if len(self._heroes) > 2 else 1
        self._harry = next((hero for hero in self._heroes if hero.name == "Harry"), None)
        self._current = 0

        self._display_mode = 0
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

    def next_display_mode(self):
        self._display_mode = (self._display_mode + 1) % len(DISPLAY_MODES)

    def display_state(self, game, resize=False, size=None):
        if resize:
            self._window.resize(*size)
            self._window.clear()
            self._init_window()
        for i, hero in enumerate(self._heroes):
            attr = curses.A_BOLD | curses.color_pair(1) if i == self._current else curses.A_NORMAL
            hero.display_state(game, DISPLAY_MODES[self._display_mode], self._pads[i], i, attr)
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

    def choose_hero(self, game, prompt="Choose a hero: ", optional=False, disallow=None):
        if len(self._heroes) == 1:
            return self._heroes[0]

        choices = ['c'] if optional else []
        choices += [str(i) for i in range(len(self._heroes)) if self._heroes[i] != disallow]
        choice = game.input(prompt, choices)
        if choice == "c":
            return None
        return self._heroes[int(choice)]

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

    @property
    def drawing_allowed(self):
        return any(hero.drawing_allowed for hero in self._heroes)

    def disallow_healing(self, game):
        for hero in self._heroes:
            hero.disallow_healing(game)

    def allow_healing(self, game):
        for hero in self._heroes:
            hero.allow_healing(game)

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

    def add_hearts_callback(self, game, callback):
        for hero in self._heroes:
            hero.add_hearts_callback(game, callback)

    def remove_hearts_callback(self, game, callback):
        for hero in self._heroes:
            hero.remove_hearts_callback(game, callback)


class HeroList(list):
    def __init__(self, *args):
        super().__init__(args)

    def __getattr__(self, attr):
        def f(game, *args, **kwargs):
            for hero in self:
                getattr(hero, attr)(game, *args, **kwargs)
        return f

    def effect(self, game, effect=None):
        if effect is None:
            raise ValueError("Effect cannot be None!")
        for hero in self:
            effect(game, hero)


class Hero(object):
    def __init__(self, name, ability, starting_deck, proficiency):
        self.name = name
        self._ability = ability
        self._max_hearts = 10
        self._hearts = 10
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
        self._hearts_callbacks = []
        # Ref counters of reasons why drawing/healing is disallowed
        self._drawing_disallowed = 0
        self._healing_disallowed = 0
        self._gaining_out_of_turn_allowed = True
        self._gaining_from_allies_allowed = True
        self._can_put_allies_in_deck = False
        self._can_put_items_in_deck = False
        self._can_put_spells_in_deck = False
        self._only_draw_four_cards = False
        self._extra_villain_rewards = []
        self._extra_creature_rewards = []
        self._extra_card_effects = []
        self._extra_shuffle_effects = []
        self._extra_damage_effects = []
        self._extra_influence_effects = []
        self._encounters = []
        self._extra_actions = {}
        self._proficiency.start_game(self)

    def display_state(self, game, mode, window, i, attr):
        window.clear()
        window.addstr(f"{i}: {self.name}", attr)
        window.addstr(f" ({self._hearts}{constants.HEART} {self._damage_tokens}{constants.DAMAGE}", attr)
        window.addstr(f" {self._influence_tokens}{constants.INFLUENCE})", attr)
        window.addstr(f" -- Deck: {len(self._deck)}, Discard: {len(self._discard)}", attr)
        if not self.healing_allowed or not self.drawing_allowed or not self.gaining_tokens_allowed(game):
            window.addstr(f", {constants.DISALLOW}", attr)
            if not self.healing_allowed:
                window.addstr(constants.HEART, attr)
            if not self.drawing_allowed:
                window.addstr(constants.CARD, attr)
            if not self.gaining_tokens_allowed(game):
                window.addstr(constants.DAMAGE + constants.INFLUENCE, attr)
        window.addstr("\n")
        if mode == DisplayMode.DEFAULT:
            if self.ability_description is not None:
                window.addstr(f"{self.ability_description}\n")
            self._proficiency.display_state(window)
            for encounter in self._encounters:
                window.addstr(f"{encounter}\n")
        if mode == DisplayMode.DEFAULT or mode == DisplayMode.HAND:
            window.addstr(f"  Hand ({len(self._hand)} cards):\n")
            for i, card in enumerate(self._hand):
                window.addstr(f"    {i}: ", curses.A_BOLD)
                card.display_name(window, curses.A_BOLD)
                window.addstr(f"\n        {card.description}\n")
        if mode == DisplayMode.DEFAULT or mode == DisplayMode.PLAY_AREA:
            window.addstr(f"  Play area ({len(self._play_area)} cards):\n")
            for i, card in enumerate(self._play_area):
                window.addstr(f"    {i}: ", curses.A_BOLD)
                card.display_name(window, curses.A_BOLD)
                window.addstr(f"\n        {card.description}\n")
        if mode == DisplayMode.DISCARD:
            window.addstr(f"  Discard ({len(self._discard)} cards):\n")
            for i, card in enumerate(self._discard):
                window.addstr(f"    {i}: ", curses.A_BOLD)
                card.display_name(window, curses.A_BOLD)
                window.addstr(f"\n        {card.description}\n")

    @property
    def ability_description(self):
        return None

    @property
    def is_stunned(self):
        return self._hearts == 0

    def recover_from_stun(self, game):
        if not self.is_stunned:
            return
        game.log(f"{self.name} recovers from stun!")
        self._hearts = self._max_hearts

    def add_hearts(self, game, amount=1, source=None):
        if amount == 0:
            return
        if self.is_stunned:
            game.log(f"{self.name} is stunned and cannot gain/lose hearts!")
            return
        if amount > 0 and self._hearts == self._max_hearts:
            game.log(f"{self.name} is already at max hearts!")
            return
        if amount > 0 and not self.healing_allowed:
            game.log(f"{self.name}: healing not allowed!")
            return
        if amount < -1 and any(card.name == "Invisibility cloak" for card in self._hand):
            game.log(f"Invisibility cloak prevents {-1 - amount}{constants.DAMAGE}!")
            amount = -1
        if amount < 0:
            game.log(f"{self.name} loses {-amount} hearts!")
        else:
            game.log(f"{self.name} gains {amount} hearts!")
        hearts_start = self._hearts
        self._hearts += amount
        if self._hearts > self._max_hearts:
            self._hearts = self._max_hearts
        if self._hearts < 0:
            self._hearts = 0
        if self.is_stunned:
            game.log(f"{self.name} has been stunned!")
            game.locations.add_control(game)
            self._damage_tokens = 0
            self._influence_tokens = 0
            self.choose_and_discard(game, len(self._hand) // 2)
        if hearts_start != self._hearts:
            hearts_gained = self._hearts - hearts_start
            for callback in self._hearts_callbacks:
                callback.hearts_callback(game, self, hearts_gained, source)

    def remove_hearts(self, game, amount=1):
        self.add_hearts(game, -amount)

    def disallow_drawing(self, game):
        self._drawing_disallowed += 1

    def allow_drawing(self, game):
        self._drawing_disallowed = max(0, self._drawing_disallowed - 1)

    @property
    def drawing_allowed(self):
        return self._drawing_disallowed == 0

    def disallow_healing(self, game):
        self._healing_disallowed += 1

    def allow_healing(self, game):
        self._healing_disallowed = max(0, self._healing_disallowed - 1)

    @property
    def healing_allowed(self):
        return self._healing_disallowed == 0 and not self.is_stunned and not self._hearts == self._max_hearts

    def disallow_gaining_tokens_out_of_turn(self, game):
        self._gaining_out_of_turn_allowed = False

    def allow_gaining_tokens_out_of_turn(self, game):
        self._gaining_out_of_turn_allowed = True

    def gaining_tokens_allowed(self, game):
        if self == game.heroes.active_hero:
            return True
        return self._gaining_out_of_turn_allowed

    def disallow_gaining_tokens_from_allies(self, game):
        self._gaining_from_allies_allowed = False

    def allow_gaining_tokens_from_allies(self, game):
        self._gaining_from_allies_allowed = True

    def can_reroll_die(self, house_die=True):
        for e in self._encounters:
            # TODO: this is a hack
            if e.name == "Forbidden Forest":
                return True
        if house_die and self._proficiency.can_reroll_house_dice:
            return True
        return False

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
                for effect in self._extra_shuffle_effects:
                    effect(game, self)
                self._deck = self._discard
                self._discard = []
                random.shuffle(self._deck)
            self._hand.append(self._deck.pop())

    def reveal_top_card(self, game):
        if len(self._deck) == 0:
            for effect in self._extra_shuffle_effects:
                effect(game, self)
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

    def discard_all_items(self, game, with_callbacks=True):
        discarded = []
        for i, card in enumerate(self._hand):
            if card.is_item():
                discarded.append(self.discard(game, i, with_callbacks))
        return discarded

    def choose_and_banish(self, game, desc="card", hand_only=False, optional=True, card_filter=lambda card: True, cancel_with='c', cancel_desc='to cancel'):
        choices = [cancel_with] if optional else []
        choices += [str(i) for i in range(len(self._hand)) if card_filter(self._hand[i])]

        if hand_only:
            prompt = f"Choose {desc} for {self.name} to banish: "
            if optional:
                prompt = f"Choose {desc} for {self.name} to banish ('{cancel_with}' {cancel_desc}): "
        else:
            prompt = f"Choose {desc} for {self.name} to banish (0-9 for hand, a-Z for discard): "
            if optional:
                prompt = f"Choose {desc} for {self.name} to banish (0-9 for hand, a-Z for discard, '{cancel_with}' {cancel_desc}): "
            discard_choices = self.choices_in_discard(game, card_filter=card_filter)
            choices.extend(discard_choices.keys())

        if len(choices) == 0 or (len(choices) == 1 and optional):
            game.log(f"{self.name} has no valid cards to banish!")
            return None

        choice = game.input(prompt, choices)
        if choice == cancel_with:
            return None
        try:
            choice = self._hand[int(choice)]
            self._hand.remove(choice)
        except ValueError:
            choice = discard_choices[choice]
            self._discard.remove(choice)
        game.log(f"{self.name} banishes {choice}")
        return choice

    def choices_in_discard(self, game, log=True, card_filter=lambda card: True):
        cards = [i for i in range(len(self._discard)) if card_filter(self._discard[i])]
        choices = {ALPHA_OPTIONS[i]: self._discard[i] for i in cards}
        if log:
            if len(choices) == 0:
                game.log(f"No valid cards in {self.name}'s discard")
            else:
                game.log(f"Cards in {self.name}'s discard:")
                for key, card in choices.items():
                    game.log(f" {key}: {card}")
        return choices

    def add_acquire_callback(self, game, callback):
        self._acquire_callbacks.append(callback)

    def remove_acquire_callback(self, game, callback):
        self._acquire_callbacks.remove(callback)

    def add_discard_callback(self, game, callback):
        self._discard_callbacks.append(callback)

    def remove_discard_callback(self, game, callback):
        self._discard_callbacks.remove(callback)

    def add_hearts_callback(self, game, callback):
        self._hearts_callbacks.append(callback)

    def remove_hearts_callback(self, game, callback):
        self._hearts_callbacks.remove(callback)

    def can_put_allies_in_deck(self, game):
        self._can_put_allies_in_deck = True

    def can_put_items_in_deck(self, game):
        self._can_put_items_in_deck = True

    def can_put_spells_in_deck(self, game):
        self._can_put_spells_in_deck = True

    @property
    def only_draw_four_cards(self):
        return self._only_draw_four_cards

    @only_draw_four_cards.setter
    def only_draw_four_cards(self, value):
        self._only_draw_four_cards = value

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
            game.log(f"No {constants.INFLUENCE} to spend!")
            return
        if len(game.hogwarts_deck._market) == 0:
            game.log("No cards to buy!")
            return
        choices = ['c', 't', 'r'] + [str(i) for i in range(len(game.hogwarts_deck._market))]
        choice = game.input("Choose card to buy ('c' to cancel): ", choices)
        if choice == "c":
            return
        from_market = True
        if choice == "t":
            choice = hogwarts.Tergeo()
            from_market = False
        elif choice == "r":
            choice = hogwarts.Reparo()
            from_market = False
        else:
            choice = game.hogwarts_deck[int(choice)]
        game.log(f"Buying {choice.name} ({choice.cost}{constants.INFLUENCE}; {choice.description})")
        cost = choice.cost
        cost += self._proficiency.cost_modifier(game, choice)
        if self._influence_tokens < cost:
            game.log(f"Not enough {constants.INFLUENCE}!")
            return
        self._influence_tokens -= cost
        if from_market:
            card = game.hogwarts_deck.remove(choice.name)
        else:
            card = choice
        top_of_deck = False
        if (card.is_ally() and self._can_put_allies_in_deck) or (card.is_item() and self._can_put_items_in_deck) or (card.is_spell() and self._can_put_spells_in_deck):
            if game.input(f"Put {card} on top of deck? (y/n): ", "yn") == "y":
                top_of_deck = True
        self._acquire(game, card, top_of_deck)

    def add_extra_card_effect(self, game, effect):
        self._extra_card_effects.append(effect)

    def add_extra_shuffle_effect(self, game, effect):
        self._extra_shuffle_effects.append(effect)

    def remove_extra_shuffle_effect(self, game, effect):
        self._extra_shuffle_effects.remove(effect)

    def add_extra_damage_effect(self, game, effect):
        self._extra_damage_effects.append(effect)

    def add_extra_influence_effect(self, game, effect):
        self._extra_influence_effects.append(effect)

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
                if len(self._hand) == 0:
                    # This can happen in the rare instance that a hero gets
                    # stunned while playing cards.
                    break
                self.play_card(game, 0)
        else:
            self.play_card(game, int(choice))

    def source_is_ally(self, game):
        call_stack = inspect.stack()
        for frame in call_stack[1:]:
            if frame.function == "add_damage" or frame.function == "add_influence":
                continue
            if frame.function == "remove_damage" or frame.function == "remove_influence":
                continue
            if frame.function == "add":
                continue
            if frame.function == "f":
                continue
            if 'self' not in frame.frame.f_locals:
                continue
            f_self = frame.frame.f_locals['self']
            if f_self == game:
                continue
            try:
                return f_self.is_ally()
            except AttributeError:
                return False
        return False

    def add_damage(self, game, amount=1):
        if amount > 0 and not self.gaining_tokens_allowed(game):
            game.log(f"{self.name}: gaining {constants.DAMAGE} on other heroes' turns not allowed!")
            return

        if amount > 0 and self.source_is_ally(game) and not self._gaining_from_allies_allowed:
            game.log(f"{self.name}: cannot gain {constants.DAMAGE} from Allies!")
            return

        self._damage_tokens += amount
        if self._damage_tokens < 0:
            self._damage_tokens = 0

    def remove_damage(self, game, amount=1):
        self.add_damage(game, -amount)

    def remove_all_damage(self, game):
        self._damage_tokens = 0

    def assign_damage(self, game):
        if self._damage_tokens == 0:
            game.log(f"No {constants.DAMAGE} to assign!")
            return
        if len(game.villain_deck.choices) == 0:
            game.log(f"No villains to assign {constants.DAMAGE} to!")
            return None
        if sum(1 for v in game.villain_deck.all if v.can_take_damage(game)) == 0:
            game.log(f"No villains to assign {constants.INFLUENCE} to!")
            return None
        choices = ['c'] + game.villain_deck.choices
        choice = game.input(f"Choose villain to assign {constants.DAMAGE} to ('c' to cancel): ", choices)
        if choice == 'c':
            return None
        if choice == 'v' and not game.villain_deck.voldemort_vulnerable(game):
            game.log("Voldemort is not vulnerable!")
            return None
        villain = game.villain_deck[choice]
        if not villain.can_take_damage(game):
            game.log(f"{villain.name} cannot be assigned {constants.DAMAGE}!")
            return None
        self.remove_damage(game)
        defeated = villain.add_damage(game)
        if defeated and villain.is_villain:
            for reward in self._extra_villain_rewards:
                reward(game)
            # Extra rewards only apply once
            self._extra_villain_rewards = []
        if defeated and villain.is_creature:
            for reward in self._extra_creature_rewards:
                reward(game)
            # Extra rewards only apply once
            self._extra_creature_rewards = []
        for effect in self._extra_damage_effects:
            effect(game, villain, 1)
        return villain

    def assign_influence(self, game):
        if self._influence_tokens == 0:
            game.log(f"No {constants.INFLUENCE} to assign!")
            return
        if len(game.villain_deck.choices) == 0:
            game.log(f"No villains to assign {constants.INFLUENCE} to!")
            return None
        if sum(1 for v in game.villain_deck.all if v.can_take_influence(game)) == 0:
            game.log(f"No villains to assign {constants.INFLUENCE} to!")
            return None
        choices = ['c'] + game.villain_deck.choices
        choice = game.input(f"Choose villain to assign {constants.INFLUENCE} to ('c' to cancel): ", choices)
        if choice == 'c':
            return None
        if choice == 'v' and not game.villain_deck.voldemort_vulnerable(game):
            game.log("Voldemort is not vulnerable!")
            return None
        villain = game.villain_deck[choice]
        if not villain.can_take_influence(game):
            game.log(f"{villain.name} cannot be assigned {constants.INFLUENCE}!")
            return None
        self.remove_influence(game)
        defeated = villain.add_influence(game)
        if defeated and villain.is_villain:
            for reward in self._extra_villain_rewards:
                reward(game)
            # Extra rewards only apply once
            self._extra_villain_rewards = []
        if defeated and villain.is_creature:
            for reward in self._extra_creature_rewards:
                reward(game)
            # Extra rewards only apply once
            self._extra_creature_rewards = []
        for effect in self._extra_influence_effects:
            effect(game, villain, 1)
        return villain

    def add_influence(self, game, amount=1):
        if amount > 0 and not self.gaining_tokens_allowed(game):
            game.log(f"{self.name}: gaining {constants.INFLUENCE} on other heroes' turns not allowed!")
            return

        if amount > 0 and self.source_is_ally(game) and not self._gaining_from_allies_allowed:
            game.log(f"{self.name}: cannot gain {constants.INFLUENCE} from Allies!")
            return

        self._influence_tokens += amount
        if self._influence_tokens < 0:
            self._influence_tokens = 0

    def remove_influence(self, game, amount=1):
        self.add_influence(game, -amount)

    def remove_all_influence(self, game):
        self._influence_tokens = 0

    def add(self, game, damage=0, influence=0, hearts=0, cards=0):
        self.add_damage(game, damage)
        self.add_influence(game, influence)
        if cards > 0:
            self.draw(game, cards)
        elif cards < 0:
            self.choose_and_discard(game, -cards)
        # hearts last so that if we're stunned, it applies last
        self.add_hearts(game, hearts)

    def add_detention(self, game, to_hand=False):
        game.log(f"{self.name} gains detention!")
        if to_hand:
            self._hand.append(hogwarts.Detention())
        else:
            self._discard.append(hogwarts.Detention())

    def add_extra_villain_reward(self, game, reward):
        self._extra_villain_rewards.append(reward)

    def add_extra_creature_reward(self, game, reward):
        self._extra_creature_rewards.append(reward)

    def add_encounter(self, game, encounter):
        self._encounters.append(encounter)

    def add_action(self, game, key, description, action):
        self._extra_actions[key] = (description, action)

    def remove_action(self, game, key):
        del self._extra_actions[key]

    def play_turn(self, game):
        game.log(f"-----{self.name}'s turn-----")
        self._proficiency.start_turn(game)
        for encounter in self._encounters:
            encounter.reward_effect(game)
        if game.locations.current.action is not None:
            self.add_action(game, *game.locations.current.action)
        while True:
            game.display_state()
            actions = ["p", "a", "b", "e", "q", "i"]
            prompt = f"Select (p)lay card, (a)ssign {constants.DAMAGE}, (i) assign {constants.INFLUENCE}, (b)uy card"
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
            if action == "i":
                self.assign_influence(game)
                continue
            if action == "b":
                self.buy_card(game)
                continue
            if action == "e":
                if self.confirm_end_turn(game):
                    return
                continue
            if action == "q":
                raise QuitGame()
            if action in self._extra_actions:
                self._extra_actions[action][1](game)
                continue
            raise ValueError("Programmer Error! Invalid choice!")

    def confirm_end_turn(self, game):
        if (len(self._hand) > 0 and
                game.input(f"{self.name} still has {len(self._hand)} cards in hand, end turn anyway? (y/n): ", "yn") != "y"):
            return False
        if (self._damage_tokens > 0 and
                any(v.can_take_damage(game) for v in game.villain_deck.all) and
                game.input(f"{self.name} still has {self._damage_tokens}{constants.DAMAGE}, end turn anyway? (y/n): ", "yn") != "y"):
            return False
        if (self._influence_tokens > 0 and
                (any(c[0].cost <= self._influence_tokens for c in game.hogwarts_deck._market.values())
                    or any(v.can_take_influence(game) for v in game.villain_deck.all)) and
                game.input(f"{self.name} still has {self._influence_tokens}{constants.INFLUENCE}, end turn anyway? (y/n): ", "yn") != "y"):
            return False
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
        return True

    def end_turn(self, game):
        self._discard += self._hand + self._play_area
        self._hand = []
        self._play_area = []
        self._damage_tokens = 0
        self._influence_tokens = 0
        self._cards_acquired = 0
        self._can_put_allies_in_deck = False
        self._can_put_items_in_deck = False
        self._can_put_spells_in_deck = False
        self._extra_villain_rewards = []
        self._extra_creature_rewards = []
        self._extra_card_effects = []
        self._extra_damage_effects = []
        self._extra_influence_effects = []
        self._extra_actions = {}
        if self._only_draw_four_cards and self._hearts <= 4:
            self.draw(game, 4, True)
        else:
            self.draw(game, 5, True)
        self._only_draw_four_cards = False
        self._proficiency.end_turn(game)


class Alohomora(hogwarts.Spell):
    def __init__(self):
        super().__init__("Alohomora", f"Gain 1{constants.INFLUENCE}", 0)

    def _effect(self, game):
        game.heroes.active_hero.add_influence(game)


class StarterAlly(hogwarts.Ally):
    def __init__(self, name):
        super().__init__(name, f"Gain 1{constants.DAMAGE} or 2{constants.HEART}", 0)

    def _effect(self, game):
        hero = game.heroes.active_hero
        if hero._hearts == hero._max_hearts:
            game.log(f"{hero.name} is already at max hearts, gaining 1{constants.DAMAGE}")
            hero.add_damage(game, 1)
            return
        if not hero.healing_allowed:
            game.log(f"{hero.name} can't heal, gaining 1{constants.DAMAGE}")
            hero.add_damage(game, 1)
            return
        choice = game.input(f"Choose effect: (d){constants.DAMAGE}, (h){constants.HEART}: ", "dh")
        if choice == "d":
            hero.add_damage(game, 1)
        elif choice == "h":
            hero.add_hearts(game, 2)


class StarterBroom(hogwarts.Item):
    def __init__(self, name):
        super().__init__(name, f"Gain 1{constants.DAMAGE}; if you defeat a Villain, gain 1{constants.INFLUENCE}", 0)

    def _effect(self, game):
        game.heroes.active_hero.add_damage(game)
        game.heroes.active_hero.add_extra_villain_reward(game, self.__villain_reward)

    def __villain_reward(self, game):
        game.heroes.active_hero.add_influence(game)
