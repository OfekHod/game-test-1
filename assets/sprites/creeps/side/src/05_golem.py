import sys, pathlib
sys.path.insert(0,'.')
from gen import wrap

P='r'
ramps = dict(
  st =("#dbd7c7","#9c9988","#5b594c","#232219"),   # lit / front
  st2=("#a5a293","#6a6759","#3a382f","#131209"),   # mid
  st3=("#6e6b5d","#403e34","#232116","#0b0a05"),   # back / shadow
  ms =("#b6dd72","#5d8a34","#2f4d1c","#12200b"),
  am =("#fff3cf","#ffc75e","#d8801c","#5a2f06"),
)
B=[]
def add(s): B.append("    "+s)
G="#08080400"

# ---------- BACK ARM (darkest, behind torso) ----------
add(f'<path d="M140 108 L166 118 L142 190 L112 178 Z" fill="url(#{P}_st3)"/>')
add(f'<path d="M112 178 L142 190 L134 268 L100 262 Z" fill="url(#{P}_st3)"/>')
add(f'<path d="M92 258 L140 264 L146 302 L136 330 L96 326 L84 296 Z" fill="url(#{P}_st3)"/>')
add('<g fill="none" stroke="#070603" stroke-width="3" opacity=".65"><path d="M90 292 L144 298"/><path d="M94 312 L140 316"/></g>')

# ---------- BACK LEG (dark) ----------
add(f'<path d="M148 204 L184 208 L180 270 L146 268 Z" fill="url(#{P}_st3)"/>')
add(f'<path d="M146 268 L180 270 L178 322 L144 320 Z" fill="url(#{P}_st3)"/>')
add(f'<path d="M124 316 L190 320 L192 340 L122 338 Z" fill="url(#{P}_st3)"/>')

# ---------- TORSO (leaning forward) ----------
add(f'<path d="M116 100 L150 84 L200 96 L214 124 L210 168 L196 206 L146 212 L124 190 L110 142 Z" fill="url(#{P}_st)"/>')
# angular facets
add(f'<path d="M116 100 L150 84 L156 122 L124 134 Z" fill="url(#{P}_st2)"/>')
add(f'<path d="M200 96 L214 124 L210 168 L184 158 L182 110 Z" fill="url(#{P}_st2)"/>')
add(f'<path d="M124 190 L146 212 L196 206 L210 168 L184 182 L140 178 Z" fill="url(#{P}_st3)"/>')
add(f'<path d="M124 134 L156 122 L162 168 L132 172 Z" fill="url(#{P}_st2)" opacity=".55"/>')
add('<g fill="none" stroke="#0b0a05" stroke-width="2.8" opacity=".6">'
    '<path d="M150 84 L156 122 L124 134"/><path d="M182 110 L184 158 L210 168"/>'
    '<path d="M156 122 L162 168 L132 172"/><path d="M140 178 L184 182"/></g>')
add('<path d="M116 100 L150 84 L154 96 L124 112 Z" fill="#f2eeda" opacity=".28"/>')

# ---------- NECK GAP + HEAD (juts forward) ----------
add(f'<path d="M196 112 L214 118 L212 156 L194 152 Z" fill="url(#{P}_st3)"/>')
add(f'<path d="M204 116 L238 108 L256 130 L252 160 L226 176 L202 166 Z" fill="url(#{P}_st2)"/>')
add(f'<path d="M204 116 L238 108 L242 124 L206 132 Z" fill="url(#{P}_st)"/>')
add(f'<path d="M202 166 L226 176 L252 160 L250 172 L224 188 L200 176 Z" fill="url(#{P}_st3)"/>')
add('<path d="M208 146 C226 154 244 150 252 140 L250 154 C238 166 216 166 206 158 Z" fill="#08080 4"/>'.replace(" 4","4"))
add(f'<g fill="url(#{P}_st3)"><path d="M212 108 L216 88 L228 104 Z"/><path d="M236 106 L250 92 L252 112 Z"/></g>')
add('<ellipse cx="238" cy="128" rx="13" ry="9" fill="#ffb63f" opacity=".5" filter="url(#'+P+'_ao2)"/>')
add('<ellipse cx="238" cy="128" rx="6" ry="4.2" fill="#fff0c4"/>')

# ---------- NEAR LEG (lit) ----------
add(f'<path d="M182 206 L220 208 L216 272 L180 270 Z" fill="url(#{P}_st)"/>')
add(f'<path d="M180 270 L216 272 L214 330 L178 328 Z" fill="url(#{P}_st)"/>')
add(f'<path d="M182 206 L196 208 L192 270 L180 270 Z" fill="url(#{P}_st2)" opacity=".7"/>')
add(f'<path d="M158 324 L232 328 L234 352 L156 348 Z" fill="url(#{P}_st)"/>')
add('<g fill="none" stroke="#0b0a05" stroke-width="2.8" opacity=".55"><path d="M182 246 L216 248"/><path d="M180 296 L214 298"/></g>')

# ---------- FRONT ARM (lightest, planted forward) ----------
add(f'<path d="M198 118 L228 112 L246 190 L216 198 Z" fill="url(#{P}_st)"/>')
add(f'<path d="M216 198 L246 190 L252 288 L218 290 Z" fill="url(#{P}_st)"/>')
add(f'<path d="M198 118 L212 114 L228 194 L216 198 Z" fill="url(#{P}_st2)" opacity=".65"/>')
add(f'<path d="M208 284 L262 288 L270 320 L258 352 L212 350 L200 318 Z" fill="url(#{P}_st)"/>')
add('<g fill="none" stroke="#0b0a05" stroke-width="3.4" opacity=".6"><path d="M206 316 L266 320"/><path d="M212 336 L262 338"/></g>')
add(f'<path d="M208 284 L234 280 L240 316 L212 318 Z" fill="url(#{P}_st2)" opacity=".7"/>')
add('<path d="M228 112 L246 190" fill="none" stroke="#f4f0dc" stroke-width="3" opacity=".35"/>')

# ---------- CORE + CRACKS ----------
add('<ellipse cx="160" cy="146" rx="32" ry="30" fill="#ffb63f" opacity=".4" filter="url(#'+P+'_ao)"/>')
add('<g fill="none" stroke="#ffd47a" stroke-width="5" stroke-linecap="round"><path d="M160 116 l-10 22 l12 15 l-8 27"/>'
    '<path d="M150 138 l-26 -10 M172 153 l24 9 M154 180 l-16 16 M160 116 l14 -18"/></g>')
add('<path d="M160 116 l-10 22 l12 15 l-8 27" fill="none" stroke="#fff6dc" stroke-width="2" stroke-linecap="round" opacity=".9"/>')

# ---------- MOSS ----------
add(f'<path d="M120 98 L150 84 L196 94 L188 106 L150 98 L126 110 Z" fill="url(#{P}_ms)"/>')
add(f'<path d="M206 116 L238 108 L242 120 L210 128 Z" fill="url(#{P}_ms)" opacity=".85"/>')
add(f'<path d="M158 324 L200 326 L200 338 L158 336 Z" fill="url(#{P}_ms)" opacity=".7"/>')

# ---------- RIM ----------
add('<g fill="none" stroke="#eef4ff" stroke-opacity=".38" stroke-width="3" stroke-linecap="round">'
    '<path d="M238 108 L256 130 L252 160"/><path d="M200 96 L214 124 L210 168"/>'
    '<path d="M228 112 L246 190 L252 288"/><path d="M220 208 L216 272"/></g>')
pathlib.Path('out_golem.svg').write_text(wrap(P, ramps, "\n".join(B), seed=53, ground=(190,346,100)))
print("golem v2")
