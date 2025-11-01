"""
Test suite for Sorting Hat item card.

Sorting Hat grants influence and enables the proficiency to put acquired
Allies on top of the deck. This test demonstrates testing proficiency-granting
cards and state flag modifications.
"""

import unittest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hogwarts.sorting_hat import SortingHat
from hogwarts import CARDS_BY_NAME
from tests.unit.fakes import FakeGame


class TestSortingHat(unittest.TestCase):
    """Test Sorting Hat item using fakes."""

    def test_card_registration(self):
        """Verify card is registered correctly."""
        card = SortingHat()
        self.assertEqual(card.name, "Sorting Hat")
        self.assertEqual(card.cost, 4)
        self.assertEqual(CARDS_BY_NAME['Sorting Hat'], SortingHat)

    def test_card_is_item(self):
        """Verify card type checking."""
        card = SortingHat()
        self.assertTrue(card.is_item())
        self.assertFalse(card.is_spell())
        self.assertFalse(card.is_ally())

    def test_grants_influence(self):
        """Test Sorting Hat grants 2 influence."""
        # Arrange: Create game with hero
        card = SortingHat()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Verify starting state
        self.assertEqual(hero._influence_tokens, 0)

        # Act: Play Sorting Hat
        card._effect(game)

        # Assert: Hero gained 2 influence
        self.assertEqual(hero._influence_tokens, 2, "Should gain 2 influence")

    def test_sets_proficiency_flag(self):
        """Test Sorting Hat sets the ally proficiency flag."""
        # Arrange: Create game with hero
        card = SortingHat()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Verify starting state - proficiency starts False
        self.assertFalse(hero._can_put_allies_in_deck, "Proficiency should start False")

        # Act: Play Sorting Hat
        card._effect(game)

        # Assert: Proficiency flag is now True
        self.assertTrue(hero._can_put_allies_in_deck, "Proficiency should be True after playing")

    def test_multiple_plays_accumulate_influence(self):
        """Test playing Sorting Hat multiple times accumulates influence."""
        # Arrange: Create game with hero
        card1 = SortingHat()
        card2 = SortingHat()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Act: Play Sorting Hat twice
        card1._effect(game)
        initial_influence = hero._influence_tokens
        card2._effect(game)

        # Assert: Influence accumulated (2 + 2 = 4)
        self.assertEqual(initial_influence, 2, "First play should grant 2 influence")
        self.assertEqual(hero._influence_tokens, 4, "Second play should grant another 2 (total 4)")

    def test_multiple_plays_flag_stays_true(self):
        """Test proficiency flag stays True after multiple plays."""
        # Arrange: Create game with hero
        card1 = SortingHat()
        card2 = SortingHat()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Act: Play Sorting Hat twice
        card1._effect(game)
        self.assertTrue(hero._can_put_allies_in_deck)

        card2._effect(game)

        # Assert: Flag still True (doesn't toggle)
        self.assertTrue(hero._can_put_allies_in_deck, "Flag should stay True")

    def test_logs_correctly(self):
        """Verify Sorting Hat logs appropriate messages."""
        card = SortingHat()
        game = FakeGame()

        # Play Sorting Hat
        card._effect(game)

        logs = game.get_logs()
        # Should log influence gain
        self.assertTrue(any("influence" in log.lower() for log in logs),
                        "Should log influence gain")


if __name__ == '__main__':
    unittest.main()
