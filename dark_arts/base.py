import curses
import random

class DarkArtsDeck(object):
    def __init__(self, window, chosen_cards):
        self._window = window
        self._init_window()
        self._pad = curses.newpad(100, 100)

        self._deck = [CARDS_BY_NAME[card_name]() for card_name in chosen_cards]
        random.shuffle(self._deck)
        self._discard = []
        self._played = []

    def _init_window(self):
        self._window.box()
        self._window.addstr(0, 1, "Dark Arts Deck")
        self._window.noutrefresh()
        beg = self._window.getbegyx()
        self._pad_start_line = beg[0] + 1
        self._pad_start_col = beg[1] + 1
        end = self._window.getmaxyx()
        self._pad_end_line = self._pad_start_line + end[0] - 3
        self._pad_end_col = self._pad_start_col + end[1] - 3

    def display_state(self, resize=False, size=None):
        if resize:
            self._window.resize(*size)
            self._window.clear()
            self._init_window()
        self._pad.clear()
        for i, card in enumerate(self._played):
            self._pad.addstr(f"{card.name}: {card.description}\n")
        self._pad.noutrefresh(0,0, self._pad_start_line,self._pad_start_col, self._pad_end_line,self._pad_end_col)

    def play_turn(self, game):
        game.log("-----Dark Arts phase-----")
        count = game.locations.current.dark_arts_count
        self._only_one_card = any(card.name == "Finite Incantatem" for card in game.heroes.active_hero._hand)
        game.log(f"Playing {count} dark arts cards")
        self.play(game, count)

    def play(self, game, count):
        if self._only_one_card:
            if len(self._played) == 0:
                game.log("Finite Incantatem: Only one dark arts card can be played!")
                count = 1
            else:
                game.log("Finite Incantatem: No more dark arts cards can be played!")
                return
        for i in range(count):
            card = self._draw()
            self._discard.append(card)
            self._played.append(card)
            card.play(game)

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

    def end_turn(self, game):
        for card in self._played:
            card._end_turn(game)
        self._played = []


CARDS_BY_NAME = {}


class DarkArtsCard(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def play(self, game):
        game.log(f"Playing {self.name} dark arts card: {self.description}")
        self._effect(game)

    def _effect(self, game):
        raise ValueError(f"Programmer Error! Forgot to implement effect for {self.name}")

    def _end_turn(self, game):
        pass
