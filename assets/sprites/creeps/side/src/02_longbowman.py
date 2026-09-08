import sys, pathlib
sys.path.insert(0,'.')
from gen import cap, wrap

# ============================== LONGBOWMAN ==============================
P='l'
ramps = dict(
  lt =("#c79a5e","#8a6435","#4e3418","#1d1207"),
  lt2=("#9d7442","#66471f","#38260e","#150d04"),
  tl =("#6ddcae","#2f9070","#175f47","#07231a"),
  tl2=("#3a9c78","#1c6650","#0d3b2d","#051813"),
  st =("#f6fafc","#c2ced5","#78868e","#2b343a"),
  wd =("#b98b4c","#7d5628","#452d12","#180f05"),
  sk =("#e8c6a0","#b4885f","#6e4d2e","#2a1a0d"),
)
J = dict(sh=(148,104), elb=(178,124), wri=(206,136),
         relb=(150,142), rwri=(166,118),
         nhip=(150,208), nknee=(158,278), nank=(154,346),
         fhip=(138,206), fknee=(124,276), fank=(112,342))
B=[]
def add(s): B.append("    "+s)

add(f'<path d="{cap(J["fhip"],J["fknee"],30,24)}" fill="url(#{P}_tl2)"/>')
add(f'<path d="{cap(J["fknee"],J["fank"],23,16)}" fill="url(#{P}_lt2)"/>')
add('<path d="M100 336 C92 347 94 358 106 358 L140 358 C148 356 144 346 132 342 L118 333 Z" fill="url(#'+P+'_lt2)"/>')
add('<path d="M106 200 C98 248 96 296 100 338 L136 344 C132 296 134 248 142 202 Z" fill="#000" opacity=".35" filter="url(#'+P+'_ao)"/>')
# quiver on back
add('<g transform="rotate(-18 128 150)">'
    f'<path d="M114 118 h30 v74 h-30 z" fill="url(#{P}_lt2)"/>'
    '<path d="M114 130 h30 M114 176 h30" stroke="#2a1a0a" stroke-width="3" fill="none" opacity=".6"/>'
    '<g stroke="#e8dfc6" stroke-width="4"><path d="M120 118 v-24"/><path d="M129 118 v-30"/><path d="M138 118 v-20"/></g>'
    '<g fill="#63dcae"><path d="M120 96 l-6 -10 h12 z"/><path d="M129 90 l-6 -10 h12 z"/><path d="M138 100 l-6 -10 h12 z"/></g>'
    '</g>')
# cloak
add(f'<path d="M130 106 C118 160 116 240 124 306 L158 306 C162 240 162 160 156 106 Z" fill="url(#{P}_tl2)"/>')
add('<path d="M136 112 C128 170 128 246 133 302" fill="none" stroke="#06201a" stroke-width="3.5" opacity=".6"/>')
add('<path d="M148 112 C145 170 145 246 148 302" fill="none" stroke="#7ee6bb" stroke-width="2" opacity=".28"/>')
# near leg
add(f'<path d="{cap(J["nhip"],J["nknee"],34,26)}" fill="url(#{P}_tl)"/>')
add(f'<path d="{cap(J["nknee"],J["nank"],25,18)}" fill="url(#{P}_lt)"/>')
add('<path d="M146 342 C138 353 140 366 154 366 L194 366 C204 364 200 352 184 348 L166 338 Z" fill="url(#'+P+'_lt)"/>')
add('<path d="M146 342 C138 353 140 366 154 366 L166 366 L164 340 Z" fill="#120b03" opacity=".45"/>')
add('<path d="M150 300 C162 302 168 306 170 312" fill="none" stroke="#2a1a0a" stroke-width="3" opacity=".5"/>')
# torso: brigandine
add(f'<path d="M130 104 C144 96 166 98 174 110 C181 128 182 154 177 178 C160 190 140 188 131 178 C124 154 124 126 130 104 Z" fill="url(#{P}_lt)"/>')
add('<g fill="#3a2510" opacity=".55"><path d="M134 118 C150 126 166 126 176 120" stroke="#3a2510" stroke-width="2.5" fill="none"/>'
    '<path d="M133 136 C150 144 166 144 177 138" stroke="#3a2510" stroke-width="2.5" fill="none"/>'
    '<path d="M132 154 C150 162 166 162 177 156" stroke="#3a2510" stroke-width="2.5" fill="none"/></g>')
