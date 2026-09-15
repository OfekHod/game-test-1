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

// ---------------------------------------------------------------- PR2 -----
// The mode exists now, so these are about the world itself: one seed, one
// world, whichever order it was built in.

test(' 1  Same seed, same world (PR2)', () => {
  const A = load(), B = load();
  A.start('openworld', 42);
  B.start('openworld', 42);
  assert.strictEqual(A.world.hash(), B.world.hash(), 'two instances disagree on seed 42');
  const first = A.world.hash();
  A.start('openworld', 42);
  assert.strictEqual(A.world.hash(), first, 'a second round on one instance differs — state bled between rounds');
  assert.deepStrictEqual(A.world.loaded(), B.world.loaded(), 'different chunks loaded');
});

test(' 2  A different seed is a different world (PR2)', () => {
  const A = load();
  A.start('openworld', 42);
  const h42 = A.world.hash(), c42 = A.world.chunkHash(0, 0);
  A.start('openworld', 43);
  assert.notStrictEqual(A.world.hash(), h42, 'seed 43 gave seed 42\'s world');
  assert.notStrictEqual(A.world.chunkHash(0, 0), c42, 'chunk 0,0 is identical under two seeds');
});

// The proof of req 1: generation draws from the seed and from nothing else.
// Math.random is replaced by a thrower for the length of two chunk builds well
// outside the start block, so every region, river, grove and stand they need
// is built under the poison.
test(' 3a No unseeded draw inside generation (PR2)', () => {
  const G2 = load();
  G2.start('openworld', 1234);
  const real = Math.random;
  Math.random = () => { throw new Error('Math.random inside generation'); };
  try {
    G2.world.gen(7, -3);
    G2.world.gen(-9, 12);
  } finally { Math.random = real; }
  assert.strictEqual(G2.world.rngLeaked(), false, 'genRng was left set');
  assert.strictEqual(G2.world.genDepth(), 0, 'genDepth was left raised');
});

// Feature-owned lists are generated once and filtered into chunks, so the
// union of what the chunks keep must be the whole list — nothing lost at a
// seam, nothing counted twice — and it must not depend on which chunk or which
// region was built first.
test(' 4  Features straddle seams without disagreeing (PR2)', () => {
  const A = load();
  A.start('openworld', 42);
  // Walk every chunk of every extent box FIRST: a chunk build is what makes a
  // river's shore segment for its region exist, so the member lists have to be
  // read after the walk or the walk itself would change them.
  // Groves and lakes are a handful of chunks each; a 12,000-unit river can
  // cross a hundred, so the union test takes the two with the most shore
  // rather than every river in the layer — the property is the same one.
  const all = A.world.features();
  const rivers = all.filter(f => f.kind === 'river' && f.members.length)
                    .sort((a, b) => b.members.length - a.members.length).slice(0, 2);
  const boxes = all.filter(f => f.kind !== 'river').concat(rivers)
                   .map(f => ({ id: f.id, kind: f.kind, box: f.box }));
  const found = new Map(), hits = new Map();
  for(const f of boxes){
    const cs = chunksOf(f.box);
    assert.ok(cs.length <= 400, f.id + ' has an absurd extent box (' + cs.length + ' chunks)');
    const seen = [];
    let hit = 0;
    for(const [cx, cy] of cs){
      const mine = A.world.chunkMembers(cx, cy, f.id);
      if(mine.length) hit++;
      for(const id of mine) seen.push(id);
    }
    found.set(f.id, seen); hits.set(f.id, hit);
  }
  const ids = new Set(boxes.map(f => f.id));
  const feats = A.world.features().filter(f => f.members.length > 0 && ids.has(f.id));
  assert.ok(feats.length > 3, 'no features to test');
  const straddlers = { grove: 0, lake: 0, river: 0 };
  for(const f of feats){
    const seen = found.get(f.id) || [], hit = hits.get(f.id) || 0;
    const a = seen.slice().sort(), b = f.members.slice().sort();
    assert.deepStrictEqual(new Set(a).size, a.length, f.id + ': a member landed in two chunks');
    assert.deepStrictEqual(a, b, f.id + ': the chunks do not add up to the feature');
    if(hit > 1) straddlers[f.kind]++;
  }
  assert.ok(straddlers.grove > 0, 'no grove straddled a chunk seam — the test proved nothing');
  // ...and the same world whichever end you build from. Two instances of the
  // same seed, walked in opposite orders, must agree chunk for chunk.
  const B = load();
  B.start('openworld', 42);
  const keys = A.world.loaded();
  const forward = keys.map(k => A.world.chunkHash(...k.split(',').map(Number)));
  const backward = keys.slice().reverse().map(k => B.world.chunkHash(...k.split(',').map(Number)));
  assert.deepStrictEqual(forward, backward.reverse(), 'chunk hashes depend on build order');
});

