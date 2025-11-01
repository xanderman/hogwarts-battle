---
name: m-implement-test-fakes-hogwarts-cards
branch: feature/m-implement-test-fakes-hogwarts-cards
status: pending
created: 2025-10-31
---

# Implement Test Fakes for Hogwarts Cards

## Problem/Goal
Create test fakes/fixtures for Hogwarts cards to enable effective unit testing. Currently, testing cards likely requires complex setup or external dependencies. This task will provide lightweight, flexible test doubles that make it easy to write fast, isolated unit tests for card-related functionality.

## Success Criteria
- [ ] Test fake/fixture factories are created for Hogwarts card entities
- [ ] Unit tests can instantiate cards using fakes without external dependencies
- [ ] Test fakes support common testing scenarios (valid cards, edge cases, etc.)
- [ ] Documentation or examples show how to use the fakes in tests

## Context Manifest

### How Hogwarts Cards Currently Work: Complete Architecture

Hogwarts cards form the core deck-building mechanic of this Harry Potter cooperative deck-building game. When you understand how cards work in this codebase, you're understanding the heart of the game engine.

**Card Architecture and Registration:**

Every Hogwarts card in the system follows a consistent registration pattern. Each card module defines a class that inherits from one of three base types (`Spell`, `Ally`, or `Item`), implements its unique effect, and then registers itself in the global `CARDS_BY_NAME` dictionary. This registration happens at module import time through the pattern `CARDS_BY_NAME['Card Name'] = CardClass`. The `CARDS_BY_NAME` dictionary is the central registry used throughout the system - when the game initializes a deck from YAML config files (like `config/game_one.yaml`), it looks up card names in this dictionary to instantiate actual card objects.

The base card class `_HogwartsCard` (defined in `hogwarts/base.py`) establishes the interface that all cards must follow:
- `name`: String identifier for the card
- `description`: Human-readable effect description including unicode symbols for game tokens
- `cost`: Influence tokens required to purchase from the market
- `rolls_house_die`: Boolean flag indicating if the card triggers a die roll
- `_effect(game)`: Abstract method that each card must implement with its unique behavior
- `discard_effect(game, hero)`: Optional hook for effects that trigger when the card is discarded
- Type checking methods: `is_spell()`, `is_ally()`, `is_item()` - each returns False in base, overridden in subclasses
- `even_cost`: Property that checks if cost is non-zero and divisible by 2
- `color`: Property that returns curses color pair for display (spell=red, ally=cyan, item=yellow)

**Card Type Hierarchy:**

The three card types form a simple inheritance tree:

1. **Spell** (red color, `curses.color_pair(2)`): Offensive and utility magic. Examples include `Reparo` (gain influence or draw), `Expelliarmus` (gain damage and draw), `Confundus` (gain damage with conditional control removal). Spells typically provide damage or utility effects.

2. **Ally** (cyan color, `curses.color_pair(3)`): Character cards representing people helping the heroes. Examples include `Albus Dumbledore` (all heroes gain damage/influence/hearts/cards), `Fleur Delacour` (gain influence, bonus hearts if another ally played), `Horace Slughorn` (all heroes choose influence or hearts, rolls house die). Allies often affect multiple heroes and can trigger cross-ally synergies.

3. **Item** (yellow color, `curses.color_pair(4)`): Equipment and artifacts. Examples include `Elder Wand` (gain damage/hearts per spell played), `Felix Felicis` (choose 2 of 4 benefits), `Gillyweed` (gain heart, bonus hearts per ally). Items often provide conditional effects or interact with other card types.

There's also a special `_WeasleyTwin` base class (inherits from Ally) used for Fred and George Weasley cards that check if other heroes have Weasley cards in hand for bonus effects.

**The Card Lifecycle:**

When a card is played during a hero's turn, the system follows this exact sequence:

1. Hero selects a card from their hand through the game input system
2. `hero.play_card(game, which)` is called, which:
   - Removes the card from `hero._hand` at index `which`
   - Calls `card.play(game)` which logs the play and invokes `card._effect(game)`
   - Iterates through any `hero._extra_card_effects` callbacks registered by previously played cards
   - Appends the card to `hero._play_area` for visibility and interaction with other cards

This means cards can see what's already been played (by examining `game.heroes.active_hero._play_area`) and can register callbacks that trigger when future cards are played this turn. This is the foundation for combo effects.

