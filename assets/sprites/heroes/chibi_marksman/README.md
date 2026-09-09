# Chibi Marksman

A hero sprite built to sit next to the game's existing `carry` rather than next
to my creep set. Same renderer as `assets/sprites/creeps/render3d`, restyled:

| | existing carry | creep set | this |
|---|---|---|---|
| Proportions | ~2 heads | ~7 heads | ~2 heads |
| Cell | 92x122 | 576x720 | 92x122 |
| Palette | bone/tan, near-black, gold | faction colours | bone/tan, near-black, gold |
| Camera | high 3/4 | shallow 3/4 | high 3/4 (elev 0.46) |

Palette is sampled from the carry sheet itself (`#b3a790`, `#d3c6b0`, `#736652`,
near-black, plus the gold accent). The one deliberate difference is a teal band
at the back of the helmet, tying it to the Radiant creeps.

## Surface treatment

Texture here is **quantised, not continuous**. `patches()` in `rt.py` steps
noise into a few discrete levels, so surfaces break into hard-edged tonal
blocks that read as painted 2D shapes. Continuous `fbm` grain — and any bump
mapping — reads as real surface roughness instead, which is the opposite of the
intent, so `bAmp` is 0 on every material of this sprite.

Definition comes from modelled geometry rather than surface noise: helmet rim
seam, ear cups, collar, diagonal chest strap and buckle, hip pouch, knee pads,
boot soles, and a sight rail and magazine on the weapon. Geometry survives the
downsample to 92x122; painted detail would not.

Rendering at 4x and downsampling keeps the block edges clean.

Look is tuned per character through the `STYLE` dict in `chibi_marksman.py`,
passed to `render(..., style=STYLE)`:

| Key | Here | Effect |
|---|---|---|
| `shadowTint` | `(0.50,0.432,0.428)` | Colour the cel shadow band leans to. The creep default `(0.44,0.49,0.66)` is cool and reads pale on tan. |
| `lift` | `0.36` | How far the lit band lifts toward white. With the warm shadow this is what gives the high-contrast read. |
| `ink` | `1.45` | Silhouette line strength. |
| `spec` | `0.26` | Stepped specular pop — kept low, a hard specular reads as glossy realism. |
| `contrast` | `1.0` | Extra shadow deepening; not needed once `lift` is up. |

Omitting `style` reproduces the creep look exactly, so the creep sheets are
unaffected by these controls.

## Files

| File | Size | Format |
|---|---|---|
| `chibi_marksman_carry.png` | 736x122 | 1 row x 8 walk frames — the `carry` format |
| `chibi_marksman_dirs8.png` | 736x976 | 8 rows x 8 walk frames — the `support` `dirs:8` format |

## Dropping it in

Both sheets already match `heroSheets` conventions in `index.html`.

Single-facing (mirrored by the engine when facing left):

```js
chibiMarksman: { w:92, h:122, walk:8, atk:0, scale:2.99, foot:0.95 },
```

Eight-facing (never mirrored):

```js
chibiMarksman: { w:92, h:122, walk:8, atk:0, scale:2.99, foot:0.95, dirs:8 },
```

then `loadHeroSheet('chibiMarksman', <url or data URI>)`.

**Row order matters.** `heroDirRow()` computes `a = (90 - facingDeg) mod 360`
and `row = round(a/45)`, so rows run **S, SE, E, NE, N, NW, W, SW** — row 0
faces down, and rows advance counter-clockwise. The `dirs8` sheet is written in
exactly that order, which is *not* the order the creep sheets use.

`foot` is 0.95 because the render places the character's feet at 95% of the
cell height, matching the existing carry.

The carry-format sheet is the **front** view: both goggle lenses read, and the
weapon is held screen-right so the engine's mirror-on-left-facing rule keeps it
on the outside of the turn.

## Rebuilding

```sh
cd ../../creeps/render3d/src
python3 build_chibi.py
```

The model is `chibi_marksman.py` in that directory. Frames render at 4x and are
downsampled, which is sharper than rendering straight to 92x122.
