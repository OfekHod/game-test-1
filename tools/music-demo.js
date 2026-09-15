// Builds a standalone page for auditioning the match theme's two reactions:
// how close the enemy HEROES are, and how close the MOBS are. The second one
// has four voices to choose between and the page is where the choice is made,
// so both dials and the picker are live while the music plays.
//
// The synth, the arranger and both pieces are lifted straight out of
// index.html, between the "music:engine" markers, so what you hear on the page
// is byte for byte what plays in the game — there is no second copy to drift.
// The engine has no game dependencies at all: the only thing the game hands it
// is one number between 0 and 1, and on this page that number is a slider.
//
// The output has no <!doctype>, <html>, <head> or <body>: the artifact host
// supplies those itself, and a browser opening the file from disk fills them
// in. Same arrangement as tools/artifact-html.js, for the same reason.
//
//   node tools/music-demo.js <out.html>
const fs = require('fs');
const path = require('path');

const out = process.argv[2];
if(!out){ console.error('usage: node tools/music-demo.js <out.html>'); process.exit(2); }

const src = path.join(__dirname, '..', 'index.html');
const html = fs.readFileSync(src, 'utf8');

const BEGIN = '/* music:engine begin';
const END   = '/* music:engine end */';
const a = html.indexOf(BEGIN), b = html.indexOf(END);
if(a < 0 || b < 0 || b < a){
  console.error('music-demo: could not find the music:engine markers in index.html');
  process.exit(1);
}
const engine = html.slice(html.indexOf('*/', a) + 2, b).trim();
for(const need of ['function createLaneMusic(ctx, song, opts)', 'function arrangeLaneSong(song)', 'LANE_SONGS.play']){
  if(engine.indexOf(need) < 0){
    console.error('music-demo: the marked block is missing ' + need);
    process.exit(1);
  }
}
for(const [re, what] of [[/setIntensity\(v\)\{/, 'setIntensity'], [/setQuarry\(v\)\{/, 'setQuarry'],
                         [/setFlavour\(key\)\{/, 'setFlavour']]){
  if(!re.test(engine.replace(/\s/g, ''))){
    console.error('music-demo: the marked block has no ' + what + ' — nothing to audition');
    process.exit(1);
  }
}
if(!/quarry:\s*\{/.test(engine)){
  console.error('music-demo: the match theme has no quarry flavours to choose between');
  process.exit(1);
}

const page = `<title>Lane Adaptive Music</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;800&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
  /* The game's own night palette and display face, same as the soundboard.
     This is a piece of the game's furniture, not a document. */
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
  .wrap{ max-width:760px; margin:0 auto; }

  header{ padding:38px 0 20px; }
  h1{ font:800 30px/1.1 var(--display); margin:0; letter-spacing:.2px; text-wrap:balance; }
  h1 em{ font-style:normal; color:var(--gold); }
  .lede{ color:var(--dim); margin:10px 0 0; max-width:62ch; }

  .status{ display:flex; align-items:center; gap:10px; margin-top:18px; padding:9px 13px;
           border:1px solid var(--line); border-radius:8px; background:var(--stage);
           font:400 13px/1 var(--mono); color:var(--dim); }
  .status .dot{ width:8px; height:8px; border-radius:50%; background:var(--dim); flex:none; }
  .status.live{ color:var(--ink); }
  .status.live .dot{ background:var(--gold); }
  .status.blocked .dot{ background:var(--hurt); }

  h2{ font:600 11px/1 var(--mono); letter-spacing:.16em; text-transform:uppercase;
      color:var(--dim); margin:34px 0 12px; }

  button{ font:800 14px/1 var(--display); color:#1A160E; background:var(--gold);
          border:0; border-radius:7px; padding:11px 18px; cursor:pointer; flex:none;
          box-shadow:0 2px 0 rgba(0,0,0,.45); }
  button:hover{ filter:brightness(1.08); }
  button:active{ transform:translateY(1px); box-shadow:0 1px 0 rgba(0,0,0,.45); }
  button:focus-visible{ outline:2px solid var(--ink); outline-offset:2px; }
  button.ghost{ background:transparent; color:var(--ink); border:1px solid var(--line);
                box-shadow:none; font-weight:600; }
  button.ghost:hover{ background:#2A241A; }
  button.ghost[aria-pressed=true]{ background:#2E2719; border-color:var(--gold); color:var(--gold); }

  .transport{ display:flex; align-items:center; gap:10px; flex-wrap:wrap;
              padding:14px; border:1px solid var(--line); border-radius:10px; background:var(--stage); }
  .transport .sp{ flex:1; }
  .transport button.ghost{ font:600 13px/1 var(--body); padding:9px 13px; }
  .transport .pos{ font:400 12px/1 var(--mono); color:var(--dim); }

  /* The slider is the page. It gets the room a control gets when it is the
     only thing you are meant to touch. */
  .dial{ margin-top:14px; padding:20px 18px 16px; border:1px solid var(--line);
         border-radius:10px; background:var(--stage); }
  .dial .top{ display:flex; align-items:baseline; gap:12px; }
  .dial .num{ font:800 44px/1 var(--display); color:var(--gold); font-variant-numeric:tabular-nums; }
  .dial .says{ color:var(--dim); font-size:14px; }
  .dial .says b{ color:var(--ink); font-weight:500; }
  input[type=range]{ width:100%; margin:16px 0 0; accent-color:var(--gold); height:26px; }
  /* Ticks where the layers come in, positioned from the engine's own numbers. */
  .ticks{ position:relative; height:34px; margin-top:2px; }
  .ticks i{ position:absolute; top:0; width:1px; height:9px; background:var(--line); }
  .ticks i.on{ background:var(--gold); }
  .ticks span{ position:absolute; top:12px; transform:translateX(-50%); white-space:nowrap;
               font:400 11px/1.35 var(--mono); color:var(--dim); text-align:center; }
  .ticks span.on{ color:var(--gold); }

  /* The picker. Four cards, one live — this is the decision the page exists
     to make, so it gets more room than a row of radio buttons would. */
  .flav{ display:grid; grid-template-columns:repeat(auto-fit,minmax(168px,1fr)); gap:10px; margin:0 0 14px; }
  .flav button{ text-align:left; padding:13px 14px; background:var(--stage); color:var(--ink);
                border:1px solid var(--line); box-shadow:none; font:400 13px/1.45 var(--body); }
  .flav button:hover{ background:#2A241A; }
  .flav button[aria-pressed=true]{ border-color:var(--gold); background:#2E2719; }
  .flav b{ display:block; font:800 17px/1.2 var(--display); color:var(--ink); }
  .flav[data-live] button[aria-pressed=true] b{ color:var(--gold); }
  .flav .v{ display:block; font:400 11px/1.35 var(--mono); letter-spacing:.09em; text-transform:uppercase;
            color:var(--dim); margin:5px 0 7px; }
  .flav p{ margin:0; color:var(--dim); }
  .flav button[aria-pressed=true] .v{ color:var(--gold); }
  /* One line that says what you are hearing, because "which of the four is
     this" is the only question the picker has to answer and a highlighted
     border on its own does not answer it while the music is running. */
  .nowvoice{ display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin:0 0 12px;
         padding:12px 15px; border:1px solid var(--line); border-left:3px solid var(--gold);
         border-radius:9px; background:var(--stage); }
  .nowvoice b{ font:800 19px/1.1 var(--display); color:var(--gold); }
  .nowvoice span{ font:400 13px/1.4 var(--body); color:var(--dim); }
  .nowvoice .sp{ flex:1; }

  .presets{ display:flex; gap:8px; flex-wrap:wrap; margin-top:16px; }
  .presets button{ font:600 13px/1 var(--body); padding:9px 12px; }
  .presets .n{ font:600 12px/1 var(--mono); color:var(--dim); display:block; margin-top:3px; }
  .presets button[aria-pressed=true] .n{ color:var(--gold); }

  .rows{ display:flex; flex-direction:column; gap:1px; background:var(--line);
         border:1px solid var(--line); border-radius:10px; overflow:hidden; }
  .row{ background:var(--stage); padding:12px 14px; border-left:3px solid var(--rail,var(--bone)); }
  .row .hd{ display:flex; align-items:baseline; gap:10px; }
  .row .hd b{ font:600 16px/1.25 var(--display); }
  .row .hd .amt{ margin-left:auto; font:600 12px/1 var(--mono); color:var(--dim); font-variant-numeric:tabular-nums; }
  .row.live .hd .amt{ color:var(--gold); }
  .row p{ margin:3px 0 0; color:var(--dim); font-size:13.5px; max-width:62ch; }
  .bar{ height:4px; border-radius:2px; background:#2C2619; margin-top:9px; overflow:hidden; }
  .bar i{ display:block; height:100%; width:0; background:var(--rail,var(--bone)); transition:width .08s linear; }

  .mixgrid{ display:grid; grid-template-columns:repeat(auto-fit,minmax(118px,1fr)); gap:1px;
            background:var(--line); border:1px solid var(--line); border-radius:10px; overflow:hidden; }
  .mixgrid div{ background:var(--stage); padding:11px 13px; }
  .mixgrid span{ display:block; font:400 11px/1 var(--mono); color:var(--dim);
                 letter-spacing:.08em; text-transform:uppercase; }
  .mixgrid b{ font:600 15px/1.4 var(--mono); font-variant-numeric:tabular-nums; }

  .note{ color:var(--dim); font-size:13.5px; margin-top:26px; border-top:1px solid var(--line);
         padding-top:15px; max-width:64ch; }
  .note b{ color:var(--ink); font-weight:500; }
  @media (prefers-reduced-motion:reduce){ *{ transition:none !important; } }
  @media (max-width:560px){ .dial .num{ font-size:36px; } }
</style>
<div class="wrap">
  <header>
    <h1>Lane — <em>adaptive music</em></h1>
    <p class="lede">The match theme reacts to two things, on two separate axes. <b>Enemy heroes</b>
      closing in bring the celeste and the sour ninth; <b>mobs</b> nearby bring one of four forest
      voices instead, which are written to be worth hearing rather than worrying about. Both are zero
      in an empty field, and at zero the piece is exactly what it has always been. Drag either and
      listen — the whole point of both mechanics is whether you can tell, without looking, that the
      number went up, and which number it was. <b>The forest is the new half</b>, so it comes
      first: press <em>Hear all four</em> and it plays each of its voices for eight seconds, in
      order.</p>
    <div class="status" id="status"><span class="dot"></span><span id="statusText">Press play to start audio</span></div>
  </header>

  <div class="transport">
    <button id="play">Play</button>
    <button class="ghost" id="tPlay" aria-pressed="true">Match theme</button>
    <button class="ghost" id="tMenu" aria-pressed="false">Menu theme</button>
    <span class="sp"></span>
    <button id="tour">Hear all four</button>
    <button class="ghost" id="walkIn">Walk a hero in</button>
    <button class="ghost" id="campIn">Walk into a camp</button>
    <button class="ghost" id="allOut">Everything leaves</button>
    <span class="pos" id="pos">bar &mdash;</span>
  </div>

  <h2>Mobs &mdash; the forest</h2>
  <p class="lede">A camp at the edge of a clearing is the good news, so it does not get the celeste and
    it never gets the ninth. It gets one of these four instead &mdash; pick one and it switches on the
    next beat, with the music still running. They differ by instrument, register, rhythm and harmony,
    not by amount: you should know which one you are hearing inside a bar.</p>
  <p class="nowvoice"><b id="liveName">&mdash;</b><span id="liveWhat">press <em>Hear all four</em> and it plays each of them for eight seconds, in order</span><span class="sp"></span><span id="liveStep"></span></p>
  <div class="flav" id="flav"></div>
  <div class="dial">
    <div class="top">
      <span class="num" id="qnum">0.00</span>
      <span class="says" id="qsays">Nothing in the trees. <b>Silent.</b></span>
    </div>
    <input id="qdial" type="range" min="0" max="100" value="0" aria-label="Mobs nearby">
    <div class="ticks" id="qticks"></div>
    <div class="presets" id="qpresets"></div>
  </div>

  <div class="rows" style="margin-top:14px">
    <div class="row" id="Q0" style="--rail:var(--bone)">
      <div class="hd"><b>Forest shading</b><span class="amt">0%</span></div>
      <p>No new notes. The guitar brightens a third as much as a hero makes it, and the reverb tail
        <em>lengthens</em> &mdash; which is the opposite of what the threat does to it. A player who can
        hear which way the room went knows which kind of company he has before either cue has played a
        note.</p>
      <div class="bar"><i></i></div>
    </div>
    <div class="row" id="Q1" style="--rail:#8FD98F">
      <div class="hd"><b>One in the trees</b><span class="amt">0%</span></div>
      <p>The live voice arrives. One mob reaches this at about 743 units, a camp of three at 948, the
        apex at 1338 &mdash; so a camp is heard from outside the clearing and a lone wanderer about as
        you see it.</p>
      <div class="bar"><i></i></div>
    </div>
    <div class="row" id="Q2" style="--rail:#5FBF7A">
      <div class="hd"><b>Standing in it</b><span class="amt">0%</span></div>
      <p>The voice fills out: the marimba doubles into the gaps and grows a floor, the drums flurry and
        the bass finally walks, the hum climbs the chord, the second horn answers. One mob at 423, a
        camp at 717, the apex at 762.</p>
      <div class="bar"><i></i></div>
    </div>
    <div class="row" id="Q3" style="--rail:var(--bone)">
      <div class="hd"><b>Left open by the fight</b><span class="amt">100%</span></div>
      <p>The fight always wins. Everything on this axis fades out across exactly the run-up to the
        celeste and is silent from the beat it speaks, so the two cues can never argue. In Open World
        there are no enemy heroes at all, so this stays wide open for the whole round.</p>
      <div class="bar"><i></i></div>
    </div>
  </div>

  <h2>Enemy heroes &mdash; the threat</h2>
  <div class="dial">
    <div class="top">
      <span class="num" id="num">0.00</span>
      <span class="says" id="says">Nothing near you. <b>The piece as written.</b></span>
    </div>
    <input id="dial" type="range" min="0" max="100" value="0" aria-label="Threat">
    <div class="ticks" id="ticks"></div>
    <div class="presets" id="presets"></div>
  </div>

  <h2>What is playing at this setting</h2>
  <div class="rows">
    <div class="row" id="L1" style="--rail:var(--mana)">
      <div class="hd"><b>Shading</b><span class="amt">0%</span></div>
      <p>No new notes. The guitar is picked harder and brightens with it, the pad rises and opens, the
        reverb tail shortens so the room closes in, and the guitar and piano step back a couple of
        decibels to leave room for what is coming. Curved, so it front-loads: this is all the warning
        there is before you can see anybody.</p>
      <div class="bar"><i></i></div>
    </div>
    <div class="row" id="L2" style="--rail:var(--gold)">
      <div class="hd"><b>Celeste warning</b><span class="amt">0%</span></div>
      <p>Three rising notes a bar, at MIDI 74&ndash;83 &mdash; above everything else in the piece, so it
        cannot be mistaken for part of it. One hero alone reaches this at about 697 units, two at 971,
        three at 1117 &mdash; so a group is heard well before it is seen, and a lone hero is heard about
        as it arrives.</p>
      <div class="bar"><i></i></div>
    </div>
    <div class="row" id="L3" style="--rail:#E8894A">
      <div class="hd"><b>Dive pulse</b><span class="amt">0%</span></div>
      <p>Straight eighths on the celeste, a piano note on every bar, and the bass finally moving off the
        root onto the fifth. One hero at 403 units, two at 644, three at 804. The tempo has not changed
        and never does.</p>
      <div class="bar"><i></i></div>
    </div>
    <div class="row" id="L4" style="--rail:var(--hurt)">
      <div class="hd"><b>Dread</b><span class="amt">0%</span></div>
      <p>The celeste doubles to sixteenths &mdash; the same voice at twice the rate, not a second one. A
        heartbeat on the root twice a beat, a minor ninth held over the chord until it sours, and one
        wrong note three octaves up. One hero inside 283 units gets here on its own &mdash; that is
        inside its own attack range, so it is already hitting you &mdash; and three do it from 628.</p>
      <div class="bar"><i></i></div>
    </div>
  </div>

  <h2>What the mix is doing</h2>
  <div class="mixgrid">
    <div><span>Pad</span><b id="mPad">&times;1.00</b></div>
    <div><span>Pad opens to</span><b id="mPadLp">1600 Hz</b></div>
    <div><span>Guitar cutoff</span><b id="mGtr">3400 Hz</b></div>
    <div><span>Picked harder</span><b id="mSpread">&times;1.00</b></div>
    <div><span>Room</span><b id="mWet">0.90</b></div>
    <div><span>Forest voices</span><b id="mForest">&times;0.55</b></div>
  </div>

  <p class="note">In the game this number is not a slider. Every living enemy hero contributes
    <b>one over its distance</b>, windowed to be exactly 1 at 250 units and exactly 0 at 1600, and the
    shares are <b>added and capped</b> &mdash; added rather than averaged, so <b>one hero close enough
    pins it on its own and a group gets there from further out</b>. It saturates at <b>250 for one, 430
    for two, 570 for three</b>; the celeste starts at 697, 971 and 1117. 1600 is the gap between the two
    lanes, so a hero laning in the other one contributes exactly nothing and an empty lane is the piece
    as written, to the sample. The game smooths it too &mdash; a third of a second up, two and a half
    down &mdash; so what the music follows is the shape of a gank rather than the jitter of someone
    strafing at the edge of the ring.</p>
  <p class="note" style="margin-top:14px">The forest number is the same arithmetic over the mobs: a
    share each, <b>1 at 300 units and 0 at 1100</b>, added and capped, with the apex counted from
    <b>1.8&times; further out</b> because it matters from 1.8&times; further out. It is slower both ways
    than the threat &mdash; <b>half a second up, nearly two down</b> &mdash; because nothing in the trees
    is about to kill you and a cue that snapped on as you walked past a camp would be an alarm, which
    is the one thing this is not. In the game the voice is whichever one is set as the default;
    <b>?mob=grove|hunt|glade|horns</b> overrides it, including on the published build.
    Keys: <b>space</b> play, <b>&larr; &rarr;</b> threat, <b>&uarr; &darr;</b> forest,
    <b>1&ndash;4</b> threat presets, <b>5&ndash;8</b> the four voices,
    <b>Q</b> hear all four, <b>A</b> walk a hero in, <b>D</b> walk into a camp.</p>
</div>
<script>
(function(){

${engine}

  /* ------------------------------------------------------------- playback */

  const SONGS = {
    play: { key: 'play', label: 'Match theme' },
    menu: { key: 'menu', label: 'Menu theme' },
  };
  let ctx = null, track = null, which = 'play', failed = false, level = 0.8;
  let intensity = 0, quarry = 0, ramp = null;
  const built = {};

  // The four forest voices, read straight off the piece rather than listed
  // here: a flavour added in index.html appears on this page with its own
  // name and its own description and nothing to keep in step.
  const FLAVOURS = Object.keys(LANE_SONGS.play.quarry || {})
    .map(k => Object.assign({ key: k }, LANE_SONGS.play.quarry[k]));
  let flavour = LANE_SONGS.play.quarryDefault || (FLAVOURS[0] || {}).key || null;

  // Arranging a piece is a few hundred pushes and a sort, so both are done up
  // front and kept: switching themes must not stall on a rebuild.
  function song(key){
    const s = Object.assign({}, LANE_SONGS[key]);
    s.events = arrangeLaneSong(s);
    return s;
  }

  // A track built on an offline context that is never rendered. It exists so
  // the meters can ask the engine itself where a layer comes in and how far up
  // it is, before anything has been played and without duplicating the rule
  // here where it could drift.
  const probe = (function(){
    try{
      const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
      if(!OAC) return null;
      return createLaneMusic(new OAC(2, 4410, 44100), song('play'), { lite: true });
    }catch(err){ return null; }
  })();
  // One question, one answer: where every layer is and what the mix is doing,
  // both straight off the engine, so nothing on this page is a second copy of
  // a rule that lives in index.html.
  function readout(){
    if(!probe) return null;
    probe.setIntensity(intensity);
    probe.setQuarry(quarry);
    probe.setFlavour(flavour);
    return {
      gains:  probe.tiers.map((_, t) => probe.layerGain(t)),
      qgains: probe.quarryTiers.map((_, t) => probe.layerGain(t, 'quarry', flavour)),
      sh: probe.shading(),
    };
  }
  const TIERS = probe ? probe.tiers : [0, 0.24, 0.55, 0.80];
  const QTIERS = probe ? probe.quarryTiers : [0, 0.18, 0.60];

  const el = id => document.getElementById(id);
  function paintStatus(){
    const s = el('status'), t = el('statusText');
    el('play').textContent = (track && track.running) ? 'Stop' : 'Play';
    s.classList.remove('live', 'blocked');
    if(failed || !ctx){
      if(failed){ s.classList.add('blocked'); t.textContent = 'This browser will not start audio on this page'; }
      else t.textContent = 'Press play to start audio';
      return;
    }
    if(ctx.state === 'running' && track && track.running){
      s.classList.add('live');
      t.textContent = SONGS[which].label + ' — drag the slider while it plays';
      return;
    }
    s.classList.add('blocked');
    t.textContent = ctx.state === 'running' ? 'Stopped' : 'Audio is ' + ctx.state + ' — press play again';
  }

  function stop(){
    if(track) track.stop(0.5);
    paintStatus();
  }
  function start(){
    if(failed) return;
    try{
      const AC = window.AudioContext || window.webkitAudioContext;
      if(!AC) throw new Error('no Web Audio');
      if(!ctx) ctx = new AC();
      if(ctx.state === 'suspended'){
        const r = ctx.resume();
        if(r && r.then) r.then(paintStatus, paintStatus);
      }
      for(const k in built){ if(k !== which && built[k].running) built[k].stop(0.5); }
      if(!built[which]){
        const m = createLaneMusic(ctx, song(which), {});
        m.out.connect(ctx.destination);
        built[which] = m;
      }
      track = built[which];
      track.setLevel(level);
      track.setIntensity(intensity);
      track.setQuarry(quarry);
      if(flavour) track.setFlavour(flavour);
      if(!track.running) track.start(0.8);
    }catch(err){
      failed = true;
      console.error('audio unavailable', err);
    }
    paintStatus();
  }
  function toggle(){ (track && track.running) ? stop() : start(); }

  /* ---------------------------------------------------------------- dial */

  // What the number means, in the terms the game will produce it in.
  const SAYS = [
    [0.02, 'Nothing within 1600 units. <b>The piece as written.</b>'],
    [0.12, 'Something is out at the edge of the ring. <b>The guitar is picked a little harder.</b>'],
    [0.24, 'Closing. <b>Still no new voice — this is the warning about the warning.</b>'],
    [0.40, 'One around 700 out, or the team at 1100. <b>The celeste is in.</b>'],
    [0.55, 'Closer than you can see. <b>The pulse is coming in.</b>'],
    [0.70, 'One inside 450, or three inside 700. <b>The bass has started moving.</b>'],
    [0.86, 'Inside its own attack range. <b>The dread is arriving.</b>'],
    [1.01, 'One at 250, two at 430, three at 570. <b>Sixteenths, heartbeat, sour ninth. Leave.</b>'],
  ];
  const PRESETS = [
    ['Nobody near', 0.00], ['One at 900', 0.28],
    ['One at 500', 0.59], ['One on top of you', 1.00],
  ];
  // The same three distances the game's own table is written against.
  const QSAYS = [
    [0.02, 'Nothing within 1100 units. <b>Silent.</b>'],
    [0.18, 'Something is out past the treeline. <b>The guitar has brightened a little and the room has grown.</b>'],
    [0.40, 'One mob at 743, a camp at 948, the apex at 1338. <b>The voice is in.</b>'],
    [0.60, 'Close enough to pull. <b>Still the one figure.</b>'],
    [1.01, 'One at 423, a camp at 717, the apex at 762. <b>You are standing in it.</b>'],
  ];
  const QPRESETS = [
    ['Empty forest', 0.00], ['A camp at 950', 0.19],
    ['At the edge of it', 0.62], ['In among them', 1.00],
  ];

  function setIntensity(v, fromSlider){
    intensity = Math.max(0, Math.min(1, v));
    if(track) track.setIntensity(intensity);
    if(!fromSlider) el('dial').value = String(Math.round(intensity * 100));
    paintDial();
  }
  function setQuarry(v, fromSlider){
    quarry = Math.max(0, Math.min(1, v));
    if(track) track.setQuarry(quarry);
    if(!fromSlider) el('qdial').value = String(Math.round(quarry * 100));
    paintDial();
  }
  function setFlavour(key){
    flavour = key;
    if(track) track.setFlavour(key);
    paintDial();
  }
  function paintDial(){
    const v = intensity;
    el('num').textContent = v.toFixed(2);
    for(const [upto, text] of SAYS){ if(v < upto){ el('says').innerHTML = text; break; } }
    el('qnum').textContent = quarry.toFixed(2);
    for(const [upto, text] of QSAYS){ if(quarry < upto){ el('qsays').innerHTML = text; break; } }

    const r = readout();
    const amts = [v].concat(r ? r.gains.slice(1) : [0, 0, 0]);
    ['L1', 'L2', 'L3', 'L4'].forEach((id, i) => {
      const row = el(id), amt = amts[i] || 0;
      row.classList.toggle('live', amt > 0.02);
      row.querySelector('.bar i').style.width = (amt * 100).toFixed(1) + '%';
      row.querySelector('.amt').textContent = Math.round(amt * 100) + '%';
    });
    // The forest rows: its own shading, its two layers, and the duck — which
    // is drawn as what is LEFT rather than as what was taken, so the bar
    // emptying is the forest going quiet.
    const duck = r ? r.sh.duck : 1;
    const qamts = [r ? r.sh.qd : 0].concat(r ? r.qgains.slice(1) : [0, 0]).concat([duck]);
    ['Q0', 'Q1', 'Q2', 'Q3'].forEach((id, i) => {
      const row = el(id), amt = qamts[i] || 0;
      row.classList.toggle('live', i === 3 ? amt < 0.98 : amt > 0.02);
      if(i === 3) row.style.setProperty('--rail', amt < 0.98 ? 'var(--hurt)' : 'var(--bone)');
      row.querySelector('.bar i').style.width = (amt * 100).toFixed(1) + '%';
      row.querySelector('.amt').textContent = Math.round(amt * 100) + (i === 3 ? '% open' : '%');
    });
    if(r){
      el('mPad').textContent = '\\u00d7' + r.sh.padMul.toFixed(2);
      el('mPadLp').textContent = Math.round(r.sh.padLp) + ' Hz';
      el('mGtr').textContent = Math.round(r.sh.gtrLp * r.sh.gtrLpQ) + ' Hz';
      el('mSpread').textContent = '\\u00d7' + r.sh.spread.toFixed(2);
      el('mWet').textContent = r.sh.wet.toFixed(2);
      el('mForest').textContent = '\\u00d7' + r.sh.forest.toFixed(2);
    }

    const ps = el('presets').children;
    for(let i = 0; i < ps.length; i++)
      ps[i].setAttribute('aria-pressed', String(Math.abs(PRESETS[i][1] - v) < 0.005));
    const qs = el('qpresets').children;
    for(let i = 0; i < qs.length; i++)
      qs[i].setAttribute('aria-pressed', String(Math.abs(QPRESETS[i][1] - quarry) < 0.005));
    const fs = el('flav').children;
    for(let i = 0; i < fs.length; i++)
      fs[i].setAttribute('aria-pressed', String(FLAVOURS[i].key === flavour));
    paintLive();
  }

  // Ticks read their positions off the engine, so if a threshold moves in
  // index.html the picture moves with it.
  (function ticks(){
    const mk = (box, v, text) => {
      const i = document.createElement('i'), s = document.createElement('span');
      i.style.left = s.style.left = (v * 100) + '%';
      s.textContent = text;
      box.appendChild(i); box.appendChild(s);
    };
    const LABELS = ['', 'celeste in', 'pulse in', 'dread in'];
    for(let t = 1; t < TIERS.length; t++) mk(el('ticks'), TIERS[t], LABELS[t] || ('tier ' + t));
    const QLABELS = ['', 'voice in', 'fills out'];
    for(let t = 1; t < QTIERS.length; t++) mk(el('qticks'), QTIERS[t], QLABELS[t] || ('tier ' + t));
  })();

  (function presets(){
    const mk = (box, list, offset, set) => {
      list.forEach(([label, v], i) => {
        const b = document.createElement('button');
        b.className = 'ghost';
        b.innerHTML = label + '<span class="n">' + v.toFixed(2) + ' &middot; key ' + (i + offset) + '</span>';
        b.addEventListener('click', () => { set(v); if(!(track && track.running)) start(); });
        box.appendChild(b);
      });
    };
    mk(el('presets'), PRESETS, 1, v => setIntensity(v));
    mk(el('qpresets'), QPRESETS, 1, v => setQuarry(v));
  })();

  // The picker. Pressing one switches the live voice under the running music
  // — nothing is rebuilt, because every flavour is already arranged into the
  // same event list and fire() drops the ones that are not playing.
  (function picker(){
    const box = el('flav');
    FLAVOURS.forEach((f, i) => {
      const b = document.createElement('button');
      b.innerHTML = '<b>' + f.label + '</b><span class="v">' + f.voices +
                    ' &middot; key&nbsp;' + (i + 5) + '</span><p>' + f.blurb + '</p>';
      b.addEventListener('click', () => {
        if(tourTimer) stopTour();
        setFlavour(f.key);
        // Pressing a voice with nothing in the trees is asking to hear it, so
        // put something in the trees.
        if(quarry < 0.62) setQuarry(0.62);
        if(!(track && track.running)) start();
      });
      box.appendChild(b);
    });
  })();

  // An enemy does not teleport to point blank, and a slider dragged by hand
  // does not move the way one walking in does. This is the shape the game will
  // actually produce: eight seconds from the edge of the ring to on top of
  // you, then a slow release once they give up.
  // The 'set' argument is which axis is being walked, so one easing drives a hero
  // arriving and a player walking into a camp — the two differ in how long
  // they take and in nothing else.
  function walk(set, from, to, seconds){
    if(ramp) cancelAnimationFrame(ramp);
    const t0 = performance.now();
    const step = now => {
      const k = Math.min(1, (now - t0) / (seconds * 1000));
      // Eased, because a hero does not cover the last hundred units at the
      // same rate the ring's edge is crossed: the number moves slowly out
      // there, where the falloff is shallow, and quickly once they are close.
      set(from + (to - from) * (k * k * (3 - 2 * k)));
      ramp = k < 1 ? requestAnimationFrame(step) : null;
    };
    if(!(track && track.running)) start();
    ramp = requestAnimationFrame(step);
  }
  const walkHero = () => walk(setIntensity, intensity, 1, 8);
  const walkCamp = () => walk(setQuarry, quarry, 1, 6);
  // Both at once, so the duck is audible as the thing it is: the forest
  // getting out of the way rather than simply stopping.
  function leave(){
    if(ramp) cancelAnimationFrame(ramp);
    const t0 = performance.now(), i0 = intensity, q0 = quarry;
    const step = now => {
      const k = Math.min(1, (now - t0) / 5000), e = k * k * (3 - 2 * k);
      setIntensity(i0 * (1 - e)); setQuarry(q0 * (1 - e));
      ramp = k < 1 ? requestAnimationFrame(step) : null;
    };
    ramp = requestAnimationFrame(step);
  }

  /* ------------------------------------------------------------- the tour

     The one button that cannot be got wrong: it starts the music if it is not
     running, puts something in the trees if there is nothing there, and plays
     all four voices in order with the name of the live one in front of you.
     Switching by hand works and always did, but it asks the listener to
     remember what the last one sounded like, which is the hardest possible
     way to compare four things. */
  const TOUR_SECONDS = 8;
  let tourTimer = null, tourIdx = 0;
  function paintLive(){
    const f = FLAVOURS.find(x => x.key === flavour);
    el('liveName').textContent = f ? f.label : '\\u2014';
    el('liveWhat').innerHTML = f
      ? (quarry < 0.05
          ? 'would be playing &mdash; but there is nothing in the trees. Raise the dial below.'
          : f.voices + ' &middot; ' + f.blurb)
      : 'press <em>Hear all four</em> and it plays each of them for eight seconds, in order';
    el('liveStep').textContent = tourTimer ? (tourIdx + ' of ' + FLAVOURS.length) : '';
    // Not 'Stop': the transport already has a Stop, and two buttons a few
    // pixels apart both saying it is a way to stop the wrong one.
    el('tour').textContent = tourTimer ? 'Stop the tour' : 'Hear all four';
  }
  function stopTour(){
    if(tourTimer){ clearInterval(tourTimer); tourTimer = null; }
    paintDial();
  }
  function tour(){
    if(tourTimer){ stopTour(); return; }
    if(!(track && track.running)) start();
    // Deep enough that the second layer is in: the four differ most where
    // they have all of their notes.
    if(quarry < 0.85) setQuarry(0.85);
    tourIdx = 0;
    const step = () => {
      if(tourIdx >= FLAVOURS.length){ stopTour(); return; }
      setFlavour(FLAVOURS[tourIdx].key);
      tourIdx++;
      paintLive();
    };
    step();
    tourTimer = setInterval(step, TOUR_SECONDS * 1000);
    paintLive();
  }

  /* --------------------------------------------------------------- input */

  el('play').addEventListener('click', toggle);
  el('dial').addEventListener('input', e => {
    if(ramp){ cancelAnimationFrame(ramp); ramp = null; }
    setIntensity(e.target.value / 100, true);
  });
  el('qdial').addEventListener('input', e => {
    if(ramp){ cancelAnimationFrame(ramp); ramp = null; }
    setQuarry(e.target.value / 100, true);
  });
  function pick(key){
    which = key;
    el('tPlay').setAttribute('aria-pressed', String(key === 'play'));
    el('tMenu').setAttribute('aria-pressed', String(key === 'menu'));
    if(track && track.running) start(); else paintStatus();
  }
  el('tPlay').addEventListener('click', () => pick('play'));
  el('tMenu').addEventListener('click', () => pick('menu'));
  el('tour').addEventListener('click', tour);
  el('walkIn').addEventListener('click', walkHero);
  el('campIn').addEventListener('click', walkCamp);
  el('allOut').addEventListener('click', leave);

  document.addEventListener('keydown', e => {
    if(e.metaKey || e.ctrlKey || e.altKey) return;
    if(e.target && e.target.tagName === 'INPUT' && e.key !== ' ') return;
    const k = e.key.toLowerCase();
    if(k === ' ' || e.key === 'Spacebar'){ e.preventDefault(); toggle(); return; }
    if(e.key === 'ArrowLeft' || e.key === 'ArrowRight'){
      e.preventDefault();
      setIntensity(intensity + (e.key === 'ArrowRight' ? 1 : -1) * (e.shiftKey ? 0.1 : 0.02));
      return;
    }
    if(e.key === 'ArrowUp' || e.key === 'ArrowDown'){
      e.preventDefault();
      setQuarry(quarry + (e.key === 'ArrowUp' ? 1 : -1) * (e.shiftKey ? 0.1 : 0.02));
      return;
    }
    if(k >= '1' && k <= '4'){ e.preventDefault(); const p = PRESETS[+k - 1]; setIntensity(p[1]); if(!(track && track.running)) start(); return; }
    if(k >= '5' && k <= '8'){
      e.preventDefault();
      const f = FLAVOURS[+k - 5];
      if(f){ setFlavour(f.key); if(quarry < 0.62) setQuarry(0.62); if(!(track && track.running)) start(); }
      return;
    }
    if(k === 'q'){ e.preventDefault(); tour(); return; }
    if(k === 'a'){ e.preventDefault(); walkHero(); return; }
    if(k === 'd'){ e.preventDefault(); walkCamp(); return; }
    if(k === 's'){ e.preventDefault(); leave(); return; }
  });

  /* The loop position, so it is obvious that the layers are locked to the bar
     and not to when you happened to let go of the slider. */
  (function tickPos(){
    const p = el('pos');
    setInterval(() => {
      if(!track || !track.running){ p.textContent = 'bar \\u2014'; return; }
      const beats = track.position();
      p.textContent = 'bar ' + (Math.floor(beats / 4) + 1) + ' \\u00b7 beat ' + (Math.floor(beats % 4) + 1);
    }, 120);
  })();

  paintDial();
  paintStatus();
})();
<\/script>
`;

fs.writeFileSync(out, page);
console.log(`wrote ${out} (${Buffer.byteLength(page)} bytes), engine lifted from ${src}`);
