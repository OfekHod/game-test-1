# Tutorial

A third button next to **Match** and **Survival**. Eighteen steps that teach one
mechanic at a time on a map built for the purpose, ending by dropping you into a
real Match.

## Its own map

The tutorial does not run on the Match map. It builds its own: the same
skeleton — a base each side, an outpost guarding each lane, two lanes between
them — and then almost nothing else.

| The Match map has | The tutorial map has |
|---|---|
| five neutral camps in the corridor, each ringed with trees | one camp, where the forest step needs it |
| ~48 loose trees scattered across the world | nine, in one hedge, where the walking step needs it |
| a river down the length of the corridor, and two lakes | one river, across the practice ground, ending short of both lanes |
| two outposts per lane per side — eight buildings | one per lane per side — four |

### The practice box

Everything before the forest step is placed inside a box: `x` up to
`TUT_ARENA_X`, `y` within `TUT_ARENA_Y` of `BASE_Y`, and never closer than
`TOWER_RANGE + 260` to an **enemy** tower.

The box exists because every step places its target relative to where you are
standing, and the show angle points up and to the right — so without a bound the
practice ground *ratchets north-east* across the map. `x` was capped from the
start but `y` was not, and five steps at roughly -0.41 of a radius each climbs
some 780 units: out of the corridor, up toward the top lane, where the enemy's
outpost is. Walking from there to a camp placed further east crossed that
outpost's reach at about **487 units against a range of 588**, which is a dead
hero halfway through a lesson on trees. With the box, the same walk stays 723
out.

Only the enemy's buildings are checked. Your own never shoot you, and a tower
only ever targets the other side's *creeps* — it ignores a forest mob standing
underneath it — so this rule protects the player, not the practice targets.
Checking every building instead fenced the tutorial out of the open ground
beside its own base for no reason, which broke the pack step outright.

Three things are held back on top of that — wave spawning, the enemy team
(parked dead, the trick Survival already uses) and the clock — and each is
lifted by the step that teaches it.

**Earlier drafts shared a map with Match and it never worked.** The first opened
in the Survival arena and rebuilt the Match map halfway through, which teleports
you into a different world at step 14. The second stayed on the Match map, and
the opening kept running into the jungle: camp mobs before the step that
introduces them, treelines that read as forest even with the camps held empty,
the corridor river underfoot, practice creeps sniped by the player's own base.
Each fix moved the arena somewhere else on a map with no good place for it.
Authoring the ground is what finally made the opening quiet.

## The steps

Each step is one card, one thing to learn, one condition that clears it. The
card never blocks play — it is transparent to input except its own buttons, so a
tap that lands on it still shoots. Every step has **Skip step**, and **Exit**
drops you back to the menu.

| # | Step | What comes on | Cleared by |
|---|---|---|---|
| 1 | **Walking** | A three-leg route, ~2200 units: open ground, the river, the hedge | Standing in all three rings |
| 2 | **Shooting** | One forest mob, 330 units out, auto-assist off | Killing it |
| 3 | **The blink** | One forest mob, 470 units out, auto-assist off | Killing it *with the blink* |
| 4 | **Experience and mana** | A pack of five mobs, drops switched on, assist back on | Clearing them and picking up the drops |
| 5 | **Levels and stats** | Stat strip pulses; a level granted if you lack one | Spending a point |
| 6 | **Your squad** | Tank and support walk out of the base | Taking control of each |
| 7 | **Rocket and heal** | A mob each for them | Casting both skills |
| 8 | **Stun, then switch** | A huddle of four tough mobs, awake | A rocket that stuns three, then three kills with the carry |
| 9 | **Orders** | A marked spot on the ground | Posting a hero on it |
| 10 | **Assemble** | The ALL button pulses | Calling the squad back |
| 11 | **The forest** | The camp is stocked and ringed | Clearing it |
| 12 | **Your base** | Your tower's range drawn | Standing inside it |
| 13 | **The map** | — | Holding on the minimap to scout |
| 14 | **Pushing a lane** | — | Dragging a hero to a minimap half |
| 15 | **Waves** | Wave spawning, both sides | Collecting six orbs from the fighting |
| 16 | **The enemy** | Their carry walks over and spars | Landing a hit on him yourself |
| 17 | **Their towers** | Nearest enemy outpost marked | Putting a hit on an enemy tower |
| 18 | **How a round is won** | Scoreboard appears | **Play a Match** |

### Notes on particular steps

