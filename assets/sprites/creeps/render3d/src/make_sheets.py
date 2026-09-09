"""Render 8-direction animation sprite sheets for every creep.

One sheet per clip. Columns are the 8 facings (camera yaw, 45 degrees apart);
rows are the animation frames. Sheets land in ../sheets/<creep>_<clip>.png
"""
import importlib, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rt import render

CLIPS = [("idle", 0, 4), ("walk", 1, 8), ("attack", 2, 6)]
NAMES = ["radiant_vanguard", "radiant_longbowman", "dire_ghoul",
         "dire_hexcaster", "neutral_rock_golem"]
CW, CH, DIRS, SS = 192, 240, 8, 2

def main(names=NAMES, clips=CLIPS, cw=CW, ch=CH, dirs=DIRS, ss=SS, outdir=None):
    out = pathlib.Path(outdir or (HERE.parent / "sheets"))
    out.mkdir(parents=True, exist_ok=True)
    for n in names:
        m = importlib.import_module(n)
        for clip_name, clip_id, frames in clips:
            render(f"{n}_{clip_name}", m.BODY, str(out / f"{n}_{clip_name}.png"),
                   m.RIG, m.CAM, clip=clip_id, frames=frames, dirs=dirs,
                   cw=cw, ch=ch, SS=ss)

if __name__ == "__main__":
    main()
