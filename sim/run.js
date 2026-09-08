// node sim/run.js [games]     -- headline result for the shipped configuration
//
// Single process, one match after another. For anything beyond a handful of
// games use sim/parallel.js, which prints the same report using every core.
const { load } = require('./harness.js');
const { playMatch, printReport } = require('./match.js');
const N = parseInt(process.argv[2] || '25', 10);
const G = load();

const results = [];
for(let r = 0; r < N; r++) results.push(playMatch(G));
printReport(results, `${N} games, player idle`);
