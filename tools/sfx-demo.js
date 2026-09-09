// Builds a standalone soundboard for the game's sound effects.
//
// The synth is lifted straight out of index.html, between the "sfx:engine"
// markers, so what you hear on the page is byte for byte what plays in the
// game — there is no second copy to drift. Only rng, mtof and clamp are
// supplied here, because the engine's three dependencies live elsewhere in the
// file and are one line each.
//
// The output has no <!doctype>, <html>, <head> or <body>: the artifact host
// supplies those itself, and a browser opening the file from disk fills them
// in. Same arrangement as tools/artifact-html.js, for the same reason.
//
//   node tools/sfx-demo.js <out.html>
const fs = require('fs');
const path = require('path');

const out = process.argv[2];
if(!out){ console.error('usage: node tools/sfx-demo.js <out.html>'); process.exit(2); }

const src = path.join(__dirname, '..', 'index.html');
const html = fs.readFileSync(src, 'utf8');

const BEGIN = '/* sfx:engine begin';
const END   = '/* sfx:engine end */';
const a = html.indexOf(BEGIN), b = html.indexOf(END);
if(a < 0 || b < 0 || b < a){
  console.error('sfx-demo: could not find the sfx:engine markers in index.html');
  process.exit(1);
}
const engine = html.slice(html.indexOf('*/', a) + 2, b).trim();
if(!/function createLaneSfx\(ctx\)/.test(engine)){
  console.error('sfx-demo: the marked block does not define createLaneSfx');
  process.exit(1);
}

