// Builds a headless, instrumented copy of the game from lane.html.
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

const HTML = path.join(__dirname, '..', 'lane.html');

function extract(){
  const html = fs.readFileSync(HTML, 'utf8');
  const blocks = html.match(/<script>([\s\S]*?)<\/script>/g) || [];
  if(!blocks.length) throw new Error('no <script> block found in lane.html');
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
    start: (mode) => { globalThis.__M = blankMetrics(); startRound(mode || 'regular'); },
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
    })
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
  require(file);
  fs.unlinkSync(file);
  return globalThis.__GAME;
}

module.exports = { extract, build, load };
