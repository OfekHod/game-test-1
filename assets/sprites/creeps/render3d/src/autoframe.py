"""Fit each creep's cell shape and camera so the sprite fills its frame.

Three problems, solved together:
  * the cameras were set by eye and left ~45% of the cell empty;
  * the figure is not centred on the camera target, so zooming alone clips it;
  * one cell aspect for every creep wastes space - the golem is wide, the
    hexcaster is tall.

Because each hero ships its own files, the cell does not have to be uniform.
This measures each creep's own proportions, picks a cell of the same aspect at
a fixed pixel budget, then iterates camera height and zoom until the worst pose
across all eight facings just fits.
"""
import importlib, pathlib, re, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rt import render
from PIL import Image

CREEPS = ["radiant_vanguard", "radiant_longbowman", "dire_ghoul",
          "dire_hexcaster", "neutral_rock_golem"]
BUDGET = 420000          # pixels per frame, held roughly constant across heroes
TARGET_H, TARGET_W = 0.94, 0.94
PROBES = ((1, 4), (2, 3))

def union_box(mod, name, clip, frames, cw, ch):
    tmp = f"/tmp/_af_{name}.png"
    render(f"af_{name}", mod.BODY, tmp, mod.RIG, mod.CAM, clip=clip, frames=frames,
           dirs=8, dir_base=0, cols=8, cw=cw, ch=ch, SS=1, style=mod.STYLE)
    im = Image.open(tmp).convert("RGBA")
    top, bot, left, right = ch, 0, cw, 0
    for r in range(im.height // ch):
        for c in range(8):
            bb = im.crop((c*cw, r*ch, (c+1)*cw, (r+1)*ch)).split()[3] \
                   .point(lambda v: 255 if v > 40 else 0).getbbox()
            if not bb:
                continue
            left, top = min(left, bb[0]), min(top, bb[1])
            right, bot = max(right, bb[2]), max(bot, bb[3])
    pathlib.Path(tmp).unlink(missing_ok=True)
    (HERE / f"_af_{name}.html").unlink(missing_ok=True)
    return top, bot, left, right

def measure(mod, name, cw, ch):
    top, bot, left, right = ch, 0, cw, 0
    for clip, frames in PROBES:
        t, b, l, r = union_box(mod, name, clip, frames, cw, ch)
        top, bot, left, right = min(top, t), max(bot, b), min(left, l), max(right, r)
    return (bot-top)/ch, (right-left)/cw, (top+bot)/2

def rd(v, m=8):
    return int(round(v/m))*m

def fit(name):
    f = pathlib.Path(f"{name}.py")
    mod = importlib.import_module(name)
    # 1. content aspect at a neutral probe cell
    cw, ch = 128, 160
    hf, wf, _ = measure(mod, name, cw, ch)
    aspect = (wf*(cw/ch))/hf
    CW, CH = rd((BUDGET*aspect)**0.5), rd((BUDGET/aspect)**0.5)
    t = f.read_text()
    t = re.sub(r'\nCELL = \([0-9]+, [0-9]+\)', '', t)
    t = t.replace("CAM = dict(", f"CELL = ({CW}, {CH})\nCAM = dict(")
    f.write_text(t)
    print(f"{name}: content aspect {aspect:.2f} -> cell {CW}x{CH}")
    # 2. iterate camera on that cell shape (probe at 1/4 scale)
    pw, ph = rd(CW/4), rd(CH/4)
    for i in range(5):
        importlib.reload(mod)
        hf, wf, cy = measure(mod, name, pw, ph)
        t = f.read_text()
        fl = float(re.search(r'fl=([0-9.]+)', t).group(1))
        ty = float(re.search(r'target=\(0\.0, ([0-9.]+), 0\.0\)', t).group(1))
        dist = float(re.search(r'dist=([0-9.]+)', t).group(1))
        ty_new = round(ty + ((ph/2)-cy)*((dist/fl)/ph), 4)
        scale = min(TARGET_H/hf, TARGET_W/wf)
        fl_new = round(fl*scale, 4)
        t = re.sub(r'fl=[0-9.]+', f'fl={fl_new}', t)
        t = re.sub(r'target=\(0\.0, [0-9.]+, 0\.0\)', f'target=(0.0, {ty_new}, 0.0)', t)
        f.write_text(t)
        print(f"  pass{i}: fill {hf:.0%}h {wf:.0%}w")
        if abs(scale-1) < 0.025 and abs(ty_new-ty) < 0.004:
            break

if __name__ == "__main__":
    for n in CREEPS:
        fit(n)
