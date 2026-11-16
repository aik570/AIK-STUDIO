#!/usr/bin/env bash
# Builds aik-site/media/flight/ from the approved Higgsfield sources.
#   bash build-flight-media.sh <out-dir>
# Needs network access to the Higgsfield CDN, ffmpeg and python3 with Pillow.
#
# Sources (Higgsfield job ids), in playback order:
#   3c2b9415  mountain plate without the eagle (edit of e609c256 frame 0)  2688x1520 still
#   5d3e7cb1  the eagle flies in: plate -> e609c256 frame 60             1920x1080, 24 fps
#   e609c256  approved eagle shot, played from frame 61                  2560x1440, 24 fps
#   ec0a76e8  the eagle recedes into the valley, frames 0-150            2560x1440, 24 fps
#   7a2bc872  settle: ec0a76e8 frame 150 -> Hero (e10dc4a5)              2560x1440, 24 fps
#   e10dc4a5  approved Hero image                                         3840x2160 still
#   9f97bbe7  9:16 extension of e10dc4a5 (sky above, clouds below)        1520x2688 still
#
# The portrait Hero is the extension with the original e10dc4a5 pixels pasted
# back over its middle (feathered 56 px), so letters and mountains are the
# approved image, not a re-render. flight.json records where that original
# frame sits ("inner"), which lines the film's last frame up with it.
#
# Replacing the eagle: change the clips in the "film" list below (or the files
# they point to). Durations and sizes are read from the videos at runtime.
#
# Videos are remuxed, never re-encoded (bit-identical picture, audio dropped).
set -euo pipefail
OUT=${1:-flight}
B=https://d8j0ntlcm91z4.cloudfront.net/user_3K31NSDIHA0gXz2VXZIk09GnTID
mkdir -p "$OUT" src

get() { [ -s "src/$1" ] || curl -sfo "src/$1" "$B/$2"; }
get plate.png  hf_20261018_080744_3c2b9415-ab8e-44e0-be9b-44ba968c2a44.png
get entry.mp4  hf_20261018_082216_5d3e7cb1-c298-4a9d-91b7-07c2b3d40b54.mp4
get eagle.mp4  hf_20261014_133222_e609c256-df27-41c5-b343-eb7c17a69c6f.mp4
get dive.mp4   hf_20261018_070603_ec0a76e8-92c2-47e3-81b9-d23abadeccff.mp4
get settle.mp4 hf_20261018_080746_7a2bc872-33de-47a8-a112-b8b28b7546c7.mp4
get env.png    hf_20261017_124624_e10dc4a5-025c-4503-bebd-ef7d81e376e3.png
get portrait.png hf_20261020_071902_9f97bbe7-f893-4ae7-b316-9732fa0b1674.png

for f in entry eagle dive settle; do
  ffmpeg -v error -y -i "src/$f.mp4" -map 0:v:0 -c copy -movflags +faststart "$OUT/$f.mp4"
done

ffmpeg -v error -y -sseof -0.05 -i src/settle.mp4 -frames:v 1 src/hero.png
ffmpeg -v error -y -i src/dive.mp4   -vf "select=eq(n\,186)" -vsync 0 -frames:v 1 src/fog-near.png
ffmpeg -v error -y -i src/settle.mp4 -vf "select=eq(n\,66)"  -vsync 0 -frames:v 1 src/fog-far.png

python3 - "$OUT" <<'EOF'
import json, sys
from PIL import Image, ImageFilter
out = sys.argv[1]
Image.open('src/plate.png').convert('RGB').resize((2560, 1440), Image.LANCZOS).save(f'{out}/plate.webp', quality=88, method=6)
Image.open('src/hero.png').convert('RGB').save(f'{out}/hero.webp', quality=88, method=6)

# Portrait Hero: original pixels over the extension (placement found by matching).
import numpy as np
P = Image.open('src/portrait.png').convert('RGB'); E = Image.open('src/env.png').convert('RGB')
pw, ph = P.size                                   # 1520 x 2688
w, h, xo, y = 1580, 888, 4, 916                   # e10dc4a5 scaled to w x h, shifted left by xo, at y
Es = E.resize((w, h), Image.LANCZOS).crop((xo, 0, xo + pw, h))
m = np.full((h, pw), 255.0); f = 56
for i in range(f):
    a = (i + 1) / f; a = a * a * (3 - 2 * a); m[i, :] = 255 * a; m[h - 1 - i, :] = 255 * a
P.paste(Es, (0, y), Image.fromarray(m.astype(np.uint8)))
P.save(f'{out}/hero-portrait.webp', quality=88, method=6)
inner = [round(-xo / pw, 5), round(y / ph, 5), round((w - xo) / pw, 5), round((y + h) / ph, 5)]
Image.open('src/fog-near.png').convert('RGB').resize((1600, 900), Image.LANCZOS) \
    .filter(ImageFilter.GaussianBlur(8)).save(f'{out}/fog-near.webp', quality=80, method=6)
Image.open('src/fog-far.png').convert('RGB').resize((1600, 900), Image.LANCZOS) \
    .filter(ImageFilter.GaussianBlur(4)).save(f'{out}/fog-far.webp', quality=80, method=6)
F = 1 / 24
json.dump({
  "intro": "intro/aik-logo-intro.mp4",
  "plate": "flight/plate.webp",
  "hero": "flight/hero.webp",
  "heroPortrait": {"src": "flight/hero-portrait.webp", "inner": inner},
  "studio": {"x": 0.372, "y": 0.535, "size": 0.0405},
  "film": [
    {"src": "flight/entry.mp4"},
    {"src": "flight/eagle.mp4", "from": round(61 * F, 4)},
    {"src": "flight/dive.mp4", "from": round(F, 4), "to": round(150 * F, 4), "rate": 1.33},
    {"src": "flight/settle.mp4", "from": round(F, 4), "framing": "hero", "titleBeforeEnd": 2.0}
  ]
}, open(f'{out}/flight.json', 'w'), indent=2)
EOF
du -sh "$OUT"/*
