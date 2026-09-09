import sys; sys.path.insert(0,'.')
from rt import render

BODY = r"""
void material(float id, vec3 p, vec3 n, out vec3 albedo, out float rough,
              out float metal, out float bAmp, out float bScale, out vec3 emis){
  emis=vec3(0.0);
  float g = fbm(p*38.0);
  if(id<1.5){                        // heavy purple wool
    albedo = vec3(0.105,0.078,0.165)*(0.66+0.72*fbm(p*70.0));
    metal=0.0; rough=0.95; bAmp=0.016; bScale=170.0;
  } else if(id<2.5){                 // crimson trim
    albedo = vec3(0.260,0.048,0.082)*(0.70+0.62*fbm(p*80.0));
    metal=0.0; rough=0.90; bAmp=0.014; bScale=190.0;
  } else if(id<3.5){                 // bone
    albedo = vec3(0.76,0.72,0.57)*(0.74+0.48*fbm(p*52.0));
    metal=0.0; rough=0.52+0.22*g; bAmp=0.011; bScale=125.0;
  } else if(id<4.5){                 // dark wood
    albedo = vec3(0.075,0.052,0.030)*(0.60+0.80*fbm(p*44.0));
    metal=0.0; rough=0.80; bAmp=0.013; bScale=120.0;
  } else if(id<5.5){                 // void inside the hood
    albedo = vec3(0.012,0.010,0.018); metal=0.0; rough=0.98; bAmp=0.0; bScale=1.0;
  } else {                           // witchfire
    albedo = vec3(0.0); metal=0.0; rough=1.0; bAmp=0.0; bScale=1.0;
    emis = vec3(0.45,2.35,0.42);
  }
}

vec2 map(vec3 p){
  vec2 res = vec2(1e9,0.0);
  float d;

  // ---------- staff ----------
  res = mmin(res, vec2(sdCap(p, vec3(-0.235,1.760,0.130), vec3(-0.175,0.020,0.145), 0.026,0.030),4.0));
  // skull finial
  d = sdEllip(p-vec3(-0.238,1.845,0.130), vec3(0.072,0.078,0.068));
  d = smin(d, sdEllip(p-vec3(-0.185,1.812,0.130), vec3(0.055,0.045,0.052)), 0.04);
  res = mmin(res, vec2(d,3.0));
  res = mmin(res, vec2(sdSphere(p-vec3(-0.196,1.858,-0.052),0.024),6.0));
  res = mmin(res, vec2(sdSphere(p-vec3(-0.196,1.858, 0.052),0.024),6.0));

  // ---------- robe ----------
  {
    float ang = atan(p.z, p.x-0.0);
    float folds = 0.010*sin(ang*13.0) + 0.006*sin(ang*27.0+1.3);
    d = sdCap(p, vec3(0.010,1.360,0.0), vec3(0.0,0.075,0.0), 0.185,0.300);
    d -= folds*smoothstep(1.35,0.55,p.y);
    d = max(d, 0.022-p.y);                     // flat hem on the ground
    float mat = 1.0;
    if(p.y < 0.135) mat = 2.0;                 // hem band
    else if(p.y > 1.020 && p.y < 1.105) mat = 2.0;  // sash
    res = mmin(res, vec2(d,mat));
  }
  res = mmin(res, vec2(sdSphere(p-vec3(0.212,1.062,0.0),0.042),3.0));

  // ---------- shoulders / cowl ----------
  d = sdEllip(p-vec3(0.010,1.395,0.0), vec3(0.170,0.098,0.215));
  res = mmin(res, vec2(d,1.0));

  // ---------- casting arm (-z) ----------
  res = mmin(res, vec2(sdCap(p, vec3(0.030,1.360,-0.175), vec3(0.175,1.230,-0.215), 0.085,0.068),1.0));
  res = mmin(res, vec2(sdCap(p, vec3(0.175,1.230,-0.215), vec3(0.330,1.185,-0.230), 0.068,0.052),1.0));
  // bony hand
  res = mmin(res, vec2(sdEllip(p-vec3(0.360,1.180,-0.232), vec3(0.046,0.040,0.038)),3.0));
  res = mmin(res, vec2(sdCap(p, vec3(0.382,1.196,-0.258), vec3(0.428,1.212,-0.268), 0.014,0.006),3.0));
  res = mmin(res, vec2(sdCap(p, vec3(0.386,1.180,-0.232), vec3(0.436,1.188,-0.234), 0.014,0.006),3.0));
  res = mmin(res, vec2(sdCap(p, vec3(0.382,1.164,-0.206), vec3(0.428,1.162,-0.196), 0.013,0.006),3.0));
  // witchfire orb
  res = mmin(res, vec2(sdSphere(p-vec3(0.520,1.205,-0.240),0.088),6.0));

  // ---------- staff arm (+z) ----------
  res = mmin(res, vec2(sdCap(p, vec3(0.020,1.360, 0.170), vec3(-0.110,1.235, 0.180), 0.082,0.064),1.0));
  res = mmin(res, vec2(sdCap(p, vec3(-0.110,1.235,0.180), vec3(-0.190,1.180,0.150), 0.064,0.050),1.0));
  res = mmin(res, vec2(sdEllip(p-vec3(-0.198,1.172,0.142), vec3(0.044,0.040,0.038)),3.0));

  // ---------- hood ----------
  d = sdEllip(p-vec3(0.005,1.575,0.0), vec3(0.150,0.165,0.148));
  d = smin(d, sdEllip(p-vec3(0.105,1.520,0.0), vec3(0.098,0.098,0.100)), 0.06);
  d = smin(d, sdCap(p, vec3(-0.030,1.660,0.0), vec3(-0.160,1.455,0.0), 0.082,0.034), 0.07);

  res = mmin(res, vec2(d,1.0));
  // face void
  res = mmin(res, vec2(sdEllip(p-vec3(0.162,1.516,0.0), vec3(0.070,0.080,0.084)),5.0));
  // eyes
  res = mmin(res, vec2(sdSphere(p-vec3(0.196,1.532,-0.050),0.025),6.0));
  res = mmin(res, vec2(sdSphere(p-vec3(0.196,1.532, 0.050),0.025),6.0));
  return res;
}
"""
CAM = dict(ro="vec3(0.10,0.95,-4.30)", ta="vec3(0.03,0.92,0.0)", fl="1.80")
render("dire_hexcaster", BODY, CAM, "../dire_hexcaster_raw.png", W=512, H=640, SS=1)
