"""
Test suite for Chocolate Frog item card.

Chocolate Frog allows choosing a hero to gain influence and hearts.
It also has a discard effect that grants the same benefits.
This test demonstrates testing hero selection mechanics and discard callbacks.
"""

import unittest
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hogwarts.chocolate_frog import ChocolateFrog
from hogwarts import CARDS_BY_NAME
from tests.unit.fakes import FakeGame


class TestChocolateFrog(unittest.TestCase):
    """Test Chocolate Frog item using fakes."""

    def test_card_registration(self):
        """Verify card is registered correctly."""
        card = ChocolateFrog()
        self.assertEqual(card.name, "Chocolate Frog")
        self.assertEqual(card.cost, 2)
        self.assertEqual(CARDS_BY_NAME['Chocolate Frog'], ChocolateFrog)

    def test_card_is_item(self):
        """Verify card type checking."""
        card = ChocolateFrog()
        self.assertTrue(card.is_item())
        self.assertFalse(card.is_spell())
        self.assertFalse(card.is_ally())

    def test_single_hero_gets_benefits(self):
        """Test Chocolate Frog with a single hero (no choice needed)."""
        # Arrange: Create game with one hero below max hearts
        card = ChocolateFrog()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Set hero below max hearts so they can gain
        hero._hearts = 9
        hero._max_hearts = 10

        # Verify starting state
        self.assertEqual(hero._influence_tokens, 0)
        self.assertEqual(hero._hearts, 9)

        # Act: Play Chocolate Frog (auto-selects only hero)
        card._effect(game)

        # Assert: Hero gained influence and hearts
        self.assertEqual(hero._influence_tokens, 1, "Hero should gain 1 influence")
        self.assertEqual(hero._hearts, 10, "Hero should gain 1 heart")

    def test_multiple_heroes_with_choice(self):
        """Test Chocolate Frog with multiple heroes - choice is made."""
        # Arrange: Create game with 3 heroes
        # Note: FakeHeroes.choose_hero() returns first hero deterministically,
        # not based on game.input(). This test verifies the chosen hero logic.
        card = ChocolateFrog()
        game = FakeGame(num_heroes=3)
        hero1 = game.heroes.active_hero
        other_heroes = list(game.heroes.all_heroes_except_active)

        # Set all heroes below max hearts
        for hero in [hero1] + other_heroes:
            hero._hearts = 8
            hero._max_hearts = 10

        # Act: Play Chocolate Frog (choose_hero returns hero1)
        card._effect(game)

        # Assert: hero1 gained benefits (chosen by choose_hero)
        self.assertEqual(hero1._influence_tokens, 1, "Chosen hero should gain influence")
        self.assertEqual(hero1._hearts, 9, "Chosen hero should gain heart")

        # Other heroes should not have gained anything
        for hero in other_heroes:
            self.assertEqual(hero._influence_tokens, 0, f"{hero.name} should not gain influence")
            self.assertEqual(hero._hearts, 8, f"{hero.name} should not gain hearts")

    def test_chosen_hero_at_max_hearts(self):
        """Test Chocolate Frog when chosen hero is at max hearts."""
        # Arrange: Single hero at max hearts
        card = ChocolateFrog()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Set hero at max hearts
        hero._hearts = 10
        hero._max_hearts = 10

        # Act: Play Chocolate Frog
        card._effect(game)

        # Assert: Hero gained influence but not hearts (already at max)
        self.assertEqual(hero._influence_tokens, 1, "Hero should gain influence")
        self.assertEqual(hero._hearts, 10, "Hero should stay at max hearts")

    def test_chosen_hero_healing_disallowed(self):
        """Test Chocolate Frog when chosen hero has healing blocked."""
        # Arrange: Single hero with healing disallowed
        card = ChocolateFrog()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Set hero below max but block healing
        hero._hearts = 8
        hero._max_hearts = 10
        hero.disallow_healing(game)

        # Verify healing is blocked
        self.assertFalse(hero.healing_allowed)

        # Act: Play Chocolate Frog
        card._effect(game)

        # Assert: Hero gained influence but not hearts (healing blocked)
        self.assertEqual(hero._influence_tokens, 1, "Hero should gain influence")
        self.assertEqual(hero._hearts, 8, "Hero should not gain hearts (healing blocked)")

    def test_discard_effect_grants_benefits(self):
        """Test Chocolate Frog's discard effect."""
        # Arrange: Create card and hero
        card = ChocolateFrog()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Set hero below max hearts
        hero._hearts = 9
        hero._max_hearts = 10

        # Verify starting state
        self.assertEqual(hero._influence_tokens, 0)
        self.assertEqual(hero._hearts, 9)

        # Act: Call discard_effect directly
        card.discard_effect(game, hero)

        # Assert: Hero gained influence and hearts
        self.assertEqual(hero._influence_tokens, 1, "Hero should gain 1 influence from discard")
        self.assertEqual(hero._hearts, 10, "Hero should gain 1 heart from discard")

    def test_discard_effect_at_max_hearts(self):
        """Test Chocolate Frog's discard effect when hero at max hearts."""
        # Arrange: Create card and hero at max hearts
        card = ChocolateFrog()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Set hero at max hearts
        hero._hearts = 10
        hero._max_hearts = 10

        # Act: Call discard_effect directly
        card.discard_effect(game, hero)

        # Assert: Hero gained influence but not hearts
        self.assertEqual(hero._influence_tokens, 1, "Hero should gain influence from discard")
        self.assertEqual(hero._hearts, 10, "Hero should stay at max hearts")

    def test_discard_effect_healing_disallowed(self):
        """Test Chocolate Frog's discard effect when healing is disallowed."""
        # Arrange: Create card and hero with healing blocked
        card = ChocolateFrog()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Set hero below max but block healing
        hero._hearts = 8
        hero._max_hearts = 10
        hero.disallow_healing(game)

        # Verify healing is blocked
        self.assertFalse(hero.healing_allowed)

        # Act: Call discard_effect directly
        card.discard_effect(game, hero)

        # Assert: Hero gained influence but not hearts (healing blocked)
        self.assertEqual(hero._influence_tokens, 1, "Hero should gain influence from discard")
        self.assertEqual(hero._hearts, 8, "Hero should not gain hearts (healing blocked)")

    def test_logs_correctly(self):
        """Verify Chocolate Frog logs appropriate messages."""
        card = ChocolateFrog()
        game = FakeGame()
        hero = game.heroes.active_hero

        # Set hero below max
        hero._hearts = 8

        # Play Chocolate Frog
        card._effect(game)

        logs = game.get_logs()
        # Should log influence gain
        self.assertTrue(any("influence" in log.lower() for log in logs),
                        "Should log influence gain")
        # Should log heart gain
        self.assertTrue(any("heart" in log.lower() for log in logs),
                        "Should log heart gain")


if __name__ == '__main__':
    unittest.main()
