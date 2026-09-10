// Draws the log a chopped tree drops — the sprite strip embedded in index.html
// as woodImg — and, with --embed, writes it back into index.html in place.
//
//   node tools/wood-sprite.js out.png [--embed]
//
// Same terms as tools/firebolt-sprite.js: the frames are rendered in a headless
// Chromium canvas rather than checked in as art, so the log can be retuned by
// editing the numbers below instead of by hand-editing a PNG. Playwright is NOT
// a dependency of the game or of the simulation — install it in a scratch
// directory and run this from that directory.
//
// The animation is one billet of firewood turning on the spot, about the
// screen's vertical axis, the way a platformer's coin does. That rotation is
// what the geometry below is: a cylinder of length L and radius R, spun by
// theta and projected flat.
//
//   silhouette  a stadium — a rectangle L*|cos| wide and 2R tall, capped at
//               both ends by half-ellipses R*|sin| across
//   end grain   the cap nearer the camera, an R*|sin| by R ellipse of rings,
//               which crosses the barrel and swaps ends once per turn
//   bark        streaks that run ALONG the log, so each one is a line at
//               screen y = R*cos(phi), slid sideways by R*sin(phi)*sin(theta)
//               and faded out by its own normal as it wraps out of sight
//
// A full turn, so the strip loops: the log is symmetric end for end, but the
// grain is not, and half a turn would jump.
const fs = require('fs');
const path = require('path');

const FRAMES = 16, CW = 44, CH = 28, SS = 4;   // SS: supersample, then downscale

// Runs inside the page. Kept as one string because it is evaluated in the
// browser, where none of this file's scope exists.
const RENDER = `
const FRAMES=${FRAMES}, CW=${CW}, CH=${CH}, SS=${SS};
const W=CW*SS, H=CH*SS;
const L=30*SS, R=8.6*SS;          // the billet: length and radius, in device pixels

// Bark reads as three bands rather than one smooth cylinder shade: a lit top, a
// mid, and a dark underside. A smooth gradient made the log look like a pill.
const BARK=[[0,'#3b2716'],[0.16,'#6b4a2b'],[0.42,'#8a6236'],[0.62,'#7a5530'],[1,'#33210f']];
const GRAIN=[[0,'#e0bb84'],[0.55,'#c99a5f'],[1,'#a87944']];
const RING='rgba(120,80,40,0.55)';
const EDGE='rgba(40,25,12,0.85)';

// Minkowski sum of the axis segment and the cross-section ellipse: the outline
// of a cylinder at any angle, including edge-on, where it is a bare rectangle.
function stadium(c, halfLen, capX, cy){
  c.beginPath();
  if(capX < 0.01){ c.rect(-halfLen, cy-R, halfLen*2, R*2); return; }
  c.moveTo(-halfLen, cy-R);
  c.lineTo(halfLen, cy-R);
  c.ellipse(halfLen, cy, capX, R, 0, -Math.PI/2, Math.PI/2);
  c.lineTo(-halfLen, cy+R);
  c.ellipse(-halfLen, cy, capX, R, 0, Math.PI/2, Math.PI*1.5);
  c.closePath();
}

function bandFill(c, cy, stops){
  const g=c.createLinearGradient(0, cy-R, 0, cy+R);
  for(const s of stops) g.addColorStop(s[0], s[1]);
  return g;
}

function frame(c, phase){
  c.clearRect(0,0,W,H);
  const th = phase*Math.PI*2;
  const ct = Math.cos(th), st = Math.sin(th);
  const halfLen = L*0.5*Math.abs(ct), capX = R*Math.abs(st);
  const cy = H/2;

  c.save();
  c.translate(W/2, 0);

  // ---- the barrel
  stadium(c, halfLen, capX, cy);
  c.save(); c.clip();
  c.fillStyle = bandFill(c, cy, BARK);
  c.fillRect(-W, 0, W*2, H);

  // ---- bark running the length of it
  for(let i=0;i<14;i++){
    const phi = (i/14)*Math.PI*2;
    const n = Math.sin(phi)*ct;                 // the streak's normal, towards the camera
    if(n <= 0) continue;
    const y  = cy + R*Math.cos(phi);
    const dx = R*Math.sin(phi)*st;
    const seed = Math.sin(i*78.233)*43758.5453;
    const j = seed - Math.floor(seed);
    c.globalAlpha = Math.min(1, n)*0.5*(0.5+j);
    c.strokeStyle = j > 0.5 ? '#2e1d0e' : '#a97c46';
    c.lineWidth = (0.7+j*1.1)*SS*Math.abs(ct);
    c.beginPath();
    c.moveTo(dx-halfLen*0.94, y);
    c.lineTo(dx+halfLen*0.94, y + (j-0.5)*1.6*SS);
    c.stroke();
  }
  c.globalAlpha = 1;

  // ---- the sheen along the top, which is what says "round"
  const sg=c.createLinearGradient(0, cy-R, 0, cy);
  sg.addColorStop(0,'rgba(255,226,170,0)');
  sg.addColorStop(0.55,'rgba(255,226,170,0.30)');
  sg.addColorStop(1,'rgba(255,226,170,0)');
  c.fillStyle=sg; c.fillRect(-W, cy-R, W*2, R);
  c.restore();

  // ---- the cut face, at whichever end is nearer the camera
  if(capX > 0.4){
    const ex = -Math.sign(st)*halfLen;
    c.save();
    c.translate(ex, cy);
    c.beginPath(); c.ellipse(0,0,capX,R,0,0,7);
    c.fillStyle = bandFill(c, 0, GRAIN); c.fill();
    c.strokeStyle = EDGE; c.lineWidth = 0.9*SS; c.stroke();
    // Growth rings, off-centre the way a real round is, and a heart at the middle.
    c.strokeStyle = RING; c.lineWidth = 0.6*SS;
    for(let k=1;k<=3;k++){
      const s=k/4;
      c.beginPath(); c.ellipse(capX*0.12*s, -R*0.10*s, capX*s*0.86, R*s*0.86, 0,0,7); c.stroke();
    }
    c.beginPath(); c.ellipse(capX*0.12, -R*0.10, capX*0.10, R*0.10, 0,0,7);
    c.fillStyle='rgba(120,80,40,0.7)'; c.fill();
    c.restore();
  }

  // ---- one outline over the whole thing, so it reads at 26 pixels wide
  stadium(c, halfLen, capX, cy);
  c.strokeStyle = EDGE; c.lineWidth = 1.1*SS; c.stroke();
  c.restore();
}

const strip=document.createElement('canvas');
strip.width=CW*FRAMES; strip.height=CH;
const sc=strip.getContext('2d');
const cell=document.createElement('canvas'); cell.width=W; cell.height=H;
const cc=cell.getContext('2d');
for(let f=0;f<FRAMES;f++){ frame(cc,f/FRAMES); sc.drawImage(cell,0,0,W,H,f*CW,0,CW,CH); }
window.__strip=strip.toDataURL('image/png');
`;