**1 · Walking.** A route, not three scattered points: about 2200 units in three
legs. The first is a plain walk. The second crosses the river, and the card
changes to say the water is shallow and to wade straight through. The third is
behind the hedge, and the card changes again to say trees are solid and to go
around. The ground teaches as much as the text does, which is only possible
because the tutorial owns the ground.

Each obstacle sits in the *middle* of its leg, not at the end of it: 680 units
of the second leg lie past the river and 350 of the third lie past the hedge.
Crossing water with the ring already under your feet teaches nothing about
water. The first ring is also placed clear of the west bank — the river wobbles
55 either side of its line and is 130 wide, so its bank reaches further west
than its centre suggests.

This is also the only step whose copy has to be right on both devices. Desktop
reads *"W A S D or the arrow keys to walk"*; touch reads *"Drag anywhere on the
screen"*. Which one shows is decided per frame from `isTouchDevice` OR'd with
`usedTouch`, which flips true the moment a finger lands, so a phone that was not
detected as one corrects itself on the first touch. The arrow keys were added
for this: the tutorial says they work, so they had to.

**2–4 · Forest mobs, and your own shot.** The practice targets are **forest
mobs**, not lane creeps: 70 health against a lane creep's 320, so a blink — 150
at level one — kills one outright, which is the thing step 3 is trying to show.
Three blinks to kill the target would have taught the opposite. Their camp is a
detached object that is not in `camps`, so nothing respawns them and no camp
count is disturbed.

Steps 2 and 3 switch the **auto-assist off**. Left alone it kills a mob in
about seven seconds — the whole lesson done for you while you watch. That, not
the distance, was what made the shooting step feel like it played itself. The
assist comes back at step 4, which is the step that first mentions it.

Step 2's mob sits at 330 units, inside your reach: a shot carries exactly
`attackRange` and no further (367 at level one), so a target past that is not
"a walk away", it is unshootable. Step 3's sits at 470, which is past reach and
past a single blink, so that one really is an approach.

Everything the tutorial spawns goes up and to the right, and the guide line
leads to it. The card sits along the bottom of the screen, so a target placed
below you is the one place it can be on screen and still be invisible; and
because the camera clamps at the world's west edge the hero sits left of centre,
which puts the room to the east. `tutOpenSpot` fans its search out either side of
the heading it is given rather than sweeping once around the clock, so a blocked
direction yields the nearest clear one instead of something most of the way
around.

**3 · The blink.** The "teleport" is the carry's existing `Dash` — a blink
forward that damages what it passes through, grants i-frames, and refunds its own
cooldown on a kill. The step insists on the blink for the kill: shoot the creep
the ordinary way and a replacement spawns with *"That works — but blink through
the next one."* rather than a refusal.

**5 · Levels and stats.** A level buys three points. If the first four steps did
not produce a level-up, the step grants one, so it is always reachable.

**6 · Your squad.** They walk out of the base rather than appearing beside you,
and they arrive at your level — switching to a level-1 tank halfway through a
tutorial reads as a punishment for switching.

**8 · Stun, then switch.** The one step that needs two heroes to solve. A
hero's rocket **stuns everything in its blast for three seconds** — the game's
own design, and towers deliberately do not do it — and a stunned mob cannot
move, chase or hit back. So the step spawns a huddle of four and asks for the
pair: rocket three of them with the tank, then take the carry and make three
kills yourself.

Four things had to be true for it to teach that rather than something else:

- **The pack is placed from the tank, not from the hero you are driving.** A
  rocket carries `ROCKET_TRAVEL_MAX` (700) and the tank walks behind you, so a
  pack 380 in front of the carry can be 750 from the tank: the rocket stops
  short of its own aim point and the blast lands in empty grass. This was the
  first thing that went wrong when the step was driven for real.
- **The huddle is tight** — `ROCKET_SPLASH_RADIUS * 0.38` — so a blast centred
  on the near mob still reaches the far side. At the first radius a rocket that
  detonated on contact caught two of four and the step read as broken aim.
- **They have 200 health**, so the rocket cannot finish them. A stun with
  nothing left to kill afterwards teaches half the pair.
- **Only kills made while you are driving the carry count.** The carry is an AI
  ally whenever you are not driving it, and its auto-attack was closing the step
  by itself: rocket the pack, stand still as the tank, and the lesson about
  switching completed without a switch.

