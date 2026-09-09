# Creep sprites

Five 2D enemy creep sprites in a Dota-inspired style: two Radiant, two Dire, one
neutral camp unit.

| File | Role | Notes |
| --- | --- | --- |
| `radiant_vanguard` | Radiant melee | Gold plate, teal cloth, tower shield |
| `radiant_longbowman` | Radiant ranged | Hooded archer, drawn bow |
| `dire_ghoul` | Dire melee | Hunched undead, rusted cleaver |
| `dire_hexcaster` | Dire ranged | Robed caster, skull staff |
| `neutral_rock_golem` | Neutral camp | Stone brute with glowing core |

Three variants of each creep are provided, in increasing order of realism:

- **`./`** — 3/4 view, stylized flat vector, `256x288`.
- **`./side/`** — side profile, detailed vector illustration, `320x400`.
- **`./render3d/`** — side profile, stylised 3D render, `1024x1280`.
- **`./render3d/sheets/`** — cel-shaded **8-direction animation sprite sheets**, `576x720` per frame.

Each ships as an `.svg` source and a `.png` export with a transparent
background. Prefer editing the SVG — it rescales and recolors cleanly for team
variants.

## Animation sprite sheets

`render3d/sheets/` holds the game-ready sprites: painted 2D look, 8 facings,
three clips each.

| Clip | Frames | Grid | Loops |
|---|---|---|---|
| `idle` | 6 | 3x2 | yes |
| `walk` | 12 | 4x3 | yes |
| `attack` | 8 | 4x2 | no |

**One file per hero per clip per facing**, at
`sheets/<creep>/<clip>_<DIR>.png` — e.g. `sheets/dire_ghoul/walk_SE.png`.
Frames pack row-major from the top-left, so frame *i* sits at
`(i % cols * frameW, i / cols * frameH)`.

### Cell size is per hero

| Hero | Cell | Why |
|---|---|---|
| `radiant_vanguard` | 648x648 | upright, sword out to the side |
| `radiant_longbowman` | 664x632 | drawn bow is wider than he is tall |
| `dire_ghoul` | 568x736 | hunched but tall, arm raised |
| `dire_hexcaster` | 568x744 | tallest, staff overhead |
| `neutral_rock_golem` | 712x592 | squat and wide |

A single cell shape for everyone wasted a lot of frame: the creeps filled only
**54%** of their cell height, and the golem is wide where the hexcaster is tall.
Because each hero ships its own files there is no reason to share a cell, so
`autoframe.py` measures each creep's own proportions, picks a cell of matching
aspect at a constant pixel budget, then iterates camera height and zoom until
the worst pose across all eight facings just fits. They now fill ~94% in both
axes — roughly three times the pixels on the character, before any change in
sheet size.

Re-run it after changing a model or a pose:

```sh
python3 autoframe.py      # refits CELL, fl and target in each creep script
```

Splitting per facing also keeps every file under the **4096 max texture size**
many GPUs still enforce; all eight facings in one sheet would not.

**Direction order** is `E, SE, S, SW, W, NW, N, NE`. `E` faces screen-right,
yaw increases clockwise viewed from above, camera elevation 0.38 rad (~22 deg).
Facings are **rendered, not mirrored**, so asymmetric details stay put.

Each hero folder carries a `<creep>.json` with its own cell size and clip
table. Previews are in `sheets/preview/`.

```sh
python3 make_sheets.py      # render every sheet (~1 h; skips existing files)
python3 build_previews.py   # GIFs, strips, facing rows
```

### Painted look

Shading matches `assets/sprites/heroes/chibi_marksman`: quantised `patches()`
tonal blocks rather than continuous grain, no bump mapping, a warm shadow tint
and a lifted highlight band. Continuous noise and bump both read as real
surface roughness, which fights a flat 2D style. Per-hero controls live in each
script's `STYLE` dict; see the chibi's README for what each knob does.

### How the animation works

There is no skeleton and no keyframes. The models are signed-distance fields,
so the rig animates by **warping the space** the field is evaluated in, in
`rig()` in `rt.py`: rotate the region below the hip to swing the legs, the
region beyond `uArmZ` in |z| to swing the arms, and the region above the hip to
lean the torso. `sign(p.z)` picks near limb vs far limb, which is what makes the
legs counter-swing.

