# What was measured

Roughly 600 simulated matches. The scenario throughout: the player never moves,
their tank and healer run the default lane-push routine, and we measure whether
the enemy team can destroy the player's base.

## Two structural bugs worth remembering

Both were invisible for many versions and both were found by measurement rather
than by reading the code.

**`WORLD_W` was derived from `BASE_W`.** A change that doubled the logical
resolution to zoom the desktop camera out also doubled the map, from 4000 to
8000 units. Lanes became twice as long, waves never met, ~39 creeps piled up
alive, and the enemy's deepest push in a whole match was still on its own half.
Every experiment run during that period measured a broken map. *Anything
describing the world must not be derived from anything describing the view.*

**`threatNear` counted only enemy heroes.** A hero being shot to pieces by a
tower, with no enemy hero nearby, did not register as being in danger and never
retreated. 97% of enemy deaths were to towers the AI did not consider dangerous.

A third, smaller: several constants measured *against* `TOWER_RANGE`
(`LANE_TOWER_KEEP`, `EARLY_LEASH_X`, camp placement) were typed as literals and
silently became wrong when the range changed. They are derived now.

## What worked

| change | effect |
|---|---|
| tower damage 220 → 100 | 0% → ~40% base kills. At 220 a tower one-shot most heroes so `siegeViable` was false for everyone and the AI would never engage a building at all |
| health-first AI builds | outposts destroyed 3.6 → 4.0 of 4 |
| tank leads, ranged shelter behind | deaths 8.9 → 1.8/game |
| allies in front count as shield | 72% → 80% |
| a *retreating* ally stops counting | deaths 4.8 → 2.6, wins held |
| tank clears the wave while blocking | fastest median win measured (359s) |
| orb collection radii widened | 76% → ~90%; 8.2 orbs were lying uncollected at any moment |
| XP doubled + level curve +15 → +8 | levels 9-10 → 13-16, and ~95-100% |

## What did NOT work

Recorded because these are the expensive ones to rediscover.

- **Faster waves** (20s → 12s): nothing. More creeps feed the towers.
- **Cheaper buildings**, three separate attempts (outposts 400→300, →200, base
  500→250): worse every time. Faster-falling outposts pull the attackers into
  the base guns before they are ready.
- **A symmetric surge wave** (5 big + 10 small per lane, both teams): worse.
  A defending wave fights alongside its towers, so doubling both waves helps
  whoever is defending.
- **Longer matches with strong towers**: 8 minutes gave *fewer* base kills than
  6. Time only multiplies an already-winning position.
- **Grouped push, naive version**: handing three heroes the same lane left them
  601 units apart, trickling into the defence one at a time — worse than each
  holding its own lane.
- **Raising XP alone**: does not raise levels. It makes the enemy win *sooner*
  (238s, then 200s, then 157s), so they farm less. Levels were capped by match
  duration, not income.
- **Making the carry more cautious**, three ways (two-creep shield, wider shield
  window, retreat at 60%): every version reduced deaths and reduced wins in
  proportion.

## Base range mends three times as fast, and costs the AI nothing

`BASE_REGEN_MULT` triples both regen rates inside your own main tower's range.
It is a player-facing convenience — walking home is a move rather than thirty
wasted seconds — so the thing worth measuring was whether it quietly hands the
idle-player scenario a win it did not have. It does not. Two matched 80-game
sweeps, everything else identical:

| | base destroyed | outposts | tower dmg | enemy deaths | median win |
|---|---|---|---|---|---|
| `BASE_REGEN_MULT` 3 | 77/80 | 3.9 | 1543 | 0.6 | 226s |
| `BASE_REGEN_MULT` 1 | 75/80 | 3.9 | 1550 | 0.8 | 227s |

Two games and one second apart on eighty — noise. Both sides get the bonus and
both bases are the same size, and the enemy AI has no "go home and heal"
behaviour to exploit it with, so the only hero it reliably changes is the
player's own, who in this scenario is standing in his base doing nothing anyway.

## A river doubles mana regen, and one 80-game run will lie to you about it

`RIVER_MANA_MULT` doubles mana regen — mana only — while a hero stands in a
river, on top of whatever the base ring is paying. Four 80-game sweeps, two of
each configuration, everything else identical:

| | base destroyed | outposts | tower dmg | enemy deaths | median win |
|---|---|---|---|---|---|
| `RIVER_MANA_MULT` 2, run 1 | 77/80 | 3.8 | 1528 | 0.7 | 202s |
| `RIVER_MANA_MULT` 1, run 1 | 74/80 | 3.8 | 1529 | 0.6 | 223s |
| `RIVER_MANA_MULT` 2, run 2 | 79/80 | 3.6 | 1466 | 0.9 | 234s |
| `RIVER_MANA_MULT` 1, run 2 | 78/80 | 3.9 | 1552 | 0.8 | 227s |

**Run 1 on its own reads as a 21-second speed-up and it is not one.** Against
three same-configuration runs that had clustered at 223-227s, 202s looked like a
real effect — cheaper mana, more shots fired, a faster push — and the second
pair of runs put the same configuration at 234s, on the other side of the
control. The `x2` spread is 202-234 and it straddles both `x1` values.

The lesson is the one `docs/SIM.md` already gives and this nearly ignored: on
this scenario 80 games fixes the *median win* to something like +/-15s, so a
difference smaller than about 30s is not a difference until a second pair of
runs says the same thing. Base kills behaved: 156/160 with the bonus against
152/160 without.

