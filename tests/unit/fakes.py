"""
Test fakes for Hogwarts Battle unit tests.

This module provides working test doubles (fakes) for testing cards and game logic
without requiring the full game infrastructure. These fakes are designed to support
the most common testing scenarios while remaining simple and maintainable.
"""

import random


class DummyCard:
    """
    Simple card placeholder for testing draw mechanics and deck manipulation.

    Use this instead of FakeHero when you need placeholder objects in decks/discard
    for testing card drawing, shuffling, and other deck operations.

    Example:
        hero._deck = [DummyCard("Card 1"), DummyCard("Card 2")]
        hero.draw(game, 2)  # Draws the dummy cards
    """

    def __init__(self, name="Dummy Card"):
        self.name = name

    def is_spell(self):
        return False

    def is_ally(self):
        return False

    def is_item(self):
        return False

    def __str__(self):
        return self.name


class FakeHero:
    """
    A simplified but functional Hero implementation for testing.

    Provides working token tracking, card management, proficiency system support,
    and state flags that cards commonly interact with. Unlike MagicMock, this
    provides real behavior that can be inspected and verified.

    Proficiency Methods:
        - can_put_allies_in_deck(game): Enable placing acquired Allies on top of deck
        - can_put_items_in_deck(game): Enable placing acquired Items on top of deck
        - can_put_spells_in_deck(game): Enable placing acquired Spells on top of deck
    """

    def __init__(self, name="Test Hero", starting_cards=None):
        self.name = name
        self._max_hearts = 10
        self._hearts = 10
        self._damage_tokens = 0
        self._influence_tokens = 0

        # Card locations
        self._deck = []
        self._hand = []
        self._play_area = []
        self._discard = starting_cards if starting_cards else []

        # State flags - use reference counters like real hero
        self._drawing_disallowed = 0
        self._healing_disallowed = 0
        self._gaining_out_of_turn_allowed = True
        self._gaining_from_allies_allowed = True

        # Callback lists
        self._extra_card_effects = []
        self._extra_villain_rewards = []
        self._extra_creature_rewards = []
        self._extra_shuffle_effects = []
        self._extra_damage_effects = []
        self._extra_influence_effects = []
        self._acquire_callbacks = []
        self._discard_callbacks = []
        self._hearts_callbacks = []

        # Proficiency support
        self._can_put_allies_in_deck = False
        self._can_put_items_in_deck = False
        self._can_put_spells_in_deck = False
        self._only_draw_four_cards = False

    @property
    def is_stunned(self):
        return self._hearts == 0

    @property
    def drawing_allowed(self):
        return self._drawing_disallowed == 0

    @property
    def healing_allowed(self):
        return (self._healing_disallowed == 0 and
                not self.is_stunned and
                self._hearts < self._max_hearts)

    def gaining_tokens_allowed(self, game):
        """Check if hero can gain tokens (damage/influence)."""
        # If this hero is the active hero, always allowed
        if self == game.heroes.active_hero:
            return True
        return self._gaining_out_of_turn_allowed

    def disallow_drawing(self, game):
        self._drawing_disallowed += 1

    def allow_drawing(self, game):
        self._drawing_disallowed = max(0, self._drawing_disallowed - 1)

    def disallow_healing(self, game):
        self._healing_disallowed += 1

    def allow_healing(self, game):
        self._healing_disallowed = max(0, self._healing_disallowed - 1)

    def disallow_gaining_tokens_out_of_turn(self, game):
        self._gaining_out_of_turn_allowed = False

    def allow_gaining_tokens_out_of_turn(self, game):
        self._gaining_out_of_turn_allowed = True

    def disallow_gaining_tokens_from_allies(self, game):
        self._gaining_from_allies_allowed = False

    def allow_gaining_tokens_from_allies(self, game):
        self._gaining_from_allies_allowed = True

    def can_put_allies_in_deck(self, game):
        """Enable proficiency to put acquired Allies on top of deck."""
        self._can_put_allies_in_deck = True

    def can_put_items_in_deck(self, game):
        """Enable proficiency to put acquired Items on top of deck."""
        self._can_put_items_in_deck = True

    def can_put_spells_in_deck(self, game):
        """Enable proficiency to put acquired Spells on top of deck."""
        self._can_put_spells_in_deck = True

    def add_damage(self, game, amount=1, source=None):
        """Add damage tokens to this hero."""
        if amount > 0 and not self.gaining_tokens_allowed(game):
            game.log(f"{self.name}: gaining damage on other heroes' turns not allowed!")
            return

        # Check if source is an ally and gaining from allies is disallowed
        if source and hasattr(source, 'is_ally') and source.is_ally():
            if not self._gaining_from_allies_allowed:
                game.log(f"{self.name}: cannot gain damage from Allies!")
                return

        self._damage_tokens += amount
        if self._damage_tokens < 0:
            self._damage_tokens = 0

        if amount > 0:
            game.log(f"{self.name} gains {amount} damage")

    def remove_damage(self, game, amount=1):
        self.add_damage(game, -amount)

    def remove_all_damage(self, game):
        self._damage_tokens = 0

    def add_influence(self, game, amount=1, source=None):
        """Add influence tokens to this hero."""
        if amount > 0 and not self.gaining_tokens_allowed(game):
            game.log(f"{self.name}: gaining influence on other heroes' turns not allowed!")
            return

        # Check if source is an ally and gaining from allies is disallowed
        if source and hasattr(source, 'is_ally') and source.is_ally():
            if not self._gaining_from_allies_allowed:
                game.log(f"{self.name}: cannot gain influence from Allies!")
                return

        self._influence_tokens += amount
        if self._influence_tokens < 0:
            self._influence_tokens = 0

        if amount > 0:
            game.log(f"{self.name} gains {amount} influence")

    def remove_influence(self, game, amount=1):
        self.add_influence(game, -amount)

    def remove_all_influence(self, game):
        self._influence_tokens = 0

    def add_hearts(self, game, amount=1, source=None):
        """Add or remove hearts from this hero."""
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

        hearts_start = self._hearts
        self._hearts += amount

        if self._hearts > self._max_hearts:
            self._hearts = self._max_hearts
        if self._hearts < 0:
            self._hearts = 0

        if amount < 0:
            game.log(f"{self.name} loses {-amount} hearts!")
        else:
            game.log(f"{self.name} gains {amount} hearts!")

        # Handle stunning
        if self.is_stunned:
            game.log(f"{self.name} has been stunned!")
            # Simplified stun - just clear tokens and half the hand
            self._damage_tokens = 0
            self._influence_tokens = 0
            discard_count = len(self._hand) // 2
            for _ in range(discard_count):
                if self._hand:
                    self._discard.append(self._hand.pop())

        # Trigger callbacks
        if hearts_start != self._hearts:
            hearts_gained = self._hearts - hearts_start
            for callback in self._hearts_callbacks:
                # Support both object-based callbacks and plain callables
                if hasattr(callback, 'hearts_callback'):
                    callback.hearts_callback(game, self, hearts_gained, source)
                else:
                    callback(game, self, hearts_gained, source)

    def remove_hearts(self, game, amount=1):
        self.add_hearts(game, -amount)

    def draw(self, game, count=1, end_of_turn=False):
        """Draw cards from deck to hand."""
        if not end_of_turn and not self.drawing_allowed:
            game.log("Drawing not allowed!")
            return

        game.log(f"{self.name} draws {count} cards")

        for i in range(count):
            if len(self._deck) == 0:
                if len(self._discard) == 0:
                    # Out of cards
                    break
                # Shuffle discard into deck
                for effect in self._extra_shuffle_effects:
                    effect(game, self)
                self._deck = self._discard
                self._discard = []
                random.shuffle(self._deck)

            if self._deck:
                self._hand.append(self._deck.pop())

    def add(self, game, damage=0, influence=0, hearts=0, cards=0):
        """Convenience method to add multiple resources at once."""
        self.add_damage(game, damage)
        self.add_influence(game, influence)
        if cards > 0:
            self.draw(game, cards)
        elif cards < 0:
            # Simplified: just discard from hand without choice
            discard_count = min(-cards, len(self._hand))
            for _ in range(discard_count):
                if self._hand:
                    self._discard.append(self._hand.pop())
        # Hearts last so stun applies correctly
        self.add_hearts(game, hearts)

    def play_card(self, game, which):
        """Play a card from hand to play area."""
        if which >= len(self._hand):
            raise IndexError("Card index out of range")

        card = self._hand.pop(which)
        card.play(game)

        # Trigger extra card effects
        for effect in self._extra_card_effects:
            effect(game, card)

        self._play_area.append(card)

    def add_extra_card_effect(self, game, effect):
        """Register a callback that fires when future cards are played."""
        self._extra_card_effects.append(effect)

    def add_extra_villain_reward(self, game, reward):
        """Register a callback that fires when a villain is defeated."""
        self._extra_villain_rewards.append(reward)

    def add_extra_creature_reward(self, game, reward):
        """Register a callback that fires when a creature is defeated."""
        self._extra_creature_rewards.append(reward)

    def add_extra_shuffle_effect(self, game, effect):
        """Register a callback that fires when deck is shuffled."""
        self._extra_shuffle_effects.append(effect)

    def add_acquire_callback(self, game, callback):
        """Register a callback that fires when a card is acquired."""
        self._acquire_callbacks.append(callback)

    def add_discard_callback(self, game, callback):
        """Register a callback that fires when a card is discarded."""
        self._discard_callbacks.append(callback)

    def add_hearts_callback(self, game, callback):
        """Register a callback that fires when hearts change."""
        self._hearts_callbacks.append(callback)


