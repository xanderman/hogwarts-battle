import curses

from . import ENCOUNTERS_BY_NAME, Encounter
import constants


class ForbiddenForest(Encounter):
    def __init__(self):
        super().__init__(
            "Forbidden Forest",
            f"If there are >=2 Creatures, lose 1{constants.HEART}",
            f"You can reroll any die once",
            ["Aragog", "Grawp"])
        self._got_card = False
        self._got_heart = False
        self._got_influence = False

    def _display_to_complete(self, window):
        window.addstr(f"roll {constants.CARD}")
        if self._got_card:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f" and {constants.HEART}")
        if self._got_heart:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))
        window.addstr(f" and {constants.INFLUENCE}")
        if self._got_influence:
            window.addstr("✔", curses.A_BOLD | curses.color_pair(1))

    def die_roll_applies(self, game, result):
        if self.completed:
            return False
        return ((constants.CARD in result and not self._got_card) or
                (result == constants.INFLUENCE and not self._got_influence) or
                (result == constants.HEART and not self._got_heart) or
                (result == (constants.HEART + constants.HEART) and not self._got_heart))

    def apply_die_roll(self, game, result):
        if not self.die_roll_applies(game, result):
            raise ValueError(f"Programmer Error! Nagini only applies to {constants.CARD} or {constants.HEART} or {constants.INFLUENCE}")
        if constants.CARD in result:
            self._got_card = True
        elif result == constants.INFLUENCE:
            self._got_influence = True
        else:
            self._got_heart = True
        if self._got_card and self._got_heart and self._got_influence:
            self.completed = True

    def effect(self, game):
        creatures = sum(1 for card in game.villain_deck.current if card.is_creature)
        if creatures >= 2:
            game.log(f"{self.name}: {creatures} creatures in play! {game.heroes.active_hero.name} loses 1{constants.HEART}")
            game.heroes.active_hero.remove_hearts(game)

    def reward_effect(self, game):
        pass

ENCOUNTERS_BY_NAME['Forbidden Forest'] = ForbiddenForest


class FilthyHalfBreed(Encounter):
    def __init__(self):
        super().__init__(
            "Filthy Half-Breed",
            f"If there are >=2 Spells in the market, lose 1{constants.HEART}",
            f"1/game: discard this; ALL heroes draw a card and may banish a card in hand",
            ["Centaur", "Dolores Umbridge"])
        self._played_costs = set()

    def _display_to_complete(self, window):
        window.addstr(f"Play 3{constants.CARD} with different {constants.INFLUENCE} cost in one turn")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" {len(self._played_costs)}/3", curses.A_BOLD)

    def effect(self, game):
        spells = sum(1 for slot in game.hogwarts_deck._market.values() if slot[0].is_spell())
        if spells >= 2:
            game.log(f"{self.name}: {spells} spells in market! {game.heroes.active_hero.name} loses 1{constants.HEART}")
            game.heroes.active_hero.remove_hearts(game)
        self._played_costs = set()
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if self.completed:
            return
        if card.cost != 0 and card.cost not in self._played_costs:
            self._played_costs.add(card.cost)
        if len(self._played_costs) >= 3:
            self.completed = True

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'F', "(F)ilthy Half-Breed", self.__reward_action)

    def __reward_action(self, game):
        game.log(f"{self.name} discarded; ALL heroes draw a card and may banish a card in hand")
        for hero in game.heroes.all_heroes:
            hero.draw(game)
            hero.choose_and_banish(game, hand_only=True)

ENCOUNTERS_BY_NAME['Filthy Half-Breed'] = FilthyHalfBreed


class Escape(Encounter):
    def __init__(self):
        super().__init__(
            "Escape!",
            f"Lose 1{constants.HEART} for each Item or Ally played",
            f"1/game: discard this; remove 2{constants.CONTROL}",
            ["Ukrainian Ironbelly"])
        self._spells_played = 0

    def _display_to_complete(self, window):
        window.addstr(f"Play 6 Spells in one turn")
        if self.completed:
            window.addstr(" ✔", curses.A_BOLD | curses.color_pair(1))
        else:
            window.addstr(f" {self._spells_played}/6", curses.A_BOLD)

    def effect(self, game):
        self._spells_played = 0
        game.heroes.active_hero.add_extra_card_effect(game, self.__extra_effect)

    def __extra_effect(self, game, card):
        if self.completed:
            return
        if card.is_item() or card.is_ally():
            game.log(f"{self.name}: Item or Ally played, {game.heroes.active_hero.name} loses 1{constants.HEART}")
            game.heroes.active_hero.remove_hearts(game)
        if card.is_spell():
            self._spells_played += 1
        if self._spells_played >= 6:
            self.completed = True

    def reward_effect(self, game):
        game.heroes.active_hero.add_action(game, 'E', "(E)scape", self.__reward_action)

    def __reward_action(self, game):
        if not game.locations.can_remove_control:
            game.log(f"{constants.CONTROL} cannot be removed! {self.name} not discarded")
            return
        game.log(f"{self.name} discarded; remove 2{constants.CONTROL}")
        game.locations.remove_control(game, 2)

ENCOUNTERS_BY_NAME['Escape!'] = Escape
