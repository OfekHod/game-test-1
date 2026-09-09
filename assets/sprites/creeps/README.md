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

Each ships as an `.svg` source and a `.png` export with a transparent
background. Prefer editing the SVG — it rescales and recolors cleanly for team
variants.

## 3D render set

`render3d/` is not illustration — each creep is a signed-distance-field model
raymarched in a GLSL fragment shader, so the shading is computed rather than
drawn: soft shadows, ambient occlusion, and a bloom pass over the emissive
materials (ember eyes, witchfire, the golem's core).

The look is deliberately **stylised, not photoreal**: flat unnoised albedo,
no bump mapping or procedural surface grain, and smooth-union (`smin`) blending
so parts flow into one another instead of meeting at hard seams. Three knobs
control that, if you want to push it either way:

| Knob | Where | Effect |
|---|---|---|
| `KSM` | `#define` at the top of each creep's `BODY` | Blend radius between parts. Higher = softer, more melted forms. |
| `material()` | each creep script | Flat colour, roughness, metalness. Add `fbm(p*N)` terms back in for surface noise. |
| `bAmp` / `bScale` | `material()` outputs | Bump mapping. Currently `0` — raise `bAmp` for surface relief. |

Lighting lives in `rt.py`: a warm key with soft raymarched shadows, a cool
fill, a back rim, and a hemisphere ambient.

The renderer runs the shader through headless Chromium's WebGL2 (SwiftShader)
and reads the framebuffer back as a PNG — no GPU and no external 3D library
required. The whole set takes about 50 seconds to render.

```sh
cd render3d/src && python3 render_all.py
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