add('<g fill="#e2c48c" opacity=".5"><circle cx="140" cy="123" r="1.8"/><circle cx="156" cy="127" r="1.8"/><circle cx="170" cy="122" r="1.8"/>'
    '<circle cx="139" cy="141" r="1.8"/><circle cx="156" cy="145" r="1.8"/><circle cx="171" cy="140" r="1.8"/>'
    '<circle cx="139" cy="159" r="1.8"/><circle cx="156" cy="163" r="1.8"/><circle cx="171" cy="158" r="1.8"/></g>')
add('<path d="M132 150 C150 160 168 160 178 152 L177 178 C160 190 140 188 131 178 Z" fill="#1d1207" opacity=".33" filter="url(#'+P+'_ao)"/>')
add(f'<path d="M130 178 C148 190 168 189 178 179 L180 194 C166 205 142 205 129 193 Z" fill="url(#{P}_lt2)"/>')
add('<path d="M170 108 C178 130 179 156 174 178" fill="none" stroke="#f0d3a0" stroke-width="2.5" opacity=".45"/>')
# rear (draw) arm
add(f'<path d="{cap((146,110),J["relb"],26,20)}" fill="url(#{P}_lt2)"/>')
add(f'<path d="{cap(J["relb"],J["rwri"],20,15)}" fill="url(#{P}_lt2)"/>')
add(f'<ellipse cx="166" cy="117" rx="9" ry="8" fill="url(#{P}_sk)"/>')
# hood + head
add(f'<path d="{cap((150,88),(150,106),22,28)}" fill="url(#{P}_tl2)"/>')
add('<path d="M132 46 C150 32 176 38 184 60 C189 76 184 92 174 98 L146 100 C132 88 128 62 132 46 Z" fill="url(#'+P+'_tl)"/>')
add('<path d="M132 46 C128 62 132 88 146 100 L156 98 C144 88 140 62 145 44 Z" fill="#06201a" opacity=".4"/>')
add('<path d="M118 52 C126 36 146 30 160 36 C144 40 132 50 126 64 Z" fill="url(#'+P+'_tl2)"/>')
add('<path d="M152 62 C166 58 180 62 184 72 C180 86 166 94 154 92 C146 86 146 70 152 62 Z" fill="#1a1207"/>')
add(f'<path d="M156 66 C168 62 178 66 181 74 C177 84 166 90 157 88 Z" fill="url(#{P}_sk)" opacity=".85"/>')
add('<ellipse cx="170" cy="73" rx="5" ry="3.4" fill="#141a12"/>')
add('<path d="M136 40 C152 30 172 34 181 50" fill="none" stroke="#8fecc2" stroke-width="2.5" opacity=".45"/>')
# bow + string + arrow
add('<path d="M214 34 C250 96 250 182 214 244 L206 240 C240 180 240 98 206 38 Z" fill="url(#'+P+'_wd)"/>')
add('<path d="M212 40 C244 100 244 178 212 238" fill="none" stroke="#e0b473" stroke-width="2" opacity=".45"/>')
add('<path d="M210 36 L166 119 L210 242" fill="none" stroke="#efe7d0" stroke-width="2.4"/>')
add(f'<path d="M204 128 C214 124 220 130 220 138 C220 148 212 152 204 150 Z" fill="url(#{P}_sk)"/>')
add('<path d="M168 120 L242 130" fill="none" stroke="#2d1d0c" stroke-width="4.5"/>')
add('<path d="M168 120 L242 130" fill="none" stroke="#c9a86e" stroke-width="2.6"/>')
add('<path d="M242 130 L226 122 L228 137 Z" fill="#dff8ec"/>')
add('<g fill="#63dcae"><path d="M172 116 l-8 4 l8 5 z"/></g>')
add('<g fill="none" stroke="#fff5d6" stroke-opacity=".38" stroke-width="2.4" stroke-linecap="round">'
    '<path d="M184 60 C189 76 184 92 174 98"/><path d="M174 110 C181 128 182 154 177 178"/>'
    '<path d="M166 216 L162 278"/></g>')
pathlib.Path('out_longbowman.svg').write_text(wrap(P, ramps, "\n".join(B), seed=23))
print("longbowman ok")