**Token System and Hero Interaction:**

Cards manipulate game state primarily through hero token methods. The hero object (`Hero` class in `heroes/base.py`) maintains:
- `_damage_tokens`: Lightning bolt tokens (ϟ) used to damage villains
- `_influence_tokens`: Money bag tokens (💰) used to buy cards
- `_hearts`: Heart tokens (💜) representing health (starts at 10, max 10)
- `_deck`, `_hand`, `_play_area`, `_discard`: Card location tracking

Cards call these key hero methods from their `_effect()`:
- `hero.add_damage(game, amount)`: Adds damage tokens, checks if gaining out-of-turn is allowed, checks if source is ally (some effects disallow ally damage)
- `hero.add_influence(game, amount)`: Adds influence tokens with same restrictions
- `hero.add_hearts(game, amount)`: Adds hearts if not stunned, not at max, and healing allowed. Negative amounts for damage. If hearts reach 0, hero is stunned (adds control token, clears tokens, discards half hand)
- `hero.draw(game, count)`: Draws cards from deck, auto-shuffles discard if deck empty, triggers shuffle effects
- `hero.add(game, damage=0, influence=0, hearts=0, cards=0)`: Convenience method that calls all token methods in sequence (hearts last so stun applies correctly)

All token manipulation goes through the game object reference, allowing proper logging and state tracking.

**Complex Card Patterns and Callback System:**

Many cards implement sophisticated conditional logic through callback registration:

**Extra Card Effects**: Cards like `Elder Wand` register callbacks that trigger when future cards are played this turn. The pattern:
```python
def _effect(self, game):
    # Check already-played cards
    for card in game.heroes.active_hero._play_area:
        if card.is_spell():
            # Apply effect for existing cards
    # Register for future cards
    game.heroes.active_hero.add_extra_card_effect(game, self.__callback)

def __callback(self, game, card):
    if card.is_spell():
        # Apply effect for new card
```

**State Tracking**: Cards that need to track whether their bonus has triggered use instance variables like `self._used_ability` to prevent double-application.

**Conditional Effects**: Cards check game state to determine available options:
- `hero.drawing_allowed`: Can the hero draw cards (some Dark Arts effects disable)
- `hero.healing_allowed`: Can the hero gain hearts (disabled if stunned, at max, or by effects)
- `hero.gaining_tokens_allowed(game)`: Can the hero gain damage/influence out of turn
- `game.locations.can_remove_control`: Can control tokens be removed

**User Choice Cards**: Cards like `Reparo` offer choices using `game.input(prompt, valid_choices)`. The game object handles input validation and UI display. Common patterns:
- Binary choice: `game.input("(i)nfluence or (d)raw?", "id")`
- Cancel option: `game.input("Choose or (c)ancel", ['c', '0', '1', '2'])`
- Conditional availability: Remove options from valid_choices if not applicable

**Cross-Hero Effects**: Cards affecting all heroes use `game.heroes.all_heroes`, which is a `HeroList` object. Calling methods on HeroList automatically applies to all heroes: `game.heroes.all_heroes.add(game, damage=1, influence=1)`.

**Discard Effects**: Some cards like `Detention` and `Old Sock` have effects that trigger when discarded via `discard_effect(game, hero)`. This is called automatically when the card enters the discard pile through normal game flow (end of turn, hero stunned, card-specific discard).

**Villain Reward Callbacks**: Cards like `StarterBroom` can register rewards that trigger when a villain is defeated: `hero.add_extra_villain_reward(game, callback)`. These are one-time effects that clear after use.

**House Die Rolling**: Cards with `rolls_house_die=True` trigger die rolls that can grant random bonuses (damage, influence, hearts, or cards to all heroes). Different house dice have different probability distributions (Gryffindor, Hufflepuff, Ravenclaw, Slytherin defined in `game.py`).

**Card Inspection Patterns**: Many cards check other cards in play:
- Inspect play area: `for card in game.heroes.active_hero._play_area`
- Check other heroes' cards: `for hero in game.heroes: for card in hero._hand`
- Examine discard: `hero.choices_in_discard(game, card_filter=lambda card: card.is_item())`

**Market and Acquisition**: Cards are purchased from `game.hogwarts_deck._market` (a defaultdict of lists keyed by card name). When a hero spends influence, `hero.buy_card(game)` removes from market and adds to hero's discard (or optionally top of deck). The market is defined in YAML files and contains 6 slots that refill from the deck.

