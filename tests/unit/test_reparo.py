"""
Test Reparo card using test fakes.

Reparo allows the player to choose between gaining 2 influence or drawing a card.
This test demonstrates how to use pre-programmed inputs to test different choices.
"""

import unittest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hogwarts.reparo import Reparo
from hogwarts import CARDS_BY_NAME
from tests.unit.fakes import FakeGame, DummyCard


class TestReparo(unittest.TestCase):
    """Test Reparo spell using test fakes."""

    def test_card_registration(self):
        """Verify card is registered correctly."""
        card = Reparo()
        self.assertEqual(card.name, "Reparo")
        self.assertEqual(card.cost, 3)
        self.assertEqual(CARDS_BY_NAME['Reparo'], Reparo)

    def test_card_is_spell(self):
        """Verify card type checking."""
        card = Reparo()
        self.assertTrue(card.is_spell())
        self.assertFalse(card.is_ally())
        self.assertFalse(card.is_item())

    def test_choose_influence(self):
        """Test choosing influence option."""
        # Arrange: Create game with pre-programmed input
        card = Reparo()
        game = FakeGame(inputs=['i'])  # Choose influence
        hero = game.heroes.active_hero

        # Verify starting state
        self.assertEqual(hero._influence_tokens, 0)

        # Act: Execute card effect
        card._effect(game)

        # Assert: Should gain 2 influence
        self.assertEqual(hero._influence_tokens, 2, "Should gain 2 influence when 'i' chosen")
        self.assertEqual(len(hero._hand), 0, "Should not draw cards")

    def test_choose_draw(self):
        """Test choosing draw option."""
        # Arrange: Create game with pre-programmed input
        card = Reparo()
        game = FakeGame(inputs=['d'])  # Choose draw
        hero = game.heroes.active_hero

        # Put a card in deck to draw
        hero._deck = [DummyCard("Card to Draw")]

        # Act: Execute card effect
        card._effect(game)

        # Assert: Should draw 1 card
        self.assertEqual(hero._influence_tokens, 0, "Should not gain influence")
        self.assertEqual(len(hero._hand), 1, "Should draw 1 card when 'd' chosen")

    def test_multiple_uses(self):
        """Test playing Reparo multiple times with different choices."""
        # Arrange: Create game with multiple inputs
        card = Reparo()
        game = FakeGame(inputs=['i', 'd'])  # First influence, then draw
        hero = game.heroes.active_hero
        hero._deck = [DummyCard("Card 1"), DummyCard("Card 2")]

        # Act: Execute effect twice
        card._effect(game)
        self.assertEqual(hero._influence_tokens, 2, "First use: gain influence")
        self.assertEqual(len(hero._hand), 0, "First use: no draw")

        card._effect(game)
        self.assertEqual(hero._influence_tokens, 2, "Second use: no more influence")
        self.assertEqual(len(hero._hand), 1, "Second use: draw card")

    def test_drawing_not_allowed(self):
        """Test that when drawing is disallowed, influence is gained automatically."""
        # Arrange: Create game and disable drawing
        card = Reparo()
        game = FakeGame()
        hero = game.heroes.active_hero
        hero.disallow_drawing(game)

        # No input needed - should auto-choose influence
        # Act: Execute card effect
        card._effect(game)

        # Assert: Should gain influence without asking for input
        self.assertEqual(hero._influence_tokens, 2, "Should auto-gain influence when drawing disallowed")
        self.assertFalse(hero.drawing_allowed, "Drawing should still be disallowed")

    def test_logs_choice(self):
        """Verify appropriate logging for each choice."""
        # Test influence choice logging
        card = Reparo()
        game = FakeGame(inputs=['i'])
        hero = game.heroes.active_hero

        card._effect(game)
        logs = game.get_logs()
        self.assertTrue(any("influence" in log for log in logs), "Should log influence gain")

        # Test draw choice logging
        game = FakeGame(inputs=['d'])
        hero = game.heroes.active_hero
        hero._deck = [DummyCard("Card")]

        card._effect(game)
        logs = game.get_logs()
        self.assertTrue(any("draws" in log for log in logs), "Should log card draw")


if __name__ == '__main__':
    unittest.main()
