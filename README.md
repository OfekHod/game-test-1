# Lane — browser MOBA prototype

A single-file browser game: two teams of three heroes, two lanes, four outposts
and a base per side. You control one hero directly and switch between them; the
other two follow a deliberately simple lane-push routine so you always know
where they will be.

## Layout

```
lane.html          the game — open it in a browser, nothing to install
sim/               headless simulation harness (Node, no dependencies)
  harness.js       lifts the game out of lane.html and instruments it
  run.js           headline result for the shipped configuration
  sweep.js         one configuration per invocation, one comparable line out
  analyse.js       timeline: when buildings fall, deaths, farming intensity
  stub.js          minimal DOM so the game runs under Node
docs/
  FINDINGS.md      what was measured, including what did NOT work
  TUNING.md        every constant that matters and the evidence for its value
  AI.md            how the enemy team thinks
  SIM.md           how to run experiments
  MULTIPLAYER.md   LAN plan and what internet play would additionally cost
```

## Running the simulation

```bash
node sim/run.js 40                     # 40 full matches, player idle
node sim/analyse.js 25                 # timeline breakdown
node sim/sweep.js 20 "half tower dmg" "const TOWER_DMG = 100;=>const TOWER_DMG = 50;"
```

A full 10-minute match simulates in about 1.2 seconds — roughly 80x realtime —
so a hundred matches is about two minutes.

## Why the harness reads lane.html

There is deliberately no second copy of the game source. `harness.js` extracts
the script from the shipped HTML and patches counters into it, so a tuning
experiment and the playable build can never disagree. If a hook stops matching
after an edit, the harness throws rather than quietly reporting zeros.

## Known state

Measured over 40 matches with the player idle (never moving):

| | |
|---|---|
| enemy destroys your base | 38/40 (95%) |
| median win | 231s of a 600s match |
| enemy deaths per game | 0.97 |
| end levels | carry 11, tank 13, support 8 |

The support is the weakest part of the design: it heals rather than last-hits,
so it collects far fewer experience orbs and finishes several levels behind.
