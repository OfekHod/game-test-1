// Drive the game and photograph it.
//
// The boot sequence is the same every time — launch, wait out the consent
// screen, click through the menu, wait for a state — so it lives here rather
// than being rewritten per change. What varies is the last step, which is what
// --at and --shot are for.
//
//   node tools/shoot.js --shot out.png
//   node tools/shoot.js --start match --at 45 --shot out.png
//   node tools/shoot.js --start tutorial --phone --shot tut.png
//   node tools/shoot.js --start match --at 214 --speed 8 --shot late.png
//
// Playwright is NOT a dependency of this repo and must not become one —
// README.md promises none and package.json has none. Install it in a scratch
// directory and point NODE_PATH at it:
//
//   cd "$SCRATCH" && npm init -y
//   PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i playwright
//   NODE_PATH="$SCRATCH/node_modules" node tools/shoot.js --shot out.png
//
// Never run `playwright install`. The browser is already on disk; see the
// executablePath note below.

const path = require('path');
const fs = require('fs');

function loadPlaywright(){
  try { return require('playwright'); }
  catch(e){
    console.error(`cannot find playwright.

It is deliberately not a dependency of this repo. Install it in a scratch
directory and re-run with NODE_PATH pointing at it:

  cd "$SCRATCH" && npm init -y
  PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i playwright
  NODE_PATH="$SCRATCH/node_modules" node tools/shoot.js --shot out.png
`);
    process.exit(1);
  }
}

// chromium.executablePath() reports a version that is often not the one on
// disk, so read the path off the filesystem instead of asking the library.
function findChromium(){
  const root = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  const dirs = fs.existsSync(root)
    ? fs.readdirSync(root).filter(d => d.startsWith('chromium-')).sort()
    : [];
  for(const d of dirs.reverse()){
    const exe = path.join(root, d, 'chrome-linux', 'chrome');
    if(fs.existsSync(exe)) return exe;
  }
  throw new Error('no chromium under ' + root + ' — do NOT run `playwright install`, ' +
                  'set PLAYWRIGHT_BROWSERS_PATH at the one already on disk');
}

function parseArgs(argv){
  const a = { start: null, at: 0, speed: 1, shot: null, phone: false,
              wait: 0, game: path.join(__dirname, '..', 'index.html'), timeout: 300 };
  for(let i = 2; i < argv.length; i++){
    const k = argv[i];
    if(k === '--phone') a.phone = true;
    else if(k === '--start')   a.start  = argv[++i];
    else if(k === '--at')      a.at     = Number(argv[++i]);
    else if(k === '--speed')   a.speed  = Number(argv[++i]);
    else if(k === '--shot')    a.shot   = argv[++i];
    else if(k === '--wait')    a.wait   = Number(argv[++i]);
    else if(k === '--game')    a.game   = path.resolve(argv[++i]);
    else if(k === '--timeout') a.timeout= Number(argv[++i]);
    else throw new Error('unknown argument ' + k);
  }
  if(!a.shot) throw new Error('--shot <file.png> is required');
  if(a.at && !a.start) throw new Error('--at needs --start');
  return a;
}

// The match clock, read the way a player reads it: off the HUD.
async function clockSeconds(page){
  return page.evaluate(() => {
    const el = [...document.querySelectorAll('*')]
      .find(e => e.children.length === 0 && /^\d?\d:\d\d$/.test((e.textContent||'').trim()));
    if(!el) return null;
    const m = /(\d?\d):(\d\d)/.exec(el.textContent);
    return m ? (+m[1]) * 60 + (+m[2]) : null;
  });
}

const BUTTON = { match: '#startBtn', survival: '#startSurvBtn', tutorial: '#startTutBtn' };

async function main(){
  const a = parseArgs(process.argv);
  const { chromium, devices } = loadPlaywright();

  if(a.speed > 1 && !/^\/|^[A-Za-z]:/.test(a.game))
    throw new Error('--speed only works on a local file, and the game path is not one');

  const browser = await chromium.launch({
    executablePath: findChromium(),
    // Headless is capped near the display rate otherwise. Worth ~28%.
    // Do NOT add --use-angle=swiftshader here: it software-renders the canvas
    // and measured 0.4fps against 10.
    args: ['--disable-frame-rate-limit', '--disable-gpu-vsync'],
  });

  const ctx = await browser.newContext(
    a.phone ? devices['iPhone 13'] : { viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();

  const problems = [];
  page.on('pageerror', e => problems.push('pageerror: ' + e.message));
  page.on('console', m => {
    if(m.type() !== 'error') return;
    // The webfont is fetched from the network and there is none here. That is
    // the ONLY error worth ignoring; everything else is a real finding.
    if(/net::ERR_|fonts\.googleapis\.com/.test(m.text())) return;
    problems.push('console: ' + m.text());
  });
  // Do not sit through the font timeout. Since the <link> went non-blocking
  // this costs seconds rather than the old twelve, but there is still no
  // reason to wait on a request that cannot succeed offline.
  await page.route('**fonts.googleapis.com**', r => r.abort());

  const url = 'file://' + a.game + (a.speed > 1 ? '?speed=' + a.speed : '');
  const t0 = Date.now();
  // 'domcontentloaded', not the default 'load'. The font <link> is no longer
  // parser-blocking, but it still gates the load EVENT, so goto() would sit
  // out the whole request while the game had been playable for ten seconds.
  // __laneLoaded is the real signal; wait on that and nothing else.
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => window.__laneLoaded === true, null, { timeout: a.timeout * 1000 });
  console.log('loaded in ' + (Date.now() - t0) + 'ms');

  if(a.start){
    const btn = BUTTON[a.start];
    if(!btn) throw new Error('--start must be one of ' + Object.keys(BUTTON).join(', '));
    // The consent card takes a click anywhere before the menu exists.
    await page.mouse.click(200, 200).catch(() => {});
    await page.waitForSelector(btn, { state: 'visible', timeout: a.timeout * 1000 });
    await page.click(btn);
    await page.waitForFunction(
      () => { const e = document.querySelector('#menuArt'); return !e || !e.offsetParent; },
      null, { timeout: a.timeout * 1000 });
    console.log('started ' + a.start);
  }

  if(a.at){
    // Poll the clock. Never compute a delay from wall time — headless runs
    // game time at a fraction of real, and --speed changes the fraction.
    const started = Date.now();
    const from = await clockSeconds(page);
    if(from === null) throw new Error('could not read the match clock');
    for(;;){
      const now = await clockSeconds(page);
      if(now !== null && from - now >= a.at) break;
      if(Date.now() - started > a.timeout * 1000)
        throw new Error('clock did not reach ' + a.at + 's within ' + a.timeout + 's');
      await page.waitForTimeout(100);
    }
    console.log('reached ' + a.at + 's of match clock in ' + Math.round((Date.now()-started)/1000) + 's real');
  }

  if(a.wait) await page.waitForTimeout(a.wait * 1000);

  await page.screenshot({ path: a.shot });
  console.log('wrote ' + a.shot);

  await browser.close();

  if(problems.length){
    console.error('\n' + problems.length + ' problem(s) on the page:');
    for(const p of problems) console.error('  ' + p);
    process.exitCode = 1;
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
