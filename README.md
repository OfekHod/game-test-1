# Lane — browser MOBA prototype

A single-file browser game: two teams of three heroes, two lanes, four outposts
and a base per side. You control one hero directly and switch between them; the
other two follow a deliberately simple lane-push routine so you always know
where they will be.

## Layout

```
index.html         the game — open it in a browser, nothing to install
sim/               headless simulation harness (Node, no dependencies)
  harness.js       lifts the game out of index.html and instruments it
  run.js           headline result for the shipped configuration
  parallel.js      same report, one worker per core
  match.js         one match + the report, shared by run.js and parallel.js
  sweep.js         one configuration per invocation, one comparable line out
  analyse.js       timeline: when buildings fall, deaths, farming intensity
  stub.js          minimal DOM so the game runs under Node
docs/
  GAMEPLAY.md      screenshots from a played match and a survival round
  FINDINGS.md      what was measured, including what did NOT work
  TUNING.md        every constant that matters and the evidence for its value
  AI.md            how the enemy team thinks
  SIM.md           how to run experiments
  MULTIPLAYER.md   LAN plan and what internet play would additionally cost
  TUTORIAL.md      proposed in-game tutorial: phases and how it is built
```

## Orders

You drive one hero; the other two act on the last order you gave them. There are
four, and each shows as four letters under the hero's portrait:

| | |
|---|---|
| `PUSH` | walking his lane and hitting what stands in it — the opening order |
| `MOVE` | walking to a spot you dragged him to, then holding it |
| `FLLW` | escorting one team-mate: drag a hero onto another hero, or onto that hero's portrait |
| `ASSM` | travelling as a squad behind whoever you are driving (Assemble, `0`) |
| `HOLD` | no order: standing where he was left, fighting what comes to him |
| `YOU` | the hero you are driving |

Orders are given by dragging a hero — from his body on the field or from his
portrait — with either mouse button, or with a finger on touch. Where he lands
decides which order it is: a half of the minimap is a lane, a team-mate is an
escort, open ground is a posting.

The left button is also the trigger, so a left press on a hero only becomes an
order once it travels 16 screen pixels; short of that it is the shot it always
was, and the hero you are DRIVING cannot be picked up with it at all — he stands
under the cursor in every brawl. Use his portrait or a right-drag for him. The
right button has no such conflict and grabs any hero at once.

**Taking a hero over cancels his order.** Focus him and the walk, the lane and
the dotted line all end there; switch away again and he holds that ground rather
than resuming a march you had forgotten about. An assembled squad is the one
order that survives a switch, because it re-forms on whoever you pick up.

## Your base

Standing inside your own base's ring — the faint circle its tower draws on the
field — mends you three times as fast, health and mana both. Nowhere else on the
map does, so a hero on a sliver walks home rather than dying to the next wave.
While you are inside it the HPR and MPR buttons on the stat strip turn green and
show the rate you are actually regenerating at.

## Chopping

Point the tank at a tree with nothing hostile in front of him and swing: three
hits fell it. From the first hit the tree wears what is left of the three as a
bar; on the third it throws three logs clear and goes over away from him,
leaving a stump. The logs arc out, land, and are yours a moment after the tree
has finished falling.

There is nothing to spend the wood on yet and nothing on screen that shows the
count. It is kept so that there is something to build with when there is
something to build.

A swing looks at trees LAST — after enemy heroes, after creeps, after buildings
— so a fight fought in a wood never spends a swing on the scenery. That is also
why, in practice, only the hero you are driving ever fells one: an AI hero
swings because target acquisition handed it something, and acquisition does not
look at trees.

## Running the simulation

```bash
node sim/parallel.js 40                # 40 matches spread over every core
node sim/run.js 40                     # same, single process
node sim/analyse.js 25                 # timeline breakdown
node sim/sweep.js 20 "half tower dmg" "const TOWER_DMG = 100;=>const TOWER_DMG = 50;"
```

A match is pure CPU work, so one process only ever uses one core. `parallel.js`
forks one worker per available core and hands out matches from a shared queue;
on a 4-core machine it finishes a batch in roughly a third of the time. It
detects the core count itself (`--workers N` or `SIM_WORKERS=N` to override).

## Why the harness reads index.html

There is deliberately no second copy of the game source. `harness.js` extracts
the game's script from the shipped HTML and patches counters into it, so a
tuning experiment and the playable build can never disagree. If a hook stops
matching after an edit, the harness throws rather than quietly reporting zeros.

`index.html` holds three inline scripts: a guard that reports a truncated file,
the music synthesiser, and the game. The synthesiser comes first and on its own
so that it can play while the megabyte below it is still arriving — a browser
runs no part of an inline script until it has parsed all of it, so music kept
in the game's script cannot sound until the whole file has landed. The harness
takes the LAST script, which is the game, so nothing under Node ever sees the
synthesiser: the game reaches it through `window.LaneMusic` and copes with it
being absent.

## Known state

Measured over 80 matches with the player idle (never moving):

| | |
|---|---|
| enemy destroys your base | 79/80 (99%) |
| median win | 214s of a 600s match |
| enemy deaths per game | 0.65 |
| end levels | carry 11, tank 13, support 7 |

The push got faster when the tank's rocket did: the same 80 matches against
the previous rocket (90 radius, 3s stun, no vulnerability window) finish
75/80 with a median of 252s. Both teams own a tank, and only one of them is
being driven by a player who never moves.

The support is the weakest part of the design: it heals rather than last-hits,
so it collects far fewer experience orbs and finishes several levels behind.
