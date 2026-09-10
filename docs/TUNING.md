# Constants that matter

Values as shipped, with the evidence.

## Buildings and combat

| constant | value | note |
|---|---|---|
| `TOWER_DMG` | 100 | at 220 a tower one-shot most heroes and the AI would never engage a building; at 30 towers become decorative |
| `TOWER_DMG_TAKEN` | 1.0 | buildings take a hero's hit in full |
| `TOWER_HP` | 400 | outpost. 300 and 200 both tested worse |
| `MAIN_TOWER_HP` | 500 | 250 tested worse |
| `TOWER_REGEN` | 0 | at 4/s regen healed back 82% of all damage the enemy managed, and in the final minute towers healed faster than they were damaged |
| `TOWER_RANGE` | 588 | anything measured against this must be *derived*, not typed |
| `LANE_TOWER_KEEP` | `TOWER_RANGE + 140` | derived |
| `EARLY_LEASH_X` | derived from outpost x + range | was a literal, silently parked heroes inside the guns |
| `CAMP_TOWER_KEEP` | `TOWER_RANGE + 142` | camps are placed best-of-N, not first-that-fits — a hard floor produced a jungle with zero camps |

## Economy

| constant | value | note |
|---|---|---|
| `XP_SMALL_CREEP` | 6 | doubled |
| `NEUTRAL_XP` | 32 | doubled |
| `XP_HERO_KILL` | 120 | doubled |
| `xpForLevel` | `20 + (level-1)*8` | at +15 the enemy's entire match income bought exactly level 10 |
| `AI_ORB_SNAP` | 650 | 230 left 8.2 orbs uncollected at any moment |
| `AI_ORB_PULL` | 900 | |
| `CREEP_SCALE` | 8 (320hp) | must survive more than one tower shell |
| `ROUND_TIME` | 600 | see FINDINGS on match length |
| `EARLY_PEACE` | 20 | 120 was 40% of the match spent not fighting |

## AI shape

| constant | value | note |
|---|---|---|
| `AI_BUILD.carry` | maxHp 5, range 4 | health and range are what let a carry stand near a tower |
| `AI_BUILD.tank` | maxHp 8 + secondaries | pure health capped at level 26 and wasted every later point |
| `CARRY_SHELTER` | 90 | how far behind the tank ranged heroes hold |
| `SUPPORT_SHELTER` | 110 | 170 left the healer three levels down |
| `RETREAT_IN / OUT` | 0.40 / 0.60 | hysteresis, or heroes bounce on the threshold |
| `HUNT_PATIENCE` | 5.0s | chase abandoned 5s after the last exchange of fire |
| `TURN_RATE` | 3.0 rad/s | steering, not a movement veto — a veto made the twitching worse |

## Scenery

Trees, bushes and rocks are drawn from three sprite atlases. Every one of them
is solid, so all of it is tuning.

| constant | value | note |
|---|---|---|
| `DECOR_SCALE` | 2.5 | on top of each sprite's own size; below this a tree was a shrub you could see over |
| `TREE_COUNT` | 32 | loose trees, on top of the camp rings and the corridor clumps |
| `BUSH_COUNT` / `ROCK_COUNT` | 118 / 62 | a CEILING, not a quota. What actually lands is what fits with room around it: about 45 and 38 on Match, 70 and 60 on Survival |
| `PATCH_CLEAR` | 320 | a patch needs its own clearing. Without it the counts were met at any cost, and everything the middle of the map could not hold went to the rim as one solid band |
| `SAME_KIND_KEEP` | 1.25 | in sprite widths, between two DIFFERENT sprites of the same kind. Different kinds are exempt: a boulder among the bushes is a hillside, a bush beside a different bush is a mistake |
| `PROP_BAR_HALF` / `PROP_BAR_T` | 0.40w / 6 | what a prop blocks: a horizontal bar at the foot of its sprite |
| `TREE_PATCH_MIN/MAX` | 2 / 5 | a stand is two to five of ONE silhouette |
| `TREE_PATCH_SPREAD` / `TREE_MIN_GAP` | 285 / 150 | at 128 and 104 a stand was a pile: the canopies read as one lumpy mass |
| `FOREST_BUSH_K` | 1.02 | the camp ring is berry bushes at the size the pre-atlas build drew them, ~90 across. At 2.35 the ring was a wall of green with no bushes left in it |
| `SHORE_TREE_CHANCE` | 0.17 | rolled per candidate spot on a bank. Four to sixteen trees a map, which is the point |
| `SHORE_LAKE_SAMPLES` / `SHORE_TREE_GAP` | 9 / 40 | spots tried around each lake, and how far off the water a trunk stands |
| `DECOR_ROAD_KEEP` | 130 | beyond the road edge. Solid scenery at the old 40 deflected a retreat into a tower |
| **`DECOR_TOWER_KEEP`** | **`TOWER_RANGE` + 120** | see below. This one is not cosmetic |
| `DECOR_CAMP_KEEP` | 90 | beyond the camp ring, so a clearing you have to walk into stays walkable |

