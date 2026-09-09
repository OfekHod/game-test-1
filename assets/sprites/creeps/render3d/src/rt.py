"""Raymarched SDF creep renderer: builds a GLSL shader, runs it in headless
Chromium via WebGL2, and pulls the framebuffer back out as a PNG."""
import base64, pathlib, re, subprocess, sys, tempfile, time

BS = chr(92)
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

HEADER = r"""#version 300 es
precision highp float;
out vec4 fragColor;
uniform vec2 uRes;
uniform float uSS;

// ---------- noise ----------
float hash(vec3 p){ p=fract(p*0.3183099+vec3(0.11,0.17,0.13)); p*=17.0; return fract(p.x*p.y*p.z*(p.x+p.y+p.z)); }
float vnoise(vec3 x){
  vec3 i=floor(x), f=fract(x); f=f*f*(3.0-2.0*f);
  return mix(mix(mix(hash(i+vec3(0,0,0)),hash(i+vec3(1,0,0)),f.x),
                 mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),
             mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),
                 mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);
}
float fbm(vec3 p){ float a=0.5,s=0.0; for(int i=0;i<5;i++){ s+=a*vnoise(p); p*=2.03; a*=0.5;} return s; }

// ---------- sdf primitives ----------
float sdSphere(vec3 p,float r){ return length(p)-r; }
float sdEllip(vec3 p,vec3 r){ float k0=length(p/r), k1=length(p/(r*r)); return k0*(k0-1.0)/max(k1,1e-6); }
float sdCap(vec3 p,vec3 a,vec3 b,float ra,float rb){
  vec3 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/dot(ba,ba),0.0,1.0);
  return length(pa-ba*h)-mix(ra,rb,h);
}
float sdBox(vec3 p,vec3 b,float r){ vec3 q=abs(p)-b; return length(max(q,0.0))+min(max(q.x,max(q.y,q.z)),0.0)-r; }
float sdCone(vec3 p,vec3 a,vec3 b,float ra,float rb){ return sdCap(p,a,b,ra,rb); }
float smin(float a,float b,float k){ float h=clamp(0.5+0.5*(b-a)/k,0.0,1.0); return mix(b,a,h)-k*h*(1.0-h); }
float smax(float a,float b,float k){ return -smin(-a,-b,k); }
vec2 mmin(vec2 a,vec2 b){ return a.x<b.x?a:b; }
vec2 smin2(vec2 a,vec2 b,float k){ float d=smin(a.x,b.x,k); return vec2(d, a.x<b.x?a.y:b.y); }
mat2 rot(float a){ float c=cos(a),s=sin(a); return mat2(c,-s,s,c); }
vec3 rotY(vec3 v,float a){ float c=cos(a),s=sin(a); return vec3(c*v.x+s*v.z, v.y, -s*v.x+c*v.z); }

// ---------- animation state, set per sprite cell in main() ----------
float gPhase;           // 0..1 through the clip
float gYaw;             // camera orbit, radians
uniform float uClip;    // 0 idle, 1 walk, 2 attack
uniform float uHipY;    // hip pivot height
uniform float uShldY;   // shoulder pivot height
uniform float uArmZ;    // |z| beyond which geometry counts as an arm
uniform float uAmp;     // per-creep amplitude scale
uniform float uLip;     // Lipschitz compensation for the rig warp
uniform float uLegAmp;  // 0 disables the leg hinge (robed figures: the cut tears the hem)
uniform vec3  uShadowTint;  // colour the cel shadow band is tinted toward
uniform float uInk;         // silhouette ink line strength
uniform float uSpec;        // stepped specular strength
uniform float uContrast;    // 1 = flat cel ramp, >1 deepens the shadow band
const float TAU = 6.28318530718;

// Hinge the region below a pivot, opposite sign per side of the body.
// Limbs are separated in z, so sign(p.z) selects near vs far leg/arm.
vec3 hingeLegs(vec3 p, float ang){
  // Hard cut at the hip plane keeps this a *rigid* transform below the pivot,
  // so the distance field stays exactly valid inside the leg region. A varying
  // angle here would shear space and tear the legs apart while marching.
  if(p.y > uHipY) return p;
  float s = (p.z < 0.0) ? 1.0 : -1.0;
  float a = s*ang;
  p.y -= uHipY; p.xy *= rot(a); p.y += uHipY;
  return p;
}
vec3 hingeArms(vec3 p, float ang, float sameDir){
  float hw = smoothstep(uShldY+0.10, uShldY-0.16, p.y);
  float zw = smoothstep(uArmZ*0.35, uArmZ*1.05, abs(p.z));
  float w = hw*zw;
  if(w <= 0.001) return p;
  float s = mix((p.z < 0.0) ? 1.0 : -1.0, 1.0, sameDir);
  float a = s*ang*w;
  p.y -= uShldY; p.xy *= rot(a); p.y += uShldY;
  return p;
}
vec3 leanTorso(vec3 p, float ang){
  float w = smoothstep(uHipY-0.10, uHipY+0.22, p.y);
  if(w <= 0.001) return p;
  float a = ang*w;
  p.y -= uHipY; p.xy *= rot(a); p.y += uHipY;
  return p;
}
vec3 rig(vec3 p){
  float ph = gPhase;
  if(uClip < 0.5){
    float b = sin(ph*TAU);
    p.y -= 0.010*uAmp*b;
    p = hingeArms(p, 0.055*uAmp*b, 0.0);
    p = leanTorso(p, 0.020*uAmp*b);
  } else if(uClip < 1.5){
    float sw = sin(ph*TAU);
    p.y -= 0.026*uAmp*abs(cos(ph*TAU));
    p = hingeLegs(p,  0.46*uAmp*uLegAmp*sw);
    p = hingeArms(p, -0.24*uAmp*sw, 0.0);
    p = leanTorso(p, 0.045*uAmp);
  } else {
    float w = smoothstep(0.0,0.34,ph) - smoothstep(0.34,0.52,ph)*1.9
            + smoothstep(0.52,1.0,ph)*0.9;
    p = hingeArms(p, -0.85*uAmp*w, 1.0);
    p = leanTorso(p, -0.30*uAmp*w);
  }
  return p;
}
"""

