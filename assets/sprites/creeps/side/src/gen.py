import math, pathlib, sys

def cap(p0, p1, w0, w1):
    (x0,y0),(x1,y1) = p0,p1
    dx,dy = x1-x0, y1-y0
    L = math.hypot(dx,dy) or 1
    nx,ny = -dy/L, dx/L
    r0,r1 = w0/2, w1/2
    a=(x0+nx*r0, y0+ny*r0); b=(x1+nx*r1, y1+ny*r1)
    c=(x1-nx*r1, y1-ny*r1); d=(x0-nx*r0, y0-ny*r0)
    return (f"M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f} "
            f"A{r1:.1f} {r1:.1f} 0 0 0 {c[0]:.1f} {c[1]:.1f} "
            f"L{d[0]:.1f} {d[1]:.1f} A{r0:.1f} {r0:.1f} 0 0 0 {a[0]:.1f} {a[1]:.1f} Z")

def defs(pref, ramps, seed=11):
    out=[]
    for name,(a,b,c,d) in ramps.items():
        out.append(f'''<linearGradient id="{pref}_{name}" x1="1" y1="0" x2="0.15" y2="1">
      <stop offset="0" stop-color="{a}"/><stop offset=".28" stop-color="{b}"/>
      <stop offset=".62" stop-color="{c}"/><stop offset="1" stop-color="{d}"/></linearGradient>''')
    out.append(f'<filter id="{pref}_sh" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="9"/></filter>')
    out.append(f'<filter id="{pref}_ao" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="5"/></filter>')
    out.append(f'<filter id="{pref}_ao2" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="2.2"/></filter>')
    out.append(f'''<filter id="{pref}_grain" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="3" seed="{seed}" result="n"/>
      <feColorMatrix in="n" type="saturate" values="0" result="ng"/>
      <feComponentTransfer in="ng" result="nc">
        <feFuncR type="linear" slope=".15" intercept=".43"/>
        <feFuncG type="linear" slope=".15" intercept=".43"/>
        <feFuncB type="linear" slope=".15" intercept=".43"/>
      </feComponentTransfer>
      <feComposite in="nc" in2="SourceGraphic" operator="in" result="m"/>
      <feBlend in="SourceGraphic" in2="m" mode="overlay"/>
    </filter>''')
    return "\n    ".join(out)

def wrap(pref, ramps, body, seed=11, ground=(152,368,84)):
    gx,gy,gr = ground
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 400" width="320" height="400">
  <defs>
    {defs(pref, ramps, seed)}
  </defs>
  <ellipse cx="{gx}" cy="{gy}" rx="{gr}" ry="12" fill="#000" opacity=".55" filter="url(#{pref}_sh)"/>
  <g filter="url(#{pref}_grain)">
{body}
  </g>
</svg>'''