If the pack dies with either half unmet — no stun, or the kills made by your
allies — a fresh one spawns with a line saying which half is missing.

This is also the step that wakes the neutral AI for good. That meant holding the
map's one camp with an infinite respawn timer rather than a zero one, so the
forest does not quietly stock itself three steps early.

**9–10 · Orders and Assemble.** The drag gesture is taught here on open ground;
step 14 points the same gesture at the minimap.

**11 · The forest.** The map's one camp, stocked by this step and empty until it,
so the first forest mob you ever meet is one you were sent to.

**15 · Waves.** It does not ask for a last hit, because the last hit does not do
anything here. `killCreep` drops what the kill was carrying whoever landed it —
creep on creep included, through the filter in `resolveCreepCombat` that passes a
null attacker — and `lastHits` is a line on the end screen and nothing else.
Asking for one taught a habit from a different game. What pays is being where
the wave dies, so the step marks the middle of the nearest lane and asks for six
orbs.

**16 · The enemy.** Their carry is driven by `tutSparAI` rather than by his own
AI: he walks to arm's length, holds there, and fires once every two seconds
instead of five times a second. He carries `TUT_SPAR_HP` rather than his own, and
the step wants a hit **from the hero you are driving** — three allied heroes
shoot him the moment he arrives, and a step about meeting an enemy is worth
nothing if he is a corpse before you have looked at him. Respawning him on their
side of the map and sending him down a lane, as it did, meant walking into an
outpost to reach him.

**18 · Into a Match.** The button starts a real round on the real map. It is
called from the button handler, never from inside `update()` — `startRound`
rebuilds the world, and nothing good comes of doing that half way through a
frame.

## How it is built

**A flag, not a third game mode.** `gameMode` stays `'regular' | 'survival'` and
two things carry the rest: `tutMap`, a plain `let` declared early because
`generateForest()` and `drawBackground()` run at module scope long before the
tutorial module exists; and `tut`, the step machine. Around thirty places branch
on `gameMode==='survival'` and the sim harness string-matches into this file, so
a third mode value would have meant auditing every one of them. The tutorial runs
as `gameMode='regular'` with `tutMap` true, so only `buildMap`, `generateWater`
and `generateForest` behave differently.

**Six holds**, each one guard, each lifted by the step that needs it:

| Hold | Where | Lifted at |
|---|---|---|
| Kills drop nothing | `spawnKillDrops` | step 4 |
| Auto-assist off | `updateActiveControl` | step 4 |
| Neutral AI asleep | `updateNeutrals` | step 8 |
| Camp stocked | the forest step's `resetCamps` | step 11 |
| No waves | the spawn timer in `update()` | step 15 |
| Enemy heroes parked dead | `tutStart` | step 16, then the Match |
| Clock frozen | the `tut.on` branch in `update()` | the Match |

Every hold also lifts in `tutStop`, which runs on **Exit**, on the Match button
and at `endRound` — so skipping the step that owns one never leaves it stuck on.

The frozen clock has one consequence worth knowing: `inEarlyPeace()` and
`isEarlyGame()` both read `ROUND_TIME - timeLeft`, so with the clock held they
would report "the round just started" forever, which leashes every AI hero to its
own half — and would strand a hero sent to push a lane in step 14. Both now
return false while the tutorial is on.

**Progress detection** is a handful of one-line `tutNote(...)` calls at sites that
already exist — `killCreep`, `collectXpOrb`, `collectMana`, `applyStatPoint`,
`focusHero`, `useSkill`, `soloOrder`, `laneOrder`, `assembleOnFocus`,
`applyTowerHit`, `applyHeroHit` — each behind `if(tut.on)`, so a normal Match and
the headless sim never enter any of it. `triggerDash` sets `tut.dashWindow`
around its damage sweep, which is how step 3 knows a kill belonged to the blink.
No hook string `sim/harness.js` matches on was touched.

**The task appears twice.** On the card at the bottom of the screen, and again
in world space over your hero's head — high enough to clear two rows of damage
numbers, which stack upward from the same point. Your eyes are on your hero, not
on the bottom of the screen.

**The card** is a DOM panel above the bottom dock — the dock's height is measured
in JS, because the HUD is a percentage of a stage whose height nothing in CSS
knows. World-space marks are drawn after the fog, on purpose: a mark is what you
are being sent to find, so it must not be hidden by the fact that you have not
found it yet. They are sized in world units to match the damage numbers, the only
other text out there that reads at a glance.

