"""Render 8-direction animation sprite sheets, one file per hero per clip per facing.

Layout rationale: a single sheet holding all 8 facings at this cell size would be
4608px wide, past the 4096 max texture size many GPUs still enforce. Splitting per
facing keeps every file well under that, and keeps each hero's assets together.

Each file packs its clip's frames row-major into a compact grid (see CLIPS).
Existing files are skipped, so an interrupted run can simply be re-run.
"""
import importlib, json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rt import render

# name, clip id, frames, grid columns
CLIPS = [("idle", 0, 4, 2), ("walk", 1, 8, 4), ("attack", 2, 6, 3)]
DIR_NAMES = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
NAMES = ["radiant_vanguard", "radiant_longbowman", "dire_ghoul",
         "dire_hexcaster", "neutral_rock_golem"]
CW, CH, SS = 576, 720, 2
OUT = HERE.parent / "sheets"

def write_json(creep, outdir):
    clips = {}
    for clip, _cid, frames, cols in CLIPS:
        rows = -(-frames // cols)
        clips[clip] = {
            "frames": frames, "cols": cols, "rows": rows,
            "loops": clip != "attack",
            "files": {d: f"{clip}_{d}.png" for d in DIR_NAMES},
        }
    (outdir / f"{creep}.json").write_text(json.dumps({
        "name": creep,
        "frameWidth": CW, "frameHeight": CH,
        "directions": len(DIR_NAMES),
        "directionOrder": DIR_NAMES,
        "directionStepDegrees": 360 // len(DIR_NAMES),
        "layout": ("one PNG per clip per facing; frames packed row-major, "
                   "left-to-right then top-to-bottom, starting at the top-left"),
        "clips": clips,
        "note": ("E faces screen-right (the original side profile); yaw increases "
                 "clockwise viewed from above. Camera elevation 0.38 rad (~22 deg). "
                 "Facings are rendered, not mirrored."),
    }, indent=2) + "\n")

def main(names=NAMES, clips=CLIPS, cw=CW, ch=CH, ss=SS, outroot=None):
    root = pathlib.Path(outroot or OUT)
    for creep in names:
        m = importlib.import_module(creep)
        outdir = root / creep
        outdir.mkdir(parents=True, exist_ok=True)
        for clip, cid, frames, cols in clips:
            for d, dn in enumerate(DIR_NAMES):
                dst = outdir / f"{clip}_{dn}.png"
                if dst.exists():
                    print(f"[skip] {creep}/{clip}_{dn}")
                    continue
                render(f"{creep}_{clip}_{dn}", m.BODY, str(dst), m.RIG, m.CAM,
                       clip=cid, frames=frames, dirs=1, dir_base=d, cols=cols,
                       cw=cw, ch=ch, SS=ss)
        write_json(creep, outdir)
        print(f"=== {creep} complete ===")

if __name__ == "__main__":
    main()
