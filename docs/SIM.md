# Running experiments

## The harness

`sim/harness.js` reads `index.html`, pulls out the last `<script>` block, and
string-patches instrumentation into it. Nothing is duplicated: the simulation
runs the same code the browser does.

`load(edits)` accepts `[find, replace]` pairs applied to the source before it is
evaluated, which is how sweeps change constants. Both the hooks and the edits
throw if they fail to match — an earlier version of this harness silently
reported "0 tower damage" for an afternoon because a hook had drifted after a
refactor, so failures are now loud.

Node caches modules by path, so every `load()` writes a uniquely-named temp file.
Without that, a sweep would reuse the first configuration for every run and every
row would come out identical.

`sim/stub.js` also unrefs every timer the game creates. The game starts a 400ms
layout-refresh interval at load; under Node that would keep the process alive
after a report has printed, so scripts hung until killed. Only timers created
while game code is running are affected — during `load()` and inside `start()`,
`step()` and `state()`; a timer a script sets for itself fires as normal, so a
script can still `await` a delay. With the game's timers unref'd the process
exits as soon as a script finishes.

## The determinism gate

`node sim/world.js` is the Open World mode's own gate, and it takes no
argument. It asks the one question an endless world lives or dies by: **build
the same seed twice, in any order, from either side of a chunk boundary — is it
the same world?**

```bash
node sim/world.js
```

Seventeen tests, each naming the PR it landed in, and each PR ran every test up
to and including its own, so scaffolding that quietly rots is caught by a later
PR's gate as well as by its own. What they cover:

- **Same seed, same world** — two instances, and the same instance started
  twice, hash identical; a different seed hashes differently.
- **No unseeded draw inside generation.** `Math.random` is replaced with a
  throw, and a whole block of world is built under it. This is the test the
  others rest on: a single leaked `Math.random` would give a world that looks
  right and comes back different, with nothing on screen to say so. The game
  carries the same trap itself — generation runs with an explicit stream and a
  depth counter, and `?owdebug` turns a draw taken at depth into an error.
- **Order independence across a seam.** A lake, a grove whose stand trees cross
  a chunk boundary, a bowl and a river are each built A-then-B on one instance
  and B-then-A on another; both chunks must agree, and the union of the chunks'
  member lists must be the feature's complete list with nothing missing and
  nothing counted twice.
- **Streaming equals isolation.** A chunk built during play, with its camps
  stocked and its towers live, hashes the same as that chunk built alone.
- **Round trips.** Walk away until a chunk unloads, walk back: the stump you
  left is there, the tree you hit twice is still on two, nothing has moved into
  the hole, and the hash is the pristine one.
- **Match is unaffected.** A Match started after an Open World round is today's
  Match, on today's clamps, with nothing left loaded.
- **The gradient, the bowls and the walk** — the content tests: all-easy at
  home and all-medium 93k out over ten seeds, a giant that never leaves its
  bowl, a long walk that goes past bowls with giants alive in them, and eight
  two-minute walks that never stop dead against a prop.
- **Timings**, printed rather than asserted: ms per chunk, ms per region build,
  and what the start block came out holding.

It must print every test green **and exit on its own** — a hang means a timer
is keeping Node alive, which is what `sim/stub.js` is for (above). Any change
that touches generation runs it.

## Cost

A match that ends on a base kill (~250s of game time) costs a few seconds of
wall time; one that runs the full 600s costs about four times that. Measured on
a 4-core Xeon: 12 games took 60s in one process and 15-20s with `parallel.js`.

## Using every core

```bash
node sim/parallel.js 40               # one worker per core, auto-detected
node sim/parallel.js 40 --workers 2   # or SIM_WORKERS=2
```

Node is single-threaded, so `run.js` uses one core no matter how many exist.
`parallel.js` forks one worker per core (`os.availableParallelism`, which
honours container CPU limits) and dispatches matches one at a time from a
shared queue. The queue is the important part: match length is random, so a
fixed slice per worker leaves fast workers idle while an unlucky one finishes
its 600s games.

More workers than cores does not help. The sim never waits on I/O, so extra
processes just time-slice the same cores and pay Node's startup cost again;
12 workers on 4 cores measured slower than 4. The worker count is capped at
the number of games, so `parallel.js 1` forks exactly one worker.

The dominant cost is not the simulation but how often you call `state()` — it
rebuilds arrays over every tower and hero. Sample once per simulated second
(`if(i % 20) continue`), not every frame. Doing this wrong made early runs 60x
slower and caused them to time out.

## Sample sizes

Base-destroy rate has real variance. Two 25-game samples of the identical build
gave 25/25 and 23/25. Treat anything under 40 games as indicative, and never
report a single 20-game run as a percentage without saying so.

## Reproducing the headline

```bash
node sim/run.js 40
```

Expect roughly 95% base destruction, ~0.9 enemy deaths per game, median win
around 230-270s. If it comes back far from that, something regressed.