## The aggression/deaths trade

It held almost the whole way: safer carry, fewer wins.

| build | base kills | deaths/game |
|---|---|---|
| cautious | 64% | 1.1 |
| free damage when shielded | 72% | 2.5 |
| allies count as shield | 80% | 4.8 |

It only bent once — when the shield model was corrected to exclude *retreating*
allies and the tank was allowed to clear creeps while blocking. That improved
wins, speed and safety together, because it fixed two wrong beliefs rather than
tuning a threshold.

## Match length

Shipped configuration, buildings at full strength:

| length | base destroyed |
|---|---|
| 5 min | 60% |
| 6 min | 68% |
| 7 min | 72% |
| 10 min | 95% |

The median win is ~250s in every case — the difference is entirely the tail.
Games that stall need eight or nine minutes, usually after an early death costs
a full push cycle.

In every match where the base survived, the enemy still led on points.

# Rendering cost

Everything above is balance, measured in the Node harness. This section is
frame cost, measured in headless Chromium on a 4-core box with no GPU. Absolute
milliseconds there are much worse than on real hardware — the raster is
software — but the *ratios* and the op counts hold, and every number below is
measured, not estimated.

## The one that mattered: the canvas was six times too big

`W` and `H` are **world units**. `VIEW_AREA` fixes how much map is on screen,
so on desktop `W` is ~3200 while the stage might be 1300 CSS px wide.
`applyLayout` handed those straight to `setupCanvas` as the pixel size and then
multiplied by `DPR` on top. At a 1280x800 viewport that is a 6.4-megapixel
canvas painting a 1.0-megapixel display; on a retina desktop (`devicePixelRatio`
2) it is 25.6 megapixels. Every full-frame pass paid it: the background blit,
the water, the fog composite, the vignette.

The browser was only downscaling the surplus away again, so capping the
world-to-pixel scale at what the display actually has changes no pixel a player
can see. Verified by magnifying the same seeded map 3x side by side.

| | before | after |
|---|---|---|
| frozen scene, med frame | 71.8 ms | 21.1 ms |
| live match, med frame | 73.3 ms | 26.4 ms |
| live match, fps | 6.5 | 18.9 |
| game seconds per 60s of wall clock | 19 | 56 |

That last row is the honest summary: the sim was running at a third of real
time and now runs at ~93% of it.

## The premise of the bug report did not hold

The report was "slow for the first minute, then it gets better". Frame cost
does the opposite — it *rises* with game time, because ally creeps, on-screen
creeps and ground orbs all grow. Nothing in `render()` or any `draw*` function
is gated on match time; the only reads of `timeLeft` are in the AI.

| per frame | game 10-15s | game 120-125s |
|---|---|---|
| `drawImage` | 36.6 | 135.4 |
| `ctx.save` | 220.2 | 492.2 |
| `lineTo` | 2128.6 | 3208.4 |
| vision sources | 16.0 | 28.9 |
| live xp orbs | 10.6 | 170.4 |

`isEarlyGame()` (120s) and `inEarlyPeace()` (20s) look like first-minute
suspects and are not: they only widen the AI's orb and camp search radii, over
3 camps and a handful of orbs.

## What IS elevated at the start, and it is raster, not code

`drawWater` costs ~21 ms/frame for the first ~100 frames of **every** match and
~8 ms after — on *byte-identical* op counts (same `polyPath` calls, same
`lineTo` count, same caustic fill area). It is Skia warming its pattern and path
caches for a freshly generated river, and it recurs per match, not per page.
Nothing can be precomputed to dodge it: the only thing that warms a raster
cache is rasterising. So the load screen holds until a few real frames have
been drawn behind it, and those frames take the hit instead of the opening
seconds of play.

The hold is a flat three seconds by choice, not by measurement — long enough
for the cloud reveal that follows it to have a run-up. It still waits on the
warm frames as well, so on a slow device it is the work that sets the length,
not the constant.

`startRound` itself is one 250-267 ms frame, 121 ms of which is
`drawBackground` baking the 4000x4000 ground canvas. Note that a plain
`performance.now()` around it reports only ~28 ms: canvas calls are recorded,
not executed, so the cost does not appear until something forces the raster.
Measure it with a flush or you will conclude there is nothing there.

## Where the rest of the frame goes

`drawFog` is 82-86% of `render()` at every point in a match. Stubbing it out
took the frame from 65.6 ms to 8.4 ms. Its own off-screen cull at the top of the
carve loop rejects **nothing**, ever, because `W x H` is 40% of a 4000x4000
world — every vision source is always on screen.

`rebuildVision` registers every ally creep as a vision source, and
`carveVision` then sorts a 46-ray fan plus 8 rays per nearby tree and lays down
a clipped radial-gradient fill per source. It is the largest single op emitter
in the frame.

The untaken lever: skipping the carve for ally-creep sources only, leaving the
vision *logic* untouched, measured `drawFog` 47.6 -> 33.1 ms/frame. It is not
done here because it changes the picture — creeps would stop lighting up
terrain — and that is a design call, not an optimisation.

Two smaller ones, both late-game growth rather than opening cost:
`drawCoinSprite` is 61% of all `drawImage` calls after two minutes (170 orbs
alive with an idle player), and `drawCreep` does 2-4 `ctx.save`/`restore` per
creep.