class FakeHeroList(list):
    """
    A fake HeroList that supports the __getattr__ metaprogramming pattern.

    When you call a method on FakeHeroList, it calls that method on all contained heroes.
    Example: hero_list.add_damage(game, 1) calls add_damage on every hero.
    """

    def __init__(self, *heroes):
        super().__init__(heroes)

    def __getattr__(self, attr):
        def f(game, *args, **kwargs):
            for hero in self:
                getattr(hero, attr)(game, *args, **kwargs)
        return f


class FakeHeroes:
    """
    A fake Heroes collection that manages multiple heroes and tracks the active hero.
    """

    def __init__(self, heroes=None, active_index=0):
        if heroes is None:
            # Default: single test hero
            heroes = [FakeHero("Test Hero")]
        self._heroes = heroes
        self._current = active_index

    @property
    def active_hero(self):
        return self._heroes[self._current]

    @property
    def all_heroes(self):
        return FakeHeroList(*self._heroes)

    @property
    def all_heroes_except_active(self):
        return FakeHeroList(*[h for h in self._heroes if h != self.active_hero])

    def __len__(self):
        return len(self._heroes)

    def __getitem__(self, index):
        return self._heroes[index]

    def __iter__(self):
        return iter(self._heroes)

    def next(self):
        """Move to next hero."""
        self._current = (self._current + 1) % len(self._heroes)

    def choose_hero(self, game, prompt="Choose a hero: ", optional=False, disallow=None):
        """Simplified: always return active hero or first non-disallowed hero."""
        if len(self._heroes) == 1:
            return self._heroes[0]

        for hero in self._heroes:
            if hero != disallow:
                return hero

        return None if optional else self._heroes[0]


