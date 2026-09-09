"""Render 8-direction animation sprite sheets, one file per hero per clip per facing.

Each hero has its own cell size, fitted to its own proportions by autoframe.py,
so a wide creep (the golem) is not padded into a tall frame. Cells are chosen at
a constant pixel budget, so every hero gets a comparable amount of detail.

A single sheet holding all 8 facings would exceed the 4096 max texture size many
GPUs still enforce, so facings are separate files; frames within a clip are
packed row-major into a compact grid.

Existing files are skipped, so an interrupted run can simply be re-run.
"""
import importlib, json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rt import render

# name, clip id, frames, grid columns
CLIPS = [("idle", 0, 6, 3), ("walk", 1, 12, 4), ("attack", 2, 8, 4)]
DIR_NAMES = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
NAMES = ["radiant_vanguard", "radiant_longbowman", "dire_ghoul",
         "dire_hexcaster", "neutral_rock_golem"]
SS = 2
OUT = HERE.parent / "sheets"

def write_json(creep, outdir, cw, ch):
    clips = {}
    for clip, _cid, frames, cols in CLIPS:
        clips[clip] = {
            "frames": frames, "cols": cols, "rows": -(-frames // cols),
            "loops": clip != "attack",
            "files": {d: f"{clip}_{d}.png" for d in DIR_NAMES},
        }
    (outdir / f"{creep}.json").write_text(json.dumps({
        "name": creep,
        "frameWidth": cw, "frameHeight": ch,
        "directions": len(DIR_NAMES),
        "directionOrder": DIR_NAMES,
        "directionStepDegrees": 360 // len(DIR_NAMES),
        "layout": ("one PNG per clip per facing; frames packed row-major, "
                   "left-to-right then top-to-bottom, from the top-left"),
        "clips": clips,
        "note": ("Cell size is fitted to this creep's own proportions, so it "
                 "differs between heroes. E faces screen-right; yaw increases "
                 "clockwise viewed from above. Camera elevation 0.38 rad. "
                 "Facings are rendered, not mirrored."),
    }, indent=2) + "\n")

def main(names=NAMES, clips=CLIPS, ss=SS, outroot=None):
    root = pathlib.Path(outroot or OUT)
    for creep in names:
        m = importlib.import_module(creep)
        cw, ch = m.CELL
        outdir = root / creep
        outdir.mkdir(parents=True, exist_ok=True)
        for clip, cid, frames, cols in clips:
            for d, dn in enumerate(DIR_NAMES):
                dst = outdir / f"{clip}_{dn}.png"
                if dst.exists():
                    continue
                render(f"{creep}_{clip}_{dn}", m.BODY, str(dst), m.RIG, m.CAM,
                       clip=cid, frames=frames, dirs=1, dir_base=d, cols=cols,
                       cw=cw, ch=ch, SS=ss, style=m.STYLE)
        write_json(creep, outdir, cw, ch)
        print(f"=== {creep} complete ({cw}x{ch}) ===")

if __name__ == "__main__":
    main()
