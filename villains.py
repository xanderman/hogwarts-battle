import random

class VillainDeck(object):
    def __init__(self, window, max_villains=3):
        self._window = window
        self._deck = game_one_villains
        self._max = max_villains

        random.shuffle(self._deck)
        self.current = []

    def display_state(self):
        self._window.erase()
        self._window.box()
        self._window.addstr(0, 1, f"Villains ({len(self._deck)} left)")
        for i, villain in enumerate(self.current):
            villain.display_state(self._window, 3*i+1, i)
        self._window.refresh()

    def reveal(self, game):
        while len(self.current) < self._max and len(self._deck) > 0:
            villain = self._deck.pop()
            self.current.append(villain)
            villain.on_reveal(game)

    def choose_hero(self, game):
        while True:
            try:
                choice = int(game.input("Choose a villain: "))
                if choice < 0 or choice >= len(self.current):
                    raise ValueError()
                return self.current[choice]
            except ValueError:
                self.log("Invalid villain!")


class Villain(object):
    def __init__(self, name, description, reward_desc, health, effect=lambda game: None, on_reveal=lambda game: None, reward=lambda game: None):
        self.name = name
        self.description = description
        self.reward_desc = reward_desc
        self._health = health
        self.effect = effect
        self.on_reveal = on_reveal
        self._reward = reward

        self._damage = 0

    def display_state(self, window, row, i):
        window.addstr(row  , 1, f"{i}: {self.name} ({self._damage}↯/{self._health}💜)")
        window.addstr(row+1, 1, f"     {self.description}")
        window.addstr(row+2, 1, f"     Reward: {self.reward_desc}")

    def __str__(self):
        return f"{self.name} ({self._damage}/{self._health}), {self.description}"

    def add_damage(self, game, amount=1):
        self._damage += amount
        if self._damage >= self._health:
            self.reward(game)
            game.villain_deck.current.remove(self)
            return True
        return False

    def remove_damage(self, amount=1):
        self._damage -= amount
        if self._damage < 0:
            self._damage = 0

    def reward(self, game):
        game.log(f"{self.name} defeated!")
        self._reward(game)


class Draco(Villain):
    def __init__(self):
        super().__init__("Draco Malfoy", "When 💀 is added, active hero loses 2💜",
                         "Remove 1💀", 6,
                         on_reveal=lambda game: game.add_control_callback(self),
                         reward=self.__reward)

    def control_callback(self, game, amount):
        if amount < 1:
            return
        game.log(f"{self.name}: 💀 added, {game.active_hero.name} loses 2💜 for each")
        for _ in range(amount):
            game.active_hero.remove_health(game, 2)

    def __reward(self, game):
        game.remove_control_callback(self)
        game.locations.current.remove_control(game)


class Crabbe(Villain):
    def __init__(self):
        super().__init__("Crabbe & Goyle", "When forced to discard, lose 1💜",
                         "ALL heroes draw 1 card", 5,
                         on_reveal=lambda game: game.add_discard_callback(self),
                         reward=self.__reward)

    def discard_callback(self, game, hero):
        game.log(f"{self.name}: {hero.name} discarded, so loses 1💜")
        hero.remove_health(game, 1)

    def __reward(self, game):
        game.remove_discard_callback(self)
        game.all_heroes(lambda game, hero: hero.draw(game))


game_one_villains = [
    Draco(), Crabbe(),
    Villain("Quirinus Quirrell", "Active hero loses 1💜",
            "ALL heroes gain 1💜 and 1💰", 6,
            effect=lambda game: game.active_hero.remove_health(game),
            reward=lambda game: game.all_heroes(lambda game, hero: hero.add(game, influence=1, hearts=1))),
]
