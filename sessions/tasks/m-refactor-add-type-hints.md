---
name: m-refactor-add-type-hints
branch: feature/m-refactor-add-type-hints
status: pending
created: 2025-10-31
---

# Add Type Hints

## Problem/Goal
Add comprehensive type hints to the Python codebase to improve code clarity, catch potential type errors early, and enable better IDE support and static analysis.

## Success Criteria
- [ ] All Python functions/methods have type hints for parameters and return types
- [ ] Type checking passes with mypy or similar static type checker
- [ ] Existing tests continue to pass after type hints are added
- [ ] Complex types use appropriate constructs (Optional, Union, generics, etc.)

## Context Manifest

### How This Python Codebase Currently Works: Architecture & Organization

This is a **terminal-based implementation of the Harry Potter: Hogwarts Battle board game** built with Python's curses library. The codebase consists of approximately 8,302 lines of Python code spread across 196 files, organized into a clear domain-driven structure. Currently, **the codebase has ZERO type hints** - it's pure Python 3 without any typing annotations. The only files with type hints are in the `sessions/` directory which is the cc-sessions framework (not part of the game code itself).

**Python Version & Environment:**
- Target: Python 3.9.6+ (README states 3.9.6 tested, features available from 3.4+)
- Current system: Python 3.14.0 available
- Shebang: `#!/opt/homebrew/bin/python3`
- Dependencies: PyYAML (for YAML config parsing), curses (standard library)
- No existing type checking configuration (no mypy.ini, pyproject.toml, or setup.py)

**Module Structure & Import Patterns:**

The codebase is organized into domain modules with a consistent pattern:
1. Each module has a `base.py` that defines core classes and registries
2. Each module has an `__init__.py` that:
   - Imports base classes first (`from .base import *`)
   - Dynamically imports all other .py files in the directory using `importlib`
   - Skips files starting with `_` or `test_`
3. Individual entity files register themselves in global dictionaries (e.g., `VILLAINS_BY_NAME`, `CARDS_BY_NAME`, `ENCOUNTERS_BY_NAME`)

**Core Modules:**

1. **game.py** (333 lines) - Main entry point and game loop
   - `Game` class: Central orchestrator holding all game state
   - Command-line argument parsing with custom `argparse.Action` subclasses
   - Curses-based UI with window management and resizing
   - Contains main game loop, input handling, logging system

