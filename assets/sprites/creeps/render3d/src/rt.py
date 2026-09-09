"""Raymarched SDF creep renderer: builds a GLSL shader, runs it in headless
Chromium via WebGL2, and pulls the framebuffer back out as a PNG."""
import base64, pathlib, re, subprocess, sys, tempfile, time

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
"""

FOOTER = r"""
// ---------- raymarch ----------
vec2 march(vec3 ro,vec3 rd){
  float t=0.35; vec2 res=vec2(-1.0);
  for(int i=0;i<160;i++){
    vec3 p=ro+rd*t; vec2 h=map(p);
    if(h.x<0.0006*t){ res=vec2(t,h.y); break; }
    t+=h.x*0.85; if(t>7.0) break;
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
  for(int i=0;i<48;i++){
    float h=map(ro+rd*t).x;
    res=min(res,k*h/t); t+=clamp(h,0.006,0.09);
    if(res<0.004||t>maxt) break;
  }
  return clamp(res,0.0,1.0);
}
float calcAO(vec3 p,vec3 n){
  float occ=0.0,sca=1.0;
  for(int i=0;i<6;i++){
    float h=0.012+0.13*float(i)/5.0;
    float d=map(p+n*h).x;
    occ+=(h-d)*sca; sca*=0.82;
  }
  return clamp(1.0-1.9*occ,0.0,1.0);
}
// GGX
float D_GGX(float NoH,float a){ float a2=a*a; float d=NoH*NoH*(a2-1.0)+1.0; return a2/(3.14159*d*d); }
float V_Smith(float NoV,float NoL,float a){
  float a2=a*a;
  float gv=NoL*sqrt(NoV*NoV*(1.0-a2)+a2);
  float gl=NoV*sqrt(NoL*NoL*(1.0-a2)+a2);
  return 0.5/max(gv+gl,1e-5);
}
vec3 shade(vec3 p,vec3 n,vec3 rd,vec3 albedo,float rough,float metal,float ao){
  vec3 V=-rd;
  vec3 F0=mix(vec3(0.04),albedo,metal);
  vec3 diffC=albedo*(1.0-metal);
  vec3 col=vec3(0.0);
  // key
  {
    vec3 L=normalize(vec3(0.55,0.75,-0.50)); vec3 H=normalize(L+V);
    float NoL=max(dot(n,L),0.0), NoV=max(dot(n,V),1e-4), NoH=max(dot(n,H),0.0), VoH=max(dot(V,H),0.0);
    float sh=softShadow(p+n*0.004,L,0.02,3.0,5.5);
    vec3 F=F0+(1.0-F0)*pow(1.0-VoH,5.0);
    float a=max(rough*rough,0.002);
    vec3 spec=F*D_GGX(NoH,a)*V_Smith(NoV,NoL,a);
    col += (diffC/3.14159 + spec) * vec3(1.0,0.95,0.88) * 2.35 * NoL * mix(0.40,1.0,sh);
  }
  // cool fill
  {
    vec3 L=normalize(vec3(-0.72,0.28,-0.40)); vec3 H=normalize(L+V);
    float NoL=max(dot(n,L),0.0), NoV=max(dot(n,V),1e-4), NoH=max(dot(n,H),0.0), VoH=max(dot(V,H),0.0);
    vec3 F=F0+(1.0-F0)*pow(1.0-VoH,5.0);
    float a=max(rough*rough,0.002);
    vec3 spec=F*D_GGX(NoH,a)*V_Smith(NoV,NoL,a);
    col += (diffC/3.14159 + spec*0.6) * vec3(0.44,0.54,0.72) * 0.80 * NoL;
  }
  // back rim
  {
    vec3 L=normalize(vec3(-0.35,0.32,0.88));
    float NoL=max(dot(n,L),0.0);
    float fres=pow(clamp(1.0-max(dot(n,V),0.0),0.0,1.0),2.5);
    col += diffC * vec3(0.66,0.82,1.0) * 0.85 * NoL * (0.45+0.55*fres);
  }
  // hemisphere ambient
  {
    float up=0.5+0.5*n.y;
    vec3 amb=mix(vec3(0.105,0.115,0.140), vec3(0.290,0.330,0.410), up);
    col += diffC*amb*ao;
    float NoV=max(dot(n,V),1e-4);
    vec3 F=F0+(max(vec3(1.0-rough),F0)-F0)*pow(1.0-NoV,5.0);
    col += F*amb*1.1*ao;
  }
  return col;
}
vec3 bumpNormal(vec3 p,vec3 n,float scale,float amp){
  if(amp<=0.0) return n;
  float e=0.0018;
  float f0=fbm(p*scale);
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
  vec3 albedo, emis; float rough,metal,bAmp,bScale;
  material(res.y,p,n,albedo,rough,metal,bAmp,bScale,emis);
  n=bumpNormal(p,n,bScale,bAmp);
  float ao=calcAO(p,n);
  return shade(p,n,rd,albedo,rough,metal,ao)+emis;
}
void main(){
  vec3 col=vec3(0.0); float a=0.0;
  int S=int(uSS);
  for(int j=0;j<3;j++){
    for(int i=0;i<3;i++){
      if(i>=S||j>=S) continue;
      vec2 off=(vec2(float(i),float(j))+0.5)/float(S);
      vec2 q=(gl_FragCoord.xy+off-0.5-0.5*uRes)/uRes.y;
      vec3 ro=CAM_RO;
      vec3 ta=CAM_TA;
      vec3 ww=normalize(ta-ro), uu=normalize(cross(vec3(0,1,0),ww)), vv=cross(ww,uu);
      vec3 rd=normalize(q.x*uu+q.y*vv+CAM_FL*ww);
      float aa; col+=render(ro,rd,aa); a+=aa;
    }
  }
  float inv=1.0/float(S*S);
  col*=inv; a*=inv;
  // tonemap (ACES-ish) + gamma
  col=(col*(2.51*col+0.03))/(col*(2.43*col+0.59)+0.14);
  col=pow(clamp(col,0.0,1.0),vec3(1.0/2.2));
  fragColor=vec4(col, a);
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
  gl.uniform2f(gl.getUniformLocation(pr,'uRes'),%(W)d,%(H)d);
  gl.uniform1f(gl.getUniformLocation(pr,'uSS'),%(SS)d);
  gl.viewport(0,0,%(W)d,%(H)d);
  gl.clearColor(0,0,0,0); gl.clear(gl.COLOR_BUFFER_BIT);
  gl.drawArrays(gl.TRIANGLES,0,3);
  out(cv.toDataURL('image/png'));
}catch(e){}
}
</script></body></html>"""

def render(name, body_glsl, cam, out_png, W=512, H=640, SS=1, budget=580000):
    fs = HEADER + body_glsl + FOOTER
    fs = fs.replace("CAM_RO", cam["ro"]).replace("CAM_TA", cam["ta"]).replace("CAM_FL", cam["fl"])
    fs = fs.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    html = HTML % dict(W=W, H=H, FS=fs, SS=SS)
    d = pathlib.Path(f"_{name}.html"); d.write_text(html)
    t0 = time.time()
    p = subprocess.run([CHROME,"--headless","--no-sandbox","--enable-unsafe-swiftshader",
                        f"--virtual-time-budget={budget}","--dump-dom",f"file://{d.resolve()}"],
                       capture_output=True, text=True, timeout=900)
    dt = time.time()-t0
    dom = p.stdout
    err = re.search(r'ERR:([^<]{0,600})', dom)
    if err:
        print(f"[{name}] SHADER ERROR: {err.group(1)[:600]}"); return False
    m = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', dom)
    if not m:
        print(f"[{name}] no image; dom head: {dom[:300]}"); return False
    pathlib.Path(out_png).write_bytes(base64.b64decode(m.group(1)))
    print(f"[{name}] {W}x{H} SS={SS} in {dt:.1f}s -> {out_png}")
    return True
