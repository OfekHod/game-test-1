"""Build the chibi hero sheets in the host game's own conventions.

Two outputs:
  chibi_marksman_carry.png  736x122  - one row of 8 walk frames, front view.
      Matches the `carry` entry's format (no `dirs`), which the engine mirrors
      only when the hero faces left, so the art holds its weapon to the right.
  chibi_marksman_dirs8.png  736x976  - 8 rows of 8 walk frames.
      Matches the `support` entry's `dirs:8` format. heroDirRow() computes
      a = (90 - facingDeg) mod 360 and rows = round(a/45), so row 0 faces DOWN
      and rows advance counter-clockwise: S, SE, E, NE, N, NW, W, SW.

Frames are rendered at 4x and downsampled, which is sharper than rendering
straight to 92x122, and it lets the procedural surface grain survive the
reduction as texture rather than noise.
"""
import importlib, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rt import render
from PIL import Image

CW, CH, SS, UP = 92, 122, 2, 4
FRAMES = 8
OUT = HERE.parent.parent.parent / "heroes" / "chibi_marksman"

# my direction indices, in the order the engine wants its rows
MY = {"E": 0, "SE": 1, "S": 2, "SW": 3, "W": 4, "NW": 5, "N": 6, "NE": 7}
ENGINE_ROWS = ["S", "SE", "E", "NE", "N", "NW", "W", "SW"]

def strip_for(mod, my_dir, tmp):
    """One direction's 8 walk frames, rendered big then downsampled."""
    render(f"chibi_d{my_dir}", mod.BODY, tmp, mod.RIG, mod.CAM, clip=1,
           frames=FRAMES, dirs=1, dir_base=my_dir, cols=FRAMES,
           cw=CW*UP, ch=CH*UP, SS=SS, style=mod.STYLE)
    big = Image.open(tmp).convert("RGBA")
    return big.resize((CW*FRAMES, CH), Image.LANCZOS)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    m = importlib.import_module("chibi_marksman")
    tmp = str(HERE / "_chibi_tmp.png")
    strips = {}
    for name in ENGINE_ROWS:
        strips[name] = strip_for(m, MY[name], tmp)
        print(f"  row {name} done")
    # carry-format: single row, front view - both goggle lenses read, and the
    # weapon sits screen-right to suit the engine's mirror-on-left-facing rule
    strips["S"].save(OUT / "chibi_marksman_carry.png")
    # dirs:8 format: rows in the engine's order
    sheet = Image.new("RGBA", (CW*FRAMES, CH*len(ENGINE_ROWS)), (0, 0, 0, 0))
    for r, name in enumerate(ENGINE_ROWS):
        sheet.alpha_composite(strips[name], (0, r*CH))
    sheet.save(OUT / "chibi_marksman_dirs8.png")
    pathlib.Path(tmp).unlink(missing_ok=True)
    (HERE / "_chibi_d0.html").unlink(missing_ok=True)
    for d in range(8):
        (HERE / f"_chibi_d{d}.html").unlink(missing_ok=True)
    print("carry sheet:", (OUT/'chibi_marksman_carry.png').stat().st_size//1024, "KB")
    print("dirs8 sheet:", (OUT/'chibi_marksman_dirs8.png').stat().st_size//1024, "KB")

if __name__ == "__main__":
    main()
