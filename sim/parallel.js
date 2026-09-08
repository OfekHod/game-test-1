// node sim/parallel.js [games] [--workers N]
//
// Same report as run.js, but matches are spread over every core on this
// machine. A match is pure CPU work with no waiting, so one Node process can
// only ever use one core; we fork one worker per core and let them pull
// matches from a shared queue.
//
// The queue matters more than the core count. Match length is random — most
// end on a base kill around 250s, a few run the full 600s and cost ~4x as
// much — so handing each worker a fixed slice up front leaves fast workers
// idle while the unlucky one finishes. Dynamic dispatch keeps every core busy
// until the last match.
//
// Worker count defaults to the number of cores available to this process
// (respects container CPU limits and taskset). Going above it does not help:
// the workers just time-slice the same cores and pay Node's startup cost
// again. Override with --workers N or SIM_WORKERS=N to experiment.
const os = require('os');
const { fork } = require('child_process');
const { load } = require('./harness.js');
const { playMatch, printReport } = require('./match.js');

function coreCount(){
  // availableParallelism (Node 18.14+) honours cgroup/affinity limits; cpus()
  // is the fallback for older Node and can be empty on some platforms.
  if(typeof os.availableParallelism === 'function') return os.availableParallelism();
  return Math.max(1, (os.cpus() || []).length);
}

// ---- worker ---------------------------------------------------------------
if(process.argv.includes('--worker')){
  const G = load();
  process.on('message', msg => {
    if(msg.done){ process.exit(0); }
    process.send({ game: msg.game, result: playMatch(G) });
  });
  process.send({ ready: true });
  return;
}

// ---- parent ---------------------------------------------------------------
const args = process.argv.slice(2);
const N = parseInt(args.find(a => !a.startsWith('--')) || '25', 10);
const flagIdx = args.indexOf('--workers');
const requested = flagIdx >= 0 ? parseInt(args[flagIdx + 1], 10)
                : process.env.SIM_WORKERS ? parseInt(process.env.SIM_WORKERS, 10)
                : coreCount();
if(!Number.isInteger(N) || N < 1) throw new Error('games must be a positive integer');
if(!Number.isInteger(requested) || requested < 1) throw new Error('--workers must be a positive integer');
const W = Math.min(requested, N);            // never fork more workers than there are games

const t0 = Date.now();
const results = new Array(N);
let next = 0, finished = 0, exited = 0;

function dispatch(w){
  if(next < N){ w.send({ game: next++ }); }
  else w.send({ done: true });
}

for(let i = 0; i < W; i++){
  const w = fork(__filename, ['--worker'], { stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
  w.on('message', msg => {
    if(msg.ready) return dispatch(w);
    results[msg.game] = msg.result;
    finished++;
    dispatch(w);
  });
  w.on('exit', code => {
    exited++;
    if(code !== 0) { console.error(`worker exited with code ${code}`); process.exitCode = 1; }
    if(exited === W){
      if(finished !== N){ console.error(`only ${finished}/${N} games completed`); process.exit(1); }
      const secs = ((Date.now() - t0) / 1000).toFixed(1);
      printReport(results, `${N} games, player idle  (${W} workers on ${coreCount()} cores, ${secs}s)`);
    }
  });
  w.on('error', err => { console.error(err); process.exit(1); });
}
