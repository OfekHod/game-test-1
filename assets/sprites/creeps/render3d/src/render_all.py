"""Render every creep at full resolution, then apply the bloom pass.

Each creep is a signed-distance model raymarched in a GLSL fragment shader.
rt.py runs that shader through headless Chromium's WebGL2 (SwiftShader) and
reads the framebuffer back as a PNG; bloom.py adds the emissive glow.

Finished sprites land in the parent directory as <name>.png.
Requires: numpy, pillow, and the Chromium bundled at CHROME in rt.py.
"""
import pathlib, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bloom import bloom

W, H, SS = 1024, 1280, 3
NAMES = ["radiant_vanguard", "radiant_longbowman", "dire_ghoul",
         "dire_hexcaster", "neutral_rock_golem"]

for n in NAMES:
    t0 = time.time()
    src = (HERE / f"{n}.py").read_text().replace(
        "W=512, H=640, SS=1", f"W={W}, H={H}, SS={SS}")
    tmp = HERE / f"_hi_{n}.py"
    tmp.write_text(src)
    r = subprocess.run([sys.executable, str(tmp)], capture_output=True, text=True, cwd=HERE)
    if r.returncode != 0:
        print(f"{n}: FAILED\n{r.stderr[:500]}")
        tmp.unlink(missing_ok=True)
        continue
    print(r.stdout.strip())
    raw = HERE.parent / f"{n}_raw.png"
    bloom(str(raw), str(HERE.parent / f"{n}.png"))
    raw.unlink(missing_ok=True)
    tmp.unlink(missing_ok=True)
    (HERE / f"_{n}.html").unlink(missing_ok=True)
    print(f"  -> {n}.png  ({time.time()-t0:.0f}s)")
