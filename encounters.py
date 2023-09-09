from collections import Counter

import curses

import hogwarts

# In game 7 these are Horcurxes, but in the expansions the concept is generalized into Encounters.
class EncountersDeck(object):
    def __init__(self, window, game_num):
        if game_num < 7:
            raise ValueError("Progammer Error! Encounters deck only exists in games 7+")
        self._game_num = game_num
        self._window = window
        self._init_window()
        self._pad = curses.newpad(100, 100)

        # TODO: randomize encounters for "replay" game
        self._deck = CARDS[game_num]
        self._current = self._deck.pop(0)

    def _init_window(self):
        self._window.box()
        self._window.addstr(0, 1, self._title)
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
        self._window.clear()
        self._window.box()
        self._window.addstr(0, 1, f"{self._title} ({len(self._deck)} left)")
        self._window.noutrefresh()
        self._pad.clear()
        self.current.display_state(self._pad)
        self._pad.noutrefresh(0,0, self._pad_start_line,self._pad_start_col, self._pad_end_line,self._pad_end_col)

    @property
    def _title(self):
        return "Horcruxes" if self._game_num == 7 else "Encounters"

    @property
    def current(self):
        return self._current

    @property
    def all_copmlete(self):
        return len(self._deck) == 0 and type(self._current) == NullEncounter

    def play_turn(self, game):
        game.log(f"-----{self._title} phase-----")
        game.log(str(self._current))
        self._current.effect(game)

    def check_completion(self, game):
        if not self._current.completed:
            return
        self._current.on_complete(game)
        game.heroes.active_hero.add_encounter(game, self._current)
        self._current = self._deck.pop(0) if len(self._deck) > 0 else NullEncounter(self._game_num)


class Encounter(object):
    def __init__(self, name, description, reward_str, required_villains):
        self.name = name
        self.description = description
        self.required_villains = required_villains
        self.reward_str = reward_str
        self.completed = False
        self._complete_str = "complete"

    def __str__(self):
        if self.completed:
            return f"{self.name}: {self.reward_str}"
        return f"{self.name}: {self.description}"

    def display_state(self, window):
        window.addstr(f"{self.name}\n", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f"{self.description}\n")
        window.addstr(f"To {self._complete_str}: ")
        self._display_to_complete(window)
        window.addstr(f"\nReward: {self.reward_str}\n")

    def _display_to_complete(self, window):
        raise ValueError(f"Programmer Error! Forgot to implement _display_to_complete for {self.name}")

    def die_roll_applies(self, game, result):
        return False

    def apply_die_roll(self, game, result):
        raise ValueError(f"Programmer Error! Die roll should not apply to {self.name}")

    def on_complete(self, game):
        pass

    def effect(self, game):
        raise ValueError(f"Programmer Error! Forgot to implement effect for {self.name}")

    def reward_effect(self, game):
        raise ValueError(f"Programmer Error! Forgot to implement reward_effect for {self.name}")


