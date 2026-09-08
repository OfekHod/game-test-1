import sys, pathlib
sys.path.insert(0,'.')
from gen import cap, wrap

P='v'
ramps = dict(
  au =("#fbe4a4","#d5ae57","#8a6a29","#33260b"),
  au2=("#d0a950","#96742f","#5c471a","#221906"),
  au3=("#8e7130","#5e4a1d","#33280f","#150f05"),
  tl =("#6ddcae","#2f9070","#186047","#07231a"),
  tl2=("#3a9c78","#1e6b51","#0e3f30","#051813"),
  st =("#f6fafc","#c2ced5","#78868e","#2b343a"),
  lt =("#a87b48","#6f4e28","#402a12","#180f05"),
)
J = dict(head=(152,56), neck=(152,88), sh=(150,102),
         elb=(168,164), wri=(196,202),
         nhip=(152,214), nknee=(162,288), nank=(158,354),
         fhip=(138,210), fknee=(120,282), fank=(106,346))

B=[]
def add(s): B.append("    "+s)

# ---------- FAR LEG ----------
add(f'<path d="{cap(J["fhip"],J["fknee"],36,28)}" fill="url(#{P}_au3)"/>')
add(f'<path d="{cap(J["fknee"],J["fank"],26,18)}" fill="url(#{P}_au3)"/>')
add('<path d="M96 340 C88 351 90 362 102 362 L138 362 C146 360 142 350 130 346 L116 337 Z" fill="url(#'+P+'_lt)"/>')
add(f'<ellipse cx="120" cy="282" rx="15" ry="12" fill="url(#{P}_au3)"/>')
add('<path d="M104 200 C96 250 92 300 96 342 L134 348 C130 300 132 250 140 202 Z" fill="#000" opacity=".33" filter="url(#'+P+'_ao)"/>')

# ---------- SHIELD (edge-on) ----------
add(f'<path d="M116 126 C107 162 107 218 116 254 C125 248 128 232 128 190 C128 148 125 132 116 126 Z" fill="url(#{P}_au3)"/>')
add('<path d="M116 126 C110 162 110 218 116 254 C119 248 120 232 120 190 C120 148 119 132 116 126 Z" fill="#0b0803" opacity=".6"/>')
add('<path d="M117 130 C112 162 112 216 117 250" fill="none" stroke="#e8ca7e" stroke-width="2" opacity=".5"/>')

# ---------- TABARD ----------
add(f'<path d="M132 196 C123 242 121 292 127 320 L163 320 C167 284 168 238 162 196 Z" fill="url(#{P}_tl)"/>')
add('<g fill="none" opacity=".55"><path d="M138 200 C132 244 132 288 136 316" stroke="#07231a" stroke-width="3.5"/>'
    '<path d="M152 200 C150 244 150 288 152 316" stroke="#07231a" stroke-width="3"/>'
    '<path d="M145 202 C141 244 141 286 144 314" stroke="#7ee6bb" stroke-width="2"/></g>')
add('<path d="M127 306 L163 306 L163 320 L127 320 Z" fill="#000" opacity=".35" filter="url(#'+P+'_ao2)"/>')

# ---------- TORSO ----------
add(f'<path d="M128 104 C142 95 166 97 176 110 C185 130 187 158 182 184 C164 196 140 194 130 184 C122 158 122 128 128 104 Z" fill="url(#{P}_au)"/>')
add('<path d="M172 108 C181 132 182 160 176 186" fill="none" stroke="#fdefc0" stroke-width="3" opacity=".5"/>')
add('<path d="M130 108 C124 136 124 160 130 184" fill="none" stroke="#181103" stroke-width="4.5" opacity=".55"/>')
add('<path d="M131 142 C149 152 169 152 181 144 L182 184 C164 196 140 194 130 184 Z" fill="#1b1305" opacity=".35" filter="url(#'+P+'_ao)"/>')
for i,(y0,y1) in enumerate([(184,196),(196,208),(208,221)]):
    add(f'<path d="M{130+i} {y0} C148 {y0+11} 168 {y0+11} {182-i} {y0+1} L{182-i} {y1} C168 {y1+10} 148 {y1+10} {131+i} {y1-1} Z" fill="url(#{P}_au2)"/>')
