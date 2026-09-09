import sys; sys.path.insert(0,'.')
from rt import render

BODY = r"""
void material(float id, vec3 p, vec3 n, out vec3 albedo, out float rough,
              out float metal, out float bAmp, out float bScale, out vec3 emis){
  emis=vec3(0.0);
  float g  = fbm(p*44.0);
  float g2 = fbm(p*12.0);
  if(id<1.5){                       // gold armour
    albedo = vec3(0.80,0.585,0.235)*(0.80+0.36*g)*(0.88+0.22*g2);
    metal=1.0; rough=0.22+0.34*g; bAmp=0.0018; bScale=130.0;
  } else if(id<2.5){                // teal cloth
    albedo = vec3(0.055,0.245,0.185)*(0.66+0.70*fbm(p*80.0));
    metal=0.0; rough=0.93; bAmp=0.011; bScale=200.0;
  } else if(id<3.5){                // polished steel
    albedo = vec3(0.70,0.73,0.76);
    metal=1.0; rough=0.08+0.13*g; bAmp=0.0006; bScale=150.0;
  } else if(id<4.5){                // leather
    albedo = vec3(0.125,0.074,0.038)*(0.60+0.78*fbm(p*62.0));
    metal=0.0; rough=0.82; bAmp=0.012; bScale=155.0;
  } else if(id<5.5){                // dark iron / mail
    albedo = vec3(0.140,0.140,0.160)*(0.82+0.34*g);
    metal=1.0; rough=0.40+0.26*g; bAmp=0.006; bScale=260.0;
  } else {                          // deep shadow recess
    albedo = vec3(0.020,0.020,0.024);
    metal=0.0; rough=0.95; bAmp=0.0; bScale=1.0;
  }
}

vec2 map(vec3 p){
  vec2 res = vec2(1e9,0.0);

  // ================= FAR LEG (+z) =================
  res = mmin(res, vec2(sdCap(p, vec3(0.005,0.880, 0.100), vec3(-0.045,0.530, 0.115), 0.092,0.070),5.0));
  res = mmin(res, vec2(sdCap(p, vec3(0.010,0.860, 0.100), vec3(-0.040,0.560, 0.115), 0.098,0.074),1.0));
  res = mmin(res, vec2(sdSphere(p-vec3(-0.048,0.525,0.115),0.076),1.0));
  res = mmin(res, vec2(sdCap(p, vec3(-0.048,0.510,0.115), vec3(-0.098,0.120,0.115), 0.070,0.050),1.0));
  res = mmin(res, vec2(sdBox(p-vec3(-0.052,0.040,0.115), vec3(0.096,0.024,0.046),0.022),4.0));

  // ================= FAR ARM (+z) : sword arm =================
  res = mmin(res, vec2(sdCap(p, vec3(0.005,1.370, 0.190), vec3(0.030,1.140, 0.218), 0.068,0.054),5.0));
  res = mmin(res, vec2(sdEllip(p-vec3(0.012,1.320,0.208), vec3(0.070,0.075,0.062)),1.0));
  res = mmin(res, vec2(sdSphere(p-vec3(0.032,1.132,0.220),0.058),1.0));
  res = mmin(res, vec2(sdCap(p, vec3(0.032,1.122,0.220), vec3(0.196,0.986,0.238), 0.055,0.045),1.0));
  res = mmin(res, vec2(sdEllip(p-vec3(0.214,0.974,0.240), vec3(0.055,0.051,0.046)),1.0));

  // ================= SWORD (far hand) =================
  res = mmin(res, vec2(sdCap(p, vec3(0.204,0.948,0.240), vec3(0.258,1.088,0.243), 0.022,0.019),4.0));
  res = mmin(res, vec2(sdSphere(p-vec3(0.197,0.930,0.240),0.028),1.0));
  {
    vec3 q = p - vec3(0.262,1.098,0.243); q.xy *= rot(-0.95);
    res = mmin(res, vec2(sdBox(q, vec3(0.018,0.012,0.100),0.007),1.0));
  }
  {
    vec3 q = p - vec3(0.502,1.446,0.243); q.xy *= rot(-0.948);
    vec3 qs = vec3(q.x,q.y,q.z*3.4);
    res = mmin(res, vec2(sdCap(qs, vec3(-0.352,0.0,0.0), vec3(0.386,0.0,0.0), 0.048,0.004)/3.4, 3.0));
  }

  // ================= UNDER-ARMOUR BODY =================
  res = mmin(res, vec2(sdEllip(p-vec3(0.005,1.220,0.0), vec3(0.084,0.184,0.134)),5.0));
  res = mmin(res, vec2(sdEllip(p-vec3(0.005,0.930,0.0), vec3(0.098,0.078,0.128)),5.0));

  // ================= FAULD + TABARD =================
  res = mmin(res, vec2(sdCap(p, vec3(0.005,0.985,0.0), vec3(0.0,0.884,0.0), 0.132,0.158),1.0));
  res = mmin(res, vec2(sdBox(p-vec3(0.148,0.770,0.0), vec3(0.012,0.190,0.088),0.010),2.0));

  // ================= TORSO PLATE (crisp) =================
  {
    vec3 q = p - vec3(0.020,1.300,0.0); q.xy *= rot(0.07);
    res = mmin(res, vec2(sdBox(q, vec3(0.082,0.148,0.152),0.020),1.0));
  }
  // chest ridge
  {
    vec3 q = p - vec3(0.098,1.300,0.0); q.xy *= rot(0.07);
    res = mmin(res, vec2(sdBox(q, vec3(0.020,0.140,0.030),0.014),1.0));
  }
  // abdominal lames, stacked with visible seams
  res = mmin(res, vec2(sdBox(p-vec3(0.030,1.128,0.0), vec3(0.078,0.021,0.146),0.013),1.0));
  res = mmin(res, vec2(sdBox(p-vec3(0.026,1.076,0.0), vec3(0.078,0.021,0.150),0.013),1.0));
  res = mmin(res, vec2(sdBox(p-vec3(0.020,1.024,0.0), vec3(0.078,0.021,0.152),0.013),1.0));

  // ================= NEAR LEG (-z) =================
  res = mmin(res, vec2(sdCap(p, vec3(0.020,0.880,-0.105), vec3(0.048,0.530,-0.118), 0.096,0.074),5.0));
  res = mmin(res, vec2(sdCap(p, vec3(0.024,0.860,-0.105), vec3(0.052,0.560,-0.118), 0.102,0.078),1.0));
  res = mmin(res, vec2(sdSphere(p-vec3(0.052,0.525,-0.118),0.080),1.0));
  res = mmin(res, vec2(sdCap(p, vec3(0.048,0.510,-0.118), vec3(0.014,0.120,-0.118), 0.074,0.053),1.0));
  res = mmin(res, vec2(sdBox(p-vec3(0.060,0.040,-0.118), vec3(0.110,0.026,0.048),0.022),4.0));

  // ================= PAULDRONS (layered lames) =================
  res = mmin(res, vec2(sdEllip(p-vec3(0.012,1.400,-0.196), vec3(0.126,0.098,0.094)),1.0));
  res = mmin(res, vec2(sdEllip(p-vec3(0.008,1.336,-0.212), vec3(0.122,0.046,0.086)),1.0));
  res = mmin(res, vec2(sdEllip(p-vec3(0.004,1.282,-0.222), vec3(0.114,0.042,0.078)),1.0));
  res = mmin(res, vec2(sdEllip(p-vec3(0.012,1.400, 0.196), vec3(0.122,0.094,0.090)),1.0));

  // ================= NEAR ARM (-z) : shield arm =================
  res = mmin(res, vec2(sdCap(p, vec3(0.010,1.370,-0.190), vec3(0.040,1.150,-0.228), 0.070,0.056),5.0));
  res = mmin(res, vec2(sdSphere(p-vec3(0.042,1.142,-0.230),0.060),1.0));
  res = mmin(res, vec2(sdCap(p, vec3(0.042,1.132,-0.230), vec3(0.168,1.036,-0.246), 0.056,0.046),1.0));

  // ================= SHIELD (near arm) =================
  {
    vec3 q = p - vec3(0.150,1.045,-0.300);
    q.xz *= rot(0.30);
    res = mmin(res, vec2(sdEllip(q, vec3(0.032,0.258,0.205)),1.0));
    res = mmin(res, vec2(sdEllip(q-vec3(-0.026,0.010,0.0), vec3(0.024,0.086,0.072)),1.0));
    res = mmin(res, vec2(max(sdEllip(q,vec3(0.036,0.266,0.213)), -sdEllip(q,vec3(0.058,0.234,0.181))),5.0));
  }

  // ================= NECK + HELM =================
  res = mmin(res, vec2(sdCap(p, vec3(0.010,1.440,0.0), vec3(0.016,1.530,0.0), 0.070,0.064),5.0));
  // skull cap
  res = mmin(res, vec2(sdEllip(p-vec3(0.020,1.652,0.0), vec3(0.104,0.122,0.104)),1.0));
  // face plate, pushed forward
  {
    vec3 q = p - vec3(0.086,1.628,0.0); q.xy *= rot(-0.10);
    float fp = sdBox(q, vec3(0.030,0.076,0.086),0.026);
    float sk = sdEllip(p-vec3(0.020,1.652,0.0), vec3(0.104,0.122,0.104));
    res = mmin(res, vec2(smin(fp,sk,0.045),1.0));
  }
  // brow
  res = mmin(res, vec2(sdBox(p-vec3(0.098,1.690,0.0), vec3(0.032,0.013,0.092),0.010),1.0));
  // eye slit recess
  res = mmin(res, vec2(sdBox(p-vec3(0.126,1.650,0.0), vec3(0.030,0.011,0.082),0.006),6.0));
  // nose guard
  res = mmin(res, vec2(sdBox(p-vec3(0.132,1.612,0.0), vec3(0.026,0.056,0.014),0.010),1.0));
  // neck guard flaring at the back
  res = mmin(res, vec2(sdCap(p, vec3(-0.024,1.598,0.0), vec3(-0.050,1.524,0.0), 0.080,0.070),1.0));
  // crest rail
  res = mmin(res, vec2(sdBox(p-vec3(0.014,1.772,0.0), vec3(0.090,0.026,0.010),0.007),1.0));
  {
    float dd = sdCap(p, vec3(0.024,1.788,0.0), vec3(-0.140,1.752,0.0), 0.044,0.036);
    dd = smin(dd, sdCap(p, vec3(-0.140,1.752,0.0), vec3(-0.292,1.612,0.0), 0.036,0.014), 0.05);
    res = mmin(res, vec2(dd,2.0));
  }
  return res;
}
"""
CAM = dict(ro="vec3(0.13,0.95,-4.20)", ta="vec3(0.0,0.91,0.0)", fl="1.85")
render("radiant_vanguard", BODY, CAM, "../radiant_vanguard_raw.png", W=512, H=640, SS=1)
