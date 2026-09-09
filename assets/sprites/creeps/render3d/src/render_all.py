"""Render the single-pose showcase stills, one per creep, at 2x sheet cell size.

Same models, camera, cell aspect and painted style as the sprite sheets, just
one facing and one frame rendered large. For the game-ready animation sheets
use make_sheets.py instead.
"""
import importlib, pathlib, sys, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rt import render
from bloom import bloom

SS, UP = 2, 2
NAMES = ["radiant_vanguard", "radiant_longbowman", "dire_ghoul",
         "dire_hexcaster", "neutral_rock_golem"]

for n in NAMES:
    t0 = time.time()
    m = importlib.import_module(n)
    cw, ch = m.CELL[0]*UP, m.CELL[1]*UP
    raw = HERE.parent / f"{n}_raw.png"
    ok = render(n, m.BODY, str(raw), m.RIG, m.CAM, clip=0, frames=1, dirs=1,
                cols=1, cw=cw, ch=ch, SS=SS, style=m.STYLE)
    if not ok:
        continue
    bloom(str(raw), str(HERE.parent / f"{n}.png"))
    raw.unlink(missing_ok=True)
    (HERE / f"_{n}.html").unlink(missing_ok=True)
    print(f"  -> {n}.png {cw}x{ch} ({time.time()-t0:.0f}s)")
