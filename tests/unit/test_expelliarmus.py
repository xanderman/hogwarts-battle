"""
Example test demonstrating simple card testing with fakes.

Expelliarmus is a simple spell that adds 2 damage and draws 1 card.
This test shows the basic pattern for testing straightforward card effects.
"""

import unittest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hogwarts.expelliarmus import Expelliarmus
from hogwarts import CARDS_BY_NAME
from tests.unit.fakes import FakeGame, DummyCard


class TestExpelliarmus(unittest.TestCase):
    """Test Expelliarmus spell using fakes."""

    def test_card_registration(self):
        """Verify card is registered in CARDS_BY_NAME."""
        card = Expelliarmus()
        self.assertEqual(card.name, "Expelliarmus")
        self.assertEqual(card.cost, 6)
        self.assertEqual(CARDS_BY_NAME['Expelliarmus'], Expelliarmus)

    def test_card_is_spell(self):
        """Verify card type checking."""
        card = Expelliarmus()
        self.assertTrue(card.is_spell())
        self.assertFalse(card.is_ally())
        self.assertFalse(card.is_item())

    def test_effect(self):
        """Test the card's effect: gain 2 damage and draw 1 card."""
        # Arrange: Create test game and card
        card = Expelliarmus()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Put some cards in deck so we can draw
        hero._deck = [DummyCard("Dummy Card 1"), DummyCard("Dummy Card 2")]

        # Verify starting state
        self.assertEqual(hero._damage_tokens, 0)
        self.assertEqual(len(hero._hand), 0)

        # Act: Execute card effect
        card._effect(game)

        # Assert: Verify tokens and cards changed correctly
        self.assertEqual(hero._damage_tokens, 2, "Should gain 2 damage tokens")
        self.assertEqual(len(hero._hand), 1, "Should draw 1 card")

    def test_effect_with_empty_deck(self):
        """Test drawing when deck is empty shuffles discard."""
        card = Expelliarmus()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Put cards in discard pile only
        hero._discard = [DummyCard("Card in Discard")]
        hero._deck = []

        # Act: Execute effect (should trigger shuffle and draw)
        card._effect(game)

        # Assert: Card should be drawn from shuffled discard
        self.assertEqual(hero._damage_tokens, 2)
        self.assertEqual(len(hero._hand), 1, "Should draw from shuffled discard")
        self.assertEqual(len(hero._discard), 0, "Discard should be empty after shuffle")

    def test_effect_logs_correctly(self):
        """Verify that the card effect logs appropriate messages."""
        card = Expelliarmus()
        game = FakeGame()
        hero = game.heroes.active_hero
        hero._deck = [DummyCard("Card")]

        # Act: Execute effect
        card._effect(game)

        # Assert: Check log messages
        logs = game.get_logs()
        self.assertTrue(any("damage" in log for log in logs), "Should log damage gain")
        self.assertTrue(any("draws" in log for log in logs), "Should log card draw")


if __name__ == '__main__':
    unittest.main()
