---
name: m-test-add-hogwarts-card-tests
branch: feature/m-test-add-hogwarts-card-tests
status: pending
created: 2025-11-01
---

# Add 5 More Hogwarts Card Tests

## Problem/Goal
Add comprehensive unit tests for 5 additional Hogwarts Battle cards to increase test coverage and ensure card mechanics work correctly. Tests should follow the established pattern using FakeGame framework and cover various scenarios including card registration, effect behavior, edge cases, and logging.

## Success Criteria
- [ ] Add comprehensive unit tests for 5 different Hogwarts cards (following the pattern in test_elder_wand.py)
- [ ] Each test file includes multiple test cases covering different scenarios (card registration, effect behavior, edge cases, logging)
- [ ] Tests use the FakeGame test framework and follow AAA (Arrange-Act-Assert) pattern
- [ ] All new tests pass successfully

## Selected Cards
1. **Lumos** (Spell) - Simple spell affecting all heroes with card draw
2. **Stupefy** (Spell) - Complex spell with multiple effects (damage + control removal + draw)
3. **Sorting Hat** (Item) - Item with influence and special ally placement ability
4. **Rubeus Hagrid** (Ally) - Ally affecting multiple heroes (damage to active, hearts to all)
5. **Chocolate Frog** (Item) - Item with hero selection AND discard effect

## Context Manifest

### How The Testing Framework Currently Works

This codebase uses custom test fakes rather than mocks, providing working implementations with simplified behavior. The philosophy here is that fakes are more maintainable and provide better simulation of actual game behavior than mocks.

#### The FakeGame Testing Infrastructure

When a card is tested, it operates within a `FakeGame` environment (defined in `/Users/bobgardner/src/hogwarts-battle/tests/unit/fakes.py`). The FakeGame provides:

1. **Message Logging**: The `log(message, attr=None)` method captures all game messages into `_log_messages` list. Tests can retrieve logs with `game.get_logs()` and verify that appropriate messages were logged. This is critical because card effects communicate their actions through logging (e.g., "Hero 1 gains 2 damage", "Removed control token").

