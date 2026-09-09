# Tutorial

A third button next to **Match** and **Survival**. Sixteen steps that teach one
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
| 8 | **Orders** | A marked spot on the ground | Posting a hero on it |
| 9 | **Assemble** | The ALL button pulses | Calling the squad back |
| 10 | **The forest** | The camp is stocked and ringed | Clearing it |
| 11 | **Your base** | Your tower's range drawn | Standing inside it |
| 12 | **The map** | — | Holding on the minimap to scout |
| 13 | **Pushing a lane** | — | Dragging a hero to a minimap half |
| 14 | **The enemy** | Their carry walks over and spars | Landing a hit on him yourself |
| 15 | **Push a lane, take a tower** | Wave spawning, both sides; their whole team sent home | Assembling, sending the squad down a lane, and destroying an enemy outpost |
| 16 | **How a round is won** | Scoreboard appears | **Play a Match** |

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

**8–9 · Orders and Assemble.** The drag gesture is taught here on open ground;
step 13 points the same gesture at the minimap, and step 15 asks for both at once.
Orders also clears the practice mobs the shooting steps left standing — the
removed stun step used to do that on its way past, and without it the ground you
are asked to post a hero on is dotted with mobs holding perfectly still, since
the neutral AI does not wake until the forest step.

**10 · The forest.** The map's one camp, stocked by this step and empty until it,
so the first forest mob you ever meet is one you were sent to. It is also the
step that wakes the neutral AI for good, which is why the camp is held with an
infinite respawn timer rather than a zero one — a zero timer stocks the forest
quietly, several steps before anything mentions it. Its `resetCamps()` empties
`neutralCreeps` on the way, so nothing the earlier steps spawned can wake up and
walk at you the moment the hold lifts.

**14 · The enemy.** Their carry is driven by `tutSparAI` rather than by his own
AI: he walks to arm's length, holds there, and fires once every two seconds
instead of five times a second. He carries `TUT_SPAR_HP` rather than his own, and
the step wants a hit **from the hero you are driving** — three allied heroes
shoot him the moment he arrives, and a step about meeting an enemy is worth
nothing if he is a corpse before you have looked at him. Respawning him on their
side of the map and sending him down a lane, as it did, meant walking into an
outpost to reach him.

**15 · Push a lane, take a tower.** The payoff step, and the only one that asks
for the three gestures together: assemble, point the squad down a lane, and walk
in behind the wave until the outpost falls. It replaces three steps that each
asked for a fragment of it — a stun combo on a huddle of mobs, six orbs collected
off a wave, and a single hit landed on a tower — none of which is the thing a
round is actually made of.

Five things it has to get right:

- **It is the step that lets the waves out — your side's.** A lane push is a
  wave with heroes behind it, so `tut.holdWaves` lifts here and `spawnTimer` is
  zeroed rather than making you wait out a full twenty seconds first.
- **Their base goes quiet too**, and it has to. Two bases feeding one lane at
  the same rate is a **standoff**, and once their heroes are out of it nothing on
  the field can break it: driven headless with the carry laning, the support
  following and the tank levelled to 16, the front line oscillated between 1938
  and 2760 for six straight minutes, the outpost at 3100 was never touched, and
  the lane filled with three hundred uncollected orbs. That is correct behaviour
  for a Match — it is what the enemy heroes exist to break — and an unwinnable
  lesson here. With `tut.holdFoeWaves` set, the same run takes the outpost at
  **t=61s** with the player standing still, which is about the time it takes to
  walk there. The final card lifts the hold again, because a wave left pushing an
  undefended lane walks on and takes the main tower — ending the round on the win
  screen while you are still reading about how a round is won.
