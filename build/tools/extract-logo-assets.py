"""Derives the header lockup from the approved logo animation.

    python3 extract-logo-assets.py <aik-logo-intro.mp4> <out-dir>

Nothing is redrawn: the file is pixels of the animation's frame 96 (3.2 s,
STUDIO complete, before the flare), keyed off the flat rgb(29 33 37) ground.
  aik-lockup.png          symbol + rule + STUDIO with a luminance alpha, 180 px tall
"""
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

src, out = sys.argv[1], sys.argv[2].rstrip('/') + '/'
with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', r'select=eq(n\,96)',
                    '-vsync', '0', '-frames:v', '1', tmp.name], check=True)
    a = np.asarray(Image.open(tmp.name).convert('RGB')).astype(np.float32)

bg = np.array([29, 33, 37], np.float32)
k = np.clip((a - bg) / (255 - bg), 0, 1)
k = np.clip((k - 0.015) / (1 - 0.015), 0, 1)        # drop the ground's faint grain

crop = k[250:825, 405:1665]
alpha = np.clip(crop.max(axis=2) * 1.15, 0, 1)
rgb = np.where(alpha[..., None] > 0, np.clip(crop / np.maximum(alpha[..., None], 1e-4), 0, 1), 0)
im = Image.fromarray(np.dstack([rgb * 255, alpha * 255]).round().astype(np.uint8), 'RGBA')
h = 180
im.resize((round(im.width * h / im.height), h), Image.LANCZOS).save(out + 'aik-lockup.png', optimize=True)
