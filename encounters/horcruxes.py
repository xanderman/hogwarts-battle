from collections import Counter
import curses

from . import ENCOUNTERS_BY_NAME, Encounter
import constants


class Horcrux(Encounter):
    def __init__(self, name, description, reward_str):
        super().__init__(name, description, reward_str, [])
        self._complete_str = "destroy"


class Diary(Horcrux):
    def __init__(self):
        super().__init__(
            "Diary",
            f"Each time a hero plays an ally, lose 1{constants.HEART}",
            f"If you play 2 allies, one hero gains 2{constants.HEART}")
        self._allies_played = 0
        self._used_ability = False

    def _display_to_complete(self, window):
        window.addstr(f"roll {constants.HEART} or {constants.CARD}")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        if self.completed:
            return False
        return constants.HEART in result or constants.CARD in result

    def apply_die_roll(self, game, result):
        if not self.die_roll_applies(game, result):
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

ENCOUNTERS_BY_NAME['Diary'] = Diary


class Ring(Horcrux):
    def __init__(self):
        super().__init__(
            "Ring",
            f"If you assign 2{constants.DAMAGE} to a villain, lose 2{constants.HEART}",
            f"1/turn: discard two cards to remove 1{constants.CONTROL}")
        self._damaged_villains = Counter()
        self._used_villains = set()

    def _display_to_complete(self, window):
        window.addstr(f"roll {constants.DAMAGE} or {constants.INFLUENCE}")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        if self.completed:
            return False
        return constants.DAMAGE in result or constants.INFLUENCE in result

    def apply_die_roll(self, game, result):
        if not self.die_roll_applies(game, result):
            raise ValueError(f"Programmer Error! Ring only applies to {constants.DAMAGE} or {constants.INFLUENCE}")
        self.completed = True

    def effect(self, game):
        self._damaged_villains = Counter()
        self._used_villains = set()
        game.heroes.active_hero.add_extra_damage_effect(game, self.__extra_effect)

    def __extra_effect(self, game, villain, damage):
        if self.completed or not villain.is_villain:
            return
        self._damaged_villains[villain.unique_name] += damage
        if self._damaged_villains[villain.unique_name] >= 2 and villain.unique_name not in self._used_villains:
            self._used_villains.add(villain.unique_name)
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

ENCOUNTERS_BY_NAME['Ring'] = Ring


class Locket(Horcrux):
    def __init__(self):
        super().__init__(
            "Locket",
            f"Heroes cannot gain {constants.DAMAGE} or {constants.INFLUENCE} on other heroes' turns",
            "1/turn: discard a card to roll the Slytherin die")
        self._got_damage = False
        self._got_heart = False
        self._used_ability = False

    def _display_to_complete(self, window):
        window.addstr(f"roll {constants.DAMAGE}")
        if self._got_damage:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f" and {constants.HEART}")
        if self._got_heart:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        if self.completed:
            return False
        return ((constants.DAMAGE in result and not self._got_damage) or
                (constants.HEART in result and not self._got_heart))

    def apply_die_roll(self, game, result):
        if not self.die_roll_applies(game, result):
            raise ValueError(f"Programmer Error! Locket only applies to {constants.DAMAGE} or {constants.HEART}")
        if constants.DAMAGE in result:
            self._got_damage = True
        if constants.HEART in result:
            self._got_heart = True
        if self._got_damage and self._got_heart:
            game.heroes.all_heroes.allow_gaining_tokens_out_of_turn(game)
            self.completed = True

    def effect(self, game):
        game.heroes.all_heroes.disallow_gaining_tokens_out_of_turn(game)

    def end_turn(self, game):
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
        game.heroes.active_hero.remove_action(game, 'L')

ENCOUNTERS_BY_NAME['Locket'] = Locket


class Cup(Horcrux):
    def __init__(self):
        super().__init__(
            "Cup",
            f"Remove 1{constants.DAMAGE} from all villains",
            "1/turn: discard a card to roll the Hufflepuff die")
        self._got_heart = False
        self._got_influence = False
        self._used_ability = False

    def _display_to_complete(self, window):
        window.addstr(f"roll {constants.HEART}")
        if self._got_heart:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f" and {constants.INFLUENCE}")
        if self._got_influence:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        if self.completed:
            return False
        return ((constants.HEART in result and not self._got_heart) or
                (constants.INFLUENCE in result and not self._got_influence))

    def apply_die_roll(self, game, result):
        if not self.die_roll_applies(game, result):
            raise ValueError(f"Programmer Error! Cup only applies to {constants.HEART} or {constants.INFLUENCE}")
        if constants.INFLUENCE in result:
            self._got_influence = True
        if constants.HEART in result:
            self._got_heart = True
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

ENCOUNTERS_BY_NAME['Cup'] = Cup


class Diadem(Horcrux):
    def __init__(self):
        super().__init__(
            "Diadem",
            f"If the active hero has one ally, item, and spell, lose 2{constants.HEART}",
            "1/turn: discard a card to roll the Ravenclaw die")
        self._got_card = False
        self._got_damage = False
        self._used_ability = False

    def _display_to_complete(self, window):
        window.addstr(f"roll {constants.CARD}")
        if self._got_card:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f" and {constants.DAMAGE}")
        if self._got_damage:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        if self.completed:
            return False
        return ((constants.CARD in result and not self._got_card) or
                (constants.DAMAGE in result and not self._got_damage))

    def apply_die_roll(self, game, result):
        if not self.die_roll_applies(game, result):
            raise ValueError(f"Programmer Error! Diadem only applies to {constants.CARD} or {constants.DAMAGE}")
        if constants.CARD in result:
            self._got_card = True
        if constants.DAMAGE in result:
            self._got_damage = True
        if self._got_card and self._got_damage:
            self.completed = True

    def effect(self, game):
        hero = game.heroes.active_hero
        allies = sum(1 for card in hero._hand if card.is_ally())
        items = sum(1 for card in hero._hand if card.is_item())
        spells = sum(1 for card in hero._hand if card.is_spell())
        if allies >= 1 and items >= 1 and spells >= 1:
            game.log(f"{self.name}: {hero.name} has at least one ally, item, and spell; loses 2{constants.HEART}")
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

ENCOUNTERS_BY_NAME['Diadem'] = Diadem


class Nagini(Horcrux):
    def __init__(self):
        super().__init__(
            "Nagini",
            f"Active hero loses 1{constants.HEART} and cannot gain {constants.HEART}",
            f"1/game: discard this to remove 3{constants.CONTROL}")
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
        if self.completed:
            return False
        return ((constants.DAMAGE in result and not self._got_damage) or
                (constants.CARD in result and not self._got_card) or
                (constants.HEART in result and not self._got_heart))

    def apply_die_roll(self, game, result):
        if not self.die_roll_applies(game, result):
            raise ValueError(f"Programmer Error! Nagini only applies to {constants.DAMAGE} or {constants.CARD} or {constants.HEART}")
        if constants.DAMAGE in result:
            self._got_damage = True
        if constants.CARD in result:
            self._got_card = True
        if constants.HEART in result:
            self._got_heart = True
        if self._got_damage and self._got_card and self._got_heart:
            self.completed = True

    def effect(self, game):
        game.heroes.active_hero.remove_hearts(game)
        game.heroes.active_hero.disallow_healing(game)

    def end_turn(self, game):
        game.heroes.active_hero.allow_healing(game)

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

ENCOUNTERS_BY_NAME['Nagini'] = Nagini

