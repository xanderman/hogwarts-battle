import curses
import random

import constants

class VillainDeck(object):
    def __init__(self, window, config, encounters):
        self._window = window
        self._init_window()
        self._pad = curses.newpad(100, 100)
        self._deck = build_deck(config, encounters)
        self._discard = []
        self._max = config['villains_revealed']
        self._voldemort = VOLDEMORTS_BY_NAME[config['voldemort']]() if config['voldemort'] else None
        self._rewards_allowed = True

        random.shuffle(self._deck)
        self.current = []

    def _init_window(self):
        self._window.box()
        self._window.addstr(0, 1, "Villains")
        self._window.noutrefresh()
        beg = self._window.getbegyx()
        self._pad_start_line = beg[0] + 1
        self._pad_start_col = beg[1] + 1
        end = self._window.getmaxyx()
        self._pad_end_line = self._pad_start_line + end[0] - 3
        self._pad_end_col = self._pad_start_col + end[1] - 3

    def display_state(self, game, resize=False, size=None):
        if resize:
            self._window.resize(*size)
            self._window.clear()
            self._init_window()
        self._window.clear()
        self._window.box()
        left_str = f"({len(self._deck)}"
        if self._voldemort is not None:
            left_str += " + Voldemort"
        self._window.addstr(0, 1, f"Villains {left_str} left)")
        self._window.noutrefresh()

        self._pad.clear()
        for i, villain in enumerate(self.current):
            villain.display_state(self._pad, i)
        if self.voldemort_active():
            self._display_voldemort(game)
        self._pad.noutrefresh(0,0, self._pad_start_line,self._pad_start_col, self._pad_end_line,self._pad_end_col)

    def _display_voldemort(self, game):
        self._pad.addstr("Voldemort:")
        if self.voldemort_vulnerable(game):
            self._pad.addstr(" *vulnerable*\n", curses.A_BOLD | curses.color_pair(1))
        else:
            self._pad.addstr(" *invulnerable*\n", curses.A_BOLD | curses.color_pair(2))
        self._voldemort.display_state(self._pad, 'v')

    def play_turn(self, game):
        game.log("-----Villain phase-----")
        self.all.play_turn(game)

    def reveal(self, game):
        self.all.end_turn(game)
        voldemort_was_active = self.voldemort_active()
        while len(self.current) < self._max and len(self._deck) > 0:
            death_eaters = sum(1 for v in game.villain_deck.current if v.name == "Death Eater" and not v._stunned)
            welsh_greens = sum(1 for v in game.villain_deck.current if v.name == "Common Welsh Green" and not v._stunned)
            villain = self._deck.pop()
            self.current.append(villain)
            game.log(f"Revealed {villain.type_name}: {villain.name}")
            villain._on_reveal(game)
            if death_eaters > 0 and villain.is_villain:
                game.log(f"Death Eater (x{death_eaters}): Villain revealed, ALL heroes lose {death_eaters}{constants.HEART}")
                game.heroes.all_heroes.remove_hearts(game, death_eaters)
            if welsh_greens > 0 and villain.is_creature:
                game.log(f"Common Welsh Green: Creature revealed, ALL heroes lose 2{constants.HEART}")
                game.heroes.all_heroes.remove_hearts(game, 2)
        if self.voldemort_active() and not voldemort_was_active:
            game.log("Voldemort revealed!")
            self._voldemort._on_reveal(game)
            if death_eaters > 0:
                game.log(f"Death Eater (x{death_eaters}): Villain revealed, ALL heroes lose {death_eaters}{constants.HEART}")
                game.heroes.all_heroes.remove_hearts(game, death_eaters)

    def voldemort_active(self):
        return self._voldemort is not None and len(self._deck) == 0

    def voldemort_vulnerable(self, game):
        return self.voldemort_active() and len(self.current) == 0 and (game.encounters is None or game.encounters.all_complete)

    def disallow_rewards(self):
        self._rewards_allowed = False

    def allow_rewards(self):
        self._rewards_allowed = True

    def last_defeated_villain_reward(self, game):
        if len(self._discard) == 0:
            return
        villain = self._discard[-1]
        game.log(f"Last defeated villain: {villain.name}, Reward: {villain.reward_desc}")
        villain.reward(game)

    @property
    def choices(self):
        choices = [str(i) for i in range(len(self.current))]
        if self.voldemort_active():
            choices.append('v')
        return choices

    @property
    def villain_choices(self):
        choices = [str(i) for i in range(len(self.current)) if self.current[i].is_villain]
        if self.voldemort_active():
            # Voldemort is always a Villain
            choices.append('v')
        return choices

    @property
    def creature_choices(self):
        # Voldemort is never a creature
        return [str(i) for i in range(len(self.current)) if self.current[i].is_creature]

    def __len__(self):
        voldemort = 1 if self._voldemort is not None else 0
        return len(self._deck) + len(self.current) + voldemort

    def __getitem__(self, key):
        if key == 'v':
            return self._voldemort
        return self.current[int(key)]

    @property
    def all(self):
        if self.voldemort_active():
            return _VillainList(*self.current, self._voldemort)
        return _VillainList(*self.current)

    @property
    def all_villains(self):
        villains = filter(lambda foe: foe.is_villain, self.current)
        if self.voldemort_active():
            return _VillainList(*villains, self._voldemort)
        return _VillainList(*villains)

    @property
    def all_creatures(self):
        creatures = filter(lambda foe: foe.is_creature, self.current)
        return _VillainList(*creatures)


