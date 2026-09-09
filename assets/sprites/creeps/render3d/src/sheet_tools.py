"""Slice sprite sheets into frames, emit engine metadata, and build previews."""
import json, pathlib
from PIL import Image

CLIPS = {"idle": 4, "walk": 8, "attack": 6}
DIR_NAMES = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]

def cells(sheet, cw, ch, dirs, frames):
    """sheet[direction][frame] -> Image"""
    return [[sheet.crop((d*cw, f*ch, (d+1)*cw, (f+1)*ch))
             for f in range(frames)] for d in range(dirs)]

def metadata(name, cw, ch, dirs, clips):
    return {
        "name": name,
        "frameWidth": cw, "frameHeight": ch,
        "directions": dirs,
        "directionOrder": DIR_NAMES[:dirs],
        "directionStepDegrees": 360 // dirs,
        "layout": "columns are directions, rows are frames; row 0 is the top",
        "clips": {c: {"frames": n, "sheet": f"{name}_{c}.png"} for c, n in clips.items()},
        "note": ("Direction E is the character facing screen-right (the original "
                 "side profile). Yaw increases clockwise viewed from above. "
                 "Camera elevation is 0.38 rad (~22 degrees)."),
    }

def gif(sheet_path, out_path, cw, ch, dirs, frames, direction=0, ms=110, bg=(24,27,21)):
    sh = Image.open(sheet_path).convert("RGBA")
    col = cells(sh, cw, ch, dirs, frames)[direction]
    flat = []
    for im in col:
        b = Image.new("RGBA", im.size, bg + (255,))
        b.alpha_composite(im)
        flat.append(b.convert("P", palette=Image.ADAPTIVE, colors=128))
    flat[0].save(out_path, save_all=True, append_images=flat[1:],
                 duration=ms, loop=0, disposal=2)

def strip(sheet_path, out_path, cw, ch, dirs, frames, direction=0, bg=(24,27,21)):
    """One row of frames laid out horizontally, for a static preview."""
    sh = Image.open(sheet_path).convert("RGBA")
    col = cells(sh, cw, ch, dirs, frames)[direction]
    out = Image.new("RGBA", (cw*len(col), ch), bg + (255,))
    for i, im in enumerate(col):
        out.alpha_composite(im, (i*cw, 0))
    out.convert("RGB").save(out_path)

def dir_row(sheet_path, out_path, cw, ch, dirs, frames, frame=0, bg=(24,27,21)):
    """All 8 facings at one frame, for checking the direction set."""
    sh = Image.open(sheet_path).convert("RGBA")
    cs = cells(sh, cw, ch, dirs, frames)
    out = Image.new("RGBA", (cw*dirs, ch), bg + (255,))
    for d in range(dirs):
        out.alpha_composite(cs[d][frame], (d*cw, 0))
    out.convert("RGB").save(out_path)
