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
