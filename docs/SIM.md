# Running experiments

## The harness

`sim/harness.js` reads `lane.html`, pulls out the last `<script>` block, and
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

## Cost

About 1.2s per 10-minute match. 100 matches ≈ 2 minutes.

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
