# Enemy AI

The player's own AI heroes deliberately do only one thing: hold position behind
the wave, attack what it attacks, and pull back before a tower can reach them.
Everything below applies to the enemy team only, so the player always knows
where their own heroes will be when they take control.

## Priority order

1. **Retreat** — sits *above* the mode dispatch, not inside the lane brain. A
   hero under a macro order is in `moveto` mode and never reaches `lanePush`,
   which is why an earlier retreat check did nothing while the tank was cut down.
2. **Tower danger backoff** — ranged heroes leave an unshielded tower's reach
   even mid-push, and keep shooting on the way out.
3. **Siege window** — our wave is under their tower *and will still be alive when
   we arrive*. Outranks farming, orbs, and chasing.
4. **Farm / orbs / lane**.

## Shielding

The core idea the whole siege game rests on: a tower fires at one thing and picks
the nearest by edge distance. Standing in its range is safe while something of
yours is closer to it.

`towerShieldTime` pools the HP of everything closer to the tower than you —
creeps *and* allied heroes, since the tower does not distinguish — and divides by
tower DPS. `towerShieldedAt` then asks whether that outlasts your walk back out.

Two corrections that mattered:

- **A retreating ally is not a shield.** It is about to leave and hand you the
  tower's attention. Counting it meant the carry only discovered its cover was
  gone once it had become the target.
- **The tank shields by position, not by target.** It blocks by standing there,
  so it spends that time clearing the wave in front of it — which keeps the
  *creep* shield alive too. It takes the building only when nothing is in reach.

## Roles

- **Tank** leads. It is the only hero that survives more than a few shells, and
  it dives on a budget: the shells it will eat finishing the building plus the
  shells walking out, capped at 6 seconds of optimism.
- **Carry** shelters 90 units behind the tank and clears the wave. It hits a
  building whenever it is shielded — that damage is free — and never dives an
  unshielded one.
- **Support** holds 110 behind, heals a hurt ally below 60% and stays committed
  until they are topped up.

## Movement

- **Tower avoidance is for travel, not laning.** A lane runs straight past the
  towers guarding it, so arcing around tower range while laning drags a hero 400
  units off its own lane. Crossing the map routes around; walking your lane does
  not.
- Avoidance uses **tangent steering**, not a repulsion field. A field only
  reaches equilibrium where the push balances the pull — measured, it settled 420
  units inside a 673-unit reach no matter how hard it pushed.
- Heroes **steer** at 3 rad/s rather than snapping. Refusing to move during a
  reversal made the hero stall, the AI saw no progress and switched task, and
  reversals went *up*.
- Inside the turning radius (speed ÷ turn rate ≈ 73 units) the limit is dropped,
  or a hero orbits a nearby point forever.

## Chasing

A chase is abandoned 5 seconds after the last exchange of blows, counted as wall
clock from when the chase began — accumulating only on frames where the hero
happened to be hunting ran at half speed and a 5-second limit fired at ten.

## The arena's enemy players

Survival runs a **different** brain, not a smaller one. `survHeroAI` replaces the
macro layer, `updateEnemyCarryAI` and the enemy half of `updateIdleAI` outright:
the macro brain exists to pick which of two lanes to commit to and which of its
own buildings to defend, and in the arena there is one road per hero and nothing
of theirs to defend.

What is left is the push and only the push. No camps, no orbs, no crossing the
map to a team-mate's fight, no truce and no endgame. Targets come from
`laneSeekTarget` with `h.lpath` set to the road the hero walked in on, so "in my
lane" means "on the road" — a player who steps into the trees is not something
the arena follows.

### Arriving

One joins every `SURV_HERO_EVERY` waves from `SURV_HERO_FROM`, in the order
tank, carry, healer, and each attaches to the one before it. They walk in on the
road, at that wave's level, built by the same `AI_BUILD` weights a match hero is
built by — `survSetHeroLevel` runs grantXP's own loop with the experience left
out. A hero still standing from the last wave is levelled where it is rather
than re-spawned, and it keeps its road: newcomers join *its* road, or the carry
walks in on the north lane while the tank it shelters behind came from the
south.

There is no respawn timer. Kill one and it is gone until the next wave brings it
back — which is the whole reward for turning round to fight a hero instead of
clearing the pack.

### A lane's guns come down in order

`pushTowers` narrows what an arena hero may *attack*: while an outpost on the
road it walked in on still stands, your base is not on its list. Without it the
carry walked past both outposts behind its wave and deleted a 500hp base in one
mana bar — two full play-throughs that spent their stat points, used their
skills and fought at their own towers were both overrun on wave 8, which would
have made the healer at wave 10 and the column at wave 13 content nobody ever
saw.

It only narrows the CHOICE of target. Tower danger, the keep-out in `walkLane`
and every shielding test still read every tower on the map, because a building
a hero may not attack can still kill it.

### Pacing

Three rules, all applied after the move and all written in distance from the
plaza, which is monotonic along both roads. Each says how deep this hero may
stand; only forward progress is ever undone.

- **Lead the pack, do not leave it.** A hero walks half again as fast as a mob,
  so with no cap the tank arrives half a minute ahead of the wave it came in
  with and dies alone. It may lead the front mob of its own road by
  `SURV_LEAD_AHEAD` and no more, and only while that road still has mobs on it.
  It is a CAP, not a station: a hero that stops to fight gets walked past by its
  own pack and then closes the gap again, which is what it should do.
- **Shelter.** The carry holds `CARRY_SHELTER` behind the tank and the healer
  `SUPPORT_SHELTER` behind the carry — the same numbers a Match uses.
- **The column**, from stage four: nobody is more than `SURV_GROUP_LEAD` ahead
  of the rearmost, so the three of them arrive together rather than in order.

### Backing off

`wantsRetreat` is a latch that holds until the hero is back to 60% health,
because in a Match it can walk to a base that mends it three times as fast. The
arena gives an enemy player no base and no ring, so the latch means natural
regeneration: measured, a hurt carry stood at the mouth of its road for **eighty
seconds** while the wave it walked in with died without it, and twice in ten
waves the whole enemy side was two heroes standing still.

So the arena asks a fresh question every frame (`survWantsBack`) and the answer
moves the hero back down its own road rather than off the map. A step behind the
front rank is cover, and the pack walking past puts it back in the push without
it having to decide anything. `SURV_BACK_HOLD` is the only stickiness it gets.