FOOTER = r"""
vec2 map(vec3 p){ vec2 h=mapRaw(rig(p)); h.x*=uLip; return h; }

uniform vec2  uCell;
uniform vec2  uGrid;      // cols, rows of cells in this image
uniform float uFrames;    // frames in the clip
uniform float uDirBase;   // first direction index in this image
uniform float uDirTotal;  // directions in the full set (yaw = i*TAU/uDirTotal)
uniform float uElev;
uniform float uDist;
uniform float uFL;
uniform vec3  uTarget;

vec2 march(vec3 ro,vec3 rd){
  float t=0.35; vec2 res=vec2(-1.0);
  for(int i=0;i<190;i++){
    vec3 p=ro+rd*t; vec2 h=map(p);
    if(h.x<0.0006*t){ res=vec2(t,h.y); break; }
    t+=h.x*0.80; if(t>7.0) break;
  }
  return res;
}
vec3 calcNormal(vec3 p){
  vec2 e=vec2(1.0,-1.0)*0.0009;
  return normalize(e.xyy*map(p+e.xyy).x + e.yyx*map(p+e.yyx).x +
                   e.yxy*map(p+e.yxy).x + e.xxx*map(p+e.xxx).x);
}
float softShadow(vec3 ro,vec3 rd,float mint,float maxt,float k){
  float res=1.0,t=mint;
  for(int i=0;i<28;i++){
    float h=map(ro+rd*t).x;
    res=min(res,k*h/t); t+=clamp(h,0.008,0.10);
    if(res<0.004||t>maxt) break;
  }
  return clamp(res,0.0,1.0);
}
float calcAO(vec3 p,vec3 n){
  float occ=0.0,sca=1.0;
  for(int i=0;i<4;i++){
    float h=0.016+0.14*float(i)/3.0;
    occ+=(h-map(p+n*h).x)*sca; sca*=0.80;
  }
  return clamp(1.0-1.7*occ,0.0,1.0);
}

// ---------- cel shading ----------
float toon(float x){
  return 0.34*smoothstep(0.03,0.09,x)
       + 0.33*smoothstep(0.32,0.38,x)
       + 0.33*smoothstep(0.64,0.70,x);
}
vec3 shade(vec3 p,vec3 n,vec3 rd,vec3 albedo,float rough,float metal,float ao){
  albedo = pow(clamp(albedo,0.0,1.0), vec3(1.0/2.2));
  vec3 V=-rd;
  vec3 L  = rotY(normalize(vec3( 0.55,0.75,-0.50)), gYaw);
  vec3 L2 = rotY(normalize(vec3(-0.72,0.28,-0.40)), gYaw);
  vec3 Lr = rotY(normalize(vec3(-0.35,0.32, 0.88)), gYaw);

  float sh  = softShadow(p+n*0.006,L,0.02,3.0,5.0);
  float key = toon(max(dot(n,L),0.0)*mix(0.55,1.0,sh));
  float fil = toon(max(dot(n,L2),0.0));
  float aoT = mix(1.0, smoothstep(0.25,0.85,ao), 0.55);

  vec3 shadowCol = albedo*uShadowTint;
  vec3 litCol    = mix(albedo, vec3(1.0), 0.16)*1.04;
  vec3 col = mix(shadowCol, albedo, smoothstep(0.0,0.52,key));
  col = mix(col, litCol, smoothstep(0.52,1.0,key));
  col = mix(col, albedo*vec3(0.62,0.68,0.86), 0.22*(1.0-fil));
  col *= aoT;

  vec3 H=normalize(L+V);
  float spec=pow(max(dot(n,H),0.0), mix(26.0,190.0,1.0-rough));
  col += mix(vec3(1.0),albedo,metal)*step(0.62,spec)*uSpec*sh;

  float rim = smoothstep(0.45,0.90, max(dot(n,Lr),0.0))
            * smoothstep(0.30,0.85, 1.0-abs(dot(n,V)));
  col += vec3(0.42,0.58,0.86)*rim*0.42;

  float edge = 1.0-abs(dot(n,V));
  col = mix(col, vec3(0.055,0.048,0.070), smoothstep(0.875,0.960,edge)*uInk);
  col = mix(albedo*0.5, col, clamp(uContrast,0.2,3.0));
  return col;
}
vec3 bumpNormal(vec3 p,vec3 n,float scale,float amp){
  if(amp<=0.0) return n;
  float e=0.0018, f0=fbm(p*scale);
  vec3 g=vec3(fbm((p+vec3(e,0,0))*scale)-f0,
              fbm((p+vec3(0,e,0))*scale)-f0,
              fbm((p+vec3(0,0,e))*scale)-f0)/e;
  g=g-n*dot(n,g);
  return normalize(n-amp*g);
}
vec3 render(vec3 ro,vec3 rd,out float alpha){
  vec2 res=march(ro,rd);
  alpha=0.0;
  if(res.x<0.0) return vec3(0.0);
  alpha=1.0;
  vec3 p=ro+rd*res.x;
  vec3 n=calcNormal(p);
  vec3 albedo,emis; float rough,metal,bAmp,bScale;
  material(res.y,p,n,albedo,rough,metal,bAmp,bScale,emis);
  n=bumpNormal(p,n,bScale,bAmp);
  float ao=calcAO(p,n);
  return shade(p,n,rd,albedo,rough,metal,ao)+emis*0.55;
}
void main(){
  vec2 cell=floor(gl_FragCoord.xy/uCell);
  float row = uGrid.y-1.0-cell.y;
  float idx = row*uGrid.x + cell.x;          // row-major, top-left first
  float dirI   = uDirBase + floor(idx/uFrames);
  float frameI = mod(idx, uFrames);
  gYaw   = dirI*TAU/uDirTotal;
  gPhase = (uFrames>1.0) ? frameI/uFrames : 0.0;
  vec2 fc=mod(gl_FragCoord.xy,uCell);

  vec3 col=vec3(0.0); float a=0.0;
  int S=int(uSS);
  for(int j=0;j<3;j++){
    for(int i=0;i<3;i++){
      if(i>=S||j>=S) continue;
      vec2 off=(vec2(float(i),float(j))+0.5)/float(S);
      vec2 q=(fc+off-0.5*uCell)/uCell.y;
      float ce=cos(uElev), se=sin(uElev);
      vec3 ta=uTarget;
      vec3 ro=ta+uDist*vec3(sin(gYaw)*ce, se, -cos(gYaw)*ce);
      vec3 ww=normalize(ta-ro), uu=normalize(cross(vec3(0,1,0),ww)), vv=cross(ww,uu);
      vec3 rd=normalize(q.x*uu+q.y*vv+uFL*ww);
      float aa; col+=render(ro,rd,aa); a+=aa;
    }
  }
  float inv=1.0/float(S*S);
  fragColor=vec4(clamp(col*inv,0.0,1.0), a*inv);
}
"""

