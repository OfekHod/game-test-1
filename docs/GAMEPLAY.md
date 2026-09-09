# Gameplay screenshots

Frames from one full 10-minute Match and one Survival round, played in a
headless Chromium against the shipped `index.html` (build v154). The hero you
control was driven by a small autopilot that walks its lane, trades with
creeps, focuses enemy heroes, uses its skill and backs off when low, and the
camera followed whichever of the three heroes was closest to the enemy team.
A frame was kept whenever something happened worth keeping: a kill, a hero
under 30% health with enemies on him, a building about to fall, a skill going
off inside a fight.

The match went the way [FINDINGS.md](FINDINGS.md) says it usually does. The
enemy team grouped, took our outposts one by one, and won on points with our base
at 9%. That is the state of the game, and these are honest frames of it.

Captured at 1600×1000 with the camera zoomed in to 1.4× (the desktop default
is 2×, which makes a fight the size of a thumbnail) so the action reads at
README scale.

---

## The match

![Title screen](screenshots/00-title.jpg)

### First blood — 9:17

Every hero on both sides at level 1, nose to nose in the middle of the top
lane between the two outposts. Our tank (controlled, 424/450) puts a rocket
into the pile: **BOOM**, two **CRITICAL**s, and a **KILL! +30**. The XP orbs
from the fight are already scattering down the lane on the left.

![First blood at 9:17](screenshots/01-first-blood.jpg)

### One second later

The enemy support answers with a heal wave (**+80** on all three of theirs),
and our carry is already down: his chip in the top-left corner is greyed out.
The trade ends 0–38 in points. This is the whole early game in one frame.

![Aftermath of first blood](screenshots/02-first-blood-aftermath.jpg)

### The carry gets one back — 7:27

An enemy hero who has just popped two levels on the orbs from the last
fight (**Lv.7 UP! Lv.8 UP!**) is caught on the river bank in front of our base
tower and dies there: **KILL! +30**. Our carry, back from respawn at level 1,
is the one shooting from the tower steps on the left. Two more enemy heroes
are already turning toward him from the top and bottom of the frame.

![Carry kill and double level up](screenshots/03-carry-kill.jpg)

### Tank at 85 of 450, three on one — 7:02

The tank is in the open below our top outpost with all three enemy heroes
within reach. His health bar reads 85/450 in the HUD. He still lands a
**CRITICAL 228** on one of them before backing off toward the tower.

![Tank at 85 hp against three heroes](screenshots/04-tank-1v3.jpg)

### Top outpost falls — 6:25

**+200** floats over the spot where our top outpost stood. Enemy creeps
stream past it, two enemy heroes stand in the wreckage, and our tank (mana at
8/70) has nothing left to throw at them. The red score is rolling past 800.

![Top outpost destroyed](screenshots/05-top-outpost-falls.jpg)

### Stand at the base tower — 5:47

The support (controlled) is pinned in under our base tower. A moment before
this frame he was at 11% health; an enemy hero dies at the foot of the turret
(**KILL! +30**) and his own heal wave has him back at 150/150 by the time the
frame lands. A level-11 enemy hero is still standing on the top lane above,
waiting for the next wave.

![Support holding at the base tower](screenshots/06-base-tower-stand.jpg)

### The dash — 5:25

The carry dashes along the river straight through two enemy heroes. Damage
numbers stack over both of them and the dash after-image trails behind him
across the water.

![Carry dashing through two enemy heroes](screenshots/07-carry-dash.jpg)

### Two seconds later — 5:23

The price of the dash: 35 of 180 health, 8 mana, and the enemy hero is still
right there in the river. The autopilot pulls him back under the base tower on
the next tick. The red score has just crossed 1000.

![Carry at 35 hp after the dash](screenshots/08-carry-dash-aftermath.jpg)

### The surge — 3:10

Past the five-minute mark the waves stop being a trickle. Five big creeps and
ten small ones per lane per side pour down both lanes toward our base. The
tank's rocket bursts at the fork (**90** and **74** landing), the support
heals from behind the tower, and the enemy column for the bottom lane is still
arriving at the bottom of the frame. 471 to 1384.

![Surge waves on both lanes](screenshots/09-the-surge.jpg)

### Late kill — 1:04

With a minute left and the score 959 to 1863, the tank (168/450) gets a
**KILL! +30** at the river mouth while two **+125** heals from our support
land on the squad. It changes nothing on the scoreboard, but it is the best
fight of the last two minutes.

![Late kill at the river mouth](screenshots/10-late-kill.jpg)

### Defeat

Time ran out with both bases standing and the scoreboard settled it: 1169 to
2119, our base at 9%, theirs at 99%. 877 xp looted, 25 last hits.

![Defeat screen](screenshots/11-defeat.jpg)

---

## Survival

No enemy heroes, no enemy base: just our tower in the middle of the arena and
mobs arriving in growing numbers.

### How a wave works

The round is counted in **waves**, not seconds. A wave marches, its number goes
up in the middle of the screen for a couple of seconds, and **nothing else
spawns until every mob of that wave is dead** — the HUD's right-hand slot reads
`Wave 7` where a Match reads a clock. So the pace is yours: meet a wave out on
the road and the next one is along in a moment; let the outposts grind it down
and you get a long breather to farm the camps with.

Each wave is bigger than the last — six mobs in wave 1, two more every wave
after, up to forty — and from wave 3 there is a big one in front, one more every
second wave. Past the size cap a wave stops getting wider and keeps getting
heavier: the big count goes on climbing under it. The whole wave shows on the
minimap, because a wave you have to clear is a wave you have to be able to find.

The end card reports the waves you held, with the clock and the loot under it.

### The frames below

These frames predate both the two-lane arena and the wave counter. The round was
played on the original map — four straight spokes, mobs arriving from all four
sides, waves on a shrinking timer — where today there are two snaking lanes, two
outposts on each, a river, six lakes and waves that wait to be cleared.

### Wave 23 — 2:06

Reached in two minutes, on the old timer. Under the wave counter, twenty-three
waves is a much longer and much heavier round. By wave 23 the mobs come faster
than the squad can burn them. The west outpost
(grey, in the sand circle) is already lost and swarmed, the east outpost is
being chewed on (**94** landing on it, lower centre), and the big mobs are
walking straight past the heroes toward the base.

![Survival wave 23](screenshots/12-survival-wave-23.jpg)

### Overrun

2:07 survived, 23 waves held, 11 last hits. The tower behind the panel is
taking a **CRITICAL 169** as the screen fades.

![Overrun screen](screenshots/13-overrun.jpg)

---

## How these were taken

The game's script was lifted out of `index.html` the same way `sim/harness.js`
does it, with one extra hook that exposes the live state (teams, creeps,
projectiles, towers, camera) to the page. A Playwright script then:

1. opened the page in headless Chromium at 1600×1000 and clicked **Match** or
   **Survival**;
2. ran an autopilot on every tick for the controlled hero, and switched to the
   hero nearest the enemy team whenever the current one had nothing to shoot;
3. polled the state a few times a second and saved a JPEG when a trigger
   fired: enemy hero killed in view, ally hero down in view, controlled hero
   under 30% with enemy heroes near, a building under 35% and being hit, a
   building destroyed, rocket splash or heal wave inside a fight, a dash on an
   enemy hero, or a very large number of creeps in view.

The simulation ran at 3× speed so a full match took about three and a half
minutes of wall time. About 140 frames were captured for the match and a dozen
for survival; the ones above are the pick of them.