// ---------------------------------------------------------------- PR3 -----
// The world streams now, so these are about what survives coming and going.

// Walk a squad to a place and let the loader catch up.
function goTo(G, x, y, secs, idx){
  G.world.teleport(x, y, idx);
  for(let i=0;i<secs*20;i++) G.step(0.05);
}

test(' 3b A streamed chunk is the chunk built in isolation (PR3)', () => {
  const G2 = load();
  G2.start('openworld', 42);
  goTo(G2, 7500, -2500, 10);
  assert.ok(G2.world.loaded().includes('7,-3'), 'walking there did not load 7,-3');
  assert.strictEqual(G2.world.chunkHash(7, -3), G2.world.gen(7, -3).hash,
    'the chunk that streamed in during play differs from the same chunk built alone');
});

test(' 5  A chunk round trip keeps the stump and loses nothing else (PR3)', () => {
  const G2 = load();
  G2.start('openworld', 42);
  goTo(G2, 6500, 2000, 8);
  assert.ok(G2.world.loaded().includes('6,2'), '6,2 never loaded');
  const pristine = G2.world.gen(6, 2);
  assert.strictEqual(G2.world.chunkHash(6, 2), pristine.hash, 'the hash is taken after the diff');
  const felled = G2.world.fellAt(6500, 2000);
  assert.ok(felled, 'nothing to chop');
  const stumpsAfter = G2.world.stumps();
  assert.ok(stumpsAfter > 0, 'felling left no stump');
  // A nudge, so the wanted set actually changes rather than being waited on.
  goTo(G2, 6800, 2000, 3);
  assert.ok(G2.world.stumps() > 0, 'the stump went with the first rebuild of the lists');
  goTo(G2, 12000, -6000, 14);
  assert.ok(!G2.world.loaded().includes('6,2'), '6,2 never unloaded — nothing was tested');
  goTo(G2, 6500, 2000, 14);
  assert.ok(G2.world.loaded().includes('6,2'), '6,2 did not come back');
  assert.strictEqual(G2.world.chunkHash(6, 2), pristine.hash, 'the chunk came back different');
  assert.ok(G2.world.stumps() > 0, 'the stump did not survive the round trip');
  const back = G2.world.gen(6, 2);
  assert.deepStrictEqual(back.props, pristine.props, 'props moved into the felled trees hole');
});

test('10  A partial chop survives a round trip too (A3) (PR3)', () => {
  const G2 = load();
  G2.start('openworld', 42);
  goTo(G2, 6500, 2000, 8);
  const id = G2.world.chop(6500, 2000, 2);
  assert.ok(id, 'nothing to chop');
  assert.strictEqual(G2.world.chopsOf(id), 2);
  goTo(G2, 12000, -6000, 14);
  goTo(G2, 6500, 2000, 14);
  assert.strictEqual(G2.world.chopsOf(id), 2, 'the two swings were forgotten');
});