2. **heroes/** - Hero character implementations
   - `base.py`: `Hero`, `Heroes`, `HeroList` classes
   - Individual hero files: Harry, Ron, Hermione, Neville, Ginny, Luna
   - Starting cards defined inline: `Alohomora` (spell), `StarterAlly`, `StarterBroom`

3. **villains/** - Villain/enemy implementations
   - `base.py`: `VillainDeck`, `_Foe`, `Villain`, `Creature`, `VillainCreature` classes
   - 35+ individual villain files (Quirrell, Basilisk, Death Eaters, Dragons, etc.)
   - Includes multiple Voldemort variants for different game stages

4. **hogwarts/** - Purchasable card deck
   - `base.py`: `HogwartsDeck`, `_HogwartsCard`, `Ally`, `Item`, `Spell` classes
   - 88+ card files (spells like Expelliarmus, items, allies)
   - Market system for buying cards

5. **dark_arts/** - Dark Arts event deck
   - `base.py`: `DarkArtsDeck`, `DarkArtsCard` classes
   - 38+ dark arts cards that trigger negative effects

6. **encounters/** - Special encounter system (horcruxes, monster boxes)
   - `base.py`: `EncountersDeck`, `Encounter`, `NullEncounter` classes
   - Horcrux system, Monster Box challenges

7. **locations.py** (509 lines) - Game location progression
   - `Locations` class managing location sequence
   - 40+ `Location` subclasses with varying difficulty

8. **proficiencies.py** (312 lines) - Character proficiency system
   - `Proficiency` base class and 10 specific proficiencies
   - Callback-based effects triggered by game events

9. **constants.py** (7 lines) - Unicode symbols for game tokens
   - `DAMAGE`, `INFLUENCE`, `HEART`, `CONTROL`, `CARD`, `DISALLOW`

10. **config/** - YAML configuration files for game setups
    - 7 base game configs, 4 monster box configs

**Critical Type Patterns to Understand:**

**1. The Game State Object Pattern:**
The `Game` object is passed as the first parameter to almost every method in the codebase. This is the central state container:
```python
def some_method(self, game):  # 'game' is always a Game instance
    game.heroes.active_hero.add_damage(game, 1)
    game.locations.add_control(game)
    game.villain_deck.reveal(game)
```

**2. Curses Window Objects:**
Many classes manage curses windows and pads:
```python
def __init__(self, window, ...):  # window is curses window
    self._window = window  # curses._CursesWindow
    self._pad = curses.newpad(100, 100)  # curses pad for scrolling
```

**3. Dynamic Method Dispatch via `__getattr__`:**
The codebase uses clever metaprogramming for batch operations. `HeroList` and `_VillainList` override `__getattr__` to dynamically create methods:
```python
class HeroList(list):
    def __getattr__(self, attr):
        def f(game, *args, **kwargs):
            for hero in self:
                getattr(hero, attr)(game, *args, **kwargs)
        return f
```
This allows `game.heroes.all_heroes.add_damage(game, 1)` to call `add_damage` on every hero.

**4. Callback Pattern:**
Extensive use of callback lists for event-driven behavior:
```python
self._acquire_callbacks = []  # List of objects with acquire_callback method
self._discard_callbacks = []  # List of objects with discard_callback method
self._hearts_callbacks = []   # List of objects with hearts_callback method

# Later:
for callback in self._acquire_callbacks:
    callback.acquire_callback(game, self, card)
```

**5. Optional Action Tuples:**
Some entities have optional actions as tuples:
```python
self.action = ('H', "(H)ogwarts Castle", self._action)  # (key, description, callable)
# or None if no action
```

**6. Registry Pattern:**
Global dictionaries map names to classes:
```python
VILLAINS_BY_NAME = {}  # str -> Type[Villain]
CARDS_BY_NAME = {}     # str -> Type[_HogwartsCard]
ENCOUNTERS_BY_NAME = {}  # str -> Type[Encounter]
```

**7. Return Type Variations:**
Many methods return different types based on success:
```python
def assign_damage(self, game):
    # Returns None if no damage assigned
    # Returns villain object if damage assigned
    return villain  # or None
```

**8. Mixed Container Types:**
```python
self._deck = []  # List of card instances
self._hand = []  # List of card instances
self._market = defaultdict(list)  # Dict[str, List[Card]]
```

**9. Curses Attribute Constants:**
Functions use curses module constants:
```python
curses.A_BOLD  # int
curses.A_NORMAL  # int
curses.color_pair(1)  # int
```

**10. Config Dictionary Pattern:**
YAML configs are loaded as dictionaries and accessed directly:
```python
config = safe_load(file.read())  # Dict[str, Any]
config['locations']  # List[str]
config['encounters']  # Optional[Dict]
```

**Complex Type Scenarios:**

**Polymorphic Card Types:**
Cards can be Spell, Ally, or Item - all share `_HogwartsCard` base but have different color properties and type checking methods:
```python
def is_ally(self) -> bool
def is_item(self) -> bool
def is_spell(self) -> bool
```

**Union Villain Types:**
Villains can be `Villain`, `Creature`, or `VillainCreature` (both):
```python
@property
def is_villain(self) -> bool
@property
def is_creature(self) -> bool
```

**Callable Effect Methods:**
Many classes define effect methods that take game state:
```python
def _effect(self, game):  # Defined in many subclasses
    raise NotImplementedError()
```

**State Flags and Counters:**
Extensive use of private state:
```python
self._stunned: bool
self._damage_tokens: int
self._influence_tokens: int
self._drawing_disallowed: int  # Reference counter
self._healing_disallowed: int  # Reference counter
```

**Generic List Subclasses:**
`HeroList` and `_VillainList` are list subclasses with dynamic dispatch, requiring careful typing of their contents.

**Named Tuple Usage:**
Limited, but present in heroes/base.py for display modes.

**Enum Usage:**
`DisplayMode` enum with `auto()`:
```python
class DisplayMode(Enum):
    DEFAULT = auto()
    HAND = auto()
    PLAY_AREA = auto()
    DISCARD = auto()
```

**Lambda Functions:**
Used for filtering and callbacks:
```python
card_filter=lambda card: True  # Callable[[Card], bool]
```

**Inspect Module Usage:**
`heroes/base.py` uses `inspect.stack()` to determine if method was called from an ally (for gain restriction logic) - this is very dynamic and type hints should reflect the runtime nature.

### For Type Hint Implementation: What Needs to Be Done

**Import Strategy:**
Add at top of each file:
```python
from typing import Optional, List, Dict, Any, Callable, Tuple, Union, Protocol
```

For Python 3.9+, can use built-in generics:
```python
from typing import Optional, Callable, Protocol, Union  # Still need these
list[str]  # Instead of List[str]
dict[str, Any]  # Instead of Dict[str, Any]
```

**Protocol Approach for Callbacks:**
Since callbacks are objects with specific methods, use Protocol:
```python
from typing import Protocol

class AcquireCallback(Protocol):
    def acquire_callback(self, game: 'Game', hero: 'Hero', card: '_HogwartsCard') -> None: ...

class DiscardCallback(Protocol):
    def discard_callback(self, game: 'Game', hero: 'Hero') -> None: ...
```

**Forward References:**
Extensive use needed due to circular dependencies:
```python
def method(self, game: 'Game') -> None:  # Game not yet defined
```

**Type Aliases for Clarity:**
```python
WindowPosition = Tuple[int, int]  # (line, col)
WindowSize = Tuple[int, int]  # (height, width)
ActionTuple = Tuple[str, str, Callable[['Game'], None]]  # (key, description, function)
```

**Generic Collections:**
```python
self._deck: list['_HogwartsCard']
self._market: dict[str, list['_HogwartsCard']]
self._callbacks: list[AcquireCallback]
```

**Optional Returns:**
```python
def assign_damage(self, game: 'Game') -> Optional['_Foe']:
def choose_hero(self, game: 'Game', ...) -> Optional['Hero']:
```

**Union Types for Polymorphism:**
```python
FoeType = Union[Villain, Creature, VillainCreature]
CardType = Union[Ally, Item, Spell]
```

**Method Signatures Throughout:**

Game class methods:
```python
def __init__(self, window: curses._CursesWindow, config: dict[str, Any], chosen_heroes: list[Hero]) -> None
def input(self, message: str, valid_choices: Optional[Union[list[str], range]]) -> str
def log(self, message: str, attr: int = curses.A_NORMAL) -> None
def play_turn(self) -> None
```

Hero class methods:
```python
def draw(self, game: 'Game', count: int = 1, end_of_turn: bool = False) -> None
def add_damage(self, game: 'Game', amount: int = 1) -> None
def assign_damage(self, game: 'Game') -> Optional['_Foe']
def buy_card(self, game: 'Game') -> None
def play_card(self, game: 'Game', which: int) -> None
```

Villain class methods:
```python
def add_damage(self, game: 'Game') -> bool  # Returns True if defeated
def _effect(self, game: 'Game') -> None
def reward(self, game: 'Game') -> None
```

**Curses Types:**
```python
import curses
# These are the actual types from curses module:
curses._CursesWindow  # Window type
# But curses stub files may not be complete, so might need:
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _curses import window as CursesWindow
else:
    CursesWindow = Any
```

**Config Types:**
YAML configs are loaded as dicts but have expected structure:
```python
GameConfig = dict[str, Any]  # Or create TypedDict for structure
```

**Challenges & Notes:**

1. **Curses module has limited typing support** - may need to use `Any` or cast in some places
2. **Dynamic imports** in `__init__.py` files don't affect typing but should be annotated where classes are used
3. **Global registries** (`VILLAINS_BY_NAME`, etc.) are `dict[str, type[ClassName]]`
4. **Inheritance chains** are deep - base classes must be annotated first
5. **Private methods** (starting with `_`) still need type hints
6. **Property decorators** need return type annotation
7. **Magic methods** (`__str__`, `__len__`, `__getitem__`, etc.) must be annotated
8. **Exception classes** (`QuitGame`, `DebugGame`) are simple, just need `Exception` base
9. **Callback objects** - using Protocol is cleanest approach
10. **`*args` and `**kwargs`** in dynamic dispatch methods should be typed as `Any`

### Technical Reference Details

#### Key Class Hierarchies

**Heroes:**
```
Hero (base class)
├── Harry
├── Ron
├── Hermione
├── Neville
├── Ginny
└── Luna
```

**Villains:**
```
_Foe (base class)
├── Villain
├── Creature
└── VillainCreature (both Villain and Creature)
```

**Cards:**
```
_HogwartsCard (base class)
├── Spell
├── Ally
└── Item
```

**Other Hierarchies:**
- `DarkArtsCard` (flat - all subclasses direct)
- `Location` (flat - all subclasses direct)
- `Proficiency` (flat - all subclasses direct)
- `Encounter` (some nesting for horcruxes)

#### Critical Callback Protocols Needed

```python
class AcquireCallback(Protocol):
    def acquire_callback(self, game: 'Game', hero: 'Hero', card: '_HogwartsCard') -> None: ...

class DiscardCallback(Protocol):
    def discard_callback(self, game: 'Game', hero: 'Hero') -> None: ...

class HeartsCallback(Protocol):
    def hearts_callback(self, game: 'Game', hero: 'Hero', amount: int, source: Any) -> None: ...

class ControlCallback(Protocol):
    def control_callback(self, game: 'Game', amount: int) -> None: ...
```

#### File Implementation Order

For minimal errors during incremental implementation:

1. **constants.py** - Simplest, just module-level string constants
2. **Base class files** (define types before usage):
   - villains/base.py
   - hogwarts/base.py
   - heroes/base.py
   - dark_arts/base.py
   - encounters/base.py
3. **Module manager files:**
   - locations.py
   - proficiencies.py
4. **Individual entity files** (can be done in parallel):
   - villains/*.py
   - heroes/*.py
   - hogwarts/*.py
   - dark_arts/*.py
   - encounters/*.py
5. **Main orchestrator:**
   - game.py (last, as it imports everything)

#### Type Checking Configuration (Create New)

Need to create `mypy.ini`:
```ini
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_any_unimported = False
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True

[mypy-curses]
ignore_missing_imports = True

[mypy-yaml]
ignore_missing_imports = True
```

#### Common Patterns to Handle

**Pattern 1: Methods that modify and return self (for chaining):**
Not used in this codebase - all methods return None or specific types.

**Pattern 2: Variable arguments in effect methods:**
```python
def add(self, game: 'Game', damage: int = 0, influence: int = 0,
        hearts: int = 0, cards: int = 0) -> None
```

**Pattern 3: Conditional types in polymorphic methods:**
Use `@overload` for methods that return different types based on parameters.

**Pattern 4: Generator methods:**
None present in codebase.

**Pattern 5: Context managers:**
None present in codebase.

### Implementation Strategy

1. Start with base classes to establish type foundation
2. Use Protocol for callback types
3. Use string forward references for circular dependencies: `'Game'` instead of `Game`
4. Create type aliases for complex types: `CardList = list[_HogwartsCard]`
5. Use `Optional[X]` for values that can be None
6. Use `Union[X, Y]` for polymorphic returns
7. For curses types, use `Any` if type stubs incomplete
8. Test incrementally with mypy after each module
9. Add `# type: ignore` comments only when absolutely necessary (document why)
10. Ensure all public methods have full annotations
11. Private methods should also be annotated for consistency

## User Notes
<!-- Any specific notes or requirements from the developer -->

## Work Log
<!-- Updated as work progresses -->
- [YYYY-MM-DD] Started task, initial research
