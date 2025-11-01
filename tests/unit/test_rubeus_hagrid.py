"""
Test suite for Rubeus Hagrid ally card.

Rubeus Hagrid grants damage to the active hero and hearts to ALL heroes.
This test demonstrates testing cards with mixed targeting (specific hero vs all heroes)
and edge cases around heart gain limitations.
"""

import unittest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hogwarts.rubeus_hagrid import RubeusHagrid
from hogwarts import CARDS_BY_NAME
from tests.unit.fakes import FakeGame


class TestRubeusHagrid(unittest.TestCase):
    """Test Rubeus Hagrid ally using fakes."""

    def test_card_registration(self):
        """Verify card is registered correctly."""
        card = RubeusHagrid()
        self.assertEqual(card.name, "Rubeus Hagrid")
        self.assertEqual(card.cost, 4)
        self.assertEqual(CARDS_BY_NAME['Rubeus Hagrid'], RubeusHagrid)

    def test_card_is_ally(self):
        """Verify card type checking."""
        card = RubeusHagrid()
        self.assertTrue(card.is_ally())
        self.assertFalse(card.is_spell())
        self.assertFalse(card.is_item())

    def test_single_hero_gains_damage_and_hearts(self):
        """Test Rubeus Hagrid with a single hero."""
        # Arrange: Create game with one hero below max hearts
        card = RubeusHagrid()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Set hero below max hearts so they can gain
        hero._hearts = 9
        hero._max_hearts = 10

        # Verify starting state
        self.assertEqual(hero._damage_tokens, 0)
        self.assertEqual(hero._hearts, 9)

        # Act: Play Rubeus Hagrid
        card._effect(game)

        # Assert: Hero gained 1 damage and 1 heart
        self.assertEqual(hero._damage_tokens, 1, "Active hero should gain 1 damage")
        self.assertEqual(hero._hearts, 10, "Hero should gain 1 heart")

    def test_multiple_heroes_active_gets_damage_all_get_hearts(self):
        """Test Rubeus Hagrid with multiple heroes - active gets damage, all get hearts."""
        # Arrange: Create game with 3 heroes
        card = RubeusHagrid()
        game = FakeGame(num_heroes=3)
        hero1 = game.heroes.active_hero
        other_heroes = list(game.heroes.all_heroes_except_active)

        # Set all heroes below max hearts so they can gain
        for hero in [hero1] + other_heroes:
            hero._hearts = 8
            hero._max_hearts = 10

        # Verify starting state
        self.assertEqual(hero1._damage_tokens, 0)
        for hero in other_heroes:
            self.assertEqual(hero._damage_tokens, 0)

        # Act: Play Rubeus Hagrid
        card._effect(game)

        # Assert: Only active hero got damage, all heroes got hearts
        self.assertEqual(hero1._damage_tokens, 1, "Active hero should gain damage")
        for hero in other_heroes:
            self.assertEqual(hero._damage_tokens, 0, "Non-active heroes should not gain damage")

        # All heroes should have gained 1 heart (8 -> 9)
        for hero in [hero1] + other_heroes:
            self.assertEqual(hero._hearts, 9, f"{hero.name} should gain 1 heart")

    def test_hero_at_max_hearts_cannot_gain(self):
        """Test that heroes at max hearts don't gain hearts."""
        # Arrange: Create game with 2 heroes, one at max hearts
        card = RubeusHagrid()
        game = FakeGame(num_heroes=2)
        hero1 = game.heroes.active_hero
        hero2 = list(game.heroes.all_heroes_except_active)[0]

        # Hero1 below max, hero2 at max
        hero1._hearts = 9
        hero1._max_hearts = 10
        hero2._hearts = 10
        hero2._max_hearts = 10

        # Act: Play Rubeus Hagrid
        card._effect(game)

        # Assert: Hero1 gained heart, hero2 did not
        self.assertEqual(hero1._hearts, 10, "Hero below max should gain heart")
        self.assertEqual(hero2._hearts, 10, "Hero at max should not gain heart")

    def test_healing_disallowed_prevents_heart_gain(self):
        """Test that heroes with healing disallowed don't gain hearts."""
        # Arrange: Create game with 2 heroes, one has healing blocked
        card = RubeusHagrid()
        game = FakeGame(num_heroes=2)
        hero1 = game.heroes.active_hero
        hero2 = list(game.heroes.all_heroes_except_active)[0]

        # Both heroes below max hearts
        hero1._hearts = 8
        hero2._hearts = 8

        # Block healing for hero2
        hero2.disallow_healing(game)

        # Verify starting state
        self.assertTrue(hero1.healing_allowed)
        self.assertFalse(hero2.healing_allowed)

        # Act: Play Rubeus Hagrid
        card._effect(game)

        # Assert: Only hero1 gained hearts (hero2 was blocked)
        self.assertEqual(hero1._hearts, 9, "Hero1 should gain heart")
        self.assertEqual(hero2._hearts, 8, "Hero2 should not gain heart (healing blocked)")

    def test_hero_below_max_can_gain_hearts(self):
        """Test that hero significantly below max hearts can gain."""
        # Arrange: Create game with hero at low hearts
        card = RubeusHagrid()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Set hero well below max
        hero._hearts = 5
        hero._max_hearts = 10

        # Act: Play Rubeus Hagrid
        card._effect(game)

        # Assert: Hero gained 1 heart
        self.assertEqual(hero._hearts, 6, "Hero should gain 1 heart (5 -> 6)")

    def test_logs_correctly(self):
        """Verify Rubeus Hagrid logs appropriate messages."""
        card = RubeusHagrid()
        game = FakeGame(num_heroes=2)

        # Set heroes below max so they can gain
        for hero in [game.heroes.active_hero] + list(game.heroes.all_heroes_except_active):
            hero._hearts = 8

        # Play Rubeus Hagrid
        card._effect(game)

        logs = game.get_logs()
        # Should log damage for active hero
        self.assertTrue(any("damage" in log.lower() for log in logs),
                        "Should log damage gain")
        # Should log hearts for heroes
        self.assertTrue(any("heart" in log.lower() for log in logs),
                        "Should log heart gain")


if __name__ == '__main__':
    unittest.main()
