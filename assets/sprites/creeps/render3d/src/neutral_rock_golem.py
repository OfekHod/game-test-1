import sys; sys.path.insert(0,'.')
from rt import render

BODY = r"""
#define KSM 0.028
void material(float id, vec3 p, vec3 n, out vec3 albedo, out float rough,
              out float metal, out float bAmp, out float bScale, out vec3 emis){
  emis=vec3(0.0); bAmp=0.0; bScale=1.0;
  if(id<1.5){      albedo=vec3(0.132,0.129,0.120); metal=0.0; rough=0.74; }
  else if(id<2.5){ albedo=vec3(0.205,0.370,0.115); metal=0.0; rough=0.86; }
  else if(id<3.5){ albedo=vec3(0.150,0.105,0.070); metal=0.0; rough=0.80; emis=vec3(1.90,0.80,0.18); }
  else {           albedo=vec3(0.0); metal=0.0; rough=1.0; emis=vec3(2.30,1.10,0.28); }
}

vec2 map(vec3 p){
  vec2 res = vec2(1e9,0.0);

  // ---------- back arm (+z) ----------
  res = smin2(res, vec2(sdCap(p, vec3(0.100,1.245, 0.255), vec3(0.330,0.665, 0.290), 0.150,0.132),1.0), KSM);
  { vec3 q=p-vec3(0.352,0.232,0.290); q.xy*=rot(-0.12);
    res = smin2(res, vec2(sdBox(q, vec3(0.158,0.212,0.142),0.052),1.0), KSM); }

  // ---------- back leg (+z) ----------
  res = smin2(res, vec2(sdBox(p-vec3(-0.075,0.535,0.145), vec3(0.115,0.245,0.108),0.055),1.0), KSM);
  { vec3 q=p-vec3(-0.085,0.140,0.145); q.xz*=rot(0.08);
    res = smin2(res, vec2(sdBox(q, vec3(0.140,0.135,0.122),0.042),1.0), KSM); }

  // ---------- torso ----------
  { vec3 q=p-vec3(-0.030,1.115,0.0); q.xy*=rot(-0.14);
    res = smin2(res, vec2(sdBox(q, vec3(0.200,0.310,0.300),0.070),1.0), KSM); }
  { vec3 q=p-vec3(-0.060,0.790,0.0); q.xz*=rot(0.12);
    res = smin2(res, vec2(sdBox(q, vec3(0.185,0.120,0.245),0.055),1.0), KSM); }
  // shoulder shelves
  { vec3 q=p-vec3(-0.075,1.395,-0.255); q.xy*=rot(0.10);
    res = smin2(res, vec2(sdBox(q, vec3(0.170,0.105,0.115),0.058),1.0), KSM); }
  { vec3 q=p-vec3(-0.090,1.390, 0.255); q.xy*=rot(0.08);
    res = smin2(res, vec2(sdBox(q, vec3(0.162,0.098,0.108),0.055),1.0), KSM); }
  // upper-back shards
  { vec3 q=p-vec3(-0.190,1.480,0.055); q.xy*=rot(0.42);
    res = smin2(res, vec2(sdBox(q, vec3(0.075,0.130,0.090),0.028),1.0), KSM); }
  { vec3 q=p-vec3(-0.110,1.545,-0.120); q.xy*=rot(-0.30);
    res = smin2(res, vec2(sdBox(q, vec3(0.060,0.110,0.070),0.024),1.0), KSM); }

  // ---------- neck + head thrust forward ----------
  res = smin2(res, vec2(sdCap(p, vec3(0.040,1.300,0.0), vec3(0.205,1.322,0.0), 0.130,0.118),1.0), KSM);
  { vec3 q=p-vec3(0.325,1.322,0.0); q.xy*=rot(-0.16);
    res = smin2(res, vec2(sdBox(q, vec3(0.140,0.112,0.140),0.048),1.0), KSM); }
  { vec3 q=p-vec3(0.395,1.404,0.0); q.xy*=rot(-0.16);
    res = smin2(res, vec2(sdBox(q, vec3(0.098,0.038,0.145),0.026),1.0), KSM); }   // brow
  { vec3 q=p-vec3(0.403,1.226,0.0); q.xy*=rot(-0.10);
    res = smin2(res, vec2(sdBox(q, vec3(0.092,0.046,0.128),0.028),1.0), KSM); }   // jaw
  res = smin2(res, vec2(sdSphere(p-vec3(0.503,1.326,-0.086),0.042),4.0), KSM);
  res = smin2(res, vec2(sdSphere(p-vec3(0.503,1.326, 0.086),0.042),4.0), KSM);

  // ---------- front leg (-z) ----------
  res = smin2(res, vec2(sdBox(p-vec3(0.020,0.535,-0.150), vec3(0.122,0.250,0.112),0.058),1.0), KSM);
  { vec3 q=p-vec3(0.040,0.140,-0.150); q.xz*=rot(-0.10);
    res = smin2(res, vec2(sdBox(q, vec3(0.150,0.140,0.128),0.045),1.0), KSM); }

  // ---------- front arm (-z), knuckle planted ----------
  res = smin2(res, vec2(sdCap(p, vec3(-0.100,1.258,-0.270), vec3(-0.190,0.655,-0.305), 0.158,0.138),1.0), KSM);
  { vec3 q=p-vec3(-0.205,0.228,-0.305); q.xy*=rot(0.10);
    res = smin2(res, vec2(sdBox(q, vec3(0.168,0.212,0.148),0.054),1.0), KSM); }

  // ---------- glowing core, proud of the chest ----------
  { vec3 q=p-vec3(0.212,1.030,0.0); q.xy*=rot(-0.14);
    res = smin2(res, vec2(sdEllip(q, vec3(0.108,0.140,0.152)),3.0), KSM); }
  res = smin2(res, vec2(sdCap(p, vec3(0.208,1.160,-0.045), vec3(0.150,1.348,-0.125), 0.030,0.008),3.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.210,0.900, 0.055), vec3(0.150,0.740, 0.135), 0.030,0.008),3.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.200,1.038,-0.140), vec3(0.098,1.000,-0.290), 0.028,0.008),3.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.200,1.038, 0.140), vec3(0.106,1.012, 0.290), 0.028,0.008),3.0), KSM);

  // ---------- moss on up-facing surfaces ----------
  { vec3 q=p-vec3(-0.075,1.524,-0.255); q.xy*=rot(0.10);
    res = smin2(res, vec2(sdBox(q, vec3(0.155,0.022,0.100),0.038),2.0), KSM); }
  { vec3 q=p-vec3(-0.090,1.512, 0.255); q.xy*=rot(0.08);
    res = smin2(res, vec2(sdBox(q, vec3(0.148,0.020,0.094),0.036),2.0), KSM); }
  { vec3 q=p-vec3(0.395,1.474,0.0); q.xy*=rot(-0.16);
    res = smin2(res, vec2(sdBox(q, vec3(0.090,0.018,0.132),0.022),2.0), KSM); }
  res = smin2(res, vec2(sdBox(p-vec3(0.040,0.302,-0.150), vec3(0.142,0.020,0.122),0.038),2.0), KSM);
  return res;
}
"""
CAM = dict(ro="vec3(0.16,0.86,-4.45)", ta="vec3(0.08,0.82,0.0)", fl="1.62")
render("neutral_rock_golem", BODY, CAM, "../neutral_rock_golem_raw.png", W=512, H=640, SS=1)
