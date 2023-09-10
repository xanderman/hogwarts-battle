# hogwarts-battle
Python curses implementation of Harry Potter: Hogwarts Battle

## Running the game
Playing this game requires at least minimal familiarity with the terminal.
You'll need to know at least how to run a python script (and download the code
from github).

I've tested this on Python 3.9.6. The language features I'm using are available
starting in 3.4. The game requires your terminal be at least 50 lines high if
you play with 1 or 2 heroes, and 70 lines for 3 or 4 heroes. Terminal width is
more lenient, but you'll have a hard time reading anything if the screen is
less than about 50 columns wide. It may or may not crash at smaller sizes, or
if you resize the window while playing. I've done what I can, but curses is
pretty limited.

To play, run `game.py` specifying which game number and heroes you want to play.

```bash
$ python game.py N HERO [HERO ...]
```

Currently supported values of N are 1-7 (the entire base game). Currently
supported values of HERO are Hermione, Ron, Harry, Neville, Ginny, Luna. The
game will run with only one hero, but the rules really aren't designed for
that, so YMMV. Currently only supports up to 4 heroes -- there's just no room
on the screen for more.

## Gameplay
I will not explain the rules of the game here. If you've never played the game
before, you should! You might find it hard to keep track of what's going on if
you're not already familiar with the game, but the game log is detailed enough
you could probably pick it up. All I'll say here is that it's a cooperative
deck builder, and if you don't know what either of those are, this is probably
not the best introduction. Go buy the physical game; it is a fantastic
introduction to both cooperative games and deck builders.

When you start the game, it will display the game state in several boxes for
the various cards, heroes, etc. Those take up about 45 (for 1-2 heroes) or 65
(for 3-4 heroes) lines. The rest of the available lines are used for a game
log.

The log has a running description of various actions and events, and is where
the game will prompt you for input (prompt lines are displayed in green). The
log remembers 1000 lines. You can scroll the log up and down with the arrow
keys. Pressing space will jump the log back to the bottom without changing any
game state. Pressing a valid input key will also scroll the log to the bottom,
and your input will be accepted.

The game will mostly prevent you from performing illegal actions. Inputs that
aren't one of the listed options (or navigation keys) are ignored. If you pick
an option that breaks the rules, the log will tell you and either ask for
another input or send you back to the main turn "menu". HOWEVER! the game will
typically not stop you from making stupid choices. It's entirely possible to
waste healing on heroes that are already at full health or stunned, for
instance. There's no undo (seriously, that's super hard to implement) so take
care. Sometimes an action triggers an effect that needs input, and it's
surprisingly easy for that to interrupt the "flow" of a turn and trip you up.

## Notes
Card types are represented via color. Spells are ref, allies are blue, items
are yellow -- just like the cards in the physical game. If you know the Harry
Potter universe, you should also be able to tell by name. :-)

I use a terminal that supports unicode, and I think most modern terminals do,
so the symbols for the various tokens are unicode characters (ϟ💰💜💀🃏). Most
of them are 2 bytes wide, which makes them "pop" nicely on the screen, but can
lead to some display glitches if they're printed right at a window boundary. If
the symbols don't display on your terminal, or cause other issues, you can edit
`constants.py` and change them.

Hero displays take 3/4 of the space below the Villains/Market windows. If you
have 4 heroes, it can be a little cramped, especially when you play game 7 and
start adding horcruxes to your list of abilities. I haven't figured out a good
keymap for scrolling hero (or other) windows, and scrolling is hard (just look
at the mess that is scrolling the log), so for now the overflow is just not
visible. You can cycle through a view views (everything, hand, play area,
discard) with the tab key. If the dedicated view still isn't enough to see your
whole hand, you'll just have to deal with it! (And if you want to contribute
scrolling controls, send me a PR!)

Similarly, the Dark Arts window can only show 5 cards. If you're unlucky in
later games, you may have turns where more than 5 are played. As with the hero
display, the overflow won't be visible.

The difficulty scales pretty steeply with the number of heroes. The game is
challenging with 4 heroes past game 3, but I win most of the time with 2 heroes
at game 7.

Ginny and Luna are from expansions, and their mechanics assume you've got the
rules from all 7 games. Most notably, their hero ability is scaled to be
somewhere between the game 3 and game 7 hero abilities. I've not adjusted the
scaling, though I have made it so they get no abilities before game 3, like the
OG heroes.

There are times where the rules are slightly ambiguous, like if discarding
cards from being stunned triggers the Defense Against the Dark Arts proficiency
ability. In most cases I've chosen to interpret them as favorably to the player
as I can. Where possible, I've made ordering unimportant: if a card gets a
benefit from playing another card, the benefit applies regardless of card is
played first. There are, however, situations where this is impractical. Mostly
that's around playing cards that give you benefits that are prevented by a
villain you later defeat. Sometimes you'll want to play cards and assign damage
carefully to maximize your benefits. There are other scenarios where you might
gain and lose health, which ought to cancel out, but if you started at full
health and the gain comes first, you'll gain nothing and then lose health.
These situations are somewhat rare, and even more rarely make or break your
victory, but they do come up.
