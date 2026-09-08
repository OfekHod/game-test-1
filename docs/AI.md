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