test(' 7  A Match after a world is a Match (PR3)', () => {
  const G2 = load();
  G2.start('openworld', 42);
  goTo(G2, 12000, 2000, 5);
  G2.start();                                    // no mode: a Match
  assert.strictEqual(G2.world.rngLeaked(), false, 'genRng survived the mode change');
  assert.strictEqual(G2.state().left, 600, 'the Match clock did not reset');
  assert.deepStrictEqual(G2.world.loaded(), [], 'chunks survived into the Match');
  assert.deepStrictEqual(G2.world.envelope(), [0, 0, 4000, 4000], 'the envelope was left open');
  // The clamps apply on MOVEMENT, so the hero has to actually be moved.
  G2.world.teleport(3900, 3900, 0);
  G2.world.order(0, 5300, 5300);
  for(let i=0;i<20;i++) G2.step(0.05);
  const h = G2.world.heroAt(0);
  assert.ok(h.x <= 4000 && h.y <= 4000, 'a Match hero walked out of the map at ' + JSON.stringify(h));
});

test(' 8  A split squad never builds a chunk twice (PR3)', () => {
  const G2 = load();
  G2.start('openworld', 42);
  G2.world.teleport(14000, 3000, 1);             // one hero only, far away
  for(let i=0;i<200;i++) G2.step(0.05);
  const loaded = G2.world.loaded(), wanted = G2.world.wanted();
  for(const k of wanted) assert.ok(loaded.includes(k), 'wanted chunk ' + k + ' is not loaded');
  for(const k of loaded) assert.ok(G2.world.genCount(k) <= 1, k + ' was built ' + G2.world.genCount(k) + ' times');
});

test(' 9  One object per river, however far you walk along it (PR3)', () => {
  const G2 = load();
  G2.start('openworld', 42);
  const river = G2.world.features().filter(f => f.kind === 'river' && f.members.length)
                  .sort((a, b) => b.members.length - a.members.length)[0];
  assert.ok(river, 'no river with a shore to walk');
  const first = G2.world.riverObj(river.id);
  const box = river.box;
  let hops = 0;
  for(let x = box[0] + 200; x < box[2]; x += 1500){
    const y = box[1] + (box[3]-box[1])*0.5;
    goTo(G2, x, y, 2);
    const here = G2.world.riverObj(river.id);
    if(!here) continue;
    hops++;
    assert.strictEqual(here, first || here, 'the river was rebuilt as a second object');
  }
  assert.ok(hops > 1, 'never walked along the river');
});

test('12  Timings and sizes (PR2)', () => {
  const G2 = load();
  const t0 = Date.now();
  G2.start('openworld', 42);
  const ms = Date.now() - t0;
  const c = G2.world.counts();
  console.log('        world built in ' + ms + 'ms · ' + G2.world.loaded().length + ' chunks'
    + ' · last chunk ' + G2.world.genMs().toFixed(2) + 'ms · last region ' + G2.world.regionMs().toFixed(2) + 'ms');
  console.log('        in the start block: ' + c.camps + ' camps, ' + c.mobs + ' mobs, '
    + c.trees + ' trees, ' + c.props + ' props, ' + c.lakes + ' lakes, ' + c.rivers + ' rivers');
  assert.ok(G2.world.genMs() <= 8, 'a chunk build took ' + G2.world.genMs().toFixed(2) + 'ms');
  assert.ok(c.camps > 0, 'a world with nothing to farm in the start block');
  for(const k of G2.world.loaded()) assert.strictEqual(G2.world.genCount(k), 1, k + ' was built more than once');
});

// Every chunk the box touches, so a feature's members can be counted across
// every seam its extent crosses.
function chunksOf(box){
  const out = [];
  for(let cx = Math.floor(box[0]/1000); cx <= Math.floor(box[2]/1000); cx++)
    for(let cy = Math.floor(box[1]/1000); cy <= Math.floor(box[3]/1000); cy++) out.push([cx, cy]);
  return out;
}

console.log(failed ? '\n' + failed + ' failed' : '\nall green');
process.exitCode = failed ? 1 : 0;
