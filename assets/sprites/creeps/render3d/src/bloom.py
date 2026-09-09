import numpy as np
from PIL import Image, ImageFilter

def bloom(src, dst, thresh=0.70, radius=16, strength=0.80):
    im = Image.open(src).convert("RGBA")
    arr = np.asarray(im).astype(np.float32) / 255.0
    rgb, a = arr[..., :3], arr[..., 3:4]
    bright = np.clip((rgb - thresh) / (1.0 - thresh), 0.0, 1.0) * a
    bi = Image.fromarray((bright * 255).astype(np.uint8))
    blur = np.asarray(bi.filter(ImageFilter.GaussianBlur(radius))).astype(np.float32) / 255.0
    out = np.clip(rgb + strength * blur, 0.0, 1.0)
    # let the glow bleed a little past the silhouette
    glow = blur.max(axis=2, keepdims=True)
    newa = np.clip(np.maximum(a, glow * 1.5), 0.0, 1.0)
    res = np.concatenate([out, newa], axis=2)
    Image.fromarray((res * 255).astype(np.uint8)).save(dst)
