"""Build human-readable previews from the per-facing sprite sheets."""
import pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sheet_tools as st
from PIL import Image

SHEETS = HERE.parent / "sheets"
PREV = SHEETS / "preview"
NAMES = ["radiant_vanguard", "radiant_longbowman", "dire_ghoul",
         "dire_hexcaster", "neutral_rock_golem"]

def main():
    PREV.mkdir(parents=True, exist_ok=True)
    import importlib
    for n in NAMES:
        CW, CH = importlib.import_module(n).CELL
        d = SHEETS / n
        for clip, (count, cols) in st.CLIPS.items():
            if clip == "idle":
                continue
            st.gif(d/f"{clip}_E.png", PREV/f"{n}_{clip}.gif", CW, CH, count, cols,
                   ms=80 if clip == "walk" else 100, scale=0.34)
        st.strip(d/"walk_E.png", PREV/f"{n}_walk_strip.png", CW, CH, 12, 4, scale=0.22)
        st.dir_row(d, "walk", PREV/f"{n}_directions.png", CW, CH, 12, 4, frame=3, scale=0.30)
        print(f"{n}: previews")
    rows = [Image.open(PREV/f"{n}_directions.png").convert("RGB") for n in NAMES]
    W = max(r.width for r in rows); H = sum(r.height for r in rows)
    out = Image.new("RGB", (W, H), (24, 27, 21)); y = 0
    for r in rows: out.paste(r, (0, y)); y += r.height
    out.save(PREV/"all_directions.png")
    print(f"all_directions.png {out.size}")

if __name__ == "__main__":
    main()
