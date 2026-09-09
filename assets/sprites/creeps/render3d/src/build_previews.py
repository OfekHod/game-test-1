"""Emit per-creep sheet metadata and human-readable previews."""
import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sheet_tools as st
from PIL import Image

SHEETS = HERE.parent / "sheets"
PREV = SHEETS / "preview"
CW, CH, DIRS = 192, 240, 8
NAMES = ["radiant_vanguard", "radiant_longbowman", "dire_ghoul",
         "dire_hexcaster", "neutral_rock_golem"]

def main():
    PREV.mkdir(parents=True, exist_ok=True)
    for n in NAMES:
        (SHEETS / f"{n}.json").write_text(
            json.dumps(st.metadata(n, CW, CH, DIRS, st.CLIPS), indent=2) + "\n")
        st.gif(SHEETS/f"{n}_walk.png", PREV/f"{n}_walk.gif", CW, CH, DIRS, 8, direction=0)
        st.gif(SHEETS/f"{n}_attack.png", PREV/f"{n}_attack.gif", CW, CH, DIRS, 6, direction=0, ms=130)
        st.strip(SHEETS/f"{n}_walk.png", PREV/f"{n}_walk_strip.png", CW, CH, DIRS, 8)
        st.dir_row(SHEETS/f"{n}_walk.png", PREV/f"{n}_directions.png", CW, CH, DIRS, 8, frame=2)
        print(f"{n}: json + previews")

    rows = [Image.open(PREV/f"{n}_directions.png").convert("RGB") for n in NAMES]
    W = max(r.width for r in rows); H = sum(r.height for r in rows)
    out = Image.new("RGB", (W, H), (24, 27, 21)); y = 0
    for r in rows: out.paste(r, (0, y)); y += r.height
    out.save(PREV/"all_directions.png")
    print(f"all_directions.png {out.size}")

if __name__ == "__main__":
    main()