### Chopping

A tree can be felled by a melee swing, which in this build means the tank and
nothing else. These are feel numbers, not measured ones — there is no outcome to
measure them against yet, for the reason under the table.

| constant | value | note |
|---|---|---|
| `TREE_CHOPS` | 3 | swings, not damage. A count that does not move with the axe's level is the same count in the first minute as in the last, which is what makes it a rule rather than a race |
| `TREE_BAR_HOLD` | 6 | seconds the bar stays up after a chop. It appears on the FIRST chop: an untouched tree has nothing to report, and 32 trees each wearing a full bar is a forest of health bars |
| `TREE_FALL_TIME` | 1.1 | the topple. The angle goes as the square of it, so the trunk hangs and then lets go; the sprite fades only over the last 18% |
| `WOOD_PER_TREE` | 3 | logs |
| `WOOD_DWELL` | 0.4 | seconds a log is left alone before the magnet takes it, counted from **the tree being gone**, not from the moment the logs appear. Those are a whole topple apart: the logs come out on the felling blow and tumble clear while the trunk goes over behind them (`woodDrops` is drawn after the sorted pass, so they stay on top of it the whole way down), and the sprite is still fading for the rest of `TREE_FALL_TIME`. Timed from the drop, the entire tail expired inside that fade and the logs were never once seen on their own. `spawnWood` is handed the fall as dead time in front of the dwell, so this stays the *clear* time if the topple is ever retuned |
| `WOOD_THROW` | 42 | how far past the trunk the logs are thrown, along the line the blow came in on, so they land on the FAR side of the tree from whoever swung. They used to drop on the stump — which is where the chopper is already standing, and a pickup that lands at your feet is not a pickup, it is a number going up. Measured over three fells, the furthest log ends up 120–156 units out and visibly travels back |
| `WOOD_MAGNET_RADIUS` | 260 | against 130 for the coins. Nobody competes for wood — no enemy hero can take it and no ally wants it — so all three logs can be in range of whoever felled the tree wherever they scattered, instead of the far one crawling in at the shared magnet's slowest speed. It also has to cover `WOOD_THROW`: worst case is a tree felled at the very end of the tank's reach, which puts him ~145 out, plus 42 of throw plus 35 the pop can carry = 222. A log outside this is not collected at all until the player walks back to it, and on a 30s TTL it would rot |
| `WOOD_MAGNET_MULT` | 2.2 | on the shared magnet speed. Safe only because of the overshoot clamp below |
| wood pop speed | 55–130 | against 90–220 for a coin. At coin speed a log could land outside `PICKUP_MAGNET_RADIUS`, and felling a tree you are standing next to left one log stranded a step away |
| `WOOD_TTL` | `ORB_TTL`*2 (30s) | a coin is dropped mid-fight and taken in the same breath; wood is dropped by somebody who went somewhere to chop |

**How long the tail is, and why it was three times that.** Measured from the
logs landing to the last of the three banked, in GAME seconds — what a player at
60fps waits, which is not what a headless browser at 12fps reports as wall time.

| build | logs appear → banked |
|---|---|
| as first written | 1.70s |
| one dwell timer instead of two stacked delays | 0.70s |
| overshoot clamped, dwell cut to a beat | 0.35s |
| dwell counted from the tree being gone | 0.95s |
| logs dropped on the felling blow instead of at the thud | **1.40s** |

The last two rows are longer than the 0.35s above them on purpose, and neither
is a regression. End to end is the wrong thing to measure here — what matters is
how much of it the wood is actually visible for, and at 0.35s the answer was
none of it: the logs dropped while the trunk was still lying across them and the
whole tail expired before the sprite had finished fading. The useful breakdown:

