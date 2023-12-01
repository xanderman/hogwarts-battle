from collections import Counter
from functools import reduce

import curses
import operator

import constants
import hogwarts

# In game 7 these are Horcurxes, but in the expansions the concept is generalized into Encounters.
class EncountersDeck(object):
    def __init__(self, window, game_num):
        self._game_num = game_num
        self._window = window
        self._init_window()
        self._pad = curses.newpad(100, 100)

        self._deck = build_deck(game_num)
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

    def required_villains(self):
        return reduce(operator.add, [encounter.required_villains for encounter in self._deck])

    @property
    def _title(self):
        return "Horcruxes" if self._game_num == 7 else "Encounters"

    @property
    def current(self):
        return self._current

    @property
    def all_complete(self):
        if len(self._deck) > 0:
            return False
        return type(self._current) == NullEncounter or self._current.completed

    def play_turn(self, game):
        game.log(f"-----{self._title} phase-----")
        game.log(str(self._current))
        self._current.effect(game)

    def check_completion(self, game):
        if not self._current.completed:
            return
        game.heroes.active_hero.add_encounter(game, self._current)
        self._current = self._deck.pop(0) if len(self._deck) > 0 else NullEncounter(self._game_num)
        self._current.on_reveal(game)


def build_deck(game_num):
    if isinstance(game_num, int) and game_num < 7:
        raise ValueError("Progammer Error! Encounters deck only exists in games 7+")
    if game_num == 7:
        deck = game_seven_horcruxes
    elif game_num == "m1":
        deck = monster_box_one_encounters
    elif game_num == "m2":
        deck = monster_box_two_encounters
    elif game_num == "m3":
        deck = monster_box_three_encounters
    elif game_num == "m4":
        deck = monster_box_four_encounters
    return [encounter() for encounter in deck]


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
        window.addstr(f"{self.name}", curses.A_BOLD | curses.color_pair(1))
        if self.completed:
            window.addstr(f" ({constants.DISALLOW}!)", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f"\n{self.description}\n")
        window.addstr(f"To {self._complete_str}: ")
        self._display_to_complete(window)
        window.addstr(f"\nReward: {self.reward_str}\n")

    def _display_to_complete(self, window):
        raise ValueError(f"Programmer Error! Forgot to implement _display_to_complete for {self.name}")

    def die_roll_applies(self, game, result):
        return False

    def apply_die_roll(self, game, result):
        raise ValueError(f"Programmer Error! Die roll should not apply to {self.name}")

    def on_reveal(self, game):
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
        super().__init__("Diary", f"Each time a hero plays an ally, lose 1{constants.HEART}", f"If you play 2 allies, one hero gains 2{constants.HEART}")

    def _display_to_complete(self, window):
        window.addstr(f"roll {constants.HEART} or {constants.CARD}")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        return (result == constants.HEART or result == f"{constants.CARD}") and not self.completed

    def apply_die_roll(self, game, result):
        if not (result == constants.HEART or result == constants.CARD):
            raise ValueError(f"Programmer Error! Diary only applies to {constants.HEART} or {constants.CARD}")
        self.completed = True

    def effect(self, game):
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if self.completed:
            return
        if card.is_ally():
            game.log(f"{self.name}: Ally {card.name} played, {game.heroes.active_hero.name} loses 1{constants.HEART}")
            game.heroes.active_hero.remove_hearts(game)

    def reward_effect(self, game):
        self._allies_played = 0
        self._used_ability = False
        game.heroes.active_hero.add_extra_card_effect(game, self.__reward_extra_effect)

    def __reward_extra_effect(self, game, card):
        if card.is_ally():
            self._allies_played += 1
        if self._allies_played >= 2 and not self._used_ability:
            if not game.heroes.healing_allowed:
                game.log("Healing not allowed, cannot use Diary")
                return
            self._used_ability = True
            hero = game.heroes.active_hero
            game.heroes.choose_hero(
                    game, prompt=f"{self.name}: {hero.name} played 2 allies, choose hero to gain 2{constants.HEART}: ").add_hearts(game, 2)


