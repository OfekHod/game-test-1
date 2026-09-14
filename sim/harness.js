// Builds a headless, instrumented copy of the game from index.html.
//
// The game ships as one self-contained HTML file. Rather than maintain a second
// copy of the source for testing, we lift the script out of it and patch in
// counters. That guarantees the simulation and the playable build can never
// disagree — there is only one source of truth.
//
// applyEdits lets a sweep change constants ("const TOWER_DMG = 100;" etc.)
// without touching the file on disk.
const fs = require('fs');
const path = require('path');

const HTML = path.join(__dirname, '..', 'index.html');

function extract(){
  const html = fs.readFileSync(HTML, 'utf8');
  const blocks = html.match(/<script>([\s\S]*?)<\/script>/g) || [];
  if(!blocks.length) throw new Error('no <script> block found in index.html');
  const last = blocks[blocks.length - 1];
  return last.replace(/^<script>/, '').replace(/<\/script>$/, '');
}

// Counters the reports need. Each hook is a plain string replacement against
// the game source; if one stops matching we throw rather than silently
// reporting zeros — an earlier version of this harness reported "0 tower
// damage" for a whole afternoon because a hook had drifted.
const HOOKS = [
  ['  function applyHeroHit(target, side, dirX, dirY, dmgBase, attackerHero){',
   `  function applyHeroHit(target, side, dirX, dirY, dmgBase, attackerHero){
    globalThis.__M.killer = attackerHero ? ('hero:'+attackerHero.type) : 'tower';`],

  ['  function creepHitHero(c, target){',
   `  function creepHitHero(c, target){
    globalThis.__M.killer = 'creep';`],

  ['      target.alive=false; target.respawnTimer=RESPAWN_TIME; target.hp=0;',
   `      target.alive=false; target.respawnTimer=RESPAWN_TIME; target.hp=0;
      globalThis.__M.deaths.push({ t: ROUND_TIME - timeLeft, side: target.side,
        type: target.type, by: globalThis.__M.killer || 'creep' });
      globalThis.__M.killer = null;`],

  ['  function collectXpOrb(o, h){',
   `  function collectXpOrb(o, h){
    if(h.side === 'enemy') globalThis.__M.xp[h.type] += o.value;`],

  ['  function applyCreepHit(creep, list, idx, side, dirX, dirY, dmgBase, attackerHero){',
   `  function applyCreepHit(creep, list, idx, side, dirX, dirY, dmgBase, attackerHero){
    if(list === allyCreeps && attackerHero && attackerHero.side === 'enemy')
      globalThis.__M.creepDmg[attackerHero.type] += Math.min(creep.hp, dmgBase);`],

  ['  window.__laneLoaded = true;',
   `  window.__laneLoaded = true;
  globalThis.__GAME = {
    start: (mode, seed) => { globalThis.__M = blankMetrics(); startRound(mode || 'regular', seed); },
    step:  (dt)   => update(dt),
    state: () => ({
      t: ROUND_TIME - timeLeft, left: timeLeft, dur: ROUND_TIME,
      score: { player: score.player, enemy: score.enemy },
      myTowers:  playerTowers.map(t => ({ main: !!t.main, hp: t.hp, max: t.maxHp })),
      foeTowers: enemyTowers.map(t => ({ main: !!t.main, hp: t.hp, max: t.maxHp })),
      enemy: enemyTeam.map(h => ({ type: h.type, lv: h.level, alive: h.alive,
        hp: Math.round(h.maxHp), range: Math.round(attackRange(h)) })),
      orbsOnField: xpOrbs.length,
      m: globalThis.__M
    }),
    // What sim/world.js asks the world about itself. Generation state only —
    // a match report has no use for it, and nothing here may be a getter,
    // since load() wraps each one so the game's timers stay unref'd.
    world: {
      rngLeaked: () => genRng !== null,
      genDepth:  () => genDepth,
      hash:      () => worldHash(),
      chunkHash: (cx, cy) => chunkHashOf(cx, cy),
      loaded:    () => [...loaded.keys()].sort(),
      genCount:  (key) => genCount.get(key) || 0,
      genMs:     () => lastGenMs,
      regionMs:  () => lastRegionMs,
      counts:    () => ({ trees: trees.length, props: props.length, camps: camps.length,
                          lakes: lakes.length, rivers: rivers.length, mobs: neutralCreeps.length }),
      // A pristine build: what the chunk is before the diff overlay, which is
      // what test 3b compares a streamed chunk against.
      gen: (cx, cy) => {
        if(gameMode !== 'openworld') throw new Error('world.gen needs an open world round');
        const c = buildChunk(cx, cy);
        return { hash: c.hash, props: c.props.map(p => p.id), trees: c.trees.map(t => t.id),
                 camps: c.camps.map(k => k.id) };
      },
      // Every feature of every built region, plus the rivers, with the extent
      // box registration uses and the complete member list a chunk filters.
      features: () => {
        const out = [];
        for(const reg of regionCache.values()){
          for(const l of reg.lakes) out.push({ id: l.id, kind: 'lake', region: reg.key,
            box: [l.x-l.ext, l.y-l.ext, l.x+l.ext, l.y+l.ext], members: l.shore.map(t => t.id) });
          for(const d of reg.dirt) out.push({ id: d.id, kind: 'dirt', region: reg.key,
            box: [d.x-d.ext, d.y-d.ext, d.x+d.ext, d.y+d.ext],
            at: { x: d.x, y: d.y, r: d.r, sy: d.sy }, apexN: d.apexN,
            gaps: d.gaps.length, members: d.rim.map(o => o.id) });
          for(const g of reg.groves){
            const members = [];
            for(const c of g.camps){ members.push(c.id); for(const t of c.ring) members.push(t.id); }
            for(const st of g.stands) for(const t of st.trees) members.push(t.id);
            out.push({ id: g.id, kind: 'grove', region: reg.key, n: g.camps.length,
              box: [g.x-g.ext, g.y-g.ext, g.x+g.ext, g.y+g.ext], members,
              stands: g.stands.map(st => ({ id: st.id, trees: st.trees.map(t => t.id) })) });
          }
        }
        for(const v of riverCache.values()){
          if(!v) continue;
          out.push({ id: v.id, kind: 'river', box: [v.ex0, v.ey0, v.ex1, v.ey1],
            segments: [...v.shore.keys()].sort(),
            // The mouth lake belongs to the river, so its shore is the river's
            // too — it carries the river's id and lands in the river's chunks.
            members: [].concat(...[...v.shore.values()].map(seg => seg.map(t => t.id)),
                               v.mouth ? v.mouth.shore.map(t => t.id) : []) });
        }
        return out;
      },
      // The ids of one feature's members that landed in one chunk.
      chunkMembers: (cx, cy, featureId) => {
        const c = loaded.get(cx+','+cy) || buildChunk(cx, cy);
        const pre = featureId + ':';
        const hit = (id) => id === featureId || (id && id.indexOf(pre) === 0);
        return c.trees.filter(t => hit(t.id)).map(t => t.id)
          .concat(c.camps.filter(k => hit(k.id)).map(k => k.id));
      },
      riverObj: (id) => rivers.find(r => r.id === id) || null,
      inDirt: (id, x, y, pad) => { const d = dirt.find(d => d.id === id); return d ? inDirt(d, x, y, pad||0) : null; },
      mixedCamp: () => {
        for(const c of camps){
          if(!c.roster) continue;
          const m = c.roster.filter(k => k === 1).length;
          if(m > 0 && m < c.n) return { id: c.id, x: c.x, y: c.y, n: c.n, mediums: m };
        }
        return null;
      },
      apexes: () => neutralCreeps.filter(n => n.huge).map(n => ({ x:n.x, y:n.y, area:n.area, hp:Math.round(n.hp) })),
      campKinds: (x0, y0, x1, y1) => {
        const out = { easy: 0, mixed: 0, whole: 0 };
        for(const reg of regionCache.values()) for(const c of reg.camps){
          if(c.x < x0 || c.x > x1 || c.y < y0 || c.y > y1) continue;
          const m = c.roster ? c.roster.filter(k => k === 1).length : 0;
          if(!m) out.easy++; else if(m >= c.n) out.whole++; else out.mixed++;
        }
        return out;
      },
      wanted:   () => [...wantedSet()].sort(),
      stumps:   () => stumps.length,
      envelope: () => [WX0, WY0, WX1, WY1],
      // A real chop, through the same path a hero's axe takes.
      fellAt: (x, y) => {
        let best = null, bd = Infinity;
        for(const t of trees){ const d = (t.x-x)*(t.x-x) + (t.y-y)*(t.y-y); if(d < bd){ bd = d; best = t; } }
        if(!best) return null;
        const id = best.id, at = { x: best.x, y: best.y, r: best.r };
        fellTree(best, playerTeam[0]);
        return { id, at };
      },
      chop: (x, y, n) => {
        let best = null, bd = Infinity;
        for(const t of trees){ const d = (t.x-x)*(t.x-x) + (t.y-y)*(t.y-y); if(d < bd){ bd = d; best = t; } }
        if(!best) return null;
        best.chops = n;
        return best.id;
      },
      chopsOf: (id) => { const t = trees.find(t => t.id === id); return t ? (t.chops || 0) : null; },
      // A real MOVE order, so the movement clamps actually run.
      order: (idx, x, y) => soloOrder(playerTeam[idx], x, y),
      heroAt: (idx) => ({ x: playerTeam[idx].x, y: playerTeam[idx].y,
        vx: playerTeam[idx].vx, vy: playerTeam[idx].vy, alive: playerTeam[idx].alive,
        mode: playerTeam[idx].mode, hp: Math.round(playerTeam[idx].hp) }),
      // Drive the hero the way a keyboard does, so a stall that only happens
      // under player input can be reproduced without a browser.
      press: (k, down) => { if(down) keys[k] = true; else delete keys[k]; },
      teleport: (x, y, idx) => {
        for(let i=0;i<playerTeam.length;i++){
          if(idx !== undefined && i !== idx) continue;
          const h = playerTeam[i];
          h.x = x; h.y = y; h.homeX = x; h.homeY = y;
        }
      }
    }
  };`]
];