HTML = """<html><body style="margin:0">
<canvas id="c" width="%(W)d" height="%(H)d"></canvas>
<script>
const cv=document.getElementById('c');
const gl=cv.getContext('webgl2',{preserveDrawingBuffer:true, alpha:true, premultipliedAlpha:false});
function out(s){ document.body.innerHTML='<div id="out">'+s+'</div>'; }
if(!gl){ out('ERR:no-webgl2'); } else {
const vsSrc=`#version 300 es
in vec2 p; void main(){ gl_Position=vec4(p,0.,1.); }`;
const fsSrc=`%(FS)s`;
function sh(t,s,label){
  const x=gl.createShader(t); gl.shaderSource(x,s); gl.compileShader(x);
  if(!gl.getShaderParameter(x,gl.COMPILE_STATUS)){ out('ERR:'+label+':'+gl.getShaderInfoLog(x)); throw 0; }
  return x;
}
try{
  const pr=gl.createProgram();
  gl.attachShader(pr,sh(gl.VERTEX_SHADER,vsSrc,'vs'));
  gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,fsSrc,'fs'));
  gl.linkProgram(pr);
  if(!gl.getProgramParameter(pr,gl.LINK_STATUS)){ out('ERR:link:'+gl.getProgramInfoLog(pr)); throw 0; }
  gl.useProgram(pr);
  const b=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,b);
  gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
  const l=gl.getAttribLocation(pr,'p');
  gl.enableVertexAttribArray(l); gl.vertexAttribPointer(l,2,gl.FLOAT,false,0,0);
  const U=n=>gl.getUniformLocation(pr,n);
  gl.uniform2f(U('uRes'),%(W)d,%(H)d);
  gl.uniform1f(U('uSS'),%(SS)d);
  gl.uniform2f(U('uCell'),%(CW)d,%(CH)d);
  gl.uniform2f(U('uGrid'),%(COLS)d,%(ROWS)d);
  gl.uniform1f(U('uFrames'),%(FRAMES)d);
  gl.uniform1f(U('uDirBase'),%(DIRBASE)d);
  gl.uniform1f(U('uDirTotal'),%(DIRTOTAL)d);
  gl.uniform1f(U('uClip'),%(CLIP)d);
  gl.uniform1f(U('uElev'),%(ELEV)f);
  gl.uniform1f(U('uDist'),%(DIST)f);
  gl.uniform1f(U('uFL'),%(FL)f);
  gl.uniform3f(U('uTarget'),%(TX)f,%(TY)f,%(TZ)f);
  gl.uniform1f(U('uHipY'),%(HIPY)f);
  gl.uniform1f(U('uShldY'),%(SHLDY)f);
  gl.uniform1f(U('uArmZ'),%(ARMZ)f);
  gl.uniform1f(U('uAmp'),%(AMP)f);
  gl.uniform1f(U('uLip'),%(LIP)f);
  gl.uniform1f(U('uLegAmp'),%(LEGAMP)f);
  gl.uniform3f(U('uShadowTint'),%(STR)f,%(STG)f,%(STB)f);
  gl.uniform1f(U('uInk'),%(INK)f);
  gl.uniform1f(U('uSpec'),%(SPEC)f);
  gl.uniform1f(U('uContrast'),%(CONTRAST)f);
  gl.viewport(0,0,%(W)d,%(H)d);
  gl.clearColor(0,0,0,0); gl.clear(gl.COLOR_BUFFER_BIT);
  gl.drawArrays(gl.TRIANGLES,0,3);
  out(cv.toDataURL('image/png'));
}catch(e){}
}
</script></body></html>"""

