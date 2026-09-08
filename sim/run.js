// node sim/run.js [games]     -- headline result for the shipped configuration
const { load } = require('./harness.js');
const N = parseInt(process.argv[2] || '25', 10);
const G = load();

const wins = [], lv = { carry:0, tank:0, support:0 };
let kills = 0, pointsAhead = 0;
const deaths = [], byKiller = {}, byType = {};

for(let r = 0; r < N; r++){
  G.start();
  for(let i = 0; i < 24000; i++){
    G.step(0.05);
    if(i % 20) continue;
    const s = G.state();
    if(s.myTowers.find(t => t.main).hp <= 0){ kills++; wins.push(s.t); break; }
    if(s.left <= 0) break;
  }
  const s = G.state();
  if(s.myTowers.find(t => t.main).hp > 0 && s.score.enemy > s.score.player) pointsAhead++;
  s.m.deaths.filter(d => d.side === 'enemy').forEach(d => {
    deaths.push(d);
    byKiller[d.by] = (byKiller[d.by] || 0) + 1;
    byType[d.type] = (byType[d.type] || 0) + 1;
  });
  s.enemy.forEach(h => lv[h.type] += h.lv);
}
wins.sort((a, b) => a - b);
const pct = n => Math.round(n / N * 100);
const q = p => wins.length ? Math.round(wins[Math.floor(wins.length * p)]) : '-';

console.log(`${N} games, player idle\n`);
console.log(`  base destroyed      ${kills}/${N}  (${pct(kills)}%)`);
console.log(`  win time            median ${q(0.5)}s   earliest ${q(0)}s   latest ${wins.length ? Math.round(wins[wins.length-1]) : '-'}s`);
console.log(`  otherwise on points ${pointsAhead}/${N - kills}`);
console.log(`  enemy deaths/game   ${(deaths.length / N).toFixed(2)}`);
console.log(`    by hero           ${Object.keys(byType).map(k => `${k} ${(byType[k]/N).toFixed(2)}`).join('   ')}`);
console.log(`    by killer         ${Object.keys(byKiller).map(k => `${k} ${(byKiller[k]/N).toFixed(2)}`).join('   ')}`);
console.log(`  end levels          ${Object.keys(lv).map(k => `${k} ${(lv[k]/N).toFixed(1)}`).join('   ')}`);
