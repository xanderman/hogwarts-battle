"""
Example test demonstrating combo/callback card testing with fakes.

Elder Wand gains 1 damage and 1 heart for each spell played. It checks
both already-played spells and registers a callback for future spells.
This test shows how to test cards with complex interaction patterns.
"""

import unittest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hogwarts.elder_wand import ElderWand
from hogwarts.expelliarmus import Expelliarmus
from hogwarts.reparo import Reparo
from hogwarts import CARDS_BY_NAME
from tests.unit.fakes import FakeGame


class TestElderWand(unittest.TestCase):
    """Test Elder Wand item using fakes."""

    def test_card_registration(self):
        """Verify card is registered correctly."""
        card = ElderWand()
        self.assertEqual(card.name, "Elder Wand")
        self.assertEqual(card.cost, 7)
        self.assertEqual(CARDS_BY_NAME['Elder Wand'], ElderWand)
        self.assertTrue(card.is_item())

    def test_with_no_spells(self):
        """Test Elder Wand when no spells have been played."""
        # Arrange: Create game with no cards in play area
        wand = ElderWand()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Verify starting state
        self.assertEqual(len(hero._play_area), 0)
        self.assertEqual(hero._damage_tokens, 0)
        self.assertEqual(hero._hearts, 10)

        # Act: Play Elder Wand
        wand._effect(game)

        # Assert: No spells played, so no immediate bonus
        self.assertEqual(hero._damage_tokens, 0, "No spells, no damage bonus")
        self.assertEqual(hero._hearts, 10, "No spells, no heart bonus")

        # But callback should be registered
        self.assertEqual(len(hero._extra_card_effects), 1, "Should register callback for future spells")

    def test_with_existing_spell(self):
        """Test Elder Wand when spells are already in play area."""
        # Arrange: Create game with spell already played
        wand = ElderWand()
        spell = Expelliarmus()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Hero needs to be below max hearts to gain hearts
        hero._hearts = 9

        # Simulate spell already in play area
        hero._play_area = [spell]

        # Act: Play Elder Wand
        wand._effect(game)

        # Assert: Should gain bonus for existing spell
        self.assertEqual(hero._damage_tokens, 1, "Should gain 1 damage for existing spell")
        self.assertEqual(hero._hearts, 10, "Should gain 1 heart for existing spell")

        # Callback should still be registered for future spells
        self.assertEqual(len(hero._extra_card_effects), 1, "Should register callback")

    def test_with_multiple_existing_spells(self):
        """Test Elder Wand with multiple spells already played."""
        # Arrange: Multiple spells in play area
        wand = ElderWand()
        spell1 = Expelliarmus()
        spell2 = Reparo()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Hero needs to be below max hearts to gain hearts
        hero._hearts = 8

        hero._play_area = [spell1, spell2]

        # Act: Play Elder Wand
        wand._effect(game)

        # Assert: Should gain bonus for each spell
        self.assertEqual(hero._damage_tokens, 2, "Should gain 1 damage per spell (2 total)")
        self.assertEqual(hero._hearts, 10, "Should gain 1 heart per spell (2 total)")

    def test_callback_triggers_on_future_spell(self):
        """Test that Elder Wand callback triggers when spells are played after it."""
        # Arrange: Play Elder Wand first, then a spell
        wand = ElderWand()
        spell = Expelliarmus()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Hero needs to be below max hearts to gain hearts
        hero._hearts = 9

        # Give hero some cards to draw (for Expelliarmus effect)
        hero._deck = [spell]

        # Act: Play Elder Wand (registers callback)
        wand._effect(game)

        # Verify no immediate bonus
        self.assertEqual(hero._damage_tokens, 0, "No spells yet")
        self.assertEqual(hero._hearts, 9, "No spells yet")

        # Now play a spell (Expelliarmus gives 2 damage + draws 1)
        # This should trigger Elder Wand's callback (adds 1 damage + 1 heart)
        hero._hand = [spell]
        hero.play_card(game, 0)

        # Assert: Should have damage from both Expelliarmus AND Elder Wand
        self.assertEqual(hero._damage_tokens, 3, "2 from spell + 1 from wand callback")
        self.assertEqual(hero._hearts, 10, "1 from wand callback")

    def test_callback_only_triggers_for_spells(self):
        """Test that Elder Wand callback ignores non-spell cards."""
        # Arrange: Play Elder Wand, then play an item (the wand itself)
        wand1 = ElderWand()
        wand2 = ElderWand()  # Playing a second wand (item, not spell)
        game = FakeGame()
        hero = game.heroes.active_hero

        # Act: Play first wand, then second wand
        wand1._effect(game)
        initial_damage = hero._damage_tokens
        initial_hearts = hero._hearts

        hero._hand = [wand2]
        hero.play_card(game, 0)

        # Assert: Second wand should NOT trigger first wand's callback
        # (both are items, not spells)
        self.assertEqual(hero._damage_tokens, initial_damage, "Items should not trigger spell callback")
        self.assertEqual(hero._hearts, initial_hearts, "Items should not trigger spell callback")

    def test_logs_correctly(self):
        """Verify Elder Wand logs appropriate messages."""
        wand = ElderWand()
        spell = Expelliarmus()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Test with existing spell
        hero._play_area = [spell]
        wand._effect(game)

        logs = game.get_logs()
        self.assertTrue(any("elder wand" in log.lower() for log in logs),
                        "Should log Elder Wand effect")
        self.assertTrue(any("already played" in log.lower() for log in logs),
                        "Should log bonus for already-played spell")


if __name__ == '__main__':
    unittest.main()
