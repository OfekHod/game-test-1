// node sim/analyse.js [games]  -- timeline: when buildings fall, deaths, farming
const { load } = require('./harness.js');
const N = parseInt(process.argv[2] || '25', 10);
const G = load();

const firstHit = {}, destroyed = {}, deathMin = {}, byType = {}, byKiller = {};
const baseKill = []; let games = 0;

for(let r = 0; r < N; r++){
  G.start(); games++;
  const seen = {}, gone = {};
  for(let i = 0; i < 24000; i++){
    G.step(0.05);
    if(i % 20) continue;
    const s = G.state();
    s.myTowers.forEach((t, idx) => {
      const k = t.main ? 'base' : 'outpost' + idx;
      if(t.hp < t.max && seen[k] === undefined) seen[k] = s.t;
      if(t.hp <= 0 && gone[k] === undefined) gone[k] = s.t;
    });
    if(s.myTowers.find(t => t.main).hp <= 0){ baseKill.push(s.t); break; }
    if(s.left <= 0) break;
  }
  for(const k in seen) (firstHit[k] = firstHit[k] || []).push(seen[k]);
  for(const k in gone) (destroyed[k] = destroyed[k] || []).push(gone[k]);
  G.state().m.deaths.filter(d => d.side === 'enemy').forEach(d => {
    const m = Math.floor(d.t / 60);
    deathMin[m] = (deathMin[m] || 0) + 1;
    byType[d.type] = (byType[d.type] || 0) + 1;
    byKiller[d.by] = (byKiller[d.by] || 0) + 1;
  });
}
const med = a => a && a.length ? Math.round([...a].sort((x,y)=>x-y)[Math.floor(a.length/2)]) : '-';

console.log(`${N} games\n`);
console.log('  building     first hit   destroyed   destroyed in');
Object.keys(firstHit).sort().forEach(k => {
  console.log('  ' + k.padEnd(13) + String(med(firstHit[k]) + 's').padEnd(12)
    + String(med(destroyed[k]) + 's').padEnd(12) + `${(destroyed[k]||[]).length}/${N}`);
});
console.log(`\n  base destroyed ${baseKill.length}/${N}, median ${med(baseKill)}s`);
console.log(`\n  enemy deaths/game ${(Object.values(byType).reduce((a,b)=>a+b,0)/N).toFixed(2)}`);
console.log('    by hero   ' + Object.keys(byType).map(k => `${k} ${(byType[k]/N).toFixed(2)}`).join('   '));
console.log('    by killer ' + Object.keys(byKiller).map(k => `${k} ${(byKiller[k]/N).toFixed(2)}`).join('   '));
console.log('\n  enemy deaths per minute:');
for(let m = 0; m < 10; m++) console.log(`    min ${String(m+1).padStart(2)}: ${((deathMin[m]||0)/N).toFixed(2)}`);