**Constants and Display**: The codebase uses unicode symbols defined in `constants.py`:
- `DAMAGE = 'ϟ'` (lightning bolt)
- `INFLUENCE = '💰'` (money bag)
- `HEART = '💜'` (purple heart)
- `CONTROL = '💀'` (skull)
- `CARD = '🃏'` (playing card)

These appear in card descriptions and are used throughout for consistent display.

### Current Testing Infrastructure

**Existing Test**: The codebase has ONE existing unit test file: `hogwarts/test_reparo.py`. This test provides the pattern that all future tests should follow:

```python
import unittest
from unittest.mock import MagicMock
from . import CARDS_BY_NAME
from .reparo import Reparo

class TestReparo(unittest.TestCase):
    def test_reparo(self):
        reparo = Reparo()
        self.assertEqual(reparo.name, "Reparo")
        self.assertEqual(reparo.cost, 3)
        self.assertEqual(CARDS_BY_NAME['Reparo'], Reparo)

    def test_effect(self):
        reparo = Reparo()
        game = MagicMock()
        hero = MagicMock()
        game.heroes.active_hero = hero
        hero.drawing_allowed = True
        hero.add_influence = MagicMock()
        hero.draw = MagicMock()
        game.input = MagicMock(side_effect=["i", "d"])
        reparo._effect(game)
        hero.add_influence.assert_called_once_with(game, 2)
        reparo._effect(game)
        hero.draw.assert_called_once_with(game)
```

This test demonstrates the current approach: use `unittest.mock.MagicMock` to create fake game and hero objects with just the properties/methods the card needs. This is minimal but brittle - it requires knowing exactly what the card will access.

**Testing Challenges**: Cards have complex dependencies:
1. They need a `game` object with heroes, villain deck, locations, and input handling
2. They access hero state (tokens, cards in hand/play/discard)
3. They interact with other cards through the play area
4. They register callbacks that fire on future actions
5. Some check game state (healing allowed, drawing allowed, control tokens)
6. User choices require mocking input sequences

The current MagicMock approach works for simple cards but becomes unwieldy for complex interactions. A proper fake/fixture system would provide pre-configured test doubles with sensible defaults.

### What Test Fakes Need to Provide

For comprehensive unit testing of Hogwarts cards, test fakes should enable:

**1. Card Instantiation**: Create card instances without needing the full game running. Currently this works fine - cards are simple objects. The registration check (CARDS_BY_NAME) should be included in basic tests.

**2. Game Context**: A fake `Game` object that provides:
- `log(message)`: Capture logged messages for assertion
- `input(prompt, choices)`: Mock input with pre-programmed responses or default selection
- `heroes`: Access to hero collection with active_hero
- `villain_deck`: Minimal villain state for damage assignment tests
- `locations`: Control token management
- `hogwarts_deck`: Market for purchase tests
- Die rolling methods that can be deterministic for testing

**3. Hero Fixtures**: Fake heroes with:
- Token state (damage, influence, hearts) that can be inspected before/after
- Card locations (hand, play area, discard, deck) pre-populated with test cards
- State flags (drawing_allowed, healing_allowed, stunned)
- Callback tracking to verify callbacks are registered/triggered
- Methods that actually work (add_damage, add_influence, draw, etc.)

**4. Card Interaction Testing**: Support for:
- Playing multiple cards in sequence to test combo effects
- Verifying callbacks fire at the right time
- Testing conditional effects based on game state
- Checking cross-hero effects
- Simulating villain defeats for reward testing

**5. Scenario Builders**: Factory methods to create common test scenarios:
- "Hero with simple hand" (all basic cards)
- "Hero with mixed types" (spells, allies, items)
- "Hero near death" (1 heart remaining)
- "Multiple heroes for cross-hero effects"
- "Restricted game state" (drawing disabled, healing disabled)

**6. Assertion Helpers**: Methods to check outcomes:
- Token changes (damage gained/lost, influence spent, hearts changed)
- Card movement (hand -> play area, discard -> hand)
- Callbacks registered (verify callback lists)
- Log messages (verify specific effects triggered)

### Implementation Strategy for Test Fakes

