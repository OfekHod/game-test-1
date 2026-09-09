// Draws the carry's fire bolt — the sprite strip embedded in index.html as
// boltImg — and, with --embed, writes it back into index.html in place.
//
//   node tools/firebolt-sprite.js out.png [--embed]
//
// The frames are rendered in a headless Chromium canvas rather than checked in
// as art, so the flame can be retuned by editing the numbers below instead of
// by hand-editing a PNG. Playwright is NOT a dependency of the game or of the
// simulation: install it in a scratch directory and run this from that
// directory (playwright is resolved from the working directory, not from the
// repo), the same way the screenshot scripts are run. Nothing in index.html or sim/ needs
// it, and package.json still lists no dependencies.
//
// The strip is one seamless loop: every animated quantity is either a sine of
// an integer multiple of the phase or scrolls by exactly one period, so frame
// 11 hands over to frame 0 without a jump.
const fs = require('fs');
const path = require('path');

const FRAMES = 12, CW = 240, CH = 48, SS = 3;   // SS: supersample, then downscale

// Runs inside the page. Kept as one string because it is evaluated in the
// browser, where none of this file's scope exists.
const RENDER = `
const FRAMES=${FRAMES}, CW=${CW}, CH=${CH}, SS=${SS};
const W=CW*SS, H=CH*SS;

// A flame tongue: blunt on the leading side, drawn out into a point behind it,
// which is what makes the fire read as streaming backwards rather than pulsing.
function lick(d){
  return d>0 ? Math.exp(-Math.pow(d/0.028,2)) : Math.exp(-Math.pow(-d/0.12,1.25));
}
function frac(x){ return ((x%1)+1)%1; }

// Half-thickness of the flame at u along its length, for one side of it.
function edge(u, phase, side, k){
  if(u<=0) return 0;
  const cap = u>0.88 ? Math.sqrt(Math.max(0,1-Math.pow((u-0.88)/0.125,2))) : 1;
  let half = k*(0.07+0.93*Math.pow(Math.min(u,0.88)/0.88,1.9))*(u>0.88?cap:1);
  for(let i=0;i<4;i++){
    const p = frac(i/4 + side*0.5 - phase);
    const x = 0.30 + p*0.66;
    const env = Math.sin(Math.PI*p);                  // born and dies inside the body
    half += lick(u-x)*env*k*0.78*(0.75+0.25*Math.sin(2*Math.PI*(2*phase+i*0.4)));
  }
  half += k*0.07*Math.sin(2*Math.PI*(u*3.4 - 2*phase + side*0.5))*u;
  return half;
}

function ribbon(c, x0, x1, cy, k, phase){
  c.beginPath();
  const N=170;
  for(let i=0;i<=N;i++){ const x=x0+(x1-x0)*i/N; c.lineTo(x, cy - edge(i/N,phase,0,k)); }
  for(let i=N;i>=0;i--){ const x=x0+(x1-x0)*i/N; c.lineTo(x, cy + edge(i/N,phase,1,k)); }
  c.closePath();
}
function grad(c,x0,x1,cy,stops){
  const g=c.createLinearGradient(x0,cy,x1,cy);
  for(const s of stops) g.addColorStop(s[0],s[1]);
  return g;
}

function frame(c, phase){
  c.clearRect(0,0,W,H);
  const cy=H/2, headX=W-14*SS, tailX=4*SS, bodyX=tailX+(headX-tailX)*0.30;
  const k=H*0.235;

  // the hairline the bolt drags behind it
  c.save();
  c.strokeStyle=grad(c,tailX,headX,cy,[[0,'rgba(206,80,14,0)'],[0.3,'rgba(224,102,18,0.8)'],[0.62,'rgba(245,135,31,1)']]);
  c.lineWidth=2.1*SS; c.lineCap="round";
  c.beginPath();
  for(let i=0;i<=60;i++){
    const t=i/60, x=tailX+(headX-tailX)*t;
    c.lineTo(x, cy + Math.sin(2*Math.PI*(t*2.2-phase))*1.3*SS*t);
  }
  c.stroke(); c.restore();

  // heat haze, kept faint so the silhouette stays crisp
  c.save(); c.filter='blur('+(3.2*SS)+'px)'; c.globalAlpha=0.42;
  ribbon(c,bodyX,headX,cy,k*1.05,phase);
  c.fillStyle=grad(c,bodyX,headX,cy,[[0,'rgba(198,60,10,0)'],[0.5,'rgba(240,120,26,0.8)'],[1,'rgba(255,198,84,0.95)']]);
  c.fill(); c.restore();

  // outer flame
  ribbon(c,bodyX,headX,cy,k,phase);
  c.fillStyle=grad(c,bodyX,headX,cy,[[0,'rgba(212,86,14,0)'],[0.16,'rgba(226,99,16,0.95)'],[0.46,'#F5871F'],[0.78,'#FBA82A'],[1,'#FDC53C']]);
  c.fill();
  c.strokeStyle='rgba(150,50,8,0.42)'; c.lineWidth=0.9*SS; c.stroke();

  // inner flame: the yellow heart, deliberately out of step with the outside
  ribbon(c,bodyX+(headX-bodyX)*0.26,headX-2*SS,cy,k*0.44,frac(phase+0.41));
  c.fillStyle=grad(c,bodyX,headX,cy,[[0,'rgba(250,160,36,0)'],[0.5,'rgba(253,190,58,0.9)'],[0.82,'#FDD35E'],[1,'#FFEFC0']]);
  c.fill();

  // white-hot head
  c.save(); c.globalCompositeOperation='lighter';
  const hx=headX-k*0.80, hr=k*1.22;
  const hg=c.createRadialGradient(hx,cy,0,hx,cy,hr);
  hg.addColorStop(0,'rgba(255,255,250,0.98)');
  hg.addColorStop(0.34,'rgba(255,248,222,0.86)');
  hg.addColorStop(0.58,'rgba(255,226,150,0.5)');
  hg.addColorStop(1,'rgba(255,176,64,0)');
  c.fillStyle=hg; c.beginPath(); c.ellipse(hx,cy,hr*1.3,hr,0,0,7); c.fill();
  c.restore();

  // shed embers: one spacing of travel per loop, faded in and out at both ends
  for(let i=0;i<7;i++){
    const a1=Math.sin(i*12.9898)*43758.5453, fa=a1-Math.floor(a1);
    const b1=Math.sin(i*78.233)*43758.5453,  fb=b1-Math.floor(b1);
    const p=frac(i/7+fa*0.06-phase);
    const x=bodyX+(headX-bodyX)*(0.12+p*0.9);
    const side=i%2?1:-1;
    const y=cy+side*(k*(0.95+fb*0.8)+p*k*0.55);
    c.save(); c.globalAlpha=Math.sin(Math.PI*p)*0.85;
    c.fillStyle=fb>0.5?'#FDC248':'#F5871F';
    c.beginPath(); c.ellipse(x,y,(1.6+fb*1.4)*SS,(0.8+fb*0.6)*SS,side*0.3,0,7); c.fill();
    c.restore();
  }
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
  if(!out){ console.error('usage: node tools/firebolt-sprite.js <out.png> [--embed]'); process.exit(2); }
  // Resolved from the working directory, not from next to this file: playwright
  // is installed in a scratch directory precisely so it never lands in the repo.
  let chromium;
  try { chromium = require(require.resolve('playwright', { paths:[process.cwd()] })).chromium; }
  catch(e){
    console.error('firebolt-sprite: playwright not found. Install it in a scratch\n' +
                  'directory and run this from there:\n' +
                  '  cd "$SCRATCH" && npm init -y && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i playwright\n' +
                  '  node /path/to/tools/firebolt-sprite.js out.png --embed');
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
    const re = /(  boltImg\.src = 'data:image\/png;base64,)[A-Za-z0-9+/=]+(';)/;
    if(!re.test(html)){ console.error('firebolt-sprite: no boltImg.src line in index.html'); process.exit(1); }
    fs.writeFileSync(src, html.replace(re, (m,a,z)=> a + png.toString('base64') + z));
    console.log(`embedded into ${src}`);
  }
})();