class Ring(Horcrux):
    def __init__(self):
        super().__init__("Ring", f"If you assign 2{constants.DAMAGE} to a villain, lose 2{constants.HEART}", f"1/turn: discard two cards to remove 1{constants.CONTROL}")

    def _display_to_complete(self, window):
        window.addstr(f"roll {constants.DAMAGE} or {constants.INFLUENCE}")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        return (result == constants.DAMAGE or result == constants.INFLUENCE) and not self.completed

    def apply_die_roll(self, game, result):
        if not (result == constants.DAMAGE or result == constants.INFLUENCE):
            raise ValueError(f"Programmer Error! Ring only applies to {constants.DAMAGE} or {constants.INFLUENCE}")
        self.completed = True

    def effect(self, game):
        self._damaged_villains = Counter()
        self._used_ability = set()
        game.heroes.active_hero.add_extra_damage_effect(game, self.__extra_effect)

    def __extra_effect(self, game, villain, damage):
        if self.completed:
            return
        self._damaged_villains[villain] += damage
        if self._damaged_villains[villain] >= 2 and villain not in self._used_ability:
            self._used_ability.add(villain)
            game.log(f"{self.name}: {game.heroes.active_hero.name} assigned 2{constants.DAMAGE} to {villain.name}, loses 2{constants.HEART}")
            game.heroes.active_hero.remove_hearts(game, 2)

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
        game.heroes.active_hero.remove_action(game, 'R')


class Locket(Horcrux):
    def __init__(self):
        super().__init__("Locket", f"Heroes cannot gain {constants.DAMAGE} or {constants.INFLUENCE} on other heroes' turns", "1/turn: discard a card to roll the Slytherin die")
        self._got_damage = False
        self._got_heart = False

    def _display_to_complete(self, window):
        window.addstr(f"roll {constants.DAMAGE}")
        if self._got_damage:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f" and {constants.HEART}")
        if self._got_heart:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        return ((result == constants.DAMAGE and not self._got_damage) or
                (result == constants.HEART and not self._got_heart)) and not self.completed

    def apply_die_roll(self, game, result):
        if result == constants.DAMAGE:
            self._got_damage = True
        elif result == constants.HEART:
            self._got_heart = True
        else:
            raise ValueError(f"Programmer Error! Locket only applies to {constants.DAMAGE} or {constants.HEART}")
        if self._got_damage and self._got_heart:
            game.heroes.all_heroes.allow_gaining_tokens_out_of_turn(game)
            self.completed = True

    def effect(self, game):
        game.heroes.all_heroes.disallow_gaining_tokens_out_of_turn(game)

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
        game.heroes.active_hero.remove_action(game, 'L')


class Cup(Horcrux):
    def __init__(self):
        super().__init__("Cup", f"Remove 1{constants.DAMAGE} from all villains", "1/turn: discard a card to roll the Hufflepuff die")
        self._got_heart = False
        self._got_influence = False

    def _display_to_complete(self, window):
        window.addstr(f"roll {constants.HEART}")
        if self._got_heart:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f" and {constants.INFLUENCE}")
        if self._got_influence:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        return ((result == constants.HEART and not self._got_heart) or
                (result == constants.INFLUENCE and not self._got_influence)) and not self.completed

    def apply_die_roll(self, game, result):
        if result == constants.HEART:
            self._got_heart = True
        elif result == constants.INFLUENCE:
            self._got_influence = True
        else:
            raise ValueError(f"Programmer Error! Cup only applies to {constants.HEART} or {constants.INFLUENCE}")
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
        game.heroes.active_hero.remove_action(game, 'C')


class Diadem(Horcrux):
    def __init__(self):
        super().__init__("Diadem", f"If the active hero has one ally, item, and spell, lose 2{constants.HEART}", "1/turn: discard a card to roll the Ravenclaw die")
        self._got_card = False
        self._got_damage = False

    def _display_to_complete(self, window):
        window.addstr(f"roll {constants.CARD}")
        if self._got_card:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f" and {constants.DAMAGE}")
        if self._got_damage:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        return ((result == f"{constants.CARD}" and not self._got_card) or
                (result == constants.DAMAGE and not self._got_damage)) and not self.completed

    def apply_die_roll(self, game, result):
        if result == constants.CARD:
            self._got_card = True
        elif result == constants.DAMAGE:
            self._got_damage = True
        else:
            raise ValueError(f"Programmer Error! Diadem only applies to {constants.CARD} or {constants.DAMAGE}")
        if self._got_card and self._got_damage:
            self.completed = True

    def effect(self, game):
        hero = game.heroes.active_hero
        types_in_hand = set(type(card) for card in hero._hand)
        if types_in_hand.issuperset(set([hogwarts.Ally, hogwarts.Item, hogwarts.Spell])):
            game.log(f"{self.name}: {hero.name} has one ally, item, and spell; loses 2{constants.HEART}")
            hero.remove_hearts(game, 2)

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
        game.heroes.active_hero.remove_action(game, 'D')


