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
