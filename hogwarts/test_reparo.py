import unittest
from unittest.mock import MagicMock

from . import CARDS_BY_NAME
from .reparo import Reparo

class TestReparo(unittest.TestCase):
    def test_reparo(self):
        reparo = Reparo()
        self.assertEqual(reparo.name, "Reparo")
        self.assertEqual(reparo.cost, 3)
        self.assertEqual(CARDS_BY_NAME['Reparo'], Reparo)

    def test_effect(self):
        reparo = Reparo()
        game = MagicMock()
        hero = MagicMock()
        game.heroes.active_hero = hero
        hero.drawing_allowed = True
        hero.add_influence = MagicMock()
        hero.draw = MagicMock()
        game.input = MagicMock(side_effect=["i", "d"])
        reparo._effect(game)
        hero.add_influence.assert_called_once_with(game, 2)
        reparo._effect(game)
        hero.draw.assert_called_once_with(game)