class FakeLocations:
    """
    A fake Locations object that tracks control tokens.
    """

    def __init__(self):
        self._control_tokens = 0
        self.can_remove_control = True

    def add_control(self, game):
        """Add a control token."""
        self._control_tokens += 1
        game.log(f"Added control token (total: {self._control_tokens})")

    def remove_control(self, game):
        """Remove a control token."""
        if not self.can_remove_control:
            game.log("Cannot remove control!")
            return

        if self._control_tokens > 0:
            self._control_tokens -= 1
            game.log(f"Removed control token (total: {self._control_tokens})")


class FakeGame:
    """
    A simplified Game object for testing card effects.

    Provides working implementations of the key methods cards need:
    - log(): Stores messages for inspection
    - input(): Returns pre-programmed responses
    - heroes, locations: Access to game state
    """

    def __init__(self, heroes=None, inputs=None, num_heroes=1):
        """
        Create a fake game for testing.

        Args:
            heroes: List of FakeHero objects (creates default if None)
            inputs: List of input responses to return in sequence
            num_heroes: Number of heroes to create if heroes is None
        """
        if heroes is None:
            heroes = [FakeHero(f"Hero {i+1}") for i in range(num_heroes)]

        self.heroes = FakeHeroes(heroes)
        self.locations = FakeLocations()
        self._log_messages = []
        self._inputs = inputs if inputs else []
        self._input_index = 0

    def log(self, message, attr=None):
        """Log a message (stores for test inspection)."""
        self._log_messages.append(message)

    def input(self, prompt, valid_choices=None):
        """
        Return a pre-programmed input response.

        Returns responses from the inputs list in sequence. If no more inputs
        are available, returns the first valid choice as a default.
        """
        if self._input_index < len(self._inputs):
            response = self._inputs[self._input_index]
            self._input_index += 1
            return response

        # Default: return first valid choice
        if valid_choices:
            if isinstance(valid_choices, range):
                return str(valid_choices.start)
            elif isinstance(valid_choices, list) or isinstance(valid_choices, str):
                return valid_choices[0] if valid_choices else ""

        return ""

    def get_logs(self):
        """Get all logged messages."""
        return self._log_messages

    def clear_logs(self):
        """Clear logged messages."""
        self._log_messages = []


def create_test_game(num_heroes=1, hero_names=None, inputs=None):
    """
    Convenience factory for creating a test game with common configuration.

    Args:
        num_heroes: Number of heroes to create
        hero_names: Optional list of hero names
        inputs: Pre-programmed input responses

    Returns:
        FakeGame instance ready for testing
    """
    if hero_names:
        heroes = [FakeHero(name) for name in hero_names]
    else:
        heroes = None

    return FakeGame(heroes=heroes, inputs=inputs, num_heroes=num_heroes)