add('<g fill="none" stroke="#130d03" stroke-width="2" opacity=".6"><path d="M130 196 C148 207 168 207 182 197"/><path d="M132 208 C148 219 168 219 181 209"/></g>')
add('<g fill="#f6e3ab" opacity=".6"><circle cx="140" cy="191" r="2"/><circle cx="158" cy="197" r="2"/><circle cx="175" cy="192" r="2"/>'
    '<circle cx="142" cy="204" r="2"/><circle cx="160" cy="210" r="2"/><circle cx="176" cy="204" r="2"/></g>')

# ---------- NEAR LEG ----------
add(f'<path d="{cap(J["nhip"],J["nknee"],40,31)}" fill="url(#{P}_au)"/>')
add(f'<path d="{cap(J["nhip"],J["nknee"],40,31)}" fill="#1b1305" opacity=".0"/>')
add(f'<ellipse cx="162" cy="288" rx="19" ry="14" fill="url(#{P}_au2)"/>')
add('<ellipse cx="164" cy="286" rx="9" ry="6" fill="#f7e3a8" opacity=".35"/>')
add(f'<path d="{cap(J["nknee"],J["nank"],29,21)}" fill="url(#{P}_au)"/>')
add('<path d="M146 348 C138 359 140 372 154 372 L196 372 C206 370 202 358 186 354 L168 344 Z" fill="url(#'+P+'_lt)"/>')
add('<path d="M146 348 C138 359 140 372 154 372 L168 372 L166 346 Z" fill="#120b03" opacity=".45"/>')
add('<path d="M172 356 L192 362" fill="none" stroke="#cfa365" stroke-width="2" opacity=".5"/>')
# leg core shadow (back edge)
add('<path d="M136 216 C132 252 136 292 142 350 L152 350 C148 292 146 252 150 216 Z" fill="#1b1305" opacity=".3" filter="url(#'+P+'_ao2)"/>')

# ---------- PAULDRON ----------
add(f'<path d="M126 96 C146 82 174 88 183 108 C186 122 178 132 165 134 C144 137 128 124 126 108 Z" fill="url(#{P}_au)"/>')
add('<path d="M130 100 C148 88 172 93 180 109" fill="none" stroke="#fdf0c4" stroke-width="3" opacity=".55"/>')
add('<path d="M126 108 C128 124 144 137 165 134 C150 131 134 122 130 106 Z" fill="#120c03" opacity=".42"/>')
add(f'<path d="M131 123 C149 134 169 133 181 123 L182 135 C169 146 148 147 131 136 Z" fill="url(#{P}_au2)"/>')

# ---------- NEAR ARM ----------
add(f'<path d="{cap(J["sh"],J["elb"],32,25)}" fill="url(#{P}_au2)"/>')
add(f'<ellipse cx="168" cy="164" rx="15" ry="12" fill="url(#{P}_au2)"/>')
add(f'<path d="{cap(J["elb"],J["wri"],25,19)}" fill="url(#{P}_au2)"/>')
add('<path d="M160 110 C172 132 176 150 174 162" fill="none" stroke="#f3dda2" stroke-width="2.5" opacity=".38"/>')
add('<path d="M176 172 C186 182 194 192 198 200" fill="none" stroke="#f3dda2" stroke-width="2.5" opacity=".3"/>')
add('<path d="M188 194 C200 190 212 196 214 208 C214 219 204 224 194 222 C186 220 182 210 184 200 Z" fill="url(#'+P+'_au)"/>')
add('<g fill="none" stroke="#120c03" stroke-width="1.8" opacity=".5"><path d="M190 200 L206 208"/><path d="M188 208 L202 216"/></g>')

