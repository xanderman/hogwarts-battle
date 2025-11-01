"""
Unit tests for Hogwarts Battle cards.

Test files follow naming convention test_<card_name>.py and use custom test fakes
from fakes.py. The fakes provide working implementations with simplified behavior,
making tests more maintainable than using mocks.

Key test fakes:
- FakeGame: Game object with log capture and programmable input
- FakeHero: Hero with working token tracking and card management
- FakeHeroes: Hero collection with active_hero tracking
- DummyCard: Simple placeholder card for deck/draw testing

Example test patterns demonstrated:
- test_expelliarmus.py: Simple card with direct effects
- test_reparo.py: Card with user choices and conditional logic
- test_elder_wand.py: Combo card with callbacks and card interaction
"""