- **Their whole team goes home and stays there.** `tut.homeEnemies` skips
  `updateEnemyMacro`, `applyEnemyMacro`, the carry AI and the enemy half of
  `updateIdleAI` outright, and `tutEnemiesHome` walks each of them back to his own
  spawn. Skipping every one of them matters: any single path left running pulls a
  hero back out to defend the outpost, and three enemy heroes holding an outpost
  is a fight a level-six squad loses. They are put back on their feet rather than
  left as the corpses the opening parked, so you can see on the minimap where
  they went — and their carry gets his own health back, since the sparring step
  handed him `TUT_SPAR_HP`.
- **The order of the two gestures is enforced.** Assemble pulls the other two
  onto whoever you are driving, so a lane order given *first* is undone by the
  assemble that follows it. A lane order that arrives before the assemble is
  dropped with a nudge rather than being banked into a goal that then sits at
  "destroy the outpost" over a squad standing in its own base.
- **The finish reads the outpost's own hp, not a hook.** A creep takes a tower
  down without ever going through `applyTowerHit` — `creepsVsTowers` subtracts
  from `t.hp` directly — so a step watching only the hero's hits would hang on
  the last seven points while the wave finished the job. The step records which
  outposts were standing when it began and waits for one of them to fall, so
  taking the other lane counts too: marking one lane and refusing the other would
  be a rule the card never stated.
- **The card and the goal change with the stage**, the way the walking step's do:
  one line for the assemble, one for the lane, and then the outpost's health as a
  percentage while you cut it down.

**16 · Into a Match.** The button starts a real round on the real map. It is
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

**Eight holds**, each one guard, each lifted by the step that needs it:

| Hold | Where | Lifted at |
|---|---|---|
| Kills drop nothing | `spawnKillDrops` | step 4 |
| Auto-assist off | `updateActiveControl` | step 4 |
| Neutral AI asleep | `updateNeutrals` | step 10 |
| Camp stocked | the forest step's `resetCamps` | step 10 |
| No waves | the spawn timer in `update()` | step 15 |
| Enemy heroes parked dead | `tutStart` | step 14, then the Match |
| Enemy heroes sent home | `tut.homeEnemies`, in `update()` | on at step 15, off at the Match |
| Enemy waves held | `tut.holdFoeWaves`, in `spawnWave` | on at step 15, off at step 16 |
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
`applyHeroHit` — each behind `if(tut.on)`, so a normal Match and
the headless sim never enter any of it. Buildings have no hook at all: the one
step that watches a tower reads its `hp`, for the reason given above. `triggerDash` sets `tut.dashWindow`
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

No step teaches the stun any more — the combo step that did was replaced by the
lane push — but the step existed long enough to find that the stun did not work,
and those fixes are in every mode and stay.

`explodeRocket` says everything caught in the blast is frozen for `STUN_TIME`.
It was not — three holes, all of them visible as a mob wearing a stun mark while
it walks at you and hits you:

- **Forest mobs never consulted it at all.** `updateNeutrals` had no stun check,
  which is the one the combo step ran straight into.
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
- **Dragging the hero you are DRIVING onto a minimap half now actually sends
  him down that lane.** `laneOrder` set `mode='lane'` and then called `focusHero`
  to hand him over, and `focusHero` deliberately cancels the standing order of
  whichever hero you take over — "you are driving him now, so the old order is
  finished" — so it wiped the order that had just been given. The floater said TOP LANE, the old step 14 ticked, and the hero stood
  exactly where he was. Dragging one of the *other* two always worked, which is
  why it hid for so long. The fix is to hand him over first and write the order
  second. The siege step is what found it: it is the first thing in the game that
  cares whether the hero actually walks.
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

- **Length.** Sixteen steps, and the last playable one is a full lane push, so
  the run is roughly seven to nine minutes and most of the tail is that push.
- **The match clock.** `ROUND_TIME` is 600 seconds and the timer reads `10:00`,
  but the start screen calls the mode "Match · 5:00". Step 18 deliberately does
  not name a number rather than adding a third claim; the copy and the constant
  should be reconciled.