**4 · Experience and mana, from a fight.** One step, because orbs of both kinds
fall out of the same kill — teaching them apart meant conjuring each out of thin
air, which is not where either comes from. It asks you to clear a pack of five
and pick up what they leave: at 32 experience a mob that is four gold orbs and
one to three blue ones per kill, so the pile is real and the fight pays about
three levels, which is what the step after it is for.

Nothing drops before this step. `spawnKillDrops` returns early while
`tut.holdDrops` is set, so the two kills in steps 2 and 3 leave the ground clean
— orbs the player has been told nothing about, half of them gone by the time
anything mentions them, is worse than no orbs at all. This step lifts that hold
and the auto-assist hold together: a fight of five is where the assist stops
being a spoiler and starts being help.

Orbs also do not rot while the tutorial is on. They carry a 15 second `ttl` and
the countdown is skipped under `tut.on` — a step should not fail because you
read the card twice.

## The stun, which never worked

`explodeRocket` says everything caught in the blast is frozen for `STUN_TIME`.
It was not — three holes, all of them visible as a mob wearing a stun mark while
it walks at you and hits you:

- **Forest mobs never consulted it at all.** `updateNeutrals` had no stun check,
  which is the one the combo step runs straight into.
- **A stunned lane creep still slid sideways.** In `moveCreeps` the guard was on
  the x update and the y update sat outside it.
- **Frozen never covered swinging.** `resolveCreepCombat`, `creepsVsHeroes` and
  `creepsVsTowers` all let a stunned creep keep fighting whatever it was already
  touching, which is most of what a lane creep ever does.

## What this changes outside the tutorial

Everything else is either new code or guarded by `tut.on` / `tutMap`, neither of
which is ever set outside mode `'tutorial'`. These are the exceptions, and they
are all fixes to things that were broken in every mode:

- **`.party.hidden` and `.scoreHud.hidden` now have CSS rules.** The party chips
  and the scoreboard used to be on screen at all times, including over the start
  screen, and Survival's request to hide the scoreboard never worked.
- **The minimap works under a finger.** There was no touch path for it at all:
  `onTouchStart` had no minimap test, so a press there fell through to the
  undecided bucket and became the movement joystick as soon as the finger
  travelled. On a phone the minimap could only be walked at.
- **An assembled squad follows whoever you are driving.** `assembleOnFocus` set
  the other two to follow the focused hero, and `focusHero` left that pointing
  at the hero you just left — who is then standing still under AI control. So
  assembling and switching quietly stranded the other two behind you. A
  `squadTogether` flag, set by Assemble and cleared by any individual order,
  re-anchors the formation on each switch.
- **The arrow keys move your hero**, in every mode.
- **The stun freezes**, in every mode — see above.
- **A few short lines of trees stand in the Match map's corridor.** Three or four
  trunks with gaps narrower than a hero, so a chase or a retreat through the
  middle is a choice of side rather than a straight line. They are kept off the
  lanes — in Match mode creeps do not collide with anything, so a clump near a
  road is a clump creeps walk through — and out of every tower's reach: with a
  300-unit keep-out the enemy team started dying to towers half again as often,
  because a clump inside the circle deflects a hero's path around it and into
  the guns. Measured at 24 games: no clumps 23/24 at 0.7 deaths, clumps near
  towers 20/24 at 1.0, clumps clear of towers 23/24 at 0.5.
- `inEarlyPeace()` and `isEarlyGame()` gained a `!tut.on` term, a no-op when the
  tutorial is off.

## Two pre-existing bugs fixed on the way

- **`.party.hidden` and `.scoreHud.hidden` had no CSS rule.** Both elements ship
  with `class="… hidden"` and are toggled from JS, but nothing ever hid them — so
  the party chips and the scoreboard were on screen at all times, including on
  the start screen, and Survival's explicit request to hide the scoreboard had
  never worked.
- **`index.html` was renamed from `lane.html` in `7f9fb83`** but `sim/harness.js`
  and `tools/artifact-html.js` still opened the old name, so both crashed with
  `ENOENT` — the simulation harness and the artifact build were dead on `main`.

## Still open

- **Length.** Eighteen steps is roughly seven to nine minutes.
- **The match clock.** `ROUND_TIME` is 600 seconds and the timer reads `10:00`,
  but the start screen calls the mode "Match · 5:00". Step 18 deliberately does
  not name a number rather than adding a third claim; the copy and the constant
  should be reconciled.