# ---------- SWORD ----------
add('<path d="M186 214 C192 208 200 204 206 204 L210 214 C204 216 196 220 190 224 Z" fill="url(#'+P+'_lt)"/>')
add('<ellipse cx="185" cy="219" rx="7" ry="6" fill="url(#'+P+'_au2)"/>')
add('<path d="M190 192 C204 176 220 166 232 164 L240 178 C226 182 212 192 200 204 Z" fill="url(#'+P+'_au)"/>')
add('<path d="M210 180 C236 148 260 116 278 90 L288 98 C272 126 250 158 228 192 Z" fill="url(#'+P+'_st)"/>')
add('<path d="M278 90 L288 98 L292 78 Z" fill="url(#'+P+'_st)"/>')
add('<path d="M216 182 C240 150 262 120 281 94" fill="none" stroke="#ffffff" stroke-width="2" opacity=".8"/>')
add('<path d="M228 192 C250 158 272 126 288 98 L291 103 C275 132 253 164 232 196 Z" fill="#1d262b" opacity=".55"/>')

# ---------- HELM ----------
add(f'<path d="{cap((150,84),(152,104),26,32)}" fill="url(#{P}_au3)"/>')
add('<path d="M134 40 C150 28 174 32 183 50 C189 63 187 78 179 86 L150 92 C138 84 131 62 134 40 Z" fill="url(#'+P+'_au)"/>')
add('<path d="M138 42 C152 32 172 35 181 50" fill="none" stroke="#fdf1c6" stroke-width="3" opacity=".6"/>')
add('<path d="M134 40 C131 62 138 84 150 92 L159 90 C149 80 145 60 148 38 Z" fill="#191104" opacity=".35"/>')
add('<path d="M162 59 C172 55 182 56 188 60 L187 68 C179 63 169 63 162 66 Z" fill="#0a0702"/>')
add('<path d="M152 53 C164 48 178 49 185 55 L186 61 C176 56 162 55 151 60 Z" fill="url(#'+P+'_au2)"/>')
add('<path d="M181 50 L195 60 L192 72 L186 82 L176 76 L178 62 Z" fill="url(#'+P+'_au2)"/>')
add('<path d="M183 53 L192 60" fill="none" stroke="#fdf1c6" stroke-width="2" opacity=".5"/>')
add('<path d="M150 72 C162 78 175 78 182 74 L180 90 C167 95 152 91 147 84 Z" fill="url(#'+P+'_au2)"/>')
add('<path d="M153 77 C164 81 174 81 180 78" fill="none" stroke="#120c03" stroke-width="2" opacity=".5"/>')
add('<path d="M146 34 C158 26 174 28 180 38 L176 45 C166 36 155 36 148 42 Z" fill="url(#'+P+'_au2)"/>')

# ---------- PLUME ----------
add('<path d="M156 30 C134 24 106 36 88 60 C110 55 122 59 130 68 C136 52 144 38 158 36 Z" fill="url(#'+P+'_tl)"/>')
add('<path d="M154 32 C132 28 112 40 96 60" fill="none" stroke="#8fecc2" stroke-width="2.5" opacity=".45"/>')
add('<path d="M150 37 C130 36 114 47 102 62" fill="none" stroke="#07231a" stroke-width="2.5" opacity=".5"/>')

# ---------- RIM ----------
add('<g fill="none" stroke="#fff5d6" stroke-opacity=".4" stroke-width="2.6" stroke-linecap="round">'
    '<path d="M183 50 C189 63 187 78 179 86"/>'
    '<path d="M183 108 C186 122 178 132 166 134"/>'
    '<path d="M176 110 C185 130 187 158 182 184"/>'
    '<path d="M178 220 L172 286"/><path d="M174 296 L168 350"/></g>')
add('<g fill="none" stroke="#8ff0c6" stroke-opacity=".2" stroke-width="3" stroke-linecap="round">'
    '<path d="M128 106 C121 138 122 160 128 184"/><path d="M127 206 C120 250 120 296 127 318"/></g>')

pathlib.Path('out_vanguard.svg').write_text(wrap(P, ramps, "\n".join(B)))
print("ok")