Three constraints matter if you edit it:

- **The leg hinge is a hard cut at the hip plane**, not a smooth falloff. A
  varying rotation angle shears space and breaks the distance field's Lipschitz
  bound, which tears the legs into streaks while marching. A hard cut keeps the
  transform rigid below the pivot, so the field stays valid.
- **`uLip` scales returned distances** (0.85 idle / 0.45 walk / 0.35 attack) to
  compensate for the shear the arm and torso warps still introduce.
- **Robed figures set `legAmp=0`** in their `RIG` dict; the hip cut splits any
  hem that crosses it.

## 3D render set

`render3d/` is not illustration — each creep is a signed-distance-field model
raymarched in a GLSL fragment shader, so the shading is computed rather than
drawn: soft shadows, ambient occlusion, and a bloom pass over the emissive
materials (ember eyes, witchfire, the golem's core).

The look is deliberately **flat and 2D-facing**, not photoreal. Lighting is
quantised into cel bands rather than a continuous ramp, with a single stepped
specular pop, a cool rim, and an ink line along the silhouette. On top of that:
flat unnoised albedo, no bump mapping or procedural grain, and smooth-union
(`smin`) blending so parts flow together instead of meeting at hard seams.

Lights are **camera-relative** — they orbit with the yaw — so every one of the
eight facings is lit identically and reads equally well on screen.

Knobs, if you want to push it either way:

| Knob | Where | Effect |
|---|---|---|
| `KSM` | `#define` at the top of each creep's `BODY` | Blend radius between parts. Higher = softer, more melted forms. |
| `material()` | each creep script | Flat colour, roughness, metalness. Add `fbm(p*N)` terms back in for surface noise. |
| `bAmp` / `bScale` | `material()` outputs | Bump mapping. Currently `0` — raise `bAmp` for surface relief. |

The cel ramp itself is `toon()` in `rt.py` — three bands with narrow smoothstep
transitions, so edges stay antialiased instead of stair-stepping.

The renderer runs the shader through headless Chromium's WebGL2 (SwiftShader)
and reads the framebuffer back as a PNG — no GPU and no external 3D library
required. The whole set takes about 50 seconds to render.

```sh
cd render3d/src && python3 render_all.py   # single-pose stills
```

`render3d/src/rt.py` is the renderer (shader scaffolding, camera, lighting,
raymarch loop); each `render3d/src/<creep>.py` supplies just that creep's
`map()` distance function and `material()`. Models are built from tapered
capsules, ellipsoids and rounded boxes placed on the same joint skeletons used
by the vector sets, so a pose change is a coordinate edit.

Requires `numpy` and `pillow` (`pip install numpy pillow`).

Camera is a near-orthographic side profile facing right. Sprites have a
transparent background and, unlike the vector sets, **no baked contact
shadow** — the shading is lit from the scene, so add your own ground shadow.

## Side-view set

The `side/` sprites are drawn in true profile facing right at roughly 7.3 head
proportions, with layered form shading, ambient occlusion at the joints, and an
`feTurbulence` grain overlay for surface texture.

They are generated from Python rather than hand-edited. Regenerate with:

```sh
./side/src/build.sh
```

`side/src/gen.py` holds the shared scaffolding (tapered-capsule limb helper,
gradient ramps, grain and blur filters); each `side/src/0*.py` builds one creep
from a named joint skeleton. Edit the joint coordinates there to repose a
figure rather than moving path data by hand.

## Style conventions

- 3/4 view, small heads on heavy shoulders.
- Faction color coding: Radiant warm gold/teal, Dire cold purple-green with red
  or green eye glow.
- Warm rim light from the upper left.
- Silhouettes stay readable at wave size: melee wide and grounded, ranged
  narrow with a tall prop.

## Known limitations

- Contact shadows are baked into each sprite. Strip them if the engine casts its
  own shadows.
- Single idle pose only — no walk, attack, or death frames yet.
- Side-view sprites face right only; mirror horizontally for the other facing.
- The vector sets are illustration, not painted or photoreal art.
- The 3D set is modelled from primitives, so forms are chunky and rounded; it is
  a stylised render, not a sculpted character asset.

## Provenance

Original artwork drawn for this project. No third-party assets and no game art
is used or derived from, so there are no attribution or licensing obligations.
