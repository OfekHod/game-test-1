import sys; sys.path.insert(0,'.')
from rt import render

BODY = r"""
#define KSM 0.019
void material(float id, vec3 p, vec3 n, out vec3 albedo, out float rough,
              out float metal, out float bAmp, out float bScale, out vec3 emis){
  emis=vec3(0.0); bAmp=0.0; bScale=1.0;
  if(id<1.5){      albedo=vec3(0.250,0.330,0.150); metal=0.0;  rough=0.70; }
  else if(id<2.5){ albedo=vec3(0.780,0.750,0.590); metal=0.0;  rough=0.52; }
  else if(id<3.5){ albedo=vec3(0.400,0.205,0.100); metal=0.55; rough=0.58; }
  else if(id<4.5){ albedo=vec3(0.255,0.170,0.090); metal=0.0;  rough=0.78; }
  else if(id<5.5){ albedo=vec3(0.055,0.050,0.040); metal=0.0;  rough=0.90; }
  else {           albedo=vec3(0.0); metal=0.0; rough=1.0; emis=vec3(2.4,0.78,0.20); }
}

vec2 map(vec3 p){
  vec2 res = vec2(1e9,0.0);
  float d;

  // ---------- far leg (+z), digitigrade ----------
  d = sdCap(p, vec3(-0.075,0.880, 0.105), vec3(0.055,0.545, 0.115), 0.115,0.075);
  d = smin(d, sdCap(p, vec3(0.055,0.545,0.115), vec3(-0.095,0.255,0.115), 0.075,0.052), 0.05);
  d = smin(d, sdCap(p, vec3(-0.095,0.255,0.115), vec3(0.135,0.055,0.115), 0.052,0.040), 0.05);
  res = smin2(res, vec2(d,1.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.115,0.048,0.115), vec3(0.215,0.030,0.098), 0.040,0.016),1.0), KSM);

  // ---------- far arm (+z), raised with cleaver ----------
  d = sdCap(p, vec3(0.035,1.235, 0.185), vec3(-0.135,1.335, 0.235), 0.082,0.062);
  d = smin(d, sdCap(p, vec3(-0.135,1.335,0.235), vec3(-0.225,1.575,0.240), 0.062,0.046), 0.05);
  res = smin2(res, vec2(d,1.0), KSM);
  res = smin2(res, vec2(sdEllip(p-vec3(-0.235,1.610,0.240), vec3(0.052,0.050,0.046)),1.0), KSM);
  // cleaver
  res = smin2(res, vec2(sdCap(p, vec3(-0.238,1.585,0.240), vec3(-0.250,1.700,0.240), 0.021,0.019),4.0), KSM);
  {
    vec3 q = p - vec3(-0.262,1.830,0.240); q.xy *= rot(0.12);
    vec3 qs = vec3(q.x,q.y,q.z*4.2);
    res = smin2(res, vec2(sdBox(qs, vec3(0.118,0.108,0.030),0.012)/4.2, 3.0), KSM);
    vec3 qe = q - vec3(0.118,-0.020,0.0);
    vec3 qes = vec3(qe.x,qe.y,qe.z*6.0);
    res = smin2(res, vec2(sdBox(qes, vec3(0.012,0.092,0.016),0.004)/6.0, 3.0), KSM);
  }

  // ---------- hunched torso ----------
  d = sdEllip(p-vec3(-0.075,0.930,0.0), vec3(0.128,0.105,0.155));
  d = smin(d, sdEllip(p-vec3(-0.010,1.075,0.0), vec3(0.128,0.115,0.160)), 0.10);
  d = smin(d, sdEllip(p-vec3(0.060,1.190,0.0), vec3(0.132,0.110,0.165)), 0.10);
  res = smin2(res, vec2(d,1.0), KSM);
  // ribs
  res = smin2(res, vec2(sdCap(p, vec3(0.135,1.205,-0.055), vec3(0.155,1.155,-0.115), 0.020,0.016),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.140,1.145,-0.050), vec3(0.158,1.095,-0.112), 0.020,0.016),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.132,1.085,-0.045), vec3(0.150,1.038,-0.105), 0.019,0.015),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.135,1.205, 0.055), vec3(0.155,1.155, 0.115), 0.020,0.016),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.140,1.145, 0.050), vec3(0.158,1.095, 0.112), 0.020,0.016),2.0), KSM);
  // spine spurs along the back
  res = smin2(res, vec2(sdCap(p, vec3(0.040,1.290,0.0), vec3(0.030,1.400,0.0), 0.030,0.004),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(-0.045,1.195,0.0), vec3(-0.105,1.290,0.0), 0.030,0.004),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(-0.120,1.065,0.0), vec3(-0.205,1.125,0.0), 0.028,0.004),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(-0.160,0.940,0.0), vec3(-0.255,0.960,0.0), 0.026,0.004),2.0), KSM);
  // hide loincloth
  res = smin2(res, vec2(sdBox(p-vec3(-0.020,0.830,0.0), vec3(0.120,0.115,0.150),0.030),4.0), KSM);

  // ---------- near leg (-z) ----------
  d = sdCap(p, vec3(-0.060,0.880,-0.110), vec3(0.075,0.545,-0.120), 0.120,0.078);
  d = smin(d, sdCap(p, vec3(0.075,0.545,-0.120), vec3(-0.080,0.255,-0.120), 0.078,0.054), 0.05);
  d = smin(d, sdCap(p, vec3(-0.080,0.255,-0.120), vec3(0.155,0.055,-0.120), 0.054,0.042), 0.05);
  res = smin2(res, vec2(d,1.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.135,0.048,-0.120), vec3(0.240,0.028,-0.140), 0.042,0.016),1.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.140,0.046,-0.098), vec3(0.245,0.026,-0.080), 0.038,0.014),1.0), KSM);

  // ---------- near arm (-z), reaching down ----------
  d = sdCap(p, vec3(0.045,1.235,-0.185), vec3(0.175,0.905,-0.245), 0.086,0.062);
  d = smin(d, sdCap(p, vec3(0.175,0.905,-0.245), vec3(0.225,0.575,-0.250), 0.062,0.046), 0.05);
  res = smin2(res, vec2(d,1.0), KSM);
  res = smin2(res, vec2(sdEllip(p-vec3(0.232,0.540,-0.252), vec3(0.056,0.052,0.048)),1.0), KSM);
  // claws
  res = smin2(res, vec2(sdCap(p, vec3(0.245,0.505,-0.290), vec3(0.290,0.405,-0.305), 0.019,0.004),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.250,0.500,-0.250), vec3(0.300,0.395,-0.250), 0.019,0.004),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.245,0.505,-0.212), vec3(0.288,0.408,-0.196), 0.018,0.004),2.0), KSM);

  // ---------- head, thrust forward ----------
  d = sdEllip(p-vec3(0.215,1.250,0.0), vec3(0.115,0.105,0.110));
  d = smin(d, sdEllip(p-vec3(0.310,1.205,0.0), vec3(0.095,0.072,0.088)), 0.05);
  res = smin2(res, vec2(d,1.0), KSM);
  // jaw + maw
  res = smin2(res, vec2(sdBox(p-vec3(0.312,1.152,0.0), vec3(0.068,0.011,0.060),0.007),5.0), KSM);
  res = smin2(res, vec2(sdEllip(p-vec3(0.300,1.120,0.0), vec3(0.098,0.045,0.085)),1.0), KSM);
  // teeth
  res = smin2(res, vec2(sdCap(p, vec3(0.250,1.175,-0.055), vec3(0.252,1.130,-0.058), 0.014,0.002),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.305,1.172,-0.060), vec3(0.308,1.128,-0.062), 0.014,0.002),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.355,1.168,-0.048), vec3(0.356,1.132,-0.050), 0.012,0.002),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.252,1.140,-0.058), vec3(0.254,1.180,-0.060), 0.013,0.002),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.318,1.138,-0.055), vec3(0.320,1.178,-0.056), 0.013,0.002),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.250,1.175, 0.055), vec3(0.252,1.130, 0.058), 0.014,0.002),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.305,1.172, 0.060), vec3(0.308,1.128, 0.062), 0.014,0.002),2.0), KSM);
  // horns
  res = smin2(res, vec2(sdCap(p, vec3(0.190,1.330,-0.075), vec3(0.130,1.470,-0.098), 0.032,0.006),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.190,1.330, 0.075), vec3(0.130,1.470, 0.098), 0.032,0.006),2.0), KSM);
  // brow + ember eyes
  res = smin2(res, vec2(sdEllip(p-vec3(0.268,1.288,-0.070), vec3(0.055,0.032,0.048)),1.0), KSM);
  res = smin2(res, vec2(sdEllip(p-vec3(0.268,1.288, 0.070), vec3(0.055,0.032,0.048)),1.0), KSM);
  res = smin2(res, vec2(sdSphere(p-vec3(0.318,1.268,-0.072),0.026),6.0), KSM);
  res = smin2(res, vec2(sdSphere(p-vec3(0.318,1.268, 0.072),0.026),6.0), KSM);
  return res;
}
"""
CAM = dict(ro="vec3(0.10,0.92,-4.20)", ta="vec3(0.02,0.90,0.0)", fl="1.95")
render("dire_ghoul", BODY, CAM, "../dire_ghoul_raw.png", W=512, H=640, SS=1)
