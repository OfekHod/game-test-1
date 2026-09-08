# Multiplayer

Nothing here is implemented. This is the plan and the honest cost.

## What the codebase forces

- `rand()` wraps `Math.random()`, unseeded, used in ~15 places including damage
  variance, crits, AI timers *and* particle spawns. This rules out naive lockstep
  (both machines simulating, exchanging only inputs) — and note that visual
  randomness draws from the same stream, so any per-client difference in
  particles would silently desync the game state.
- Variable timestep: `dt = Math.min(0.05, (now-last)/1000)`. Determinism needs a
  fixed step.
- Simulation is cheap: ~80x realtime on one core, so a server could host on the
  order of 80 concurrent matches per core.

## LAN, host-authoritative

Skip determinism. One machine simulates; the other sends inputs and renders what
it is told. At sub-5ms latency you can apply authoritative state directly with no
prediction and it feels fine.

| piece | effort |
|---|---|
| small Node relay/host server | hours |
| second player drives an enemy-team hero (`activePlayerIdx` already exists; add the mirror, suppress AI for that hero) | small |
| input serialisation | small |
| **state snapshots + wire format** | the real work |
| interpolation | largely skippable on LAN |

**2-4 days to something playable, 1-2 weeks to feel good.** The cost is that a
self-contained HTML file gains a server dependency. A WebRTC variant with
copy-pasted connection strings keeps it single-file but makes connecting
unpleasant.

## Internet, additionally

- **Latency 30-150ms** — client-side prediction for your own hero plus
  reconciliation, and entity interpolation for everything else. The biggest
  chunk. Projectiles having travel time makes lag compensation more forgiving
  than a hitscan game.
- **NAT traversal** — signalling, STUN, and TURN as fallback; roughly 10-20% of
  connections need a relay and relays cost bandwidth.
- **Cheating** — host-authoritative P2P lets the host cheat. A dedicated server
  fixes it and is cheap given the simulation cost.
- **The unglamorous half** — matchmaking, reconnection, desync detection,
  clock sync.

Call it 5-10x the LAN work, plus ongoing hosting.

## Suggested order

Build LAN first. It forces the clean split between simulation and rendering that
internet play needs anyway, and you will learn what a state snapshot actually
costs before committing to the harder problem.

One design question to settle early: does player two control **one** hero or all
three? One hero means the other two stay AI and most existing code works.
