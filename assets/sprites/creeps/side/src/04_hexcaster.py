import sys, pathlib
sys.path.insert(0,'.')
from gen import cap, wrap

# ============================== DIRE HEXCASTER ==============================
P='h'
ramps = dict(
  rb =("#8b79a8","#524466","#2e2540","#100c1c"),
  rb2=("#6a5a86","#3b3054","#211a33","#0a0714"),
  cr =("#d0596f","#93304a","#551528","#210812"),
  bn =("#fdf8de","#d5cca4","#8e8460","#3d3722"),
  wd =("#7d6240","#4c3820","#2a1d0f","#100a05"),
  gn =("#d8ffb0","#8ce85a","#3f9a35","#123c14"),
)
B=[]
def add(s): B.append("    "+s)
# staff
add(f'<path d="{cap((108,46),(126,358),13,11)}" fill="url(#{P}_wd)"/>')
add('<path d="M110 60 C104 74 104 88 108 98" fill="none" stroke="#4c3820" stroke-width="6" stroke-linecap="round"/>')
add('<ellipse cx="109" cy="52" rx="34" ry="38" fill="#7ce85a" opacity=".25" filter="url(#'+P+'_ao)"/>')
add(f'<path d="M108 26 C126 26 136 40 134 56 C132 68 124 74 116 76 L118 90 L94 90 L96 74 C86 70 82 58 84 46 C88 32 96 26 108 26 Z" fill="url(#{P}_bn)"/>')
add('<ellipse cx="100" cy="52" rx="7" ry="8" fill="#141a10"/><ellipse cx="119" cy="52" rx="6" ry="7" fill="#141a10"/>')
add('<ellipse cx="100" cy="52" rx="4" ry="4.5" fill="#b6ff7a"/><ellipse cx="119" cy="52" rx="3.4" ry="4" fill="#b6ff7a"/>')
add('<path d="M100 66 h16 l-2 8 h-12 z" fill="#141a10"/>')
# robe
add(f'<path d="M150 96 C178 100 192 132 198 178 C204 234 210 304 212 350 L84 352 C90 302 100 232 108 178 C114 132 128 100 150 96 Z" fill="url(#{P}_rb)"/>')
add(f'<path d="M150 96 C128 100 114 132 108 178 C100 232 90 302 84 352 L124 352 C126 300 130 230 136 178 C141 132 146 106 158 98 Z" fill="url(#{P}_rb2)"/>')
add('<g fill="none" stroke="#0d0918" stroke-width="4" opacity=".5">'
    '<path d="M140 150 C130 216 122 292 118 344"/><path d="M162 152 C166 218 170 292 172 344"/>'
    '<path d="M150 148 C148 216 146 292 145 344"/><path d="M182 168 C190 232 196 300 199 346"/></g>')
add('<g fill="none" stroke="#a693c9" stroke-width="2.5" opacity=".3">'
    '<path d="M156 150 C158 216 160 292 161 344"/><path d="M174 162 C180 226 186 296 189 344"/></g>')
add(f'<path d="M84 334 C124 346 172 346 212 334 L212 352 L84 352 Z" fill="url(#{P}_cr)"/>')
add(f'<path d="M120 176 C144 190 172 189 190 176 L192 194 C170 208 138 209 118 194 Z" fill="url(#{P}_cr)"/>')
add('<circle cx="154" cy="190" r="9" fill="url(#'+P+'_bn)"/>')
# front arm
add(f'<path d="{cap((156,112),(184,138),30,24)}" fill="url(#{P}_rb)"/>')
add(f'<path d="{cap((184,138),(206,146),24,18)}" fill="url(#{P}_rb2)"/>')
add(f'<path d="M204 138 C216 134 226 140 228 148 C228 158 218 162 208 158 Z" fill="url(#{P}_bn)"/>')
add(f'<g stroke="url(#{P}_bn)" stroke-width="4" stroke-linecap="round" fill="none">'
    '<path d="M224 142 l12 -4"/><path d="M226 149 l14 0"/><path d="M224 156 l12 5"/></g>')
add('<ellipse cx="248" cy="150" rx="30" ry="30" fill="#7ce85a" opacity=".3" filter="url(#'+P+'_ao)"/>')
add('<ellipse cx="248" cy="150" rx="15" ry="15" fill="url(#'+P+'_gn)" opacity=".9"/>')
add('<ellipse cx="246" cy="147" rx="6" ry="6" fill="#f2ffe0"/>')
# hood
add(f'<path d="{cap((150,90),(150,108),24,30)}" fill="url(#{P}_rb2)"/>')
add(f'<path d="M128 44 C148 28 178 36 186 62 C192 82 184 100 172 106 L142 108 C128 98 124 64 128 44 Z" fill="url(#{P}_rb)"/>')
add(f'<path d="M128 44 C124 64 128 98 142 108 L154 106 C140 96 136 64 142 42 Z" fill="#0b0816" opacity=".45"/>')
add('<path d="M114 54 C122 36 144 28 160 34 C142 38 130 50 124 66 Z" fill="url(#'+P+'_rb2)"/>')
add('<path d="M156 60 C172 56 186 62 190 74 C186 90 170 98 156 94 C148 86 148 68 156 60 Z" fill="#080611"/>')
add('<ellipse cx="176" cy="76" rx="13" ry="9" fill="#7ce85a" opacity=".45" filter="url(#'+P+'_ao2)"/>')
add('<ellipse cx="176" cy="76" rx="5.5" ry="4" fill="#e8ffd4"/>')
add('<path d="M134 40 C152 28 174 34 184 52" fill="none" stroke="#b5a3d8" stroke-width="2.5" opacity=".45"/>')
add('<g fill="none" stroke="#c9b6ff" stroke-opacity=".3" stroke-width="2.6" stroke-linecap="round">'
    '<path d="M186 62 C192 82 184 100 172 106"/><path d="M198 178 C204 234 210 304 212 348"/></g>')
pathlib.Path('out_hexcaster.svg').write_text(wrap(P, ramps, "\n".join(B), seed=41, ground=(150,354,86)))

print("hexcaster ok")