**File Organization**: Create test fakes in a dedicated test utilities module, likely:
- `tests/unit/fakes.py` or `tests/fixtures.py` for the fake implementations
- Keep test fakes separate from production code
- Import from `hogwarts.base` and `heroes.base` to extend real classes where beneficial

**Fake vs Mock Philosophy**:
- Use **fakes** (working implementations with simplified behavior) rather than mocks where possible
- Fakes are more maintainable and catch more bugs
- Provide defaults that work for most tests, allow overrides for specific scenarios
- Example: FakeGame should have a working `log()` that stores messages, not just a mock that tracks calls

**Key Classes to Implement**:

1. **FakeGame**: Simplified game object with essential methods working
   - Store logs in list for inspection
   - Default input handler (picks first choice or programmed sequence)
   - Lazy initialization of subsystems (heroes, villains, locations)
   - Deterministic die rolls for reproducible tests

2. **FakeHero**: Hero with working token system but simplified deck management
   - Real token tracking (damage, influence, hearts)
   - Simple card lists (no shuffle complexity)
   - Callback tracking visible for testing
   - Pre-populate methods for common scenarios

3. **TestCardBuilder**: Fluent interface for creating test card scenarios
   - `with_hand([card1, card2])`: Set specific hand
   - `with_play_area([card])`: Pre-play cards
   - `with_tokens(damage=5, influence=10)`: Set token state
   - Chain methods for readable test setup

4. **HeroesFixture**: Collection of heroes for multi-hero testing
   - Create 1-4 heroes with different configurations
   - Set active hero
   - Support for all_heroes operations

**Essential Fake Behaviors**:

- Game.input() should accept a list of responses to return in sequence, or a default strategy
- Hero token methods should actually modify token counts (not just track calls)
- Card play should actually move cards and call effects (use real card objects)
- Logging should accumulate messages for assertion (not just pass)
- Callbacks should actually register and fire (track in lists, execute when appropriate)

**Testing Complex Cards**: For cards like `Elder Wand` (tracks spells played), test fakes must:
1. Allow playing cards in sequence
2. Support querying play area contents
3. Execute registered callbacks when new cards play
4. Verify callback was registered (check hero._extra_card_effects list)

For cards like `Polyjuice Potion` (copies ally effects), test fakes must:
1. Allow pre-populating play area with specific cards
2. Support input mocking to choose which ally to copy
3. Execute the copied card's effect through the real card object

### Critical Files and Paths

**Card Implementation**:
- `/Users/bobgardner/src/hogwarts-battle/hogwarts/base.py`: Base card classes (_HogwartsCard, Spell, Ally, Item)
- `/Users/bobgardner/src/hogwarts-battle/hogwarts/*.py`: 87 individual card implementations
- `/Users/bobgardner/src/hogwarts-battle/hogwarts/__init__.py`: Module initialization, CARDS_BY_NAME registry

**Hero System**:
- `/Users/bobgardner/src/hogwarts-battle/heroes/base.py`: Hero class (913 lines), HeroList, starter cards
- `/Users/bobgardner/src/hogwarts-battle/heroes/*.py`: Individual hero implementations

**Game Engine**:
- `/Users/bobgardner/src/hogwarts-battle/game.py`: Game class, turn flow, input handling, die rolls
- `/Users/bobgardner/src/hogwarts-battle/constants.py`: Token symbols and constants

**Configuration**:
- `/Users/bobgardner/src/hogwarts-battle/config/*.yaml`: Game configurations defining card pools

**Existing Test**:
- `/Users/bobgardner/src/hogwarts-battle/hogwarts/test_reparo.py`: Current test pattern using MagicMock

**Test Infrastructure** (to be created):
- `/Users/bobgardner/src/hogwarts-battle/tests/unit/fakes.py`: Test fakes for cards
- `/Users/bobgardner/src/hogwarts-battle/tests/unit/test_*.py`: Card unit tests using fakes

### Key Interfaces and Signatures

**Card Interface**:
```python
class _HogwartsCard:
    def __init__(self, name, description, cost, rolls_house_die=False)
    def play(self, game)  # Public play method
    def _effect(self, game)  # Override in subclasses
    def discard_effect(self, game, hero)  # Optional override
    def is_spell(self) -> bool
    def is_ally(self) -> bool
    def is_item(self) -> bool
    @property
    def even_cost(self) -> bool
    @property
    def color(self) -> int  # curses color pair
```