(async () => {
  const out = process.argv[2];
  if(!out){ console.error('usage: node tools/wood-sprite.js <out.png> [--embed]'); process.exit(2); }
  // Resolved from the working directory, not from next to this file: playwright
  // is installed in a scratch directory precisely so it never lands in the repo.
  let chromium;
  try { chromium = require(require.resolve('playwright', { paths:[process.cwd()] })).chromium; }
  catch(e){
    console.error('wood-sprite: playwright not found. Install it in a scratch\n' +
                  'directory and run this from there:\n' +
                  '  cd "$SCRATCH" && npm init -y && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i playwright\n' +
                  '  node /path/to/tools/wood-sprite.js out.png --embed');
    process.exit(1);
  }
  const exe = process.env.CHROMIUM_PATH ||
    (fs.readdirSync('/opt/pw-browsers').filter(d=>d.startsWith('chromium-'))
       .map(d=>'/opt/pw-browsers/'+d+'/chrome-linux/chrome').find(fs.existsSync));
  const b = await chromium.launch(exe ? { executablePath: exe } : {});
  const p = await b.newPage();
  await p.setContent('<body></body>');
  await p.evaluate(RENDER);
  const url = await p.evaluate(() => window.__strip);
  await b.close();
  const png = Buffer.from(url.split(',')[1], 'base64');
  fs.writeFileSync(out, png);
  console.log(`wrote ${out} (${png.length} bytes, ${FRAMES} frames of ${CW}x${CH})`);

  if(process.argv.includes('--embed')){
    const src = path.join(__dirname, '..', 'index.html');
    const html = fs.readFileSync(src, 'utf8');
    const re = /(  woodImg\.src = 'data:image\/png;base64,)[A-Za-z0-9+/=]*(';)/;
    if(!re.test(html)){ console.error('wood-sprite: no woodImg.src line in index.html'); process.exit(1); }
    fs.writeFileSync(src, html.replace(re, (m,a,z)=> a + png.toString('base64') + z));
    console.log(`embedded into ${src}`);
  }
})();