class Nagini(Horcrux):
    def __init__(self):
        super().__init__("Nagini", f"Active hero loses 1{constants.HEART} and cannot gain {constants.HEART}", f"1/game: discard this to remove 3{constants.CONTROL}")
        self._got_damage = False
        self._got_card = False
        self._got_heart = False

    def _display_to_complete(self, window):
        window.addstr(f"roll {constants.DAMAGE}")
        if self._got_damage:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f" and {constants.CARD}")
        if self._got_card:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f" and {constants.HEART}")
        if self._got_heart:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        return ((result == constants.DAMAGE and not self._got_damage) or
                (result == constants.CARD and not self._got_card) or
                (result == constants.HEART and not self._got_heart)) and not self.completed

    def apply_die_roll(self, game, result):
        if result == constants.DAMAGE:
            self._got_damage = True
        elif result == constants.CARD:
            self._got_card = True
        elif result == constants.HEART:
            self._got_heart = True
        else:
            raise ValueError(f"Programmer Error! Nagini only applies to {constants.DAMAGE} or {constants.CARD} or {constants.HEART}")
        if self._got_damage and self._got_card and self._got_heart:
            self.completed = True

    def effect(self, game):
        game.heroes.active_hero.remove_hearts(game)
        game.heroes.active_hero.disallow_healing(game)

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'N', "(N)agini", self.__reward_action)

    def __reward_action(self, game):
        if not game.locations.can_remove_control:
            game.log(f"{constants.CONTROL} cannot be removed! {self.name} not discarded")
            return
        game.log(f"{self.name} discarded to remove 3{constants.CONTROL}")
        game.heroes.active_hero._encounters.remove(self)
        game.heroes.active_hero.remove_action(game, 'N')
        game.locations.remove_control(game, 3)


game_seven_horcruxes = [
    Diary,
    Ring,
    Locket,
    Cup,
    Diadem,
    Nagini,
]


class PeskipiksiPesternomi(Encounter):
    def __init__(self):
        super().__init__(
            "Peskipiksi Pesternomi",
            f"If <= 4{constants.HEART}, only draw 4{constants.CARD} at end of turn",
            f"Each time you play a {constants.CARD} with EVEN {constants.INFLUENCE} cost, one hero gains 1{constants.HEART}",
            ["Cornish Pixies"])
        self._played_cards = 0

    def _display_to_complete(self, window):
        window.addstr(f"Play 2{constants.CARD} with EVEN {constants.INFLUENCE} cost in one turn")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" {self._played_cards}/2", curses.A_BOLD)

    def effect(self, game):
        self._played_cards = 0
        game.heroes.active_hero.only_draw_four_cards = True
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if self.completed:
            return
        if card.even_cost:
            self._played_cards += 1
        if self._played_cards >= 2:
            self.completed = True
            game.heroes.active_hero.only_draw_four_cards = False

    def reward_effect(self, game):
        game.heroes.active_hero.add_extra_card_effect(game, self.__reward_extra_effect)

    def __reward_extra_effect(self, game, card):
        if card.even_cost:
            if not game.heroes.healing_allowed:
                game.log(f"Healing not allowed, cannot use {self.name}")
                return
            hero = game.heroes.active_hero
            game.heroes.choose_hero(
                    game, prompt=f"{self.name}: {hero.name} played EVEN cost card, choose hero to gain 1{constants.HEART}: ").add_hearts(game, 1)


