// Render the match theme to WAV files, one per forest voice.
//
// The audition page is the place to CHOOSE a voice; this is the place to get
// one out of the browser and into a file — to send to someone who is not going
// to open a game, to compare two takes a week apart, or to keep a record of
// what a voice sounded like on the day it was written.
//
// The synth, the arranger and both pieces are lifted straight out of
// index.html between the "music:engine" markers, exactly as tools/music-demo.js
// lifts them, so a file written here is what the game plays and not a second
// copy that can drift.
//
//   node tools/music-render.js out/                     # the piece + all four voices
//   node tools/music-render.js out/ --voice glade       # just the one
//   node tools/music-render.js out/ --seconds 40        # longer takes
//   node tools/music-render.js out/ --threat 0.9        # with a hero closing in too
//
// Rendering needs Web Audio, so it needs a browser, so it needs Playwright —
// which is NOT a dependency of this repo and must not become one. Install it
// in a scratch directory and point NODE_PATH at it, the same way tools/shoot.js
// asks for it:
//
//   cd "$SCRATCH" && npm init -y
//   PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i playwright
//   NODE_PATH="$SCRATCH/node_modules" node tools/music-render.js out/
//
// Never run `playwright install`. The browser is already on disk.

const fs = require('fs');
const os = require('os');
const path = require('path');

function loadPlaywright(){
  try { return require('playwright'); }
  catch(e){
    console.error(`cannot find playwright.

It is deliberately not a dependency of this repo. Install it in a scratch
directory and re-run with NODE_PATH pointing at it:

  cd "$SCRATCH" && npm init -y
  PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i playwright
  NODE_PATH="$SCRATCH/node_modules" node tools/music-render.js out/
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
  const a = { out: null, seconds: 24, voice: null, threat: 0, quarry: 1, song: 'play',
              game: path.join(__dirname, '..', 'index.html') };
  for(let i = 2; i < argv.length; i++){
    const k = argv[i];
    if(k === '--seconds')     a.seconds = Number(argv[++i]);
    else if(k === '--voice')  a.voice   = argv[++i];
    else if(k === '--threat') a.threat  = Number(argv[++i]);
    else if(k === '--quarry') a.quarry  = Number(argv[++i]);
    else if(k === '--song')   a.song    = argv[++i];
    else if(k === '--game')   a.game    = path.resolve(argv[++i]);
    else if(!a.out)           a.out     = argv[i];
    else throw new Error('unknown argument ' + k);
  }
  if(!a.out) throw new Error('usage: node tools/music-render.js <out-dir> [--voice key] [--seconds n]');
  if(!(a.seconds > 0)) throw new Error('--seconds takes a positive number');
  return a;
}

function engineFrom(html){
  const BEGIN = '/* music:engine begin';
  const END   = '/* music:engine end */';
  const a = html.indexOf(BEGIN), b = html.indexOf(END);
  if(a < 0 || b < 0 || b < a)
    throw new Error('could not find the music:engine markers in index.html');
  const engine = html.slice(html.indexOf('*/', a) + 2, b).trim();
  for(const need of ['function createLaneMusic(ctx, song, opts)', 'function arrangeLaneSong(song)']){
    if(engine.indexOf(need) < 0) throw new Error('the marked block is missing ' + need);
  }
  return engine;
}

async function main(){
  const a = parseArgs(process.argv);
  const { chromium } = loadPlaywright();

  const html = fs.readFileSync(a.game, 'utf8');
  const engine = engineFrom(html);
  // A bare page holding nothing but the engine, at top level rather than inside
  // an IIFE, so the render below can reach the songs by name.
  const page404 = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'lane-render-')), 'engine.html');
  fs.writeFileSync(page404, '<title>Lane render</title>\n<script>\n' + engine + '\n</' + 'script>\n');

  fs.mkdirSync(a.out, { recursive: true });

  const browser = await chromium.launch({ executablePath: findChromium() });
  const page = await browser.newPage();
  const problems = [];
  page.on('pageerror', e => problems.push('pageerror: ' + e.message));
  await page.goto('file://' + page404, { waitUntil: 'domcontentloaded' });

  const voices = await page.evaluate(song =>
    Object.keys((LANE_SONGS[song] || {}).quarry || {}), a.song);
  if(a.voice && voices.indexOf(a.voice) < 0)
    throw new Error('--voice must be one of ' + (voices.join(', ') || '(this piece has none)'));

  // The piece on its own first: every other take is only meaningful against it.
  const takes = [['silent', null]].concat((a.voice ? [a.voice] : voices).map(v => [v, v]));

  for(const [name, voice] of takes){
    const b64 = await page.evaluate(async opt => {
      const SR = 44100;
      const oc = new OfflineAudioContext(1, Math.ceil(SR * opt.seconds), SR);
      const s = Object.assign({}, LANE_SONGS[opt.song]);
      s.events = arrangeLaneSong(s);
      const m = createLaneMusic(oc, s, {});
      m.out.connect(oc.destination);
      if(opt.threat) m.setIntensity(opt.threat);
      if(opt.voice){ m.setFlavour(opt.voice); m.setQuarry(opt.quarry); }
      m.renderAll(0.2, opt.seconds);
      const buf = await oc.startRendering();
      const src = buf.getChannelData(0);
      // Halve the rate on the way out: a 22kHz mono file is a third of the
      // size and every one of these voices lives well under 8kHz.
      const n = Math.floor(src.length / 2);
      const pcm = new Int16Array(n);
      for(let i = 0; i < n; i++){
        let v = (src[i * 2] + src[i * 2 + 1]) / 2;
        v = Math.max(-1, Math.min(1, v * 0.92));
        pcm[i] = v < 0 ? v * 32768 : v * 32767;
      }
      const hdr = new ArrayBuffer(44), dv = new DataView(hdr);
      const wr = (o, str) => { for(let i = 0; i < str.length; i++) dv.setUint8(o + i, str.charCodeAt(i)); };
      wr(0, 'RIFF'); dv.setUint32(4, 36 + pcm.byteLength, true); wr(8, 'WAVEfmt ');
      dv.setUint32(16, 16, true); dv.setUint16(20, 1, true); dv.setUint16(22, 1, true);
      dv.setUint32(24, SR / 2, true); dv.setUint32(28, SR, true);
      dv.setUint16(32, 2, true); dv.setUint16(34, 16, true); wr(36, 'data');
      dv.setUint32(40, pcm.byteLength, true);
      const bytes = new Uint8Array(44 + pcm.byteLength);
      bytes.set(new Uint8Array(hdr), 0);
      bytes.set(new Uint8Array(pcm.buffer), 44);
      let bin = '';
      for(let i = 0; i < bytes.length; i += 8192)
        bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 8192));
      return btoa(bin);
    }, { song: a.song, seconds: a.seconds, voice, threat: a.threat, quarry: a.quarry });

    const file = path.join(a.out, 'lane-' + a.song + '-' + name + '.wav');
    fs.writeFileSync(file, Buffer.from(b64, 'base64'));
    console.log('wrote ' + file + ' (' + fs.statSync(file).size + ' bytes)');
  }

  await browser.close();
  fs.rmSync(path.dirname(page404), { recursive: true, force: true });

  if(problems.length){
    console.error('\n' + problems.length + ' problem(s) while rendering:');
    for(const p of problems) console.error('  ' + p);
    process.exitCode = 1;
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
