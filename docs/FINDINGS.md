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

## The pass after that: work nobody can see

Same box, same headless Chromium, same method. Two benchmarks, because the
match scene is too noisy to read a 10% change out of: a live Match at 45s
(what a player sees, but every run plays a different match, and three runs of
the *identical* build measured 108, 135 and 152 ms/frame), and an Open World
round on a fixed seed with the camera parked at the base, which repeats to
about 3%.

**The title screen was rendering the whole world behind an opaque painting.**
`#startScreen` and `#introScreen` set solid backgrounds — `#EEEAE2` and
`#0a0f16`, not the translucent veil the pause and end screens use — so nothing
the canvas paints while either is up can be seen. `update()` already returned
early there; `render()` did not. Sitting on the menu cost **89.9 ms a frame**,
forever, for a picture nobody can look at. The loop now skips `render()` while
either screen is up, and the menu runs at the frame cap (16.7 ms, i.e. idle).
A round *loading* still renders: those frames are the deliberate warm-up above.

**The fog carve was paying twice for one shape.** `carvePass` clipped to its
60-odd-sided ray polygon and then filled the polygon's bounding box with the
rim gradient *through* that clip. Filling the path directly with the same
gradient is the same picture for one rasterised shape instead of two, over the
disc instead of the square around it. With it, a source whose disc lies inside
ground another source has already carved to full white is skipped outright —
the mask composites with `lighter`, and white on saturated white cannot move a
pixel — and an empty mask no longer pays for a filtered draw at all.

Five interleaved runs a side on the Match scene, medians (the new build was
ahead in all five pairs, which is what makes a 7% median readable at all in a
scene that noisy), and three a side on the fixed-seed world:

| | before | after |
|---|---|---|
| Match at 45s, render | 138.3 ms | 129.2 ms |
| Match at 45s, update | 2.41 ms | 1.73 ms |
| Match at 45s, **worst frame** | 345 ms | 168 ms |
| Match at 45s, canvas calls/frame | 11,707 | 10,047 |
| Open World, fixed seed, render | 79.0 ms | 74.3 ms |
| Open World, update | 1.15 ms | 0.91 ms |
| title screen | 89.9 ms/frame | 16.7 ms/frame |

The worst-frame row is the one to care about, and it halved in every pair. The
hitches were not raster: they were the HUD writing styles the browser then had
to re-lay out for the next `getBoundingClientRect`, sixty times a second, plus
the garbage a frame's worth of vision sources and their tree lists made. Both
are gone — writes are guarded on the value actually changing, the two boxes are
cached against `layoutSeq`, and the sources are pooled.

### What did NOT work, and is worth not trying again

**A canvas filter costs the whole source surface, not the region drawn.** The
fog's blur — `fogCtx.filter = blur(2.8px)` over the 1280x800 mask — is 22 ms of
a 75 ms frame, the largest single item left. Drawing only the strip the carves
landed in (`drawImage` with a source rect) changed nothing. Blurring a 64x64
corner of the mask changed nothing. Copying the lit strip onto a surface its
own size first and blurring that changed nothing either: 72.5 vs 74.9 ms, both
inside the noise. The cost is in having a filter at all. The only lever left on
it is `FOG_SCALE`, and that one is visible.

**A spatial grid for the trees and props is not where the time is.**
`resolveSolidCollision` is 7.5% of `update()` in the Node profile — the largest
named callee — but `update()` is 2 ms of a 75 ms frame, so the whole of it is
0.15 ms. Ordering the candidates to keep the push-out order identical would
cost most of that back.

**Match medians move by 20 s between 40-game samples.** Three consecutive
40-game runs read 20 s faster than the baseline's three and looked like a real
regression; at 120 games a side the two builds agree (99% and 98% base kills,
185 s and 188 s medians). Do not believe a 40-game median to better than that,
whatever `docs/SIM.md` already told you.

## The open world's frame: it was the fog, and the lever was not visible after all

Method as above — headless Chromium, `--disable-frame-rate-limit`, software
raster — but the scenes are the open world's, and every number below is a
median over a twenty-second sample, the builds run **interleaved**, A B A B A B,
because a scene this noisy cannot be read any other way (the pass before this
one learned that the hard way).