class StudentsOutOfBed(Encounter):
    def __init__(self):
        super().__init__(
            "Students Out of Bed",
            f"Each time a Hero shuffles, add a Detention! first",
            f"1/game: discard this; all heroes may banish a card in hand or discard",
            ["Norbert", "Troll"])
        self._got_heart = False
        self._got_card = False

    def _display_to_complete(self, window):
        window.addstr(f"roll {constants.HEART}")
        if self._got_heart:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f" and {constants.CARD}")
        if self._got_card:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        return ((result == constants.HEART and not self._got_heart) or
                (result == constants.CARD and not self._got_card)) and not self.completed

    def apply_die_roll(self, game, result):
        if result == constants.HEART:
            self._got_heart = True
        elif result == constants.CARD:
            self._got_card = True
        else:
            raise ValueError(f"Programmer Error! Students Out of Bed only applies to {constants.HEART} or {constants.CARD}")
        if self._got_heart and self._got_card:
            self.completed = True
            game.heroes.all_heroes.remove_extra_shuffle_effect(game, self.__extra_effect)

    def on_reveal(self, game):
        game.heroes.all_heroes.add_extra_shuffle_effect(game, self.__extra_effect)

    def effect(self, game):
        pass

    def __extra_effect(self, game, hero):
        if self.completed:
            return
        game.log(f"{self.name}: {hero.name} shuffles, add a Detention! first")
        hero.add_detention(game)

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'S', "(S)tudents Out of Bed", self.__reward_action)

    def __reward_action(self, game):
        game.log(f"{self.name} discarded to banish a card in hand or discard")
        game.heroes.active_hero._encounters.remove(self)
        game.heroes.active_hero.remove_action(game, 'S')
        game.heroes.all_heroes.choose_and_banish(game)


class ThirdFloorCorridor(Encounter):
    def __init__(self):
        super().__init__(
            "Third Floor Corridor",
            "No rewards for Villains or Creatures",
            "1/game: discard this; collect reward for top of Villain/Creature discard",
            ["Fluffy"])
        self._played_allies = 0
        self._played_items = 0
        self._played_spells = 0

    def _display_to_complete(self, window):
        window.addstr("Play 2 Allies")
        if self._played_allies >= 2:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" ({self._played_allies}/2)", curses.A_BOLD)

        window.addstr(", 2 Items")
        if self._played_items >= 2:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" ({self._played_items}/2)", curses.A_BOLD)

        window.addstr(", and 2 Spells")
        if self._played_spells >= 2:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" ({self._played_spells}/2)", curses.A_BOLD)

        window.addstr(" in one turn")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))

    def on_reveal(self, game):
        game.villain_deck.disallow_rewards()

    def effect(self, game):
        self._played_allies = 0
        self._played_items = 0
        self._played_spells = 0
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if self.completed:
            return
        if card.is_ally():
            self._played_allies += 1
        elif card.is_item():
            self._played_items += 1
        elif card.is_spell():
            self._played_spells += 1
        if self._played_allies >= 2 and self._played_items >= 2 and self._played_spells >= 2:
            self.completed = True
            game.villain_deck.allow_rewards()

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'T', "(T)hird Floor Corridor", self.__reward_action)

    def __reward_action(self, game):
        game.log(f"{self.name} discarded to collect reward for top of Villain/Creature discard")
        game.heroes.active_hero._encounters.remove(self)
        game.heroes.active_hero.remove_action(game, 'T')
        game.villain_deck.last_defeated_villain_reward(game)


monster_box_one_encounters = [
    PeskipiksiPesternomi,
    StudentsOutOfBed,
    ThirdFloorCorridor,
]


class UnregisteredAnimagus(Encounter):
    def __init__(self):
        super().__init__(
            "Unregistered Animagus",
            f"If there are >= 2{constants.CONTROL}, lose 1{constants.HEART}",
            f"1/game: discard this; roll the Creature die twice",
            ["Scabbers", "Peter Pettigrew"])
        self._damage_assigned = 0

    def _display_to_complete(self, window):
        window.addstr(f"Assign 5{constants.DAMAGE} in one turn")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" {self._damage_assigned}/5", curses.A_BOLD)

    def effect(self, game):
        self._damage_assigned = 0
        game.heroes.active_hero.add_extra_damage_effect(game, self.__extra_effect)
        if game.locations.current._control >= 2:
            game.log(f"{self.name}: {game.locations.current._control}{constants.CONTROL} on location! {game.heroes.active_hero.name} loses 1{constants.HEART}")
            game.heroes.active_hero.remove_hearts(game)

    def __extra_effect(self, game, creature, amount):
        if self.completed:
            return
        self._damage_assigned += amount
        if self._damage_assigned >= 5:
            self.completed = True

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'U', "(U)nregistered Anumagus", self.__reward_action)

    def __reward_action(self, game):
        game.log(f"{self.name} discarded to roll Creature die twice")
        game.heroes.active_hero._encounters.remove(self)
        game.heroes.active_hero.remove_action(game, 'U')
        game.roll_creature_die()
        game.roll_creature_die()


