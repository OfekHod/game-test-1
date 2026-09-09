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

Trees, bushes and rocks are drawn from three sprite atlases. Everything here is
world-shape rather than numbers on a hero, but it is all solid, so it is all
tuning.

| constant | value | note |
|---|---|---|
| `DECOR_SCALE` | 2.5 | on top of each sprite's own size; below this a tree was a shrub you could see over |
| `TREE_COUNT` | 32 | loose trees, on top of the camp rings and the corridor clumps |
| `BUSH_COUNT` / `ROCK_COUNT` | 118 / 62 | objects, not patches — a patch is 1–5 of them |
| `PROP_TALL` | 95 | a bush drawn this tall stands up: solid, and it hides you. Every rock does |
| `PROP_BAR_HALF` / `PROP_BAR_T` | 0.40w / 6 | what a prop blocks: a horizontal bar at the foot of its sprite |
| `TREE_PATCH_MAX` / `TREE_MIN_GAP` | 3 / 104 | a stand is up to three of ONE silhouette; the gap is still twice a trunk's collide radius |
| `DECOR_ROAD_KEEP` | 130 | beyond the road edge. Solid scenery at the old 40 deflected a retreat into a tower |
| `DECOR_TOWER_KEEP` | 300 | tower clearings stay clear |
| `DECOR_CAMP_KEEP` | 90 | beyond the camp ring, so a clearing you have to walk into stays walkable |

Solid scenery cost nothing measurable: 120 games came out at 112/120 bases
destroyed against 111/120 for the same build without any of it.
