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
| `BUSH_COUNT` / `ROCK_COUNT` | 118 / 62 | objects, not patches — a patch is 1–5 of them |
| `PROP_BAR_HALF` / `PROP_BAR_T` | 0.40w / 6 | what a prop blocks: a horizontal bar at the foot of its sprite |
| `TREE_PATCH_MIN/MAX` | 2 / 5 | a stand is two to five of ONE silhouette |
| `TREE_PATCH_SPREAD` / `TREE_MIN_GAP` | 285 / 150 | at 128 and 104 a stand was a pile: the canopies read as one lumpy mass |
| `FOREST_BUSH_K` | 1.02 | the camp ring is berry bushes at the size the pre-atlas build drew them, ~90 across. At 2.35 the ring was a wall of green with no bushes left in it |
| `SHORE_TREE_CHANCE` | 0.17 | rolled per candidate spot on a bank. Four to sixteen trees a map, which is the point |
| `SHORE_LAKE_SAMPLES` / `SHORE_TREE_GAP` | 9 / 40 | spots tried around each lake, and how far off the water a trunk stands |
| `DECOR_ROAD_KEEP` | 130 | beyond the road edge. Solid scenery at the old 40 deflected a retreat into a tower |
| **`DECOR_TOWER_KEEP`** | **`TOWER_RANGE` + 120** | see below. This one is not cosmetic |
| `DECOR_CAMP_KEEP` | 90 | beyond the camp ring, so a clearing you have to walk into stays walkable |

All of it together costs nothing. 240 games each, this map against the same
build with no scenery on it at all:

| | no scenery | shipped |
|---|---|---|
| base destroyed | 221/240 (92%) | 219/240 (91%) |
| median win | 268s | 264s |
| enemy deaths/game | 0.85 | 0.85 |
| end levels | 12.0 / 14.5 / 8.6 | 12.2 / 14.5 / 8.3 |

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
