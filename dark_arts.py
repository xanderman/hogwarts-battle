import random

class DarkArtsDeck(object):
    def __init__(self, window):
        self._window = window
        self._window.box()
        self._window.addstr(0, 1, "Dark Arts Deck")
        self._deck = game_one_cards
        random.shuffle(self._deck)
        self._discard = []

    def play(self, count, game):
        self._window.erase()
        self._window.box()
        self._window.addstr(0, 1, "Dark Arts Deck")
        game.log(f"Playing {count} dark arts cards")
        for i in range(count):
            card = self._draw()
            self._discard.append(card)
            self._window.move(i+1, 1)
            card.play(game, self._window)
        self._window.refresh()

    def _draw(self):
        if not self._deck:
            self._deck = self._discard
            random.shuffle(self._deck)
            self._discard = []
        return self._deck.pop()

    def reveal(self):
        card = self._draw()
        self._deck.append(card)
        return card

    def discard(self):
        self._discard.append(self._draw())


class DarkArtsCard(object):
    def __init__(self, name, description, effect):
        self.name = name
        self.description = description
        self.effect = effect

    def play(self, game, window):
        game.log(f"Playing {self.name} card: {self.description}")
        window.addstr(f"{self.name}: {self.description}")
        window.refresh()
        self.effect(game)


def lose_heart_and_no_drawing(game, hero):
    hero.remove_health(game)
    hero.disallow_drawing(game)

game_one_cards = [
    DarkArtsCard("Petrification", "ALL heroes loses 1 heart; no drawing cards", lambda game: game.all_heroes(lose_heart_and_no_drawing)),
    DarkArtsCard("Petrification", "ALL heroes loses 1 heart; no drawing cards", lambda game: game.all_heroes(lose_heart_and_no_drawing)),
    DarkArtsCard("Expulso", "Active hero loses 2 hearts", lambda game: game.active_hero.remove_health(game, 2)),
    DarkArtsCard("Expulso", "Active hero loses 2 hearts", lambda game: game.active_hero.remove_health(game, 2)),
    DarkArtsCard("Expulso", "Active hero loses 2 hearts", lambda game: game.active_hero.remove_health(game, 2)),
    DarkArtsCard("He Who Must Not Be Named", "Add 1💀 to the location", lambda game: game.locations.current.add_control(game)),
    DarkArtsCard("He Who Must Not Be Named", "Add 1💀 to the location", lambda game: game.locations.current.add_control(game)),
    DarkArtsCard("He Who Must Not Be Named", "Add 1💀 to the location", lambda game: game.locations.current.add_control(game)),
    DarkArtsCard("Flipendo", "Active hero loses 1 heart and discards a card", lambda game: game.active_hero.add(game, hearts=-1, cards=-1)),
    DarkArtsCard("Flipendo", "Active hero loses 1 heart and discards a card", lambda game: game.active_hero.add(game, hearts=-1, cards=-1)),
]