| | felling blow → logs out | logs out → trunk gone | trunk gone → banked |
|---|---|---|---|
| dwell from the drop | 0.68s | 0.40s | 0.0s — already collected |
| dwell from the tree gone | 0.68s | 0.40s | 0.50s |
| logs on the felling blow | **0.00s** | **0.90s** | **0.50s** |

The logs are on screen for all of the middle column as well as the right one —
held only means not yet magnetic, not invisible. Confirmed off a per-frame
canvas capture: the first frame of the topple already has three logs in it, and
they are still there twenty-one frames later when the trunk finishes fading.

Neither of the first two numbers could have been read off the code. The first
was two delays stacking — a log was not offered a collector while its mode was
still `pop`, *and* its dwell only started counting once the pop had ended, and
the pop decays exponentially towards a fixed speed threshold, so it takes most
of a second on its own. The second only gave itself up to a frame-by-frame
trace: the logs were **overshooting the hero and bouncing**.

```
343ms  magnet dd=39  49  36
424ms  magnet dd=41  24  44     <- past the hero and out the far side
509ms  magnet dd=38  63  32     <- flung back out to 63
591ms  magnet dd=42   2  51
```

A pickup drawn in faster than `PICKUP_COLLECT_RADIUS` is wide steps straight
past its collector, so it only lands when a frame happens to put it inside 24
units. `updatePickup` now clamps the step to the distance remaining — but **only
on the fast path**, the one wood passes a multiplier on. The coins' arithmetic
is untouched, deliberately: they are slow enough not to need it, and leaving
them alone is what keeps the seeded simulation below byte-identical.

**A tree is the LAST thing a swing looks at** — after enemy heroes, after creeps,
after buildings — so a fight fought in a wood never spends a swing on the
scenery. That ordering is also what keeps chopping out of the simulation
entirely: an AI hero only ever swings because target acquisition handed it
something, acquisition does not look at trees, so no AI hero ever fells one.
Measured, not assumed — ten full games with a counter patched into `chopTree`
report zero chops, and eight games run from one seed against the build before
this one come out byte for byte the same:

```
node sim/run.js 40   before: 38/40, median 216s, deaths 0.65
                     after:  34/40, median 245s, deaths 0.70
```

That spread is two different samples of forty, not a change: nothing in the
chopping path allocates a random number unless a chop happens, so the same seed
walks the same sequence and the same eight matches end on the same second with
the same score. The numbers below still stand.

All of it together costs nothing that shows in an outcome. 240 games each, this
map against the same build with no scenery on it at all:

| | no scenery | shipped |
|---|---|---|
| base destroyed | 221/240 (92%) | 221/240 (92%) |
| median win | 270s | 281s |
| enemy deaths/game | 0.77 | 0.95 |
| end levels | 12.1 / 14.8 / 8.1 | 12.4 / 15.1 / 9.2 |

The one line that is not flat is deaths, and they are mostly deaths to towers:
0.90 a game against 0.75. That is the same deflection the keep-out below is
about, an order of magnitude smaller — solid ground furniture near a lane
occasionally walks a retreating hero into somebody's guns, and no keep-out short
of removing the scenery makes it exactly zero. It does not reach the result:
bases destroyed is identical to the game.

**But solid scenery must clear a tower's REACH, not its footprint.** This is the
same trap `scatterClumps` fell into and wrote down, and solid bushes and rocks
walked straight back into it. A solid thing standing just inside a tower's
circle deflects a path around it and into the guns. Measured over 120 games
each:

| | no scenery | props at a 300 keep-out | props at `TOWER_RANGE` + 120 |
|---|---|---|---|
| base destroyed | 111/120 | **100/120** | 108/120 |
| enemy deaths to towers | 0.84 | **1.23** | 0.73 |
| end levels | 12.4 / 15.2 / 8.6 | 12.0 / 14.6 / 9.1 | 12.6 / 15.1 / 8.5 |

Ten bases in a hundred and twenty, from a keep-out number. Anything solid that
gets added to the map has to clear that circle.

A note on sample size, because this branch got it wrong three times. At 40
games the band on a 90% rate is roughly ±9 points, which is wider than every
effect measured here — three separate 40-game runs read 98%, 88% and 93% off
builds that were doing the same thing. Nothing under 120 games says anything,
and a claim of parity wants 240.