class NullEncounter(Encounter):
    def __init__(self, game_num):
        super().__init__("NullEncounter", "No encounter", "No reward", [])
        self._game_num = game_num
        self.completed = False

    def __str__(self):
        return "Nothing to see here"

    def display_state(self, window):
        if self._game_num == 7:
            window.addstr("All horcruxes destroyed!\n", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr("All encounters completed!\n", curses.A_BOLD | curses.color_pair(1))

    def effect(self, game):
        pass


class Horcrux(Encounter):
    def __init__(self, name, description, reward_str):
        super().__init__(name, description, reward_str, [])
        self._complete_str = "destroy"


class Diary(Horcrux):
    def __init__(self):
        super().__init__("Diary", "Each time a hero plays an ally, lose 1💜", "If you play 2 allies, one hero gains 2💜")

    def _display_to_complete(self, window):
        window.addstr("roll 💜 or 🃏")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        return (result == "💜" or result == "🃏") and not self.completed

    def apply_die_roll(self, game, result):
        if not (result == "💜" or result == "🃏"):
            raise ValueError("Programmer Error! Diary only applies to 💜 or 🃏")
        self.completed = True

    def effect(self, game):
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if card.is_ally():
            game.log(f"{self.name}: Ally {card.name} played, {game.heroes.active_hero.name} loses 1💜")
            game.heroes.active_hero.remove_health(game)

    def reward_effect(self, game):
        self._allies_played = 0
        self._used_ability = False
        game.heroes.active_hero.add_extra_card_effect(game, self.__reward_extra_effect)

    def __reward_extra_effect(self, game, card):
        if card.is_ally():
            self._allies_played += 1
        if self._allies_played >= 2 and not self._used_ability:
            self._used_ability = True
            hero = game.heroes.active_hero
            game.heroes.choose_hero(
                    game, prompt=f"{self.name}: {hero.name} played 2 allies, choose hero to gain 2💜: ").add_health(game, 2)

class Ring(Horcrux):
    def __init__(self):
        super().__init__("Ring", "If you assign 2↯ to a villain, lose 2💜", "1/turn: discard two cards to remove 1💀")

    def _display_to_complete(self, window):
        window.addstr("roll ↯ or 💰")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        return (result == "↯" or result == "💰") and not self.completed

    def apply_die_roll(self, game, result):
        if not (result == "↯" or result == "💰"):
            raise ValueError("Programmer Error! Ring only applies to ↯ or 💰")
        self.completed = True

    def effect(self, game):
        self._damaged_villains = Counter()
        self._used_ability = set()
        game.heroes.active_hero.add_extra_damage_effect(game, self.__extra_effect)

    def __extra_effect(self, game, villain, damage):
        self._damaged_villains[villain] += damage
        if self._damaged_villains[villain] >= 2 and villain not in self._used_ability:
            self._used_ability.add(villain)
            game.log(f"{self.name}: {game.heroes.active_hero.name} assigned 2↯ to {villain.name}, loses 2💜")
            game.heroes.active_hero.remove_health(game, 2)

    def reward_effect(self, game):
        self._used_ability = False
        game.heroes.active_hero.add_action(game, 'R', "(R)ing", self.__reward_action)

    def __reward_action(self, game):
        if self._used_ability:
            game.log(f"{self.name} already used this turn")
            return

        hero = game.heroes.active_hero
        if len(hero._hand) < 2:
            game.log(f"Not enough cards in hand to use {self.name}")
            return

        choices = ['c'] + [str(i) for i in range(len(hero._hand))]
        first = game.input(f"Choose first card for {hero.name} to discard or (c)ancel: ", choices)
        if first == 'c':
            return
        first = int(first)
        while True:
            second = game.input(f"Choose second card for {hero.name} to discard or (c)ancel: ", choices)
            if second == 'c':
                return
            second = int(second)
            if second == first:
                game.log("Cannot discard the same card twice")
                continue
            break
        if second > first:
            # Account for hand shrinking after first discard
            second -= 1
        hero.discard(game, first, with_callbacks=False)
        hero.discard(game, second, with_callbacks=False)
        game.locations.remove_control(game)
        self._used_ability = True


class Locket(Horcrux):
    def __init__(self):
        super().__init__("Locket", "Heroes cannot gain ↯ or 💰 on other heroes' turns", "1/turn: discard a card to roll the Slytherin die")
        self._got_damage = False
        self._got_heart = False

    def _display_to_complete(self, window):
        window.addstr("roll ↯")
        if self._got_damage:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(" and 💜")
        if self._got_heart:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        return ((result == "↯" and not self._got_damage) or
                (result == "💜" and not self._got_heart)) and not self.completed

    def apply_die_roll(self, game, result):
        if result == "↯":
            self._got_damage = True
        elif result == "💜":
            self._got_heart = True
        else:
            raise ValueError("Programmer Error! Locket only applies to ↯ or 💜")
        if self._got_damage and self._got_heart:
            self.completed = True

    def effect(self, game):
        game.heroes.all_heroes.disallow_gaining_tokens_out_of_turn(game)

    def on_complete(self, game):
        game.heroes.all_heroes.allow_gaining_tokens_out_of_turn(game)

    def reward_effect(self, game):
        self._used_ability = False
        game.heroes.active_hero.add_action(game, 'L', "(L)ocket", self.__reward_action)

    def __reward_action(self, game):
        if self._used_ability:
            game.log(f"{self.name} already used this turn")
            return

        hero = game.heroes.active_hero
        if len(hero._hand) < 1:
            game.log(f"Not enough cards in hand to use {self.name}")
            return

        choices = ['c'] + [str(i) for i in range(len(hero._hand))]
        choice = game.input(f"Choose card for {hero.name} to discard or (c)ancel: ", choices)
        if choice == 'c':
            return
        hero.discard(game, int(choice), with_callbacks=False)
        game.roll_slytherin_die()
        self._used_ability = True


class Cup(Horcrux):
    def __init__(self):
        super().__init__("Cup", "Remove 1↯ from all villains", "1/turn: discard a card to roll the Hufflepuff die")
        self._got_heart = False
        self._got_influence = False

    def _display_to_complete(self, window):
        window.addstr("roll 💜")
        if self._got_heart:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(" and 💰")
        if self._got_influence:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        return ((result == "💜" and not self._got_heart) or
                (result == "💰" and not self._got_influence)) and not self.completed

    def apply_die_roll(self, game, result):
        if result == "💜":
            self._got_heart = True
        elif result == "💰":
            self._got_influence = True
        else:
            raise ValueError("Programmer Error! Cup only applies to 💜 or 💰")
        if self._got_heart and self._got_influence:
            self.completed = True

    def effect(self, game):
        game.villain_deck.all_villains.remove_damage(game, 1)

    def reward_effect(self, game):
        self._used_ability = False
        game.heroes.active_hero.add_action(game, 'C', "(C)up", self.__reward_action)

    def __reward_action(self, game):
        if self._used_ability:
            game.log(f"{self.name} already used this turn")
            return

        hero = game.heroes.active_hero
        if len(hero._hand) < 1:
            game.log(f"Not enough cards in hand to use {self.name}")
            return

        choices = ['c'] + [str(i) for i in range(len(hero._hand))]
        choice = game.input(f"Choose card for {hero.name} to discard or (c)ancel: ", choices)
        if choice == 'c':
            return
        hero.discard(game, int(choice), with_callbacks=False)
        game.roll_hufflepuff_die()
        self._used_ability = True


class Diadem(Horcrux):
    def __init__(self):
        super().__init__("Diadem", "If the active hero has one ally, item, and spell, lose 2💜", "1/turn: discard a card to roll the Ravenclaw die")
        self._got_card = False
        self._got_damage = False

    def _display_to_complete(self, window):
        window.addstr("roll 🃏")
        if self._got_card:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(" and ↯")
        if self._got_damage:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        return ((result == "🃏" and not self._got_card) or
                (result == "↯" and not self._got_damage)) and not self.completed

    def apply_die_roll(self, game, result):
        if result == "🃏":
            self._got_card = True
        elif result == "↯":
            self._got_damage = True
        else:
            raise ValueError("Programmer Error! Diadem only applies to 🃏 or ↯")
        if self._got_card and self._got_damage:
            self.completed = True

    def effect(self, game):
        hero = game.heroes.active_hero
        types_in_hand = set(type(card) for card in hero._hand)
        if types_in_hand.issuperset(set([hogwarts.Ally, hogwarts.Item, hogwarts.Spell])):
            game.log(f"{self.name}: {hero.name} has one ally, item, and spell; loses 2💜")
            hero.remove_health(game, 2)

    def reward_effect(self, game):
        self._used_ability = False
        game.heroes.active_hero.add_action(game, 'D', "(D)iadem", self.__reward_action)

    def __reward_action(self, game):
        if self._used_ability:
            game.log(f"{self.name} already used this turn")
            return

        hero = game.heroes.active_hero
        if len(hero._hand) < 1:
            game.log(f"Not enough cards in hand to use {self.name}")
            return

        choices = ['c'] + [str(i) for i in range(len(hero._hand))]
        choice = game.input(f"Choose card for {hero.name} to discard or (c)ancel: ", choices)
        if choice == 'c':
            return
        hero.discard(game, int(choice), with_callbacks=False)
        game.roll_ravenclaw_die()
        self._used_ability = True


class Nagini(Horcrux):
    def __init__(self):
        super().__init__("Nagini", "Active hero loses 1💜 and cannot gain 💜", "1/game: discard this to remove 3💀")
        self._got_damage = False
        self._got_card = False
        self._got_heart = False

    def _display_to_complete(self, window):
        window.addstr("roll ↯")
        if self._got_damage:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(" and 🃏")
        if self._got_card:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(" and 💜")
        if self._got_heart:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        return ((result == "↯" and not self._got_damage) or
                (result == "🃏" and not self._got_card) or
                (result == "💜" and not self._got_heart)) and not self.completed

    def apply_die_roll(self, game, result):
        if result == "↯":
            self._got_damage = True
        elif result == "🃏":
            self._got_card = True
        elif result == "💜":
            self._got_heart = True
        else:
            raise ValueError("Programmer Error! Nagini only applies to ↯ or 🃏 or 💜")
        if self._got_damage and self._got_card and self._got_heart:
            self.completed = True

    def effect(self, game):
        game.heroes.active_hero.remove_health(game)
        game.heroes.active_hero.disallow_healing(game)

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'N', "(N)agini", self.__reward_action)

    def __reward_action(self, game):
        game.log(f"{self.name} discarded to remove 3💀")
        game.heroes.active_hero._encounters.remove(self)
        game.locations.remove_control(game, 3)


game_seven_horcruxes = [
    Diary(),
    Ring(),
    Locket(),
    Cup(),
    Diadem(),
    Nagini(),
]

CARDS = [
    -1, -1, -1, -1, -1, -1, -1,
    game_seven_horcruxes,
]
