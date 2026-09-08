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

Two variants of each creep are provided:

- **`./`** — original 3/4 view, stylized flat vector, `256x288`.
- **`./side/`** — side profile, higher detail and realism, `320x400`.

Each ships as an `.svg` source and a `.png` export with a transparent
background. Prefer editing the SVG — it rescales and recolors cleanly for team
variants.

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
- The style is detailed vector illustration, not painted or photoreal art.

## Provenance

Original artwork drawn for this project. No third-party assets and no game art
is used or derived from, so there are no attribution or licensing obligations.