const page = `<title>Lane Soundboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;800&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
  /* One world, deliberately: the game's own night palette, its own display
     face, its own gold and mana blue. No light variant — this is a piece of
     the game's furniture, not a document. */
  :root{
    --bark:#16140F; --stage:#201C15; --line:#372F22;
    --ink:#F2E8D4; --dim:#9E9179;
    --gold:#D9A029; --mana:#7FB8F2; --hurt:#FF7A6B; --bone:#D8CBB0;
    --display:'Baloo 2',ui-rounded,system-ui,sans-serif;
    --body:'IBM Plex Sans',system-ui,-apple-system,Segoe UI,sans-serif;
    --mono:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace;
  }
  *{ box-sizing:border-box; }
  body{ background:var(--bark); color:var(--ink); font:400 15px/1.55 var(--body);
        margin:0; padding:0 20px 72px; }
  .wrap{ max-width:720px; margin:0 auto; }

  header{ padding:38px 0 22px; }
  h1{ font:800 30px/1.1 var(--display); margin:0; letter-spacing:.2px; text-wrap:balance; }
  h1 em{ font-style:normal; color:var(--gold); }
  .lede{ color:var(--dim); margin:10px 0 0; max-width:58ch; }

  .status{ display:flex; align-items:center; gap:10px; margin-top:18px; padding:9px 13px;
           border:1px solid var(--line); border-radius:8px; background:var(--stage);
           font:400 13px/1 var(--mono); color:var(--dim); }
  .status .dot{ width:8px; height:8px; border-radius:50%; background:var(--dim); flex:none; }
  .status.live{ color:var(--ink); }
  .status.live .dot{ background:var(--gold); }

  h2{ font:600 11px/1 var(--mono); letter-spacing:.16em; text-transform:uppercase;
      color:var(--dim); margin:34px 0 12px; }

  /* Not cards: a list, with a rail on the left that says which family a sound
     belongs to. Gold, mana blue, bone for the hits you land, red for the one
     you take — the same four colours the game paints those events in. */
  .rows{ display:flex; flex-direction:column; gap:1px; background:var(--line);
         border:1px solid var(--line); border-radius:10px; overflow:hidden; }
  .row{ display:flex; align-items:center; gap:14px; background:var(--stage); padding:12px 14px;
        border-left:3px solid var(--rail,var(--bone)); }
  .row .key{ font:600 12px/1 var(--mono); color:var(--dim); width:20px; flex:none; text-align:center; }
  .row .t{ flex:1; min-width:0; }
  .row .t b{ display:block; font:600 16px/1.25 var(--display); }
  .row .t span{ color:var(--dim); font-size:13.5px; display:block; }
  canvas{ width:104px; height:30px; flex:none; opacity:.85; }
  @media (max-width:560px){ canvas{ display:none; } .row .t span{ font-size:12.5px; } }

  button{ font:800 14px/1 var(--display); color:#1A160E; background:var(--rail,var(--gold));
          border:0; border-radius:7px; padding:10px 16px; cursor:pointer; flex:none;
          box-shadow:0 2px 0 rgba(0,0,0,.45); }
  button:hover{ filter:brightness(1.08); }
  button:active{ transform:translateY(1px); box-shadow:0 1px 0 rgba(0,0,0,.45); }
  button:focus-visible, .row:focus-visible{ outline:2px solid var(--ink); outline-offset:2px; }
  .row.seq button{ background:transparent; color:var(--ink); border:1px solid var(--line);
                   box-shadow:none; font-weight:600; }
  .row.seq button:hover{ background:#2A241A; }

  .vol{ display:flex; align-items:center; gap:14px; margin:26px 0 0;
        font:400 13px/1 var(--mono); color:var(--dim); }
  input[type=range]{ flex:1; accent-color:var(--gold); }
  .note{ color:var(--dim); font-size:13.5px; margin-top:26px; border-top:1px solid var(--line);
         padding-top:15px; max-width:60ch; }
  @media (prefers-reduced-motion:reduce){ *{ transition:none !important; } }
</style>
<div class="wrap">
  <header>
    <h1>Lane — <em>sound effects</em></h1>
    <p class="lede">Five one-shots, synthesised on the spot from a handful of oscillators and one shared
      noise buffer: no samples, no files, a few hundred bytes in all. This page runs the same code the
      game does. The traces are each sound's real envelope, rendered offline.</p>
    <div class="status" id="status"><span class="dot"></span><span id="statusText">Click anything to start audio</span></div>
  </header>

  <h2>Impacts</h2>
  <div class="rows">
    <div class="row" style="--rail:var(--bone)"><span class="key">1</span><span class="t"><b>Hit a creep</b><span>A light papery tick. You hear fifty a minute, so it stays out of the way.</span></span><canvas data-wave="creep"></canvas><button data-i="creep">Play</button></div>
    <div class="row" style="--rail:var(--gold)"><span class="key">2</span><span class="t"><b>Crit a creep</b><span>The same hit with a ring six milliseconds in — noticed without becoming a second sound.</span></span><canvas data-wave="crit"></canvas><button data-i="crit">Play</button></div>
    <div class="row" style="--rail:var(--bone)"><span class="key">3</span><span class="t"><b>Hit a hero</b><span>Lower and heavier: a thock rather than a tick. Something with weight took that.</span></span><canvas data-wave="hero"></canvas><button data-i="hero">Play</button></div>
    <div class="row" style="--rail:var(--hurt)"><span class="key">4</span><span class="t"><b>Take a hit</b><span>Duller and twice as long, with a sawtooth swept shut underneath. The one you must react to.</span></span><canvas data-wave="hurt"></canvas><button data-i="hurt">Play</button></div>
  </div>

  <h2>Pickups</h2>
  <div class="rows">
    <div class="row" style="--rail:var(--gold)"><span class="key">5</span><span class="t"><b>Gold</b><span>A blip and a note a fifth above it. Pick up another within a second and it climbs a rung.</span></span><canvas data-wave="gold"></canvas><button data-p="gold">Play</button></div>
    <div class="row" style="--rail:var(--mana)"><span class="key">6</span><span class="t"><b>Mana</b><span>A fifth lower and gliding up rather than clinking, with a breath of high noise over it.</span></span><canvas data-wave="mana"></canvas><button data-p="mana">Play</button></div>
  </div>

  <h2>How they land in a match</h2>
  <div class="rows">
    <div class="row seq" style="--rail:var(--gold)"><span class="key">Q</span><span class="t"><b>Eight gold in a row</b><span>What clearing a wave's drops sounds like. The ladder is most of why it feels like anything.</span></span><button data-d="goldrun">Play</button></div>
    <div class="row seq" style="--rail:var(--mana)"><span class="key">W</span><span class="t"><b>Six mana in a row</b><span>The same climb, lower and rounder.</span></span><button data-d="manarun">Play</button></div>
    <div class="row seq" style="--rail:var(--bone)"><span class="key">E</span><span class="t"><b>A wave dies</b><span>Five creeps with a crit among them, then the drops. The busiest second the game has.</span></span><button data-d="wave">Play</button></div>
    <div class="row seq" style="--rail:var(--hurt)"><span class="key">R</span><span class="t"><b>A trade</b><span>You hitting a hero, them hitting you, interleaved. This is the pair that has to be told apart.</span></span><button data-d="trade">Play</button></div>
    <div class="row seq" style="--rail:var(--bone)"><span class="key">T</span><span class="t"><b>Across the screen</b><span>One hit walked left to right. In the game the pan and the level are where it happened.</span></span><button data-d="pan">Play</button></div>
  </div>

  <div class="vol"><span>Volume</span><input id="vol" type="range" min="0" max="100" value="55" aria-label="Volume"><span id="volv">0.55</span></div>
  <p class="note">Levels are the shipped ones, with no music underneath and nothing ducking them. In a
    match they sit below the score, which takes a little more edge off the top. Off the edge of the
    view a sound is never scheduled at all, so the other lane is silent.</p>
</div>
<script>
(function(){
  const rng = seed => { let a = seed >>> 0; return function(){
    a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296; }; };
  const mtof = m => 440 * Math.pow(2, (m - 69) / 12);
  const clamp = (v, lo, hi) => v < lo ? lo : v > hi ? hi : v;

${engine}

  /* ------------------------------------------------------------ playback */

  let ctx = null, rig = null, level = 0.55, live = false;
  function ready(){
    if(!rig){
      ctx = new (window.AudioContext || window.webkitAudioContext)();
      rig = createLaneSfx(ctx);
    }
    if(ctx.state === 'suspended') ctx.resume();
    rig.master.gain.value = level;
    if(!live){
      live = true;
      document.getElementById('status').classList.add('live');
      document.getElementById('statusText').textContent = 'Audio running — keys 1-6, Q W E R T';
    }
    return rig;
  }
  const mid = { pan: 0, gain: 1 };
  const hit = (k, p) => ready().impact(k, p || mid);
  const pick = (k, n, p) => ready().pickup(k, n || 0, p || mid);
  const later = (ms, fn) => setTimeout(fn, ms);

  const DEMOS = {
    goldrun(){ for(let i = 0; i < 8; i++) later(i * 150, () => pick('gold', i)); },
    manarun(){ for(let i = 0; i < 6; i++) later(i * 190, () => pick('mana', i)); },
    wave(){
      [0, 90, 150, 260, 300].forEach((ms, i) => later(ms, () =>
        hit(i === 3 ? 'crit' : 'creep', { pan: (i - 2) * 0.22, gain: 1 })));
      for(let i = 0; i < 5; i++) later(520 + i * 140, () => pick('gold', i, { pan: (i - 2) * 0.15, gain: 1 }));
      for(let i = 0; i < 2; i++) later(600 + i * 210, () => pick('mana', i, { pan: 0.12, gain: 0.9 }));
    },
    trade(){
      [0, 380, 760].forEach(ms => later(ms, () => hit('hero', { pan: 0.35, gain: 1 })));
      [190, 560].forEach(ms => later(ms, () => hit('hurt', { pan: -0.2, gain: 1 })));
    },
    pan(){ for(let i = 0; i < 9; i++) later(i * 130, () => hit('hero', { pan: -0.8 + i * 0.2, gain: 1 })); },
  };

  /* -------------------------------------------------------------- traces
     Each row's picture is that sound rendered through an OfflineAudioContext
     and reduced to peaks — the real envelope, not a drawing of one. It needs
     no gesture, so the page has its waveforms before anything is clicked. */

  const COLOR = { creep:'--bone', crit:'--gold', hero:'--bone', hurt:'--hurt', gold:'--gold', mana:'--mana' };
  function trace(cv, kind){
    const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    if(!OAC) return;
    const sec = 0.75, sr = 44100;
    const oc = new OAC(1, Math.floor(sr * sec), sr);
    const r = createLaneSfx(oc);
    const p = { pan: 0, gain: 1 };
    if(kind === 'gold' || kind === 'mana') r.pickup(kind, 0, p); else r.impact(kind, p);
    oc.startRendering().then(buf => {
      const d = buf.getChannelData(0);
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = cv.clientWidth || 104, h = cv.clientHeight || 30;
      cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
      const c = cv.getContext('2d');
      c.setTransform(dpr, 0, 0, dpr, 0, 0);
      const css = getComputedStyle(document.documentElement);
      c.fillStyle = css.getPropertyValue(COLOR[kind] || '--bone').trim() || '#D8CBB0';
      const cols = w, per = Math.floor(d.length / cols);
      // Normalised per sound: these are shapes to compare, not levels.
      let peak = 1e-6;
      for(let i = 0; i < d.length; i++){ const v = Math.abs(d[i]); if(v > peak) peak = v; }
      for(let x = 0; x < cols; x++){
        let m = 0;
        for(let i = x * per, e = i + per; i < e; i++){ const v = Math.abs(d[i]); if(v > m) m = v; }
        const bar = Math.max(0.6, (m / peak) * (h / 2));
        c.fillRect(x, h / 2 - bar, 1, bar * 2);
      }
    }).catch(() => {});
  }
  document.querySelectorAll('canvas[data-wave]').forEach(cv => trace(cv, cv.dataset.wave));

  /* ---------------------------------------------------------------- input */

  document.addEventListener('click', e => {
    const b = e.target.closest('button');
    if(!b){ ready(); return; }
    if(b.dataset.i) hit(b.dataset.i);
    else if(b.dataset.p) pick(b.dataset.p, 0);
    else if(b.dataset.d) DEMOS[b.dataset.d]();
  });
  const KEYS = { '1':()=>hit('creep'), '2':()=>hit('crit'), '3':()=>hit('hero'), '4':()=>hit('hurt'),
                 '5':()=>pick('gold',0), '6':()=>pick('mana',0),
                 q:DEMOS.goldrun, w:DEMOS.manarun, e:DEMOS.wave, r:DEMOS.trade, t:DEMOS.pan };
  document.addEventListener('keydown', e => {
    if(e.metaKey || e.ctrlKey || e.altKey) return;
    const f = KEYS[e.key.toLowerCase()];
    if(f){ e.preventDefault(); f(); }
  });
  const vol = document.getElementById('vol'), volv = document.getElementById('volv');
  vol.addEventListener('input', () => {
    level = vol.value / 100;
    volv.textContent = level.toFixed(2);
    if(rig) rig.master.gain.value = level;
  });
})();
<\/script>
`;

fs.writeFileSync(out, page);
console.log(`wrote ${out} (${Buffer.byteLength(page)} bytes), engine lifted from ${src}`);
