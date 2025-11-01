"""
Test suite for Stupefy spell card.

Stupefy is a complex spell with multiple effects: grants damage and draws a card
for the active hero, then removes a control token from the location.
This test demonstrates testing multi-effect cards and control token mechanics.
"""

import unittest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hogwarts.stupefy import Stupefy
from hogwarts import CARDS_BY_NAME
from tests.unit.fakes import FakeGame, DummyCard


class TestStupefy(unittest.TestCase):
    """Test Stupefy spell using fakes."""

    def test_card_registration(self):
        """Verify card is registered correctly."""
        card = Stupefy()
        self.assertEqual(card.name, "Stupefy")
        self.assertEqual(card.cost, 6)
        self.assertEqual(CARDS_BY_NAME['Stupefy'], Stupefy)

    def test_card_is_spell(self):
        """Verify card type checking."""
        card = Stupefy()
        self.assertTrue(card.is_spell())
        self.assertFalse(card.is_ally())
        self.assertFalse(card.is_item())

    def test_basic_effect(self):
        """Test Stupefy grants damage, draws card, and removes control."""
        # Arrange: Create game with hero, cards in deck, and control tokens
        card = Stupefy()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Give hero cards to draw
        hero._deck = [DummyCard("Card 1"), DummyCard("Card 2")]

        # Add control tokens to location
        game.locations.add_control(game)
        game.locations.add_control(game)

        # Verify starting state
        self.assertEqual(hero._damage_tokens, 0)
        self.assertEqual(len(hero._hand), 0)
        self.assertEqual(game.locations._control_tokens, 2)

        # Act: Play Stupefy
        card._effect(game)

        # Assert: Hero gained damage and drew, control removed
        self.assertEqual(hero._damage_tokens, 1, "Should gain 1 damage")
        self.assertEqual(len(hero._hand), 1, "Should draw 1 card")
        self.assertEqual(game.locations._control_tokens, 1, "Should remove 1 control token")

    def test_with_cards_in_deck(self):
        """Test Stupefy when hero has cards in deck."""
        # Arrange
        card = Stupefy()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Put multiple cards in deck
        hero._deck = [DummyCard("Card 1"), DummyCard("Card 2"), DummyCard("Card 3")]

        # Add control tokens
        game.locations.add_control(game)

        # Act: Play Stupefy
        card._effect(game)

        # Assert: Drew exactly 1 card
        self.assertEqual(len(hero._hand), 1, "Should draw exactly 1 card")
        self.assertEqual(len(hero._deck), 2, "Should have 2 cards left in deck")

    def test_empty_deck_triggers_shuffle(self):
        """Test Stupefy triggers shuffle when deck is empty."""
        # Arrange: Hero with empty deck but cards in discard
        card = Stupefy()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Empty deck, cards in discard
        hero._deck = []
        hero._discard = [DummyCard("Discard 1"), DummyCard("Discard 2")]

        # Add control tokens
        game.locations.add_control(game)

        # Verify starting state
        self.assertEqual(len(hero._deck), 0)
        self.assertEqual(len(hero._discard), 2)

        # Act: Play Stupefy
        card._effect(game)

        # Assert: Shuffle happened, then drew 1 card
        self.assertEqual(len(hero._hand), 1, "Should draw 1 card after shuffle")
        self.assertEqual(len(hero._deck), 1, "Deck should have 1 card (2 shuffled - 1 drawn)")
        self.assertEqual(len(hero._discard), 0, "Discard should be empty after shuffle")

    def test_no_control_tokens_to_remove(self):
        """Test Stupefy when there are no control tokens."""
        # Arrange: Game with no control tokens
        card = Stupefy()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Give hero cards to draw
        hero._deck = [DummyCard("Card 1")]

        # Verify no control tokens
        self.assertEqual(game.locations._control_tokens, 0)

        # Act: Play Stupefy
        card._effect(game)

        # Assert: Damage and draw still work, control tokens don't go negative
        self.assertEqual(hero._damage_tokens, 1, "Should gain damage")
        self.assertEqual(len(hero._hand), 1, "Should draw card")
        self.assertEqual(game.locations._control_tokens, 0, "Control tokens should not go negative")

    def test_control_removal_disabled(self):
        """Test Stupefy when control removal is disabled."""
        # Arrange: Game with control tokens but removal disabled
        card = Stupefy()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Give hero cards to draw
        hero._deck = [DummyCard("Card 1")]

        # Add control tokens but disable removal
        game.locations.add_control(game)
        game.locations.add_control(game)
        game.locations.can_remove_control = False

        # Verify starting state
        self.assertEqual(game.locations._control_tokens, 2)

        # Act: Play Stupefy
        card._effect(game)

        # Assert: Damage and draw work, but control not removed
        self.assertEqual(hero._damage_tokens, 1, "Should gain damage")
        self.assertEqual(len(hero._hand), 1, "Should draw card")
        self.assertEqual(game.locations._control_tokens, 2, "Control should not be removed (disabled)")

    def test_logs_all_effects(self):
        """Verify Stupefy logs messages for all effects."""
        card = Stupefy()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Give hero cards and add control tokens
        hero._deck = [DummyCard("Card 1")]
        game.locations.add_control(game)

        # Play Stupefy
        card._effect(game)

        logs = game.get_logs()
        # Should log damage gain
        self.assertTrue(any("damage" in log.lower() for log in logs),
                        "Should log damage gain")
        # Should log card draw (or related message)
        self.assertTrue(any("draw" in log.lower() or "card" in log.lower() for log in logs),
                        "Should log card draw")
        # Should log control token removal
        self.assertTrue(any("control" in log.lower() for log in logs),
                        "Should log control token removal")


if __name__ == '__main__':
    unittest.main()