DEFAULT_STYLE = dict(shadowTint=(0.44, 0.49, 0.66), ink=1.0, spec=0.42, contrast=1.0)


def render(name, body_glsl, out_png, rig, cam, clip=1, frames=8, dirs=8,
           cw=192, ch=240, SS=2, budget=2400000, cols=None, dir_base=0,
           dir_total=8, style=None):
    """Render one sprite sheet.

    The image holds `dirs` directions x `frames` frames, packed row-major into
    `cols` columns. Default cols=dirs reproduces the classic layout (one column
    per facing). Pass dirs=1 with dir_base=d to get a single-facing sheet.
    """
    import math
    cols = cols or dirs
    rows = math.ceil(dirs*frames/cols)
    st = dict(DEFAULT_STYLE); st.update(style or {})
    fs = HEADER + body_glsl + FOOTER
    fs = fs.replace(BS, BS + BS).replace("`", BS + "`").replace("${", BS + "${")
    W, H = cw * cols, ch * rows
    html = HTML % dict(W=W, H=H, FS=fs, SS=SS, CW=cw, CH=ch,
                       COLS=cols, ROWS=rows, FRAMES=frames, CLIP=clip,
                       DIRBASE=dir_base, DIRTOTAL=dir_total,
                       ELEV=cam["elev"], DIST=cam["dist"], FL=cam["fl"],
                       TX=cam["target"][0], TY=cam["target"][1], TZ=cam["target"][2],
                       HIPY=rig["hipY"], SHLDY=rig["shldY"], ARMZ=rig["armZ"],
                       AMP=rig["amp"], LIP={0:0.85, 1:0.45, 2:0.35}.get(clip,0.5),
                       LEGAMP=rig.get("legAmp", 1.0),
                       STR=st["shadowTint"][0], STG=st["shadowTint"][1],
                       STB=st["shadowTint"][2], INK=st["ink"], SPEC=st["spec"],
                       CONTRAST=st["contrast"])
    d = pathlib.Path(f"_{name}.html"); d.write_text(html)
    t0 = time.time()
    p = subprocess.run([CHROME, "--headless", "--no-sandbox", "--enable-unsafe-swiftshader",
                        f"--virtual-time-budget={budget}", "--dump-dom", f"file://{d.resolve()}"],
                       capture_output=True, text=True, timeout=2400)
    dt = time.time() - t0
    err = re.search(r'ERR:([^<]{0,600})', p.stdout)
    if err:
        print(f"[{name}] SHADER ERROR: {err.group(1)[:600]}"); return False
    m = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', p.stdout)
    if not m:
        print(f"[{name}] no image; dom head: {p.stdout[:300]}"); return False
    pathlib.Path(out_png).write_bytes(base64.b64decode(m.group(1)))
    print(f"[{name}] {W}x{H} ({cols}x{rows} cells, {dirs}dir x {frames}f) SS={SS} in {dt:.0f}s -> {out_png}")
    return True
