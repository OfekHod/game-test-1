import sys, pathlib
sys.path.insert(0,'.')
from gen import cap, wrap

# ============================== DIRE GHOUL ==============================
P='g'
ramps = dict(
  fl =("#c3cc9c","#8b9769","#4e5836","#1b2011"),
  fl2=("#8e9a6c","#5c6741","#333b21","#12160b"),
  bn =("#fdf8de","#d5cca4","#8e8460","#3d3722"),
  rs =("#c9a06a","#8a5c34","#4a2c14","#1b1006"),
  hd =("#8a6a40","#54401f","#2c2010","#100b05"),
)
B=[]
def add(s): B.append("    "+s)
# far leg (digitigrade)
add(f'<path d="{cap((122,196),(138,244),30,24)}" fill="url(#{P}_fl2)"/>')
add(f'<path d="{cap((138,244),(114,298),24,17)}" fill="url(#{P}_fl2)"/>')
add(f'<path d="{cap((114,298),(140,332),17,13)}" fill="url(#{P}_fl2)"/>')
add('<path d="M130 326 C138 320 154 324 158 332 C160 340 152 344 140 344 L120 344 C114 340 118 330 130 326 Z" fill="url(#'+P+'_fl2)"/>')
# far arm + cleaver raised behind
add(f'<path d="{cap((154,132),(122,166),26,21)}" fill="url(#{P}_fl2)"/>')
add(f'<path d="{cap((122,166),(104,134),21,16)}" fill="url(#{P}_fl2)"/>')
add(f'<ellipse cx="103" cy="130" rx="11" ry="10" fill="url(#{P}_fl2)"/>')
add('<g transform="rotate(-14 100 120)">'
    f'<path d="M94 132 h14 v-30 h-14 z" fill="url(#{P}_hd)"/>'
    f'<path d="M74 102 h54 l4 -44 C112 50 88 52 70 62 Z" fill="url(#{P}_rs)"/>'
    '<path d="M74 102 h54 l1 -12 h-56 z" fill="#3d2410" opacity=".7"/>'
    '<path d="M78 92 C96 84 116 82 128 88" fill="none" stroke="#f2e3c4" stroke-width="3" opacity=".55"/>'
    '<circle cx="86" cy="72" r="3" fill="#2c1908"/><circle cx="118" cy="66" r="3" fill="#2c1908"/>'
    '</g>')
# spine + spurs (back curve)
add(f'<path d="M160 130 C138 148 124 172 120 200 L140 206 C144 180 154 156 172 140 Z" fill="url(#{P}_fl2)"/>')
add(f'<g fill="url(#{P}_bn)"><path d="M156 126 l-6 -22 l14 12 z"/><path d="M140 142 l-12 -20 l18 8 z"/>'
    '<path d="M128 162 l-16 -14 l18 2 z"/><path d="M121 186 l-18 -8 l17 -4 z"/></g>')
# torso
add(f'<path d="M150 126 C176 122 192 136 194 158 C196 182 186 202 166 210 C144 216 128 208 122 192 C118 168 128 136 150 126 Z" fill="url(#{P}_fl)"/>')
add('<path d="M150 126 C128 136 118 168 122 192 L136 196 C132 170 138 142 158 130 Z" fill="#12160b" opacity=".38"/>')
# ribs
add(f'<g fill="none" stroke="url(#{P}_bn)" stroke-width="6" stroke-linecap="round" opacity=".92">'
    '<path d="M164 140 C178 144 186 152 188 162"/>'
    '<path d="M162 156 C176 160 184 168 186 178"/>'
    '<path d="M158 172 C172 176 180 183 182 192"/></g>')
add('<g fill="none" stroke="#20260f" stroke-width="2" opacity=".5">'
    '<path d="M164 140 C178 144 186 152 188 162"/><path d="M162 156 C176 160 184 168 186 178"/></g>')