**Hero Token Methods**:
```python
def add_damage(self, game, amount=1)
def add_influence(self, game, amount=1)
def add_hearts(self, game, amount=1, source=None)
def draw(self, game, count=1, end_of_turn=False)
def add(self, game, damage=0, influence=0, hearts=0, cards=0)
```

**Hero State Properties**:
```python
@property
def drawing_allowed(self) -> bool
@property
def healing_allowed(self) -> bool
def gaining_tokens_allowed(self, game) -> bool
@property
def is_stunned(self) -> bool
```

**Hero Card Management**:
```python
def play_card(self, game, which: int)  # which is index in _hand
def discard(self, game, which: int, with_callbacks=True)
def choose_and_discard(self, game, count=1, with_callbacks=True)
```

**Hero Callback Registration**:
```python
def add_extra_card_effect(self, game, effect: Callable[[Game, Card], None])
def add_extra_villain_reward(self, game, reward: Callable[[Game], None])
def add_extra_damage_effect(self, game, effect: Callable[[Game, Villain, int], None])
```

**Game Interface** (minimum for cards):
```python
def log(self, message: str, attr=curses.A_NORMAL)
def input(self, message: str, valid_choices: List[str]) -> str
def roll_gryffindor_die(self)
def roll_hufflepuff_die(self)
def roll_ravenclaw_die(self)
def roll_slytherin_die(self)
# Attributes
game.heroes  # Heroes collection with active_hero
game.villain_deck  # VillainDeck
game.locations  # Locations (control tokens)
game.hogwarts_deck  # HogwartsDeck (market)
```

**Heroes Collection Interface**:
```python
@property
def active_hero(self) -> Hero
@property
def all_heroes(self) -> HeroList
def choose_hero(self, game, prompt="Choose a hero: ", optional=False, disallow=None) -> Hero
```

### Example Test Patterns

**Simple Card Test** (like Expelliarmus):
```python
def test_expelliarmus():
    card = Expelliarmus()
    game = FakeGame()
    hero = game.heroes.active_hero

    card._effect(game)

    assert hero._damage_tokens == 2
    assert len(hero._hand) == 1  # drew 1 card
```

**Choice Card Test** (like Reparo):
```python
def test_reparo_choose_influence():
    card = Reparo()
    game = FakeGame(inputs=['i'])
    hero = game.heroes.active_hero

    card._effect(game)

    assert hero._influence_tokens == 2

def test_reparo_choose_draw():
    card = Reparo()
    game = FakeGame(inputs=['d'])
    hero = game.heroes.active_hero

    card._effect(game)

    assert len(hero._hand) == 1
```

**Conditional Effect Test** (like Confundus):
```python
def test_confundus_remove_control_when_all_damaged():
    card = Confundus()
    game = FakeGame()
    hero = game.heroes.active_hero
    game.villain_deck.add_villain(FakeVillain(took_damage=True))

    card._effect(game)

    assert hero._damage_tokens == 1
    assert game.locations.control_removed  # Verify control was removed
```

**Combo Card Test** (like Elder Wand):
```python
def test_elder_wand_with_existing_spell():
    wand = ElderWand()
    spell = Expelliarmus()
    game = FakeGame()
    hero = game.heroes.active_hero
    hero._play_area = [spell]  # Spell already played

    wand._effect(game)

    assert hero._damage_tokens == 1
    assert hero._hearts == 11  # 10 starting + 1

def test_elder_wand_with_future_spell():
    wand = ElderWand()
    spell = Expelliarmus()
    game = FakeGame()
    hero = game.heroes.active_hero

    wand._effect(game)
    hero.play_card(game, 0)  # Assuming spell in hand

    assert len(hero._extra_card_effects) == 1  # Callback registered
    # Verify spell triggered wand effect
```

**Cross-Hero Test** (like Albus Dumbledore):
```python
def test_dumbledore_affects_all_heroes():
    card = AlbusDumbledore()
    game = FakeGame(num_heroes=3)

    card._effect(game)

    for hero in game.heroes:
        assert hero._damage_tokens == 1
        assert hero._influence_tokens == 1
        assert hero._hearts == 11
        assert len(hero._hand) == 1
```

## User Notes
<!-- Any specific notes or requirements from the developer -->

## Work Log
<!-- Updated as work progresses -->
- [YYYY-MM-DD] Started task, initial research
