"""Slice the per-facing sprite sheets into frames and build previews."""
import pathlib
from PIL import Image

DIR_NAMES = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
CLIPS = {"idle": (6, 3), "walk": (12, 4), "attack": (8, 4)}   # frames, cols

def frames(path, cw, ch, count, cols):
    """Frames of one clip/facing sheet, in playback order."""
    sh = Image.open(path).convert("RGBA")
    out = []
    for i in range(count):
        r, c = divmod(i, cols)
        out.append(sh.crop((c*cw, r*ch, (c+1)*cw, (r+1)*ch)))
    return out

def gif(path, out_path, cw, ch, count, cols, ms=110, bg=(24, 27, 21), scale=0.5):
    fs = frames(path, cw, ch, count, cols)
    flat = []
    for im in fs:
        b = Image.new("RGBA", im.size, bg + (255,))
        b.alpha_composite(im)
        if scale != 1:
            b = b.resize((int(b.width*scale), int(b.height*scale)), Image.LANCZOS)
        flat.append(b.convert("P", palette=Image.ADAPTIVE, colors=128))
    flat[0].save(out_path, save_all=True, append_images=flat[1:],
                 duration=ms, loop=0, disposal=2)

def strip(path, out_path, cw, ch, count, cols, bg=(24, 27, 21), scale=0.35):
    fs = frames(path, cw, ch, count, cols)
    w, h = int(cw*scale), int(ch*scale)
    out = Image.new("RGBA", (w*len(fs), h), bg + (255,))
    for i, im in enumerate(fs):
        out.alpha_composite(im.resize((w, h), Image.LANCZOS), (i*w, 0))
    return out.convert("RGB").save(out_path)

def dir_row(sheet_dir, clip, out_path, cw, ch, count, cols, frame=2,
            bg=(24, 27, 21), scale=0.35):
    """All 8 facings at one frame, read from the eight per-facing files."""
    w, h = int(cw*scale), int(ch*scale)
    out = Image.new("RGBA", (w*len(DIR_NAMES), h), bg + (255,))
    for i, d in enumerate(DIR_NAMES):
        p = pathlib.Path(sheet_dir) / f"{clip}_{d}.png"
        im = frames(p, cw, ch, count, cols)[frame % count]
        out.alpha_composite(im.resize((w, h), Image.LANCZOS), (i*w, 0))
    return out.convert("RGB").save(out_path)