# sternum shadow
add('<path d="M150 190 C166 200 182 198 190 188 L188 200 C178 212 158 214 146 204 Z" fill="#12160b" opacity=".4" filter="url(#'+P+'_ao)"/>')
# hide loincloth
add(f'<path d="M126 198 C146 214 172 212 186 200 L190 236 C168 252 138 250 122 234 Z" fill="url(#{P}_hd)"/>')
add('<g fill="none" stroke="#100b05" stroke-width="3" opacity=".6"><path d="M144 212 L140 244"/><path d="M166 214 L166 246"/></g>')
# near leg
add(f'<path d="{cap((134,200),(156,252),36,28)}" fill="url(#{P}_fl)"/>')
add(f'<path d="{cap((156,252),(130,306),28,20)}" fill="url(#{P}_fl)"/>')
add(f'<path d="{cap((130,306),(162,340),20,15)}" fill="url(#{P}_fl)"/>')
add('<path d="M150 332 C160 326 178 330 183 340 C185 348 176 352 162 352 L138 352 C131 348 136 336 150 332 Z" fill="url(#'+P+'_fl)"/>')
add(f'<g stroke="url(#{P}_bn)" stroke-width="5" stroke-linecap="round" fill="none">'
    '<path d="M180 344 l14 6"/><path d="M172 350 l12 8"/><path d="M160 351 l4 10"/></g>')
add(f'<ellipse cx="156" cy="252" rx="15" ry="12" fill="url(#{P}_fl2)"/>')
# near arm + claws
add(f'<path d="{cap((164,136),(186,200),30,23)}" fill="url(#{P}_fl)"/>')
add(f'<path d="{cap((186,200),(194,256),23,17)}" fill="url(#{P}_fl)"/>')
add(f'<ellipse cx="195" cy="260" rx="14" ry="12" fill="url(#{P}_fl)"/>')
add(f'<g stroke="url(#{P}_bn)" stroke-width="6" stroke-linecap="round" fill="none">'
    '<path d="M188 268 C184 282 182 292 184 300"/>'
    '<path d="M196 270 C196 284 196 294 199 302"/>'
    '<path d="M204 266 C208 280 210 290 212 298"/></g>')
add('<path d="M170 146 C182 168 188 186 188 198" fill="none" stroke="#d6e0ae" stroke-width="2.5" opacity=".3"/>')
# head
add(f'<path d="{cap((172,126),(162,136),22,26)}" fill="url(#{P}_fl2)"/>')
add(f'<path d="M170 96 C190 88 214 96 220 114 C224 130 214 142 196 146 C176 148 164 138 164 122 C164 108 166 100 170 96 Z" fill="url(#{P}_fl)"/>')
add('<path d="M170 96 C166 100 164 108 164 122 C164 138 176 148 196 146 C180 140 174 126 176 106 Z" fill="#12160b" opacity=".35"/>')
# jaw + teeth
add(f'<path d="M172 132 C190 142 210 140 220 130 L218 142 C208 154 184 154 172 144 Z" fill="#140f06"/>')
add(f'<g fill="url(#{P}_bn)"><path d="M180 138 l4 10 l5 -10 z"/><path d="M194 142 l4 10 l5 -10 z"/><path d="M208 138 l4 9 l5 -9 z"/>'
    '<path d="M186 134 l4 -9 l5 9 z"/><path d="M202 134 l4 -9 l5 9 z"/></g>')
# horns
add(f'<g fill="url(#{P}_bn)"><path d="M176 92 C170 76 174 62 182 58 C182 74 182 84 186 92 Z"/>'
    '<path d="M202 94 C206 80 216 70 224 70 C218 82 212 90 210 98 Z"/></g>')
# eye
add('<ellipse cx="200" cy="112" rx="13" ry="9" fill="#e8451f" opacity=".5" filter="url(#'+P+'_ao2)"/>')
add('<ellipse cx="200" cy="112" rx="6" ry="4.5" fill="#ffe9a8"/>')
add('<g fill="none" stroke="#dce8b4" stroke-opacity=".4" stroke-width="2.5" stroke-linecap="round">'
    '<path d="M220 114 C224 130 214 142 197 146"/><path d="M194 158 C196 182 186 202 167 210"/>'
    '<path d="M176 214 L182 250"/></g>')
pathlib.Path('out_ghoul.svg').write_text(wrap(P, ramps, "\n".join(B), seed=31, ground=(150,350,80)))
print("ghoul ok")
