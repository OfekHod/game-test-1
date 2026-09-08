// node sim/sweep.js <games> "<label>" "find=>replace" ...
// Runs one configuration and prints a single comparable line.
const { load } = require('./harness.js');
const N = parseInt(process.argv[2], 10);
const label = process.argv[3];
const edits = process.argv.slice(4).filter(s => s !== 'NONE').map(s => {
  const i = s.indexOf('=>');
  if(i < 0) throw new Error('edit needs the form "find=>replace": ' + s);
  return [s.slice(0, i), s.slice(i + 2)];
});

const G = load(edits);
let kills = 0, lost = 0, dmg = 0, deaths = 0;
const wins = [];
for(let r = 0; r < N; r++){
  G.start();
  let prev = null;
  for(let i = 0; i < 24000; i++){
    G.step(0.05);
    if(i % 20) continue;
    const s = G.state();
    const up = s.myTowers.filter(t => !t.main && t.hp > 0).length;
    if(prev === null) prev = up;
    while(up < prev){ lost++; prev--; }
    if(s.myTowers.find(t => t.main).hp <= 0){ kills++; wins.push(s.t); break; }
    if(s.left <= 0) break;
  }
  const s = G.state();
  dmg += s.myTowers.filter(t => !t.main).reduce((a, t) => a + (t.max - t.hp), 0);
  deaths += s.m.deaths.filter(d => d.side === 'enemy').length;
}
wins.sort((a, b) => a - b);
console.log(label.padEnd(38)
  + `base ${kills}/${N}`.padEnd(11)
  + `outposts ${(lost / N).toFixed(1)}`.padEnd(15)
  + `dmg ${Math.round(dmg / N)}`.padEnd(11)
  + `deaths ${(deaths / N).toFixed(1)}`.padEnd(13)
  + `win@${wins.length ? Math.round(wins[Math.floor(wins.length/2)]) : '-'}s`);
