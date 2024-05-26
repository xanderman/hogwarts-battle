import curses

from . import ENCOUNTERS_BY_NAME, Encounter
import constants


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

ENCOUNTERS_BY_NAME['Peskipiksi Pesternomi'] = PeskipiksiPesternomi


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
        if self.completed:
            return False
        return ((constants.CARD in result and not self._got_card) or
                (result == constants.HEART and not self._got_heart) or
                (result == (constants.HEART + constants.HEART) and not self._got_heart))

    def apply_die_roll(self, game, result):
        if not self.die_roll_applies(game, result):
            raise ValueError(f"Programmer Error! Students Out of Bed only applies to {constants.HEART} or {constants.CARD}")
        if constants.CARD in result:
            self._got_card = True
        else:
            self._got_heart = True
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

ENCOUNTERS_BY_NAME['Students Out of Bed'] = StudentsOutOfBed


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

ENCOUNTERS_BY_NAME['Third Floor Corridor'] = ThirdFloorCorridor
