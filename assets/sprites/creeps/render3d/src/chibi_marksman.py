"""Chibi hero sized and coloured to sit alongside the game's existing carry.

Proportions follow that sprite rather than my creep set: roughly two heads tall
with an oversized helmet, a compact body, and a high camera. Palette is sampled
from the carry sheet (bone/tan, near-black gear, one gold accent).
"""

BODY = r"""
#define KSM 0.020

void material(float id, vec3 p, vec3 n, out vec3 albedo, out float rough,
              out float metal, out float bAmp, out float bScale, out vec3 emis){
  emis=vec3(0.0);
  bAmp=0.0; bScale=1.0;                 // flat: bump reads as real roughness
  float big  = patches(p,  6.5, 3.0);   // broad painted blocks
  float mid  = patches(p, 14.0, 2.0);   // a second, smaller pass
  float tone = mix(0.90, 1.14, big) * mix(0.96, 1.06, mid);
  if(id<1.5){                        // bone/tan plate
    albedo = vec3(0.560,0.462,0.320) * tone;
    metal=0.0; rough=0.88;
  } else if(id<2.5){                 // dark gear
    albedo = vec3(0.062,0.058,0.056) * mix(0.80,1.35,big);
    metal=0.20; rough=0.66;
  } else if(id<3.5){                 // gold accent
    albedo = vec3(0.790,0.436,0.052) * mix(0.90,1.12,big);
    metal=0.45; rough=0.40;
  } else if(id<4.5){                 // goggle glass
    albedo = vec3(0.400,0.500,0.552); metal=0.70; rough=0.14;
  } else if(id<5.5){                 // leather strap
    albedo = vec3(0.250,0.170,0.092) * mix(0.86,1.18,big);
    metal=0.0; rough=0.84;
  } else if(id<6.5){                 // teal band
    albedo = vec3(0.058,0.272,0.202) * mix(0.88,1.14,big);
    metal=0.0; rough=0.82;
  } else {                           // recessed seam
    albedo = vec3(0.014,0.013,0.014); metal=0.0; rough=0.95;
  }
}

vec2 mapRaw(vec3 p){
  vec2 res = vec2(1e9,0.0);

  // ---------- legs (short, chibi) ----------
  res = smin2(res, vec2(sdCap(p, vec3(0.010,0.250, 0.088), vec3(0.004,0.075, 0.092), 0.078,0.066),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.014,0.250,-0.088), vec3(0.020,0.075,-0.092), 0.080,0.068),2.0), KSM);
  res = smin2(res, vec2(sdBox(p-vec3(0.030,0.036, 0.092), vec3(0.078,0.030,0.058),0.026),5.0), KSM);
  res = smin2(res, vec2(sdBox(p-vec3(0.036,0.036,-0.092), vec3(0.080,0.030,0.060),0.026),5.0), KSM);

  // ---------- torso ----------
  res = smin2(res, vec2(sdEllip(p-vec3(0.005,0.372,0.0), vec3(0.145,0.128,0.164)),2.0), KSM);
  // chest plate
  res = smin2(res, vec2(sdBox(p-vec3(0.078,0.392,0.0), vec3(0.062,0.096,0.138),0.034),1.0), KSM);
  // belt
  res = smin2(res, vec2(sdCap(p, vec3(0.0,0.278,0.0), vec3(0.0,0.250,0.0), 0.158,0.160),5.0), KSM);
  res = smin2(res, vec2(sdBox(p-vec3(0.152,0.266,0.0), vec3(0.024,0.030,0.038),0.012),3.0), KSM);
  // shoulder pads
  res = smin2(res, vec2(sdEllip(p-vec3(0.0,0.462,-0.178), vec3(0.100,0.078,0.078)),1.0), KSM);
  res = smin2(res, vec2(sdEllip(p-vec3(0.0,0.462, 0.178), vec3(0.097,0.075,0.075)),1.0), KSM);

  // ---------- arms, both forward on the weapon ----------
  res = smin2(res, vec2(sdCap(p, vec3(0.010,0.452, 0.196), vec3(0.196,0.372, 0.208), 0.066,0.052),2.0), KSM);
  res = smin2(res, vec2(sdCap(p, vec3(0.010,0.452,-0.196), vec3(0.158,0.352,-0.196), 0.064,0.050),2.0), KSM);
  res = smin2(res, vec2(sdEllip(p-vec3(0.220,0.368, 0.206), vec3(0.052,0.048,0.046)),5.0), KSM);
  res = smin2(res, vec2(sdEllip(p-vec3(0.178,0.348,-0.196), vec3(0.050,0.046,0.044)),5.0), KSM);

  // ---------- weapon: long marksman piece, held level ----------
  {
    vec3 q = p - vec3(0.250,0.378, 0.186); q.xz *= rot(-0.62); q.xy *= rot(0.05);
    res = mmin(res, vec2(sdBox(q, vec3(0.175,0.038,0.040),0.018),2.0));
    res = mmin(res, vec2(sdBox(q-vec3(0.010,0.058,0.0), vec3(0.086,0.020,0.024),0.010),3.0));
    res = mmin(res, vec2(sdBox(q-vec3(-0.150,-0.048,0.0), vec3(0.062,0.052,0.030),0.024),5.0));
    res = mmin(res, vec2(sdCap(q, vec3(0.175,-0.004,0.0), vec3(0.268,-0.004,0.0), 0.026,0.020),2.0));
  }

  // ---------- head: oversized, the whole point of the silhouette ----------
  res = smin2(res, vec2(sdCap(p, vec3(0.005,0.490,0.0), vec3(0.008,0.548,0.0), 0.086,0.096),2.0), KSM);
  res = smin2(res, vec2(sdEllip(p-vec3(0.020,0.778,0.0), vec3(0.256,0.266,0.256)),1.0), KSM);
  // helmet shell: clipped to the upper half so it reads as a rim, not a seam
  res = mmin(res, vec2(max(sdEllip(p-vec3(0.005,0.790,0.0), vec3(0.272,0.278,0.270)),
                           0.788-p.y), 1.0));
  // brow brim, tucked back above the visor rather than jutting over it
  res = mmin(res, vec2(sdBox(p-vec3(0.112,0.906,0.0), vec3(0.074,0.024,0.212),0.026),1.0));
  // dark visor band, wrapped around the face
  res = mmin(res, vec2(sdEllip(p-vec3(0.174,0.792,0.0), vec3(0.102,0.076,0.258)),2.0));
  // goggle lenses, standing proud of the band so they still read at 92px
  res = mmin(res, vec2(sdBox(p-vec3(0.250,0.794,-0.112), vec3(0.030,0.040,0.070),0.014),4.0));
  res = mmin(res, vec2(sdBox(p-vec3(0.250,0.794, 0.112), vec3(0.030,0.040,0.070),0.014),4.0));
  // gold crest under the visor, pulled back so it is a band not a beak
  res = mmin(res, vec2(sdEllip(p-vec3(0.120,0.678,0.0), vec3(0.208,0.078,0.252)),3.0));
  res = mmin(res, vec2(sdEllip(p-vec3(0.040,0.634,0.0), vec3(0.236,0.058,0.246)),3.0));
  // teal band at the back, tying it to my creep set
  res = mmin(res, vec2(sdEllip(p-vec3(-0.206,0.848,0.0), vec3(0.092,0.084,0.184)),6.0));
  // jaw shadow
  // ---------- definition: seams, pads and kit ----------
  // helmet rim line where the shell meets the face
  {
    float ring = max(sdEllip(p-vec3(0.005,0.790,0.0), vec3(0.278,0.284,0.276)),
                    -sdEllip(p-vec3(0.005,0.790,0.0), vec3(0.258,0.264,0.256)));
    res = mmin(res, vec2(max(ring, abs(p.y-0.786)-0.013), 7.0));
  }
  // ear cups
  res = mmin(res, vec2(sdEllip(p-vec3(0.038,0.788,-0.244), vec3(0.062,0.062,0.030)),2.0));
  res = mmin(res, vec2(sdEllip(p-vec3(0.038,0.788, 0.244), vec3(0.062,0.062,0.030)),2.0));
  // collar
  res = mmin(res, vec2(sdCap(p, vec3(0.0,0.532,0.0), vec3(0.0,0.500,0.0), 0.118,0.126),5.0));
  // diagonal chest strap + buckle
  {
    vec3 q = p - vec3(0.120,0.398,0.0); q.yz *= rot(0.62);
    res = mmin(res, vec2(sdBox(q, vec3(0.026,0.026,0.168),0.010),5.0));
  }
  res = mmin(res, vec2(sdBox(p-vec3(0.150,0.406,-0.052), vec3(0.020,0.026,0.026),0.008),3.0));
  // hip pouch
  res = mmin(res, vec2(sdBox(p-vec3(0.086,0.302,-0.128), vec3(0.044,0.042,0.038),0.018),5.0));
  // knee pads
  res = mmin(res, vec2(sdEllip(p-vec3(0.052,0.176,-0.092), vec3(0.058,0.048,0.058)),1.0));
  res = mmin(res, vec2(sdEllip(p-vec3(0.046,0.176, 0.092), vec3(0.056,0.046,0.056)),1.0));
  // boot soles
  res = mmin(res, vec2(sdBox(p-vec3(0.030,0.012,-0.092), vec3(0.078,0.014,0.058),0.010),7.0));
  res = mmin(res, vec2(sdBox(p-vec3(0.024,0.012, 0.092), vec3(0.076,0.014,0.056),0.010),7.0));
  // weapon kit: sight rail and magazine
  {
    vec3 q = p - vec3(0.250,0.378, 0.186); q.xz *= rot(-0.62); q.xy *= rot(0.05);
    res = mmin(res, vec2(sdBox(q-vec3(0.030,0.082,0.0), vec3(0.052,0.020,0.016),0.008),7.0));
    res = mmin(res, vec2(sdBox(q-vec3(-0.040,-0.078,0.0), vec3(0.038,0.052,0.024),0.012),2.0));
  }
  return res;
}
"""
STYLE = dict(shadowTint=(0.500,0.432,0.428), ink=1.45, spec=0.26, contrast=1.0, lift=0.36)
CAM = dict(target=(0.0, 0.55, 0.0), dist=4.20, fl=3.45, elev=0.46)
RIG = dict(hipY=0.26, shldY=0.47, armZ=0.17, amp=0.42, legAmp=1.0)