class FullMoonRises(Encounter):
    def __init__(self):
        super().__init__(
            "Full Moon Rises",
            f"Each time {constants.CONTROL} is added active Hero adds a Detention! to hand",
            f"1/game: discard this; ALL heroes gain 3{constants.HEART} and may banish a card in hand or discard",
            ["Werewolf", "Fenrir Greyback"])
        self._foes_defeated = 0

    def _display_to_complete(self, window):
        window.addstr(f"Defeat 3 foes in one turn")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" {self._foes_defeated}/3", curses.A_BOLD)

    def on_reveal(self, game):
        game.locations.add_control_callback(game, self)

    def control_callback(self, game, amount):
        if self.completed or amount < 1:
            return
        game.log(f"{self.name}: {amount}{constants.CONTROL} added, {game.heroes.active_hero.name} adds a Detention! to hand for each")
        for _ in range(amount):
            game.heroes.active_hero.add_detention(game, to_hand=True)

    def effect(self, game):
        self._foes_defeated = 0
        game.heroes.active_hero.add_extra_damage_effect(game, self.__extra_effect)
        game.heroes.active_hero.add_extra_influence_effect(game, self.__extra_effect)

    def __extra_effect(self, game, foe, amount):
        if self.completed:
            return
        if foe._defeated:
            self._foes_defeated += 1
        if self._foes_defeated >= 3:
            self.completed = True

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'F', "(F)ull Moon Rises", self.__reward_action)

    def __reward_action(self, game):
        game.log(f"{self.name} discarded; ALL heroes gain 3{constants.HEART} and may banish a card in hand or discard")
        game.heroes.active_hero._encounters.remove(self)
        game.heroes.active_hero.remove_action(game, 'F')
        game.heroes.all_heroes.add_hearts(game, 3)
        game.heroes.all_heroes.choose_and_banish(game)


class DefensiveTraining(Encounter):
    def __init__(self):
        super().__init__(
            "Defensive Training",
            f"Heroes cannot remove {constants.CONTROL}",
            f"1/game: discard this; ALL heroes gain 2{constants.INFLUENCE} and 2{constants.HEART}",
            ["Boggart"])
        self._got_damage = 0

    def _display_to_complete(self, window):
        window.addstr(f"roll 3{constants.DAMAGE}")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" {self._got_damage}/3", curses.A_BOLD)

    def die_roll_applies(self, game, result):
        return result == constants.DAMAGE and self._got_damage < 3

    def apply_die_roll(self, game, result):
        if result == constants.DAMAGE:
            self._got_damage += 1
        else:
            raise ValueError(f"Programmer Error! Defensive Training only applies to {constants.DAMAGE}")
        if self._got_damage >= 3:
            self.completed = True
            game.locations.allow_remove_control(game)

    def on_reveal(self, game):
        game.locations.disallow_remove_control(game)

    def effect(self, game):
        pass

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'D', "(D)efensive Training", self.__reward_action)

    def __reward_action(self, game):
        game.log(f"{self.name} discarded; ALL heroes gain 2{constants.INFLUENCE} and 2{constants.HEART}")
        game.heroes.active_hero._encounters.remove(self)
        game.heroes.active_hero.remove_action(game, 'D')
        game.heroes.all_heroes.add(game, influence=2, hearts=2)


monster_box_two_encounters = [
    UnregisteredAnimagus,
    FullMoonRises,
    DefensiveTraining,
]

monster_box_three_encounters = [
]

monster_box_four_encounters = [
]