class _VillainList(list):
    def __init__(self, *args):
        super().__init__(args)

    def __getattr__(self, attr):
        def f(game, *args, **kwargs):
            for villain in self:
                getattr(villain, attr)(game, *args, **kwargs)
        return f

    def effect(self, game, effect=None):
        if effect is None:
            raise ValueError("Programmer Error! Forgot to pass effect to _VillainList.effect")
        for villain in self:
            effect(game, villain)


def build_deck(config, encounters):
    if isinstance(config['villains'], list):
        return [VILLAINS_BY_NAME[name]() for name in config['villains']]
    total_villains = config['villains']
    names = set(encounters.required_villains())
    available = list(VILLAINS_BY_NAME.keys())
    while len(names) < total_villains:
        names.add(random.choice(available))
    return [VILLAINS_BY_NAME[name]() for name in names]


VILLAINS_BY_NAME = {}

VOLDEMORTS_BY_NAME = {}


class _Foe(object):
    def __init__(self, name, description, reward_desc, hearts=0, cost=0):
        self.name = name
        self.unique_name = name
        self.description = description
        self.reward_desc = reward_desc
        self._hearts = hearts
        self._cost = cost

        self._damage = 0
        self._can_take_damage = True
        self._took_damage = 0
        self._max_damage_per_turn = -1
        self._influence = 0
        self._took_influence = 0
        self._max_influence_per_turn = 1
        self._stunned = False
        self._stunned_by = None

    def display_state(self, window, i):
        window.addstr(f"{i}: {self.name}")
        if self._hearts > 0:
            window.addstr(f" ({self._damage}/{self._hearts}{constants.HEART})")
        if self._cost > 0:
            window.addstr(f" ({self._influence}/{self._cost}{constants.INFLUENCE})")
        window.addstr(f" {self.type_name}", curses.A_BOLD)
        if self._stunned:
            window.addstr(" *stunned*", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f"\n     {self.description}")
        window.addstr(f"\n     Reward: {self.reward_desc}\n")

    def play_turn(self, game):
        if self._stunned:
            game.log(f"Villain: {self.name} ({self._damage}/{self._hearts}) is stunned!")
            if game.heroes.active_hero == self._stunned_by:
                game.log(f"{self.name} was stunned by {self._stunned_by.name}, so recovers")
                self._stunned = False
                self._stunned_by = None
                self._on_recover_from_stun(game)
            return
        game.log(f"Villain: {self}")
        self._effect(game)

    def _on_reveal(self, game):
        pass

    def _on_stun(self, game):
        pass

    def _on_recover_from_stun(self, game):
        pass

    def _effect(self, game):
        raise ValueError(f"Programmer Error! Forgot to implement effect for {self.name}")

    def end_turn(self, game):
        self._can_take_damage = True
        self._took_damage = 0
        self._max_damage_per_turn = -1
        self._took_influence = 0
        self._max_influence_per_turn = 1

    def __str__(self):
        return f"{self.name}: {self.description}"

    @property
    def is_villain(self):
        return False

    @property
    def is_creature(self):
        return False

    @property
    def type_name(self):
        return "ERROR! Forgot to override type_name in subclass!"

    @property
    def took_damage(self):
        return self._took_damage > 0

    def can_take_damage(self, game):
        if not self._can_take_damage:
            return False
        if self._hearts == 0:
            return False
        if self._damage >= self._hearts:
            return False
        if self._max_damage_per_turn >= 0 and self._took_damage >= self._max_damage_per_turn:
            return False
        if self == game.villain_deck._voldemort and not game.villain_deck.voldemort_vulnerable(game):
            return False
        return True

    def add_damage(self, game):
        if self._hearts == 0:
            raise Exception(f"Prgammer Error! {self.name} cannot take damage!")
        self._took_damage += 1
        self._damage += 1
        if self._defeated:
            self._apply_defeat(game)
            return True
        return False

    def remove_damage(self, game, amount=1):
        self._damage -= amount
        if self._damage < 0:
            self._damage = 0

    @property
    def took_influence(self):
        return self._took_influence > 0

    def can_take_influence(self, game):
        if self._cost == 0:
            return False
        if self._influence >= self._cost:
            return False
        if self._took_influence >= self._max_influence_per_turn:
            return False
        if self == game.villain_deck._voldemort and not game.villain_deck.voldemort_vulnerable(game):
            return False
        return True

    def add_influence(self, game):
        if self._cost == 0:
            raise Exception(f"Programmer Error! {self.name} cannot take influence!")
        if self._took_influence >= self._max_influence_per_turn:
            raise Exception(f"Programmer Error! {self.name} cannot take more influence!")
        self._took_influence += 1
        self._influence += 1
        if self._defeated:
            self._apply_defeat(game)
            return True
        return False

    def remove_influence(self, game, amount=1):
        self._influence -= amount
        if self._influence < 0:
            self._influence = 0

    def stun(self, game):
        self._stunned = True
        self._stunned_by = game.heroes.active_hero
        self._on_stun(game)

    @property
    def _defeated(self):
        return self._damage >= self._hearts and self._influence >= self._cost

    def _apply_defeat(self, game):
        self.remove_callbacks(game)
        if game.villain_deck._rewards_allowed:
            self.reward(game)
        else:
            game.log(f"{self.name} defeated, but rewards are not allowed!")
        if self == game.villain_deck._voldemort:
            game.villain_deck._voldemort = None
        else:
            game.villain_deck.current.remove(self)
        game.villain_deck._discard.append(self)

    def remove_callbacks(self, game):
        pass

    def reward(self, game):
        game.log(f"{self.name} defeated! {self.reward_desc}")
        self._reward(game)

    def _reward(self, game):
        raise ValueError(f"Programmer Error! Forgot to implement reward for {self.name}")


class Villain(_Foe):
    @property
    def is_villain(self):
        return True

    @property
    def type_name(self):
        return "Villain"


class Creature(_Foe):
    @property
    def is_creature(self):
        return True

    @property
    def type_name(self):
        return "Creature"


class VillainCreature(_Foe):
    @property
    def is_villain(self):
        return True

    @property
    def is_creature(self):
        return True

    @property
    def type_name(self):
        return "Villain-Creature"