2. **Input Simulation**: The `input(prompt, valid_choices=None)` method returns pre-programmed responses from an `inputs` list passed during construction. When creating `FakeGame(inputs=['i', 'd'])`, the first call to `game.input()` returns 'i', the second returns 'd', etc. If inputs are exhausted, it returns the first valid choice as a default. This allows testing of branching card logic (like Reparo's choice between influence or drawing).

3. **Hero Management**: The game contains a `FakeHeroes` object accessible via `game.heroes`, which tracks multiple heroes and the currently active hero. `game.heroes.active_hero` returns the active hero. `game.heroes.all_heroes` returns a `FakeHeroList` that uses metaprogramming - when you call a method on it, that method is called on ALL contained heroes (e.g., `game.heroes.all_heroes.draw(game)` calls `draw(game)` on every hero).

4. **Location/Control Management**: The game has a `game.locations` object (FakeLocations) that tracks control tokens. `game.locations.add_control(game)` increments tokens, `game.locations.remove_control(game)` decrements them (if allowed). This is used for cards like Stupefy that remove control tokens.

#### The FakeHero Implementation

FakeHero provides working token tracking and state management:

**Resource Tokens**: Heroes track `_damage_tokens`, `_influence_tokens`, `_hearts`, and `_max_hearts`. The `add_damage(game, amount, source)`, `add_influence(game, amount, source)`, and `add_hearts(game, amount, source)` methods modify these with full validation logic:
- Damage/influence gains are blocked when `gaining_tokens_allowed(game)` returns False (happens when gaining on another hero's turn and `_gaining_out_of_turn_allowed` is False)
- Damage/influence from ally sources are blocked when `_gaining_from_allies_allowed` is False
- Heart gains are blocked when `healing_allowed` is False (calculated from `_healing_disallowed` counter and stun state)
- Hearts can't go above `_max_hearts` or below 0
- When hearts reach 0, the hero becomes stunned: tokens are cleared and half the hand is discarded

**Card Management**: Heroes have four card locations:
- `_deck`: Cards available to draw
- `_hand`: Cards in hand
- `_play_area`: Cards that have been played this turn
- `_discard`: Discarded cards

The `draw(game, count, end_of_turn)` method draws cards from deck to hand. If the deck is empty, it triggers a shuffle: discard pile becomes the new deck (after running `_extra_shuffle_effects` callbacks), then gets randomized with `random.shuffle()`.

The convenience method `add(game, damage=0, influence=0, hearts=0, cards=0)` is crucial - it applies multiple resource changes at once. For cards>0 it draws, for cards<0 it discards from hand. Hearts are applied LAST so stun logic applies correctly after other changes.

**Drawing State Control**: The `_drawing_disallowed` counter tracks whether drawing is allowed. `disallow_drawing(game)` increments it, `allow_drawing(game)` decrements it. The property `drawing_allowed` returns `True` only when counter is 0. This reference-counting approach allows multiple effects to disable drawing without conflicts.

**Proficiency System**: Heroes have boolean flags for proficiencies:
- `_can_put_allies_in_deck`: Starts False
- `_can_put_items_in_deck`: Starts False
- `_can_put_spells_in_deck`: Starts False

When cards like Sorting Hat are played, they call `hero.can_put_allies_in_deck(game)` which sets the corresponding flag to True. This affects where acquired cards go (normally discard, but can go to top of deck if proficiency is enabled).

**Callback System**: FakeHero maintains several callback lists that cards can register with:
- `_extra_card_effects`: Triggered when any card is played via `play_card(game, which)`
- `_extra_shuffle_effects`: Triggered during deck shuffling
- `_discard_callbacks`: Triggered when cards are discarded (though discarding logic itself isn't fully implemented in fakes)
- `_hearts_callbacks`: Triggered when hearts change, receives `(game, hero, hearts_gained, source)`

The callback pattern is demonstrated in Elder Wand tests - the wand registers a callback that grants bonuses whenever future spells are played.

#### Card Implementations

All cards inherit from base classes in `/Users/bobgardner/src/hogwarts-battle/hogwarts/base.py`:
- `Spell`: Inherits from `_HogwartsCard`, `is_spell()` returns True
- `Ally`: Inherits from `_HogwartsCard`, `is_ally()` returns True
- `Item`: Inherits from `_HogwartsCard`, `is_item()` returns True

Each card implements:
- `__init__`: Sets name, description, and cost via `super().__init__()`
- `_effect(game)`: The main card effect that executes when played
- `discard_effect(game, hero)`: Optional effect that triggers when discarded (defaults to no-op in base class)

Cards are registered in the `CARDS_BY_NAME` dictionary: `CARDS_BY_NAME['Card Name'] = CardClass`

Cards use the `constants` module for display symbols: `constants.DAMAGE` (ϟ), `constants.INFLUENCE` (💰), `constants.HEART` (💜), `constants.CONTROL` (💀), `constants.CARD` (🃏).

#### Test Organization Patterns

Tests live in `/Users/bobgardner/src/hogwarts-battle/tests/unit/` with naming convention `test_<card_name>.py` (using snake_case conversion of card names).

Each test file follows this structure:
```python
import unittest
import sys
import os

# Path setup for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hogwarts.<card_module> import <CardClass>
from hogwarts import CARDS_BY_NAME
from tests.unit.fakes import FakeGame, DummyCard

class Test<CardClass>(unittest.TestCase):
    # Test methods here

if __name__ == '__main__':
    unittest.main()
```

**Standard Test Cases** (demonstrated in existing tests):

1. **Card Registration Test**: Verify the card is properly registered with correct name, cost, and type
   ```python
   def test_card_registration(self):
       card = CardClass()
       self.assertEqual(card.name, "Card Name")
       self.assertEqual(card.cost, X)
       self.assertEqual(CARDS_BY_NAME['Card Name'], CardClass)
       self.assertTrue(card.is_spell())  # or is_ally() or is_item()
   ```

2. **Basic Effect Test**: Verify the card's primary effect works correctly
   - Arrange: Create FakeGame, get hero, set up initial state (put cards in deck for drawing, adjust hearts, etc.)
   - Act: Call `card._effect(game)` directly
   - Assert: Verify tokens/state changed correctly

3. **Edge Cases**: Test boundary conditions like:
   - Empty deck/discard (triggers shuffle)
   - Hero at max hearts (can't gain more)
   - Drawing when disallowed
   - Multiple heroes (for cards affecting all heroes)

4. **Logging Test**: Verify appropriate log messages are generated
   ```python
   logs = game.get_logs()
   self.assertTrue(any("expected text" in log for log in logs))
   ```

5. **User Choice Tests** (for cards with branching logic): Use pre-programmed inputs
   ```python
   game = FakeGame(inputs=['i'])  # Will choose 'i' when prompted
   card._effect(game)
   # Verify behavior for that choice
   ```

### For This Task: What Needs to Be Tested

#### 1. Lumos (Spell) - Simple All-Heroes Card
**File**: `/Users/bobgardner/src/hogwarts-battle/hogwarts/lumos.py`
**Effect**: `game.heroes.all_heroes.draw(game)` - ALL heroes draw one card

**Test Cases Needed**:
- Card registration (name="Lumos", cost=4, is_spell=True)
- Single hero scenario: Verify hero draws 1 card
- Multiple heroes scenario: Create `FakeGame(num_heroes=3)`, verify ALL heroes draw cards
- Empty deck scenario: Hero with cards in discard only, verify shuffle-then-draw
- Drawing disallowed: One or more heroes have drawing blocked, verify they don't draw and log messages explain why
- Logging: Verify each hero logs a draw message

**Pattern**: Use `game.heroes.all_heroes` metaprogramming - the method call propagates to all heroes.

#### 2. Stupefy (Spell) - Complex Multi-Effect Card
**File**: `/Users/bobgardner/src/hogwarts-battle/hogwarts/stupefy.py`
**Effect**: Active hero gains 1 damage + draws 1 card (via `add()` method), then removes 1 control token

**Test Cases Needed**:
- Card registration (name="Stupefy", cost=6, is_spell=True)
- Basic effect: Verify damage=1, hand size increases by 1, control tokens decreased by 1
- Effect with cards in deck: Put DummyCards in deck first
- Empty deck scenario: Cards in discard, verify shuffle happens during draw
- No control tokens: Start with 0 control tokens, verify remove_control logs message but doesn't go negative
- Control removal disabled: Set `game.locations.can_remove_control = False`, verify control not removed
- Logging: Verify messages for damage gain, card draw, AND control removal

**Pattern**: This tests the combined `add()` method (which applies damage and cards together) plus a separate game state modification (locations).

#### 3. Sorting Hat (Item) - Proficiency-Granting Card
**File**: `/Users/bobgardner/src/hogwarts-battle/hogwarts/sorting_hat.py`
**Effect**: Active hero gains 2 influence, then calls `hero.can_put_allies_in_deck(game)` which sets proficiency flag

**Test Cases Needed**:
- Card registration (name="Sorting Hat", cost=4, is_item=True)
- Basic effect: Verify influence increased by 2
- Proficiency flag set: Verify `hero._can_put_allies_in_deck` changes from False to True
- Multiple plays: Play twice, verify flag stays True and influence keeps accumulating
- Logging: Verify influence gain is logged

**Pattern**: This tests token addition plus state flag modification. The proficiency system affects acquisition behavior (not directly tested here, but the flag change is testable).

**Note**: The method is called `can_put_allies_in_deck(game)` - it's a setter that enables the proficiency, not a getter.

#### 4. Rubeus Hagrid (Ally) - Mixed Target Effects
**File**: `/Users/bobgardner/src/hogwarts-battle/hogwarts/rubeus_hagrid.py`
**Effect**: Active hero gains 1 damage, then ALL heroes gain 1 heart

**Test Cases Needed**:
- Card registration (name="Rubeus Hagrid", cost=4, is_ally=True)
- Single hero: Verify active hero gets 1 damage and 1 heart
- Multiple heroes: Create 3 heroes, verify active hero gets damage, ALL get hearts
- Heroes at max hearts: Some heroes at max_hearts=10, verify they don't gain hearts (logs explain)
- Healing disallowed: Some heroes have healing blocked, verify only allowed heroes gain hearts
- Hero below max hearts: Set `hero._hearts = 8`, verify they can gain hearts
- Logging: Verify damage log for active hero, heart logs for each hero

**Pattern**: Mixed targeting - specific hero (active) for damage, all heroes for hearts. Requires testing with multiple heroes where some have different states (max hearts, healing blocked).

#### 5. Chocolate Frog (Item) - Hero Selection + Discard Effect
**File**: `/Users/bobgardner/src/hogwarts-battle/hogwarts/chocolate_frog.py`
**Effect**: `game.heroes.choose_hero()` returns a hero, then that hero gains 1 influence + 1 heart via `add()`
**Discard Effect**: `discard_effect(game, hero)` gives that hero 1 influence + 1 heart

**Test Cases Needed**:
- Card registration (name="Chocolate Frog", cost=2, is_item=True)
- Single hero scenario: Verify the only hero gets benefits (no choice needed)
- Multiple heroes with choice: Create `FakeGame(num_heroes=3, inputs=['1'])`, verify chosen hero gets benefits
- Chosen hero at max hearts: Pick hero at max_hearts, verify they get influence but not hearts
- Chosen hero healing disallowed: Pick hero with healing blocked, verify appropriate behavior
- Discard effect: Create card instance, call `card.discard_effect(game, hero)` directly, verify hero gets resources
- Discard effect at max hearts: Same but hero at max hearts
- Logging: Verify logs show which hero gained what

**Pattern**: This tests the `choose_hero()` mechanism and also the `discard_effect()` callback. The FakeHeroes.choose_hero() implementation (in fakes.py lines 370-379) returns the first hero if only one exists, otherwise uses game.input() to get a choice. For testing discard effect, you don't need to actually discard - just call the method directly.

### Technical Reference Details

#### Key Type Signatures

```python
# FakeGame creation
FakeGame(heroes=None, inputs=None, num_heroes=1)
create_test_game(num_heroes=1, hero_names=None, inputs=None)

# Card methods
card._effect(game)  # Main effect
card.discard_effect(game, hero)  # Discard callback
card.is_spell() -> bool
card.is_ally() -> bool
card.is_item() -> bool

# Hero resource methods
hero.add(game, damage=0, influence=0, hearts=0, cards=0)
hero.add_damage(game, amount=1, source=None)
hero.add_influence(game, amount=1, source=None)
hero.add_hearts(game, amount=1, source=None)
hero.draw(game, count=1, end_of_turn=False)

# Hero state control
hero.disallow_drawing(game)
hero.allow_drawing(game)
hero.disallow_healing(game)
hero.allow_healing(game)
hero.can_put_allies_in_deck(game)  # Sets flag to True

# Hero state properties
hero.drawing_allowed -> bool
hero.healing_allowed -> bool
hero.is_stunned -> bool

# Heroes collection methods
game.heroes.active_hero -> FakeHero
game.heroes.all_heroes -> FakeHeroList  # Metaprogramming proxy
game.heroes.all_heroes_except_active -> FakeHeroList
game.heroes.choose_hero(game, prompt="...", optional=False, disallow=None) -> FakeHero or None

# Locations methods
game.locations.add_control(game)
game.locations.remove_control(game)
game.locations.can_remove_control = True/False  # Control flag

# Game utility methods
game.log(message, attr=None)
game.get_logs() -> list[str]
game.clear_logs()
game.input(prompt, valid_choices=None) -> str
```

#### Data Structures

**FakeHero Internal State**:
```python
hero._damage_tokens: int  # Damage accumulated
hero._influence_tokens: int  # Influence accumulated
hero._hearts: int  # Current hearts
hero._max_hearts: int  # Maximum hearts (usually 10)
hero._deck: list[Card]  # Cards to draw from
hero._hand: list[Card]  # Cards in hand
hero._play_area: list[Card]  # Cards played this turn
hero._discard: list[Card]  # Discarded cards
hero._drawing_disallowed: int  # Reference counter (0 = allowed)
hero._healing_disallowed: int  # Reference counter (0 = allowed)
hero._can_put_allies_in_deck: bool
hero._can_put_items_in_deck: bool
hero._can_put_spells_in_deck: bool
```

**FakeLocations State**:
```python
locations._control_tokens: int  # Current control tokens
locations.can_remove_control: bool  # Whether removal allowed
```

#### DummyCard Helper

For testing draw mechanics, use `DummyCard` instead of real cards:
```python
from tests.unit.fakes import DummyCard

hero._deck = [DummyCard("Card 1"), DummyCard("Card 2")]
hero.draw(game, 2)
self.assertEqual(len(hero._hand), 2)
```

DummyCard has a name and returns False for all type checks (is_spell/is_ally/is_item).

#### File Locations for Implementation

- **Test files go here**: `/Users/bobgardner/src/hogwarts-battle/tests/unit/`
- **Naming convention**: `test_<snake_case_card_name>.py`
  - test_lumos.py
  - test_stupefy.py
  - test_sorting_hat.py
  - test_rubeus_hagrid.py
  - test_chocolate_frog.py
- **Card implementations**: `/Users/bobgardner/src/hogwarts-battle/hogwarts/<snake_case>.py`
- **Test fakes module**: `/Users/bobgardner/src/hogwarts-battle/tests/unit/fakes.py`
- **Base card classes**: `/Users/bobgardner/src/hogwarts-battle/hogwarts/base.py`

#### Running Tests

From project root:
```bash
python -m pytest tests/unit/test_<card_name>.py -v
# Or run specific test
python -m pytest tests/unit/test_<card_name>.py::TestClass::test_method -v
# Or run the file directly
python tests/unit/test_<card_name>.py
```

### Key Testing Insights

1. **Always pre-populate decks**: If a card draws, put DummyCards in `hero._deck` first, otherwise draw won't happen
2. **Test multi-hero scenarios**: For cards affecting all_heroes, create `FakeGame(num_heroes=3)` and verify each hero
3. **Use inputs list for choices**: Pass `inputs=['0', 'i', 'd']` to pre-program user responses
4. **Direct method calls**: Call `card._effect(game)` directly, don't need to go through play_card() unless testing callbacks
5. **Check both state and logs**: Verify tokens changed AND appropriate log messages generated
6. **Test edge cases**: Max hearts, empty deck, blocked drawing/healing, zero control tokens
7. **Hearts must be below max to gain**: Set `hero._hearts = 9` before testing heart gain, otherwise no gain occurs
8. **The add() method is atomic**: When you call `add(game, damage=1, cards=1)`, both happen together
9. **Proficiency methods are setters**: `can_put_allies_in_deck(game)` sets the flag, doesn't return anything
10. **Metaprogramming is real**: `game.heroes.all_heroes.draw(game)` actually calls draw on every hero, it's not stubbed

## User Notes
<!-- Any specific notes or requirements from the developer -->

## Work Log
<!-- Updated as work progresses -->
- [YYYY-MM-DD] Started task, initial research