The first thing the pass produced is not a number, it is the readout that finds
them. `?owdebug` now prints the frame total and its two halves, the worst frame
of the second **and what that frame paid for** (bake, chunk build, region
build), the tile blit count, `resolveSolidCollision` calls a frame, the fog's
largest near-tree set, the ground sprites drawn, and the heap where the browser
exposes it — §10.4(a) of `docs/OPEN_WORLD.md`, in full, and `drawFog` is broken
into carve / sheet / blur / out. Without the last of those this pass would have
optimised the wrong thing twice.

### Where an open-world frame went

Walking straight out on seed 42, desktop 1280x800:

| | ms a frame |
|---|---|
| fog | 21.0 |
| — of which the finished sheet stretched over the screen | 14.2 |
| — of which the blur | 6.5 |
| — of which the carve (the part everyone assumes is the cost) | 0.2 |
| ground sprites (128 of them) | 9.4 |
| tile blits (30 of them) | 0.06 |
| minimap, water, sky, overlays, sort | 1.2 |
| `update()` — the whole game | 0.3 |
| **frame** | **33** |

The carve is 0.2 ms. `FOG_NEAR_MAX`, which PR3 added to bound it, was solving a
problem worth a fifth of a millisecond. What the fog actually costs is the two
full-surface operations at the end of it, and both of them scale with the size
of the surface rather than with anything in the scene.

### `FOG_SCALE` 0.8 → 0.5

The previous pass wrote: *"The only lever left on it is `FOG_SCALE`, and that
one is visible."* It is not. Everything that surface carries is either a linear
gradient or a polygon that gets blurred on the way out, and `FOG_EDGE_SOFT`
scales with `FOG_SCALE`, so the feather stays the same width on screen. Halving
it halves the source of both the blur and the stretch.

Three interleaved pairs, sixty-second walk, desktop:

| | 0.8 | 0.5 |
|---|---|---|
| frame, run 1 / 2 / 3 | 34.3 / 33.5 / 35.1 ms | 19.9 / 20.4 / 20.4 ms |
| worst frame in any second | 54 / 53 / 56 ms | 32 / 33 / 33 ms |
| fog | 21.5 ms | 8.9 ms |

And the two scenes §10.4 asks for besides the walk — a nine-camp grove with
three heroes in it, and the phone (`iPhone 13`, which at device-pixel-ratio 3
rasterises *more* pixels than the 1280x800 desktop and is where this hurt most):

| | 0.8 | 0.5 |
|---|---|---|
| grove, frame | 51.8 / 57.7 / 55.8 ms | 31.4 / 18.8 / 31.9 ms |
| phone, frame | 55.0 / 59.3 / 60.8 ms | 18.8 / 22.1 / 18.9 ms |
| phone, fog | 45–50 ms | 17.2 ms |
| phone, worst frame | 76 / 76 / 79 ms | 30 / 55 / 32 ms |

The phone is three times faster for a constant.

Every pair favours the smaller surface and none of them overlap. The pictures
were compared side by side at the base and inside a nine-camp grove, where the
tree-shadow fans are the crispest geometry the mask ever holds: they are the
same picture. Both ends of the range were measured too — **1.0 costs 45 ms**
(a bigger surface, and no 1:1 fast path to be had), and 0.4 is 16.7 ms and
still looks right. 0.5 takes 85% of the available win and keeps a mask that is
still half the screen, which is the one that will survive a display nobody has
tested on.

Two things that sound like they should have worked and did not, both inside the
noise: turning **image smoothing off** for the final stretch (14.9 → 14.3 ms —
so the cost is not the filtering) and dropping **`globalAlpha`** from it
(14.9 → 14.5 ms — nor the blend).

### What the streaming actually costs, now that it can be seen

§10.4 worried about a frame that pays a region build, a chunk build and a tile
bake together: 8 + 6 + 6 ≈ 20 ms on top of the game. In sixty seconds of
walking, **the worst frame of every single second paid none of the three** —
`worst 32(bake 0 gen 0 region 0)`, over and over. The 2200-unit look-ahead
keeps them apart, exactly as designed. The worst frames are plain render
spikes.

