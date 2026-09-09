import sys; sys.path.insert(0,'.')
from rt import render

BODY = r"""
#define KSM 0.015
void material(float id, vec3 p, vec3 n, out vec3 albedo, out float rough,
              out float metal, out float bAmp, out float bScale, out vec3 emis){
  emis=vec3(0.0); bAmp=0.0; bScale=1.0;
  if(id<1.5){      albedo=vec3(0.235,0.145,0.070); metal=0.0;  rough=0.74; }
  else if(id<2.5){ albedo=vec3(0.070,0.330,0.255); metal=0.0;  rough=0.84; }
  else if(id<3.5){ albedo=vec3(0.245,0.155,0.078); metal=0.0;  rough=0.62; }
  else if(id<4.5){ albedo=vec3(0.760,0.790,0.820); metal=0.90; rough=0.22; }
  else if(id<5.5){ albedo=vec3(0.545,0.360,0.250); metal=0.0;  rough=0.60; }
  else if(id<6.5){ albedo=vec3(0.800,0.780,0.700); metal=0.0;  rough=0.66; }
  else {           albedo=vec3(0.050,0.050,0.056); metal=0.0;  rough=0.92; }
}

vec2 map(vec3 p){
  vec2 res = vec2(1e9,0.0);
  float d;

  // ---------- far leg (+z) ----------
  res = smin2(res, vec2(sdCap(p, vec3(0.005,0.900, 0.098), vec3(-0.048,0.535, 0.112), 0.086,0.066),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(-0.048,0.520,0.112), vec3(-0.098,0.130,0.112), 0.062,0.046),1.0), KSM);
  res = smin2(res, vec2(sdBox(p-vec3(-0.052,0.044,0.112), vec3(0.092,0.026,0.044),0.022),1.0), KSM);

  // ---------- quiver on the back ----------
  { vec3 q = p - vec3(-0.170,1.130,0.135); q.xy *= rot(0.30);
    res = smin2(res, vec2(sdCap(q, vec3(0.0,-0.180,0.0), vec3(0.0,0.190,0.0), 0.066,0.070),1.0), KSM); }
  { vec3 q = p - vec3(-0.235,1.395,0.135); q.xy *= rot(0.30);
    res = smin2(res, vec2(sdCap(q, vec3(-0.020,0.0,-0.022), vec3(-0.020,0.150,-0.030), 0.008,0.008),3.0), KSM);
    res = smin2(res, vec2(sdCap(q, vec3( 0.008,0.0, 0.004), vec3( 0.008,0.165, 0.004), 0.008,0.008),3.0), KSM);
    res = smin2(res, vec2(sdCap(q, vec3( 0.030,0.0, 0.028), vec3( 0.030,0.140, 0.036), 0.008,0.008),3.0), KSM);
    res = smin2(res, vec2(sdEllip(q-vec3(-0.020,0.155,-0.030), vec3(0.012,0.038,0.012)),6.0), KSM);
    res = smin2(res, vec2(sdEllip(q-vec3( 0.008,0.170, 0.004), vec3(0.012,0.038,0.012)),6.0), KSM);
    res = smin2(res, vec2(sdEllip(q-vec3( 0.030,0.145, 0.036), vec3(0.012,0.036,0.012)),6.0), KSM); }

  // ---------- cloak ----------
  { vec3 q = p - vec3(-0.030,1.020,0.0);
    d = sdCap(q, vec3(0.0,0.360,0.0), vec3(-0.020,-0.430,0.0), 0.175,0.215);
    float ang = atan(q.z,q.x);
    d -= 0.008*sin(ang*11.0)*smoothstep(1.30,0.60,p.y);
    d = max(d, -sdBox(p-vec3(0.230,1.150,0.0), vec3(0.230,0.420,0.320),0.0));  // open at the front
    res = smin2(res, vec2(d,2.0), KSM); }

  // ---------- torso ----------
  d = sdEllip(p-vec3(0.005,1.230,0.0), vec3(0.098,0.180,0.140));
  d = smin(d, sdEllip(p-vec3(0.0,0.960,0.0), vec3(0.098,0.090,0.128)), 0.09);
  res = smin2(res, vec2(d,1.0), KSM);
  // belt
  res = smin2(res, vec2(sdCap(p, vec3(0.0,1.048,0.0), vec3(0.0,1.002,0.0), 0.112,0.114),1.0), KSM);
  // chest strap
  { vec3 q = p - vec3(0.070,1.210,0.0); q.xy *= rot(0.55);
    res = smin2(res, vec2(sdBox(q, vec3(0.030,0.150,0.128),0.012),1.0), KSM); }

  // ---------- near leg (-z) ----------
  res = smin2(res, vec2(sdCap(p, vec3(0.018,0.900,-0.100), vec3(0.048,0.535,-0.114), 0.090,0.068),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.048,0.520,-0.114), vec3(0.016,0.130,-0.114), 0.064,0.048),1.0), KSM);
  res = smin2(res, vec2(sdBox(p-vec3(0.058,0.044,-0.114), vec3(0.100,0.028,0.046),0.022),1.0), KSM);

  // ---------- bow arm (-z), extended forward ----------
  res = smin2(res, vec2(sdCap(p, vec3(0.010,1.345,-0.155), vec3(0.190,1.290,-0.205), 0.062,0.050),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.190,1.290,-0.205), vec3(0.370,1.262,-0.230), 0.048,0.040),5.0), KSM);
  res = smin2(res, vec2(sdEllip(p-vec3(0.398,1.258,-0.232), vec3(0.046,0.042,0.038)),5.0), KSM);

  // ---------- draw arm (+z) ----------
  res = smin2(res, vec2(sdCap(p, vec3(0.010,1.345, 0.155), vec3(-0.075,1.245, 0.215), 0.062,0.050),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(-0.075,1.245,0.215), vec3(0.048,1.330,0.150), 0.048,0.038),5.0), KSM);
  res = smin2(res, vec2(sdEllip(p-vec3(0.062,1.336,0.140), vec3(0.040,0.038,0.034)),5.0), KSM);

  // ---------- bow ----------
  {
    vec3 b = p - vec3(0.408,1.262,-0.238);
    res = smin2(res, vec2(sdCap(b, vec3(0.0,0.0,0.0), vec3(-0.030,0.300,0.0), 0.026,0.020),3.0), KSM);
    res = smin2(res, vec2(sdCap(b, vec3(-0.030,0.300,0.0), vec3(-0.130,0.560,0.0), 0.020,0.013),3.0), KSM);
    res = smin2(res, vec2(sdCap(b, vec3(0.0,0.0,0.0), vec3(-0.030,-0.300,0.0), 0.026,0.020),3.0), KSM);
    res = smin2(res, vec2(sdCap(b, vec3(-0.030,-0.300,0.0), vec3(-0.130,-0.560,0.0), 0.020,0.013),3.0), KSM);
    // string, drawn back to the cheek
    res = smin2(res, vec2(sdCap(b, vec3(-0.140,0.580,0.0), vec3(-0.352,0.078,0.098), 0.006,0.005),6.0), KSM);
    res = smin2(res, vec2(sdCap(b, vec3(-0.140,-0.580,0.0), vec3(-0.352,0.078,0.098), 0.006,0.005),6.0), KSM);
    // nocked arrow
    res = smin2(res, vec2(sdCap(b, vec3(-0.360,0.076,0.096), vec3(0.150,0.056,-0.010), 0.010,0.009),3.0), KSM);
    res = smin2(res, vec2(sdCap(b, vec3(0.150,0.056,-0.010), vec3(0.212,0.054,-0.022), 0.020,0.002),4.0), KSM);
    res = smin2(res, vec2(sdEllip(b-vec3(-0.318,0.074,0.088), vec3(0.048,0.028,0.010)),6.0), KSM);
  }

  // ---------- head + hood ----------
  res = smin2(res, vec2(sdCap(p, vec3(0.005,1.400,0.0), vec3(0.010,1.470,0.0), 0.058,0.054),5.0), KSM);
  d = sdEllip(p-vec3(0.010,1.570,0.0), vec3(0.108,0.128,0.112));
  d = smin(d, sdEllip(p-vec3(0.082,1.528,0.0), vec3(0.078,0.082,0.086)), 0.05);
  d = smin(d, sdCap(p, vec3(-0.030,1.640,0.0), vec3(-0.135,1.470,0.0), 0.070,0.030), 0.07);
  res = smin2(res, vec2(d,2.0), KSM);
  // face opening
  res = smin2(res, vec2(sdEllip(p-vec3(0.118,1.520,0.0), vec3(0.058,0.062,0.070)),7.0), KSM);
  res = smin2(res, vec2(sdEllip(p-vec3(0.128,1.508,0.0), vec3(0.046,0.050,0.058)),5.0), KSM);
  res = smin2(res, vec2(sdEllip(p-vec3(0.158,1.520,0.0), vec3(0.026,0.020,0.018)),5.0), KSM);  // nose
  return res;
}
"""
CAM = dict(ro="vec3(0.16,0.94,-4.30)", ta="vec3(0.06,0.90,0.0)", fl="1.78")
render("radiant_longbowman", BODY, CAM, "../radiant_longbowman_raw.png", W=512, H=640, SS=1)
