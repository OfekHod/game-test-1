import sys; sys.path.insert(0,'.')
from rt import render

BODY = r"""
void material(float id, vec3 p, vec3 n, out vec3 albedo, out float rough,
              out float metal, out float bAmp, out float bScale, out vec3 emis){
  emis=vec3(0.0);
  float g  = fbm(p*30.0);
  float g2 = fbm(p*7.0);
  if(id<1.5){                        // granite
    albedo = vec3(0.185,0.180,0.160)*(0.55+0.95*g)*(0.80+0.40*g2);
    albedo = mix(albedo, vec3(0.115,0.108,0.098), 0.45*fbm(p*13.0));
    metal=0.0; rough=0.78+0.18*g; bAmp=0.030; bScale=60.0;
  } else if(id<2.5){                 // moss
    albedo = vec3(0.075,0.145,0.038)*(0.55+0.95*fbm(p*95.0));
    metal=0.0; rough=0.96; bAmp=0.030; bScale=230.0;
  } else if(id<3.5){                 // hot fissure rock
    albedo = vec3(0.075,0.058,0.048); metal=0.0; rough=0.85; bAmp=0.020; bScale=70.0;
    emis = vec3(1.85,0.72,0.14)*(0.55+0.9*fbm(p*22.0));
  } else {                           // eye
    albedo = vec3(0.0); metal=0.0; rough=1.0; bAmp=0.0; bScale=1.0;
    emis = vec3(2.3,1.05,0.24);
  }
}

vec2 map(vec3 p){
  vec2 res = vec2(1e9,0.0);

  // ---------- back arm (+z) ----------
  res = mmin(res, vec2(sdCap(p, vec3(0.100,1.245, 0.255), vec3(0.330,0.665, 0.290), 0.150,0.132),1.0));
  { vec3 q=p-vec3(0.352,0.232,0.290); q.xy*=rot(-0.12);
    res = mmin(res, vec2(sdBox(q, vec3(0.158,0.212,0.142),0.052),1.0)); }

  // ---------- back leg (+z) ----------
  res = mmin(res, vec2(sdBox(p-vec3(-0.075,0.535,0.145), vec3(0.115,0.245,0.108),0.055),1.0));
  { vec3 q=p-vec3(-0.085,0.140,0.145); q.xz*=rot(0.08);
    res = mmin(res, vec2(sdBox(q, vec3(0.140,0.135,0.122),0.042),1.0)); }

  // ---------- torso ----------
  { vec3 q=p-vec3(-0.030,1.115,0.0); q.xy*=rot(-0.14);
    res = mmin(res, vec2(sdBox(q, vec3(0.200,0.310,0.300),0.070),1.0)); }
  { vec3 q=p-vec3(-0.060,0.790,0.0); q.xz*=rot(0.12);
    res = mmin(res, vec2(sdBox(q, vec3(0.185,0.120,0.245),0.055),1.0)); }
  // shoulder shelves
  { vec3 q=p-vec3(-0.075,1.395,-0.255); q.xy*=rot(0.10);
    res = mmin(res, vec2(sdBox(q, vec3(0.170,0.105,0.115),0.058),1.0)); }
  { vec3 q=p-vec3(-0.090,1.390, 0.255); q.xy*=rot(0.08);
    res = mmin(res, vec2(sdBox(q, vec3(0.162,0.098,0.108),0.055),1.0)); }
  // upper-back shards
  { vec3 q=p-vec3(-0.190,1.480,0.055); q.xy*=rot(0.42);
    res = mmin(res, vec2(sdBox(q, vec3(0.075,0.130,0.090),0.028),1.0)); }
  { vec3 q=p-vec3(-0.110,1.545,-0.120); q.xy*=rot(-0.30);
    res = mmin(res, vec2(sdBox(q, vec3(0.060,0.110,0.070),0.024),1.0)); }

  // ---------- neck + head thrust forward ----------
  res = mmin(res, vec2(sdCap(p, vec3(0.040,1.300,0.0), vec3(0.205,1.322,0.0), 0.130,0.118),1.0));
  { vec3 q=p-vec3(0.325,1.322,0.0); q.xy*=rot(-0.16);
    res = mmin(res, vec2(sdBox(q, vec3(0.140,0.112,0.140),0.048),1.0)); }
  { vec3 q=p-vec3(0.395,1.404,0.0); q.xy*=rot(-0.16);
    res = mmin(res, vec2(sdBox(q, vec3(0.098,0.038,0.145),0.026),1.0)); }   // brow
  { vec3 q=p-vec3(0.403,1.226,0.0); q.xy*=rot(-0.10);
    res = mmin(res, vec2(sdBox(q, vec3(0.092,0.046,0.128),0.028),1.0)); }   // jaw
  res = mmin(res, vec2(sdSphere(p-vec3(0.503,1.326,-0.086),0.042),4.0));
  res = mmin(res, vec2(sdSphere(p-vec3(0.503,1.326, 0.086),0.042),4.0));

  // ---------- front leg (-z) ----------
  res = mmin(res, vec2(sdBox(p-vec3(0.020,0.535,-0.150), vec3(0.122,0.250,0.112),0.058),1.0));
  { vec3 q=p-vec3(0.040,0.140,-0.150); q.xz*=rot(-0.10);
    res = mmin(res, vec2(sdBox(q, vec3(0.150,0.140,0.128),0.045),1.0)); }

  // ---------- front arm (-z), knuckle planted ----------
  res = mmin(res, vec2(sdCap(p, vec3(-0.100,1.258,-0.270), vec3(-0.190,0.655,-0.305), 0.158,0.138),1.0));
  { vec3 q=p-vec3(-0.205,0.228,-0.305); q.xy*=rot(0.10);
    res = mmin(res, vec2(sdBox(q, vec3(0.168,0.212,0.148),0.054),1.0)); }

  // ---------- glowing core, proud of the chest ----------
  { vec3 q=p-vec3(0.212,1.030,0.0); q.xy*=rot(-0.14);
    res = mmin(res, vec2(sdEllip(q, vec3(0.108,0.140,0.152)),3.0)); }
  res = mmin(res, vec2(sdCap(p, vec3(0.208,1.160,-0.045), vec3(0.150,1.348,-0.125), 0.030,0.008),3.0));
  res = mmin(res, vec2(sdCap(p, vec3(0.210,0.900, 0.055), vec3(0.150,0.740, 0.135), 0.030,0.008),3.0));
  res = mmin(res, vec2(sdCap(p, vec3(0.200,1.038,-0.140), vec3(0.098,1.000,-0.290), 0.028,0.008),3.0));
  res = mmin(res, vec2(sdCap(p, vec3(0.200,1.038, 0.140), vec3(0.106,1.012, 0.290), 0.028,0.008),3.0));

  // ---------- moss on up-facing surfaces ----------
  { vec3 q=p-vec3(-0.075,1.524,-0.255); q.xy*=rot(0.10);
    res = mmin(res, vec2(sdBox(q, vec3(0.155,0.022,0.100),0.038),2.0)); }
  { vec3 q=p-vec3(-0.090,1.512, 0.255); q.xy*=rot(0.08);
    res = mmin(res, vec2(sdBox(q, vec3(0.148,0.020,0.094),0.036),2.0)); }
  { vec3 q=p-vec3(0.395,1.474,0.0); q.xy*=rot(-0.16);
    res = mmin(res, vec2(sdBox(q, vec3(0.090,0.018,0.132),0.022),2.0)); }
  res = mmin(res, vec2(sdBox(p-vec3(0.040,0.302,-0.150), vec3(0.142,0.020,0.122),0.038),2.0));
  return res;
}
"""
CAM = dict(ro="vec3(0.16,0.86,-4.45)", ta="vec3(0.08,0.82,0.0)", fl="1.62")
render("neutral_rock_golem", BODY, CAM, "../neutral_rock_golem_raw.png", W=512, H=640, SS=1)