function blankMetricsSrc(){
  return `
  function blankMetrics(){
    return { deaths: [], killer: null,
      xp: { carry:0, tank:0, support:0 },
      creepDmg: { carry:0, tank:0, support:0 } };
  }
  globalThis.__M = blankMetrics();
`;
}

function build(edits){
  let js = extract();
  for(const [from, to] of HOOKS){
    if(!js.includes(from)) throw new Error('harness hook no longer matches: ' + from.trim().slice(0, 60));
    js = js.split(from).join(to);
  }
  js = blankMetricsSrc() + js;
  for(const [from, to] of (edits || [])){
    if(!js.includes(from)) throw new Error('edit did not match: ' + from);
    js = js.split(from).join(to);
  }
  return js;
}

// Loads a fresh instance. Node caches modules by path, so each build gets a
// unique temp file — without this, a sweep would silently reuse the first
// configuration for every run.
let n = 0;
function load(edits){
  const file = path.join(require('os').tmpdir(), `lane_sim_${process.pid}_${n++}.js`);
  fs.writeFileSync(file, build(edits));
  require('./stub.js');
  // Everything the game schedules — the layout interval it starts while the
  // script is evaluated, the short timeouts it sets during play — must not
  // keep Node alive once the sim script is done. The stub unrefs timers only
  // while __laneInGame is raised, so raise it exactly where game code runs:
  // here, and inside each call the script makes into the game.
  const G = inGame(() => { require(file); return globalThis.__GAME; })();
  fs.unlinkSync(file);
  // world is wrapped the same way, one function at a time — it is game code
  // like any other, and an unwrapped call would leave a timer holding Node
  // open after the script is done.
  const world = {};
  for(const k of Object.keys(G.world || {})) world[k] = inGame(G.world[k]);
  return { start: inGame(G.start), step: inGame(G.step), state: inGame(G.state), world };
}
function inGame(fn){
  return (...args) => {
    globalThis.__laneInGame++;
    try { return fn(...args); } finally { globalThis.__laneInGame--; }
  };
}

module.exports = { extract, build, load };
