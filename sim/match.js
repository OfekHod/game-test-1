// Shared between run.js (one process) and parallel.js (one process per core):
// how to play a single idle-player match and how to print the headline report.
//
// Kept separate so the sequential and parallel runners can never drift apart
// in what they measure or how they print it.

// Plays one match on an already-loaded game instance. Returns a plain object
// (no game references) so it can cross a process boundary as JSON.
function playMatch(G){
  G.start();
  let win = null;
  for(let i = 0; i < 24000; i++){
    G.step(0.05);
    if(i % 20) continue;                       // state() is expensive: sample once per simulated second
    const s = G.state();
    if(s.myTowers.find(t => t.main).hp <= 0){ win = s.t; break; }
    if(s.left <= 0) break;
  }
  const s = G.state();
  return {
    win,                                        // seconds until the player's base fell, or null
    pointsAhead: win === null && s.score.enemy > s.score.player,
    deaths: s.m.deaths.filter(d => d.side === 'enemy').map(d => ({ type: d.type, by: d.by })),
    levels: Object.fromEntries(s.enemy.map(h => [h.type, h.lv]))
  };
}

function printReport(results, header){
  const N = results.length;
  const wins = results.map(r => r.win).filter(w => w !== null).sort((a, b) => a - b);
  const kills = wins.length;
  const pointsAhead = results.filter(r => r.pointsAhead).length;
  const byKiller = {}, byType = {}, lv = { carry:0, tank:0, support:0 };
  let deaths = 0;
  for(const r of results){
    for(const d of r.deaths){
      deaths++;
      byKiller[d.by] = (byKiller[d.by] || 0) + 1;
      byType[d.type] = (byType[d.type] || 0) + 1;
    }
    for(const k in r.levels) lv[k] = (lv[k] || 0) + r.levels[k];
  }
  const pct = n => Math.round(n / N * 100);
  const q = p => wins.length ? Math.round(wins[Math.floor(wins.length * p)]) : '-';

  console.log(`${header}\n`);
  console.log(`  base destroyed      ${kills}/${N}  (${pct(kills)}%)`);
  console.log(`  win time            median ${q(0.5)}s   earliest ${q(0)}s   latest ${wins.length ? Math.round(wins[wins.length-1]) : '-'}s`);
  console.log(`  otherwise on points ${pointsAhead}/${N - kills}`);
  console.log(`  enemy deaths/game   ${(deaths / N).toFixed(2)}`);
  console.log(`    by hero           ${Object.keys(byType).map(k => `${k} ${(byType[k]/N).toFixed(2)}`).join('   ')}`);
  console.log(`    by killer         ${Object.keys(byKiller).map(k => `${k} ${(byKiller[k]/N).toFixed(2)}`).join('   ')}`);
  console.log(`  end levels          ${Object.keys(lv).map(k => `${k} ${(lv[k]/N).toFixed(1)}`).join('   ')}`);
}

module.exports = { playMatch, printReport };
