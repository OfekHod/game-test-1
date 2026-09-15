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
    --gold:#D9A029; --mana:#7FB8F2; --hurt:#FF7A6B; --bone:#D8CBB0; --blink:#8FE3FF;
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
  /* A press has to be visible on its own. If the browser will not let the page
     make a sound, a button that only makes sounds looks broken. */
  .row{ transition:background .1s ease; }
  .row.hot{ background:#2E2719; }
  .status.blocked .dot{ background:var(--hurt); }

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
    <p class="lede">Every one-shot in the game and one river, synthesised on the spot from a handful of oscillators
      and two shared noise buffers: no samples, no files, a few hundred bytes in all. This page runs the same code the
      game does. The traces are each sound's real envelope, rendered offline.</p>
    <div class="status" id="status"><span class="dot"></span><span id="statusText">Press a button or a key to start audio</span></div>
  </header>

  <h2>Impacts</h2>
  <div class="rows">
    <div class="row" style="--rail:var(--bone)"><span class="key">1</span><span class="t"><b>Hit a creep</b><span>A light papery tick. You hear fifty a minute, so it stays out of the way.</span></span><canvas data-wave="creep"></canvas><button data-i="creep">Play</button></div>
    <div class="row" style="--rail:var(--gold)"><span class="key">2</span><span class="t"><b>Crit a creep</b><span>The same hit with a ring six milliseconds in — noticed without becoming a second sound.</span></span><canvas data-wave="crit"></canvas><button data-i="crit">Play</button></div>
    <div class="row" style="--rail:var(--bone)"><span class="key">3</span><span class="t"><b>Hit a hero</b><span>Lower and heavier: a thock rather than a tick. Something with weight took that.</span></span><canvas data-wave="hero"></canvas><button data-i="hero">Play</button></div>
    <div class="row" style="--rail:var(--hurt)"><span class="key">4</span><span class="t"><b>Take a hit</b><span>Duller and twice as long, with a sawtooth swept shut underneath. The one you must react to.</span></span><canvas data-wave="hurt"></canvas><button data-i="hurt">Play</button></div>
    <div class="row" style="--rail:var(--gold)"><span class="key"></span><span class="t"><b>Last-hit a creep</b><span>The tick with a brighter crack and the crit's ring cut to half. Gone, not looted.</span></span><canvas data-wave="i:kill"></canvas><button data-i="kill">Play</button></div>
    <div class="row" style="--rail:var(--gold)"><span class="key"></span><span class="t"><b>Kill a hero</b><span>A hollow crack over a timber-weight body, and two notes falling a fifth under it.</span></span><canvas data-wave="i:heroKill"></canvas><button data-i="heroKill">Play</button></div>
    <div class="row" style="--rail:var(--bone)"><span class="key"></span><span class="t"><b>Sword landing</b><span>The tank's blow. Lowest of the hits on the living &mdash; the body starts where the hero's ends.</span></span><canvas data-wave="i:heavy"></canvas><button data-i="heavy">Play</button></div>
    <div class="row" style="--rail:var(--hurt)"><span class="key"></span><span class="t"><b>You die</b><span>Timber's body under the hurt groan doubled, and a half-second wash after it.</span></span><canvas data-wave="i:death" data-sec="1.1"></canvas><button data-i="death">Play</button></div>
  </div>

  <h2>Siege</h2>
  <div class="rows">
    <div class="row" style="--rail:var(--bone)"><span class="key"></span><span class="t"><b>Shell on a tower</b><span>A short high crack with almost nothing under it. Stone does not give.</span></span><canvas data-wave="i:stone"></canvas><button data-i="stone">Play</button></div>
    <div class="row" style="--rail:var(--bone)"><span class="key"></span><span class="t"><b>Tower falls</b><span>Timber a third again the size, the dust sweeping down for six tenths of a second, and a second landing behind the first.</span></span><canvas data-wave="i:collapse" data-sec="1.2"></canvas><button data-i="collapse">Play</button></div>
    <div class="row" style="--rail:var(--hurt)"><span class="key"></span><span class="t"><b>Rocket lands</b><span>Lowpassed, not banded: pressure rather than pitch. Two bodies 30 ms apart and debris over the top.</span></span><canvas data-wave="i:boom" data-sec="1.0"></canvas><button data-i="boom">Play</button></div>
    <div class="row" style="--rail:var(--hurt)"><span class="key"></span><span class="t"><b>Tower shell lands</b><span>The same blast at half. A siege should rumble under the fight, not be the fight.</span></span><canvas data-wave="i:boom:0.5" data-sec="1.0"></canvas><button data-i="boom" data-amp="0.5">Play</button></div>
  </div>

  <h2>Shots</h2>
  <div class="rows">
    <div class="row" style="--rail:var(--gold)"><span class="key"></span><span class="t"><b>Flame round</b><span>The carry's held fire, five a second. Short, quiet, mostly high, with a moment of burn after the crack.</span></span><canvas data-wave="s:fire"></canvas><button data-s="fire">Play</button></div>
    <div class="row" style="--rail:var(--mana)"><span class="key"></span><span class="t"><b>Bolt</b><span>The support's shot. Lighter still.</span></span><canvas data-wave="s:bolt"></canvas><button data-s="bolt">Play</button></div>
    <div class="row" style="--rail:var(--hurt)"><span class="key"></span><span class="t"><b>Rocket launch</b><span>A thump for the charge and a band swept UP for once &mdash; the air shoved out ahead of the shell.</span></span><canvas data-wave="s:rocket"></canvas><button data-s="rocket">Play</button></div>
    <div class="row" style="--rail:var(--bone)"><span class="key"></span><span class="t"><b>Sword swing</b><span>A whoosh with no body at all. The weight is in the landing.</span></span><canvas data-wave="s:swing"></canvas><button data-s="swing">Play</button></div>
  </div>

  <h2>Pickups</h2>
  <div class="rows">
    <div class="row" style="--rail:var(--gold)"><span class="key">5</span><span class="t"><b>Gold</b><span>A blip and a note a fifth above it. Pick up another within a second and it climbs a rung.</span></span><canvas data-wave="gold"></canvas><button data-p="gold">Play</button></div>
    <div class="row" style="--rail:var(--mana)"><span class="key">6</span><span class="t"><b>Mana</b><span>A fifth lower and gliding up rather than clinking, with a breath of high noise over it.</span></span><canvas data-wave="mana"></canvas><button data-p="mana">Play</button></div>
  </div>

  <h2>Ability</h2>
  <div class="rows">
    <div class="row" style="--rail:var(--blink)"><span class="key">7</span><span class="t"><b>Blink</b><span>Two sounds, 120 ms apart: air closing over where you were, then a landing where you are.</span></span><canvas data-wave="blink"></canvas><button data-t="1">Play</button></div>
    <div class="row" style="--rail:var(--blink)"><span class="key"></span><span class="t"><b>Respawn</b><span>The blink's arriving half and nothing else. "The hero is now HERE."</span></span><canvas data-wave="f:respawn"></canvas><button data-f="respawn">Play</button></div>
    <div class="row" style="--rail:var(--mana)"><span class="key"></span><span class="t"><b>Heal cast</b><span>One sine gliding up a fourth with no transient. Liquid leaving the hands.</span></span><canvas data-wave="f:healCast"></canvas><button data-f="healCast">Play</button></div>
    <div class="row" style="--rail:var(--mana)"><span class="key"></span><span class="t"><b>Heal lands</b><span>The level-up's smaller, softer cousin. Three percent of pitch either way per cast.</span></span><canvas data-wave="f:heal"></canvas><button data-f="heal">Play</button></div>
    <div class="row" style="--rail:var(--gold)"><span class="key"></span><span class="t"><b>Level up</b><span>A bell run up a major arpeggio onto a two-octave chord. An enemy's plays at a third the size.</span></span><canvas data-wave="f:levelUp" data-sec="1.0"></canvas><button data-f="levelUp">Play</button></div>
    <div class="row" style="--rail:var(--blink)"><span class="key"></span><span class="t"><b>Skill ready</b><span>Two sines a fifth apart, the second held. A question answered.</span></span><canvas data-wave="f:ready"></canvas><button data-f="ready">Play</button></div>
    <div class="row" style="--rail:var(--hurt)"><span class="key"></span><span class="t"><b>Denied</b><span>A press that did nothing. A short low buzz, quieter than everything around it.</span></span><canvas data-wave="f:deny"></canvas><button data-f="deny">Play</button></div>
  </div>

  <h2>The round and the HUD</h2>
  <div class="rows">
    <div class="row" style="--rail:var(--bone)"><span class="key"></span><span class="t"><b>Wave</b><span>A low horn on the D both pieces of music are written in. A note from the score, not a thing on the map.</span></span><canvas data-wave="f:wave" data-sec="0.8"></canvas><button data-f="wave">Play</button></div>
    <div class="row" style="--rail:var(--bone)"><span class="key"></span><span class="t"><b>Switch hero</b><span>Two ticks a fifth apart. The smallest possible "that took".</span></span><canvas data-wave="u:switch" data-sec="0.3"></canvas><button data-u="switch">Play</button></div>
    <div class="row" style="--rail:var(--bone)"><span class="key"></span><span class="t"><b>Give an order</b><span>A crinkle with a blip under it, because an order is a thing written down.</span></span><canvas data-wave="u:order" data-sec="0.3"></canvas><button data-u="order">Play</button></div>
    <div class="row" style="--rail:var(--gold)"><span class="key"></span><span class="t"><b>Win</b><span>The level-up's chord an octave down and held, then a fourth up with the sparkle.</span></span><canvas data-wave="st:win" data-sec="1.8"></canvas><button data-st="win">Play</button></div>
    <div class="row" style="--rail:var(--hurt)"><span class="key"></span><span class="t"><b>Lose</b><span>The minor shape of the same chord, lower and longer, with the hurt groan under it.</span></span><canvas data-wave="st:lose" data-sec="1.8"></canvas><button data-st="lose">Play</button></div>
    <div class="row" style="--rail:var(--bone)"><span class="key"></span><span class="t"><b>Draw</b><span>A bare major triad in the middle. No sparkle, no groan.</span></span><canvas data-wave="st:draw" data-sec="1.5"></canvas><button data-st="draw">Play</button></div>
  </div>

  <h2>Ambience</h2>
  <div class="rows">
    <div class="row" style="--rail:var(--mana)"><span class="key">8</span><span class="t"><b>Standing in the river</b><span>The one sustained sound in the game. Open fifths on D &mdash; the note both pieces of music are written on &mdash; over water that never quite repeats.</span></span><button data-r="0">Play</button></div>
    <div class="row" style="--rail:var(--mana)"><span class="key">9</span><span class="t"><b>Wading across it</b><span>The same water with the tops of the ripples turned up. In a match this layer rides your walking speed.</span></span><button data-r="1">Play</button></div>
  </div>

  <h2>How they land in a match</h2>
  <div class="rows">
    <div class="row seq" style="--rail:var(--gold)"><span class="key">Q</span><span class="t"><b>Eight gold in a row</b><span>What clearing a wave's drops sounds like. The ladder is most of why it feels like anything.</span></span><button data-d="goldrun">Play</button></div>
    <div class="row seq" style="--rail:var(--mana)"><span class="key">W</span><span class="t"><b>Six mana in a row</b><span>The same climb, lower and rounder.</span></span><button data-d="manarun">Play</button></div>
    <div class="row seq" style="--rail:var(--bone)"><span class="key">E</span><span class="t"><b>A wave dies</b><span>Five creeps with a crit among them, then the drops. The busiest second the game has.</span></span><button data-d="wave">Play</button></div>
    <div class="row seq" style="--rail:var(--hurt)"><span class="key">R</span><span class="t"><b>A trade</b><span>You hitting a hero, them hitting you, interleaved. This is the pair that has to be told apart.</span></span><button data-d="trade">Play</button></div>
    <div class="row seq" style="--rail:var(--blink)"><span class="key">Y</span><span class="t"><b>Blink across the lane</b><span>Leaving on the left, arriving on the right. In a match the two ends really are that far apart.</span></span><button data-d="blinkfar">Play</button></div>
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

  let ctx = null, rig = null, level = 0.55, failed = false;
  const statusEl = () => document.getElementById('status');
  const statusTx = () => document.getElementById('statusText');
  // The status line reads the context rather than remembering that we asked it
  // to start. A page that says "running" while the browser is holding the tap
  // shut is worse than one that says nothing: the buttons look broken and the
  // page has just told you they are not.
  function paint(){
    const el = statusEl(), t = statusTx();
    el.classList.remove('live', 'blocked');
    if(failed || !ctx){ el.classList.add('blocked'); t.textContent = 'This browser will not start audio on this page'; return; }
    if(ctx.state === 'running'){ el.classList.add('live'); t.textContent = 'Audio running — keys 1-9, Q W E R T Y'; return; }
    el.classList.add('blocked');
    t.textContent = 'Audio is ' + ctx.state + ' — press a button again to start it';
  }
  function ready(){
    if(failed) return null;
    try{
      if(!rig){
        const AC = window.AudioContext || window.webkitAudioContext;
        if(!AC) throw new Error('no Web Audio');
        ctx = new AC();
        rig = createLaneSfx(ctx);
      }
      if(ctx.state === 'suspended'){
        const r = ctx.resume();
        if(r && r.then) r.then(paint, paint);
      }
      rig.master.gain.value = level;
    }catch(err){
      failed = true;
      console.error('audio unavailable', err);
    }
    paint();
    return rig;
  }
  const mid = { pan: 0, gain: 1 };
  const hit = (k, p, amp) => { const r = ready(); if(r) r.impact(k, p || mid, amp); };
  const shoot = k => { const r = ready(); if(r) r.shot(k, mid); };
  // The placed one-shots take a { pan, gain }; the unplaced ones take nothing
  // and ignore it, so one call shape serves both.
  const one = k => { const r = ready(); if(r) r[k](mid); };
  const sting = k => { const r = ready(); if(r) r.stinger(k); };
  const uiTick = k => { const r = ready(); if(r) r.ui(k); };
  const pick = (k, n, p) => { const r = ready(); if(r) r.pickup(k, n || 0, p || mid); };
  const blink = (a, b) => { const r = ready(); if(r) r.teleport(a || mid, b || mid, 0.12); };
  // The river is a place, not an event, so its two buttons are toggles rather
  // than triggers, and they share one voice: pressing "wading" while the river
  // is already running opens the splash layer instead of starting a second
  // one, which is exactly what walking does in the game.
  let riverRig = null, riverOn = false, riverMotion = 0;
  function river(motion){
    const r = ready();
    if(!r) return;
    if(!riverRig) riverRig = r.riverVoice();
    if(riverOn && riverMotion === motion){ riverOn = false; riverRig.set(0, 0, 0); }
    else { riverOn = true; riverMotion = motion; riverRig.set(1, 0, motion); }
    for(const b of document.querySelectorAll('button[data-r]'))
      b.textContent = (riverOn && +b.dataset.r === riverMotion) ? 'Stop' : 'Play';
  }
  // Independent of whether a sound came out.
  function flash(el){
    const row = el && el.closest ? el.closest('.row') : null;
    if(!row) return;
    row.classList.add('hot');
    clearTimeout(row._t);
    row._t = setTimeout(() => row.classList.remove('hot'), 220);
  }
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
    blinkfar(){ blink({ pan: -0.7, gain: 0.85 }, { pan: 0.6, gain: 1 }); },
  };

  /* ---------------------------------------------------------------- input */

  document.addEventListener('click', e => {
    const b = e.target.closest('button');
    if(!b){ ready(); return; }
    flash(b);
    if(b.dataset.i) hit(b.dataset.i, null, b.dataset.amp ? +b.dataset.amp : undefined);
    else if(b.dataset.s) shoot(b.dataset.s);
    else if(b.dataset.f) one(b.dataset.f);
    else if(b.dataset.st) sting(b.dataset.st);
    else if(b.dataset.u) uiTick(b.dataset.u);
    else if(b.dataset.p) pick(b.dataset.p, 0);
    else if(b.dataset.t) blink();
    else if(b.dataset.r) river(+b.dataset.r);
    else if(b.dataset.d) DEMOS[b.dataset.d]();
  });
  const KEYS = { '1':()=>hit('creep'), '2':()=>hit('crit'), '3':()=>hit('hero'), '4':()=>hit('hurt'),
                 '5':()=>pick('gold',0), '6':()=>pick('mana',0), '7':()=>blink(),
                 '8':()=>river(0), '9':()=>river(1),
                 q:DEMOS.goldrun, w:DEMOS.manarun, e:DEMOS.wave, r:DEMOS.trade, t:DEMOS.pan,
                 y:DEMOS.blinkfar };
  document.addEventListener('keydown', e => {
    if(e.metaKey || e.ctrlKey || e.altKey) return;
    const f = KEYS[e.key.toLowerCase()];
    if(!f) return;
    e.preventDefault();
    const b = document.querySelector('.row .key');
    const row = [...document.querySelectorAll('.row')].find(r =>
      r.querySelector('.key') && r.querySelector('.key').textContent.toLowerCase() === e.key.toLowerCase());
    if(row) flash(row.querySelector('button'));
    f();
  });

  /* -------------------------------------------------------------- traces
     Each row's picture is that sound rendered through an OfflineAudioContext
     and reduced to peaks — the real envelope, not a drawing of one. It needs
     no gesture, so the page has its waveforms before anything is clicked. */

  // A bare name is the original seven; "i:kind[:amp]", "s:kind", "f:name",
  // "st:kind" and "u:kind" reach the rest of the rig the way the buttons do.
  function play(r, spec, p){
    const [fam, kind, amp] = spec.split(':');
    if(kind == null){
      if(spec === 'blink') r.teleport(p, p, 0.12);
      else if(spec === 'gold' || spec === 'mana') r.pickup(spec, 0, p);
      else r.impact(spec, p);
    }
    else if(fam === 'i') r.impact(kind, p, amp ? +amp : undefined);
    else if(fam === 's') r.shot(kind, p);
    else if(fam === 'f') r[kind](p);
    else if(fam === 'st') r.stinger(kind);
    else if(fam === 'u') r.ui(kind);
  }
  function trace(cv, kind, sec){
    const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    if(!OAC) return;
    const sr = 44100;
    const oc = new OAC(1, Math.floor(sr * (sec || 0.75)), sr);
    const r = createLaneSfx(oc);
    const p = { pan: 0, gain: 1 };
    play(r, kind, p);
    oc.startRendering().then(buf => {
      const d = buf.getChannelData(0);
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = cv.clientWidth || 104, h = cv.clientHeight || 30;
      cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
      const c = cv.getContext('2d');
      c.setTransform(dpr, 0, 0, dpr, 0, 0);
      const css = getComputedStyle(document.documentElement);
      // The rail's colour, so the trace and the row agree about what family a
      // sound is in without a second table to keep in step.
      const row = cv.closest('.row');
      const rail = row ? getComputedStyle(row).getPropertyValue('--rail').trim() : '';
      const tok = rail.indexOf('var(') === 0 ? rail.slice(4, -1) : '';
      c.fillStyle = (tok ? css.getPropertyValue(tok).trim() : '') || '#D8CBB0';
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
  // Never fatal: a picture is worth less than a working button, and this used
  // to run before the listeners were attached, so one throw in here took the
  // whole page's interactivity with it.
  document.querySelectorAll('canvas[data-wave]').forEach(cv => {
    try{ trace(cv, cv.dataset.wave, cv.dataset.sec ? +cv.dataset.sec : 0); }catch(err){ console.error('trace failed', err); }
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