### Two more measured out of the plan

- **Rivers.** §5 planned per-stretch sub-paths for a 12,000-unit river, and
  `docs/OPEN_WORLD.md` §10.4(c) a warm-queue comparison. Water draws in
  **0.1–0.3 ms** with three rivers on screen. There is nothing there to cut.
- **`forChunksAround`.** The narrowing §11 holds in reserve for
  `resolveSolidCollision` is unnecessary for a second reason on top of the one
  the last pass found: the readout counts **3 calls a frame**, not the hundreds
  the idea was sized against. Mobs outside `CAMP_TICK_R` do not move, so they
  do not collide.

- **The tree's tilt is free, and so is the save/restore around it.** §11 held
  "sprite save/restore trim if the grove scene bites" in reserve, on the theory
  that `drawTree`'s `save/translate/rotate/scale/restore` is five calls where
  one would do. Ground sprites are 9–10 ms of a 20 ms frame, so it looked like
  the next thing to cut. Removing the rotation **entirely** — the strongest
  version of that fix, and one that changes the picture — measured 20.3 / 21.0 /
  20.9 ms against a baseline of 21.0 / 20.8 / 21.8: nothing. The cost is
  rasterising 128 sprites, at about the same nanoseconds per pixel the fog
  stretch pays, and no amount of transform bookkeeping touches it. Fewer or
  smaller sprites would, and neither is on the table.

### The last two §10.4 measurements, and the dead queue one of them found

**(c) A river entering view is one bump, not a ramp.** §3.5 designed a *warm
queue*: rasterise a new river or lake at real size before the frame's clear, so
its paths and patterns are cached by the time it can be seen, and §10.4(c) asks
for the hundred frames either side of one arriving, with and without it. The
comparison cannot be run, because **`owWarmQueue` was declared and cleared and
never once written to** — the queue was never built. So the measurement became:
is it needed? Timing every frame across six rivers entering the world:

| river enters at frame | 100 frames before | that frame | 100 frames after |
|---|---|---|---|
| 352 | 34.6 ms | 46.3 | 35.9 |
| 518 | 33.0 ms | 54.5 | 38.0 |
| 705 | 52.0 ms | 72.7 | 61.0 |
| 985 | 54.3 ms | 57.7 | 45.1 |
| 1081 | 45.3 ms | 53.6 | 36.9 |

The arriving frame costs 10–20 ms more than its neighbours; the hundred after
are indistinguishable from the hundred before, and two of the five are *faster*
afterwards. One bump, no ramp — so there is nothing for a warm queue to warm.
The dead array is deleted. (Absolute numbers are high here because the probe
build records every frame into an array; the comparison is within one run.)

**(d) Nothing grows.** Walking straight out for three minutes, first sample
against last:

| | at 2,257 | at 29,952 |
|---|---|---|
| explored | 2.5 km² | 46.1 km² |
| heap | 20 MB | **20 MB** |
| tile pool | 64/64 | 64/64 |
| loaded chunks | 20 | 57 |
| mobs | 54 | 77 |
| fog sheets | 1 | 3 |

The heap does not move across 27,700 units and eighteen times the explored
ground. The pool sits on its cap, which is what a cap is for; chunks and mobs
rise with the loaded window and stop there. `riverCache` goes 95 → 129, which
is the "no source here" markers accumulating — one boolean per region, and the
only line on this table that grows without a bound, worth a look if a session
ever runs for hours.

### A caveat about every per-call number above

Canvas work is deferred: a `drawImage` returns before the pixels exist, and the
bill lands at the next flush, inside whatever happens to be timed then. The
per-part numbers move between scenes in ways the scenes do not explain — the
tile blit reads 0.06 ms while walking and 7 ms parked in a grove, for the same
thirty to forty blits — and only the **frame total** is trustworthy to better
than a few milliseconds. Every claim in this section rests on frame totals and
on interleaved runs; the breakdown is for finding things, not for scoring them.
