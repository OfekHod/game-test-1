// node sim/world.js     -- is the world a function of its seed, and nothing else?
//
// sim/run.js asks whether a match is still balanced. This asks the other
// question, the one an endless world lives or dies by: build the same seed
// twice, in any order, on either side of a chunk boundary, and does the same
// world come out? Every test names the PR it lands in, and each PR runs every
// test up to and including its own, so scaffolding that quietly rots is caught
// by a later PR's gate as well as its own.
//
// PR1 ships the scaffolding and no world to build with it yet, so the two
// tests here are about what the scaffolding must NOT have changed: Match still
// draws freely from Math.random, and an Open World round refuses to start
// without a seed rather than inventing one.
const assert = require('assert');
const { load } = require('./harness.js');

let failed = 0;
function test(name, fn){
  try { fn(); console.log('  ok    ' + name); }
  catch(err){ failed++; console.log('  FAIL  ' + name + '\n          ' + (err && err.message)); }
}

const G = load();
console.log('world tests\n');

// The poison is the whole proof. genDepth is raised only around generation, so
// a Math.random that fires while it is up is a draw that the seed did not
// make — the one failure that would leave a world looking fine and coming back
// different. Match generates at depth 0 and draws hundreds of times, so here
// the trap is armed and must never spring: whatever PR1 moved around inside
// makeTree, scatterClumps, buildCampRings, scatterTrees and scatterShoreTrees,
// none of it generates at depth.
test('13  Match generates under a depth-gated poison (PR1)', () => {
  const real = Math.random;
  let draws = 0;
  Math.random = () => {
    if(G.world.genDepth() > 0) throw new Error('Math.random inside generation');
    draws++;
    return real();
  };
  try { G.start(); }
  finally { Math.random = real; }
  assert.ok(draws > 100, 'the poison never fired at all (' + draws + ' draws) — is it still wired in?');
  assert.strictEqual(G.world.rngLeaked(), false, 'genRng was left set after the round');
  assert.strictEqual(G.world.genDepth(), 0, 'genDepth was left raised after the round');
  assert.strictEqual(G.state().left, 600, 'Match did not start');
});

// A seed that never arrived used to be indistinguishable from seed 0: the same
// world, every time, for anyone who forgot the argument. It throws now, and it
// throws before it touches anything, so the instance is still good afterwards.
test('14  Open World without an integer seed throws (PR1)', () => {
  for(const bad of [undefined, null, '42', 1.5, NaN]){
    assert.throws(() => G.start('openworld', bad),
      /openworld needs an integer seed/, 'a seed of ' + String(bad) + ' was accepted');
  }
  G.start();
  assert.strictEqual(G.state().left, 600, 'Match will not start after the throws');
});

console.log(failed ? '\n' + failed + ' failed' : '\nall green');
process.exitCode = failed ? 1 : 0;
