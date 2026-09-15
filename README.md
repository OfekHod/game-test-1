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
tools/
  artifact-html.js  strips the document skeleton for a Claude Artifact build
  shoot.js          drives the game headless and photographs it
  music-demo.js     the music on a page with both of its dials and a voice picker
  music-render.js   the piece, and each forest voice, written out as WAV files
  sfx-demo.js       every sound effect on a soundboard
docs/
  GAMEPLAY.md      screenshots from a played match and a survival round
  FINDINGS.md      what was measured, including what did NOT work
  TUNING.md        every constant that matters and the evidence for its value
  AI.md            how the enemy team thinks
  SIM.md           how to run experiments
  MULTIPLAYER.md   LAN plan and what internet play would additionally cost
  TUTORIAL.md      proposed in-game tutorial: phases and how it is built
  OPEN_WORLD.md    proposed Open World mode: seeded, endless, streamed jungle — plan only
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

## Adaptive music

The match theme answers two questions about where you are standing, on two
separate axes, and it answers them differently on purpose.

**Enemy heroes — the threat.** A share per living enemy hero, one over the
distance, 1 at 250 units and 0 at 1600, added and capped. It brings a celeste
above everything else in the piece, then a pulse, then a heartbeat and a held
minor ninth. The layer you can hear is a head count: one hero gets the celeste
and cannot reach the pulse, two get the pulse, only three get the dread.

**Mobs — the forest.** The same arithmetic over the neutral camps: 1 at 300
units and 0 at 1100, with the apex counted from 1.8× further out. This is good
news, not bad, so it never touches the celeste and never sours anything. It
plays one of four forest voices instead, and there is exactly one live at a
time:

| | | |
|---|---|---|
| `grove` | **Rosewood** — a marimba lilting three against the four-beat bar | |
| `hunt` | **Hand drums** — palm, heel and fingers, no pitch at all, and a bass that walks | |
| `glade` | **Glass hum** — a held hum over the chord with a low bell in the gaps | **in use** |
| `horns` | **Horn call** — two long calls a chord, a fifth apart, answered at the top | |

**Glass hum is the adopted voice** and the other three are kept on purpose.
They are not dead code waiting for a tidy-up: they are written, levelled
against each other and reachable from both pickers, they cost a few hundred
events in a list that is walked by a cursor and never searched, and the reason
a choice was built rather than a single voice is that the choice may be made
again — for a boss, a night, a second mode or a second opinion.

**The picker is on the pause menu**, under Resume, and pressing one while the
game is paused previews it immediately — the forest number is frozen while
nothing moves, so a press pushes it past the second layer for as long as the
menu is up and the first frame after Resume writes the real number back.
`index.html?mob=grove` (or `hunt`, `glade`, `horns`) does the same from the
URL, which is a shortcut and not the control: the published build runs inside
a host page whose address bar is the host's, so a query string may never reach
it. The forest fades out completely as the threat rises and is silent from the beat the celeste speaks, so the two cues can never
argue — in Open World, where there are no enemy heroes, it is open all round.

`?musicdebug` draws both rings around the hero you are driving and prints both
numbers, which voice is live, and how many mobs are feeding the second one.

To hear it without playing, `node tools/music-demo.js out.html` writes a page
with both dials, the voice picker and a meter per layer; its **Hear all four**
button plays each voice for eight seconds in order. To get the sound out of the
browser entirely, `node tools/music-render.js out/` writes the piece and each
voice as a WAV. Both lift the synth and both pieces out of `index.html` between
the `music:engine` markers, so what you audition is what plays in the game.

## Fast-forward

`index.html?speed=N` steps the game loop N times per rendered frame, up to 32.
It exists because headless Chromium renders at ~10fps and the loop caps `dt` at
0.05s, so game time crawls at about half real: 45 seconds of match clock costs
124 seconds of waiting, and the median win at 214s costs the better part of ten
minutes. At `speed=8` that same 45 seconds costs 20.

It works over `file://` only. The published build is served over https, where
the flag does nothing at all — a URL nobody can speed up.

The game logic is unaffected: stepping `update(dt)` in a loop is exactly how
`sim/harness.js` has always driven a match. What does change is anything paced
by the render cadence rather than by `dt` — a fade, a camera ease, a particle
burst — because `render()` still runs once per frame. Use it to reach a state,
not to look at a transition.

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
