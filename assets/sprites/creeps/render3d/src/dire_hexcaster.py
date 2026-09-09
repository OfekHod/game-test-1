
BODY = r"""
#define KSM 0.024
void material(float id, vec3 p, vec3 n, out vec3 albedo, out float rough,
              out float metal, out float bAmp, out float bScale, out vec3 emis){
  emis=vec3(0.0); bAmp=0.0; bScale=1.0;
  if(id<1.5){      albedo=vec3(0.195,0.145,0.320); metal=0.0; rough=0.86; }
  else if(id<2.5){ albedo=vec3(0.400,0.075,0.135); metal=0.0; rough=0.82; }
  else if(id<3.5){ albedo=vec3(0.790,0.760,0.605); metal=0.0; rough=0.50; }
  else if(id<4.5){ albedo=vec3(0.180,0.125,0.070); metal=0.0; rough=0.68; }
  else if(id<5.5){ albedo=vec3(0.038,0.032,0.055); metal=0.0; rough=0.94; }
  else {           albedo=vec3(0.0); metal=0.0; rough=1.0; emis=vec3(0.50,2.30,0.48); }
}

vec2 mapRaw(vec3 p){
  vec2 res = vec2(1e9,0.0);
  float d;

  // ---------- staff ----------
  res = smin2(res, vec2(sdCap(p, vec3(-0.235,1.760,0.130), vec3(-0.175,0.020,0.145), 0.026,0.030),4.0), KSM);
  // skull finial
  d = sdEllip(p-vec3(-0.238,1.845,0.130), vec3(0.072,0.078,0.068));
  d = smin(d, sdEllip(p-vec3(-0.185,1.812,0.130), vec3(0.055,0.045,0.052)), 0.04);
  res = smin2(res, vec2(d,3.0), KSM);
  res = smin2(res, vec2(sdSphere(p-vec3(-0.196,1.858,-0.052),0.024),6.0), KSM);
  res = smin2(res, vec2(sdSphere(p-vec3(-0.196,1.858, 0.052),0.024),6.0), KSM);

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
    res = smin2(res, vec2(d,mat), KSM);
  }
  res = smin2(res, vec2(sdSphere(p-vec3(0.212,1.062,0.0),0.042),3.0), KSM);

  // ---------- shoulders / cowl ----------
  d = sdEllip(p-vec3(0.010,1.395,0.0), vec3(0.170,0.098,0.215));
  res = smin2(res, vec2(d,1.0), KSM);

  // ---------- casting arm (-z) ----------
  res = smin2(res, vec2(sdCap(p, vec3(0.030,1.360,-0.175), vec3(0.175,1.230,-0.215), 0.085,0.068),1.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.175,1.230,-0.215), vec3(0.330,1.185,-0.230), 0.068,0.052),1.0), KSM);
  // bony hand
  res = smin2(res, vec2(sdEllip(p-vec3(0.360,1.180,-0.232), vec3(0.046,0.040,0.038)),3.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.382,1.196,-0.258), vec3(0.428,1.212,-0.268), 0.014,0.006),3.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.386,1.180,-0.232), vec3(0.436,1.188,-0.234), 0.014,0.006),3.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.382,1.164,-0.206), vec3(0.428,1.162,-0.196), 0.013,0.006),3.0), KSM);
  // witchfire orb
  res = smin2(res, vec2(sdSphere(p-vec3(0.520,1.205,-0.240),0.088),6.0), KSM);

  // ---------- staff arm (+z) ----------
  res = smin2(res, vec2(sdCap(p, vec3(0.020,1.360, 0.170), vec3(-0.110,1.235, 0.180), 0.082,0.064),1.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(-0.110,1.235,0.180), vec3(-0.190,1.180,0.150), 0.064,0.050),1.0), KSM);
  res = smin2(res, vec2(sdEllip(p-vec3(-0.198,1.172,0.142), vec3(0.044,0.040,0.038)),3.0), KSM);

  // ---------- hood ----------
  d = sdEllip(p-vec3(0.005,1.575,0.0), vec3(0.150,0.165,0.148));
  d = smin(d, sdEllip(p-vec3(0.105,1.520,0.0), vec3(0.098,0.098,0.100)), 0.06);
  d = smin(d, sdCap(p, vec3(-0.030,1.660,0.0), vec3(-0.160,1.455,0.0), 0.082,0.034), 0.07);

  res = smin2(res, vec2(d,1.0), KSM);
  // face void
  res = smin2(res, vec2(sdEllip(p-vec3(0.162,1.516,0.0), vec3(0.070,0.080,0.084)),5.0), KSM);
  // eyes
  res = smin2(res, vec2(sdSphere(p-vec3(0.196,1.532,-0.050),0.025),6.0), KSM);
  res = smin2(res, vec2(sdSphere(p-vec3(0.196,1.532, 0.050),0.025),6.0), KSM);
  return res;
}
"""
CAM = dict(target=(0.0, 1.03, 0.0), dist=4.3, fl=1.3, elev=0.38)
RIG = dict(hipY=0.95, shldY=1.38, armZ=0.18, amp=0.55, legAmp=0.0)
