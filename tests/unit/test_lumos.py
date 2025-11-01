"""
Test suite for Lumos spell card.

Lumos is a simple spell that makes ALL heroes draw one card.
This test demonstrates testing cards that affect multiple heroes using
the FakeHeroList metaprogramming pattern.
"""

import unittest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hogwarts.lumos import Lumos
from hogwarts import CARDS_BY_NAME
from tests.unit.fakes import FakeGame, DummyCard


class TestLumos(unittest.TestCase):
    """Test Lumos spell using fakes."""

    def test_card_registration(self):
        """Verify card is registered correctly."""
        card = Lumos()
        self.assertEqual(card.name, "Lumos")
        self.assertEqual(card.cost, 4)
        self.assertEqual(CARDS_BY_NAME['Lumos'], Lumos)

    def test_card_is_spell(self):
        """Verify card type checking."""
        card = Lumos()
        self.assertTrue(card.is_spell())
        self.assertFalse(card.is_ally())
        self.assertFalse(card.is_item())

    def test_single_hero_draws_card(self):
        """Test Lumos with a single hero."""
        # Arrange: Create game with one hero and cards in deck
        card = Lumos()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Put cards in deck so hero can draw
        hero._deck = [DummyCard("Card 1"), DummyCard("Card 2")]

        # Verify starting state
        self.assertEqual(len(hero._hand), 0)
        self.assertEqual(len(hero._deck), 2)

        # Act: Play Lumos
        card._effect(game)

        # Assert: Hero drew 1 card
        self.assertEqual(len(hero._hand), 1, "Hero should draw 1 card")
        self.assertEqual(len(hero._deck), 1, "Deck should have 1 less card")

    def test_multiple_heroes_all_draw(self):
        """Test Lumos makes all heroes draw cards."""
        # Arrange: Create game with 3 heroes
        card = Lumos()
        game = FakeGame(num_heroes=3)

        # Give each hero cards to draw
        for hero in [game.heroes.active_hero] + list(game.heroes.all_heroes_except_active):
            hero._deck = [DummyCard(f"Card for {hero.name}")]

        # Verify starting state
        for hero in [game.heroes.active_hero] + list(game.heroes.all_heroes_except_active):
            self.assertEqual(len(hero._hand), 0)
            self.assertEqual(len(hero._deck), 1)

        # Act: Play Lumos
        card._effect(game)

        # Assert: All heroes drew 1 card
        for hero in [game.heroes.active_hero] + list(game.heroes.all_heroes_except_active):
            self.assertEqual(len(hero._hand), 1, f"{hero.name} should draw 1 card")
            self.assertEqual(len(hero._deck), 0, f"{hero.name}'s deck should be empty")

    def test_empty_deck_triggers_shuffle(self):
        """Test Lumos triggers shuffle when deck is empty."""
        # Arrange: Hero with empty deck but cards in discard
        card = Lumos()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Empty deck, cards in discard
        hero._deck = []
        hero._discard = [DummyCard("Discard 1"), DummyCard("Discard 2"), DummyCard("Discard 3")]

        # Verify starting state
        self.assertEqual(len(hero._deck), 0)
        self.assertEqual(len(hero._discard), 3)
        self.assertEqual(len(hero._hand), 0)

        # Act: Play Lumos
        card._effect(game)

        # Assert: Discard became deck (shuffle happened), then drew 1 card
        self.assertEqual(len(hero._hand), 1, "Should draw 1 card after shuffle")
        self.assertEqual(len(hero._deck), 2, "Deck should have 2 cards (3 shuffled - 1 drawn)")
        self.assertEqual(len(hero._discard), 0, "Discard should be empty after shuffle")

    def test_drawing_disallowed_prevents_draw(self):
        """Test that heroes with drawing disallowed don't draw."""
        # Arrange: Game with 2 heroes, one has drawing blocked
        card = Lumos()
        game = FakeGame(num_heroes=2)
        hero1 = game.heroes.active_hero
        hero2 = list(game.heroes.all_heroes_except_active)[0]

        # Give both heroes cards
        hero1._deck = [DummyCard("Card 1")]
        hero2._deck = [DummyCard("Card 2")]

        # Block drawing for hero2
        hero2.disallow_drawing(game)

        # Verify starting state
        self.assertTrue(hero1.drawing_allowed)
        self.assertFalse(hero2.drawing_allowed)

        # Act: Play Lumos
        card._effect(game)

        # Assert: Only hero1 drew (hero2 was blocked)
        self.assertEqual(len(hero1._hand), 1, "Hero1 should draw")
        self.assertEqual(len(hero2._hand), 0, "Hero2 should not draw (blocked)")

    def test_logs_correctly(self):
        """Verify Lumos logs appropriate messages."""
        card = Lumos()
        game = FakeGame(num_heroes=2)

        # Give heroes cards to draw
        for hero in [game.heroes.active_hero] + list(game.heroes.all_heroes_except_active):
            hero._deck = [DummyCard("Card")]

        # Play Lumos
        card._effect(game)

        logs = game.get_logs()
        # Each hero should log drawing a card
        self.assertTrue(len(logs) >= 2, "Should have logs for both heroes drawing")


if __name__ == '__main__':
    unittest.main()
