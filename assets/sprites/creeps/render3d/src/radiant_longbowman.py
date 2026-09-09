import sys; sys.path.insert(0,'.')
from rt import render

BODY = r"""
void material(float id, vec3 p, vec3 n, out vec3 albedo, out float rough,
              out float metal, out float bAmp, out float bScale, out vec3 emis){
  emis=vec3(0.0);
  float g = fbm(p*42.0);
  if(id<1.5){                        // worn leather
    albedo = vec3(0.140,0.088,0.046)*(0.58+0.82*fbm(p*58.0));
    metal=0.0; rough=0.80; bAmp=0.013; bScale=150.0;
  } else if(id<2.5){                 // teal wool hood / cloak
    albedo = vec3(0.048,0.212,0.162)*(0.66+0.70*fbm(p*76.0));
    metal=0.0; rough=0.94; bAmp=0.014; bScale=185.0;
  } else if(id<3.5){                 // bow stave, dark yew
    albedo = vec3(0.115,0.072,0.034)*(0.62+0.76*fbm(p*40.0));
    metal=0.0; rough=0.62; bAmp=0.009; bScale=110.0;
  } else if(id<4.5){                 // steel
    albedo = vec3(0.70,0.73,0.76); metal=1.0; rough=0.13+0.12*g; bAmp=0.0008; bScale=150.0;
  } else if(id<5.5){                 // skin
    albedo = vec3(0.365,0.225,0.155)*(0.86+0.24*fbm(p*70.0));
    metal=0.0; rough=0.66; bAmp=0.006; bScale=200.0;
  } else if(id<6.5){                 // bowstring / fletching
    albedo = vec3(0.62,0.60,0.52); metal=0.0; rough=0.70; bAmp=0.004; bScale=240.0;
  } else {                           // dark recess
    albedo = vec3(0.020,0.020,0.022); metal=0.0; rough=0.96; bAmp=0.0; bScale=1.0;
  }
}

vec2 map(vec3 p){
  vec2 res = vec2(1e9,0.0);
  float d;

  // ---------- far leg (+z) ----------
  res = mmin(res, vec2(sdCap(p, vec3(0.005,0.900, 0.098), vec3(-0.048,0.535, 0.112), 0.086,0.066),2.0));
  res = mmin(res, vec2(sdCap(p, vec3(-0.048,0.520,0.112), vec3(-0.098,0.130,0.112), 0.062,0.046),1.0));
  res = mmin(res, vec2(sdBox(p-vec3(-0.052,0.044,0.112), vec3(0.092,0.026,0.044),0.022),1.0));

  // ---------- quiver on the back ----------
  { vec3 q = p - vec3(-0.170,1.130,0.135); q.xy *= rot(0.30);
    res = mmin(res, vec2(sdCap(q, vec3(0.0,-0.180,0.0), vec3(0.0,0.190,0.0), 0.066,0.070),1.0)); }
  { vec3 q = p - vec3(-0.235,1.395,0.135); q.xy *= rot(0.30);
    res = mmin(res, vec2(sdCap(q, vec3(-0.020,0.0,-0.022), vec3(-0.020,0.150,-0.030), 0.008,0.008),3.0));
    res = mmin(res, vec2(sdCap(q, vec3( 0.008,0.0, 0.004), vec3( 0.008,0.165, 0.004), 0.008,0.008),3.0));
    res = mmin(res, vec2(sdCap(q, vec3( 0.030,0.0, 0.028), vec3( 0.030,0.140, 0.036), 0.008,0.008),3.0));
    res = mmin(res, vec2(sdEllip(q-vec3(-0.020,0.155,-0.030), vec3(0.012,0.038,0.012)),6.0));
    res = mmin(res, vec2(sdEllip(q-vec3( 0.008,0.170, 0.004), vec3(0.012,0.038,0.012)),6.0));
    res = mmin(res, vec2(sdEllip(q-vec3( 0.030,0.145, 0.036), vec3(0.012,0.036,0.012)),6.0)); }

  // ---------- cloak ----------
  { vec3 q = p - vec3(-0.030,1.020,0.0);
    d = sdCap(q, vec3(0.0,0.360,0.0), vec3(-0.020,-0.430,0.0), 0.175,0.215);
    float ang = atan(q.z,q.x);
    d -= 0.008*sin(ang*11.0)*smoothstep(1.30,0.60,p.y);
    d = max(d, -sdBox(p-vec3(0.230,1.150,0.0), vec3(0.230,0.420,0.320),0.0));  // open at the front
    res = mmin(res, vec2(d,2.0)); }

  // ---------- torso ----------
  d = sdEllip(p-vec3(0.005,1.230,0.0), vec3(0.098,0.180,0.140));
  d = smin(d, sdEllip(p-vec3(0.0,0.960,0.0), vec3(0.098,0.090,0.128)), 0.09);
  res = mmin(res, vec2(d,1.0));
  // belt
  res = mmin(res, vec2(sdCap(p, vec3(0.0,1.048,0.0), vec3(0.0,1.002,0.0), 0.112,0.114),1.0));
  // chest strap
  { vec3 q = p - vec3(0.070,1.210,0.0); q.xy *= rot(0.55);
    res = mmin(res, vec2(sdBox(q, vec3(0.030,0.150,0.128),0.012),1.0)); }

  // ---------- near leg (-z) ----------
  res = mmin(res, vec2(sdCap(p, vec3(0.018,0.900,-0.100), vec3(0.048,0.535,-0.114), 0.090,0.068),2.0));
  res = mmin(res, vec2(sdCap(p, vec3(0.048,0.520,-0.114), vec3(0.016,0.130,-0.114), 0.064,0.048),1.0));
  res = mmin(res, vec2(sdBox(p-vec3(0.058,0.044,-0.114), vec3(0.100,0.028,0.046),0.022),1.0));

  // ---------- bow arm (-z), extended forward ----------
  res = mmin(res, vec2(sdCap(p, vec3(0.010,1.345,-0.155), vec3(0.190,1.290,-0.205), 0.062,0.050),2.0));
  res = mmin(res, vec2(sdCap(p, vec3(0.190,1.290,-0.205), vec3(0.370,1.262,-0.230), 0.048,0.040),5.0));
  res = mmin(res, vec2(sdEllip(p-vec3(0.398,1.258,-0.232), vec3(0.046,0.042,0.038)),5.0));

  // ---------- draw arm (+z) ----------
  res = mmin(res, vec2(sdCap(p, vec3(0.010,1.345, 0.155), vec3(-0.075,1.245, 0.215), 0.062,0.050),2.0));
  res = mmin(res, vec2(sdCap(p, vec3(-0.075,1.245,0.215), vec3(0.048,1.330,0.150), 0.048,0.038),5.0));
  res = mmin(res, vec2(sdEllip(p-vec3(0.062,1.336,0.140), vec3(0.040,0.038,0.034)),5.0));

  // ---------- bow ----------
  {
    vec3 b = p - vec3(0.408,1.262,-0.238);
    res = mmin(res, vec2(sdCap(b, vec3(0.0,0.0,0.0), vec3(-0.030,0.300,0.0), 0.026,0.020),3.0));
    res = mmin(res, vec2(sdCap(b, vec3(-0.030,0.300,0.0), vec3(-0.130,0.560,0.0), 0.020,0.013),3.0));
    res = mmin(res, vec2(sdCap(b, vec3(0.0,0.0,0.0), vec3(-0.030,-0.300,0.0), 0.026,0.020),3.0));
    res = mmin(res, vec2(sdCap(b, vec3(-0.030,-0.300,0.0), vec3(-0.130,-0.560,0.0), 0.020,0.013),3.0));
    // string, drawn back to the cheek
    res = mmin(res, vec2(sdCap(b, vec3(-0.140,0.580,0.0), vec3(-0.352,0.078,0.098), 0.006,0.005),6.0));
    res = mmin(res, vec2(sdCap(b, vec3(-0.140,-0.580,0.0), vec3(-0.352,0.078,0.098), 0.006,0.005),6.0));
    // nocked arrow
    res = mmin(res, vec2(sdCap(b, vec3(-0.360,0.076,0.096), vec3(0.150,0.056,-0.010), 0.010,0.009),3.0));
    res = mmin(res, vec2(sdCap(b, vec3(0.150,0.056,-0.010), vec3(0.212,0.054,-0.022), 0.020,0.002),4.0));
    res = mmin(res, vec2(sdEllip(b-vec3(-0.318,0.074,0.088), vec3(0.048,0.028,0.010)),6.0));
  }

  // ---------- head + hood ----------
  res = mmin(res, vec2(sdCap(p, vec3(0.005,1.400,0.0), vec3(0.010,1.470,0.0), 0.058,0.054),5.0));
  d = sdEllip(p-vec3(0.010,1.570,0.0), vec3(0.108,0.128,0.112));
  d = smin(d, sdEllip(p-vec3(0.082,1.528,0.0), vec3(0.078,0.082,0.086)), 0.05);
  d = smin(d, sdCap(p, vec3(-0.030,1.640,0.0), vec3(-0.135,1.470,0.0), 0.070,0.030), 0.07);
  res = mmin(res, vec2(d,2.0));
  // face opening
  res = mmin(res, vec2(sdEllip(p-vec3(0.118,1.520,0.0), vec3(0.058,0.062,0.070)),7.0));
  res = mmin(res, vec2(sdEllip(p-vec3(0.128,1.508,0.0), vec3(0.046,0.050,0.058)),5.0));
  res = mmin(res, vec2(sdEllip(p-vec3(0.158,1.520,0.0), vec3(0.026,0.020,0.018)),5.0));  // nose
  return res;
}
"""
CAM = dict(ro="vec3(0.16,0.94,-4.30)", ta="vec3(0.06,0.90,0.0)", fl="1.78")
render("radiant_longbowman", BODY, CAM, "../radiant_longbowman_raw.png", W=512, H=640, SS=1)
