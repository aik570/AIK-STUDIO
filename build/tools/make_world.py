"""The world behind the page: every section stands in its own scene of the same mountains.
All images are AIK's own (earlier Hero frames and the eagle flight), graded to one palette:
graphite shadows, cold mid-tones, warm light on the horizon.

    python3 tools/make_world.py <old-assets-dir>

<old-assets-dir> holds bg-dusk, bg-spires, bg-walls, s-clouds, s-peaks, s-dawn, hero-plate (.webp),
restored from the first commit of this repository. Writes media/world/* and media/stills/*."""
import os, sys
import cv2, numpy as np

SRC = sys.argv[1]
os.makedirs('media/world', exist_ok=True)
os.makedirs('media/stills', exist_ok=True)


def grade(im, dark=1.0):
    """Cold steel: less colour, blue-grey mid-tones, the warm light kept only as a faint glow."""
    f = im.astype(np.float32) / 255
    lum = f @ np.array([.114, .587, .299], np.float32)
    f = f * .62 + lum[..., None] * .38                                   # much less colour
    steel = lum[..., None] * np.array([1.12, 1.0, .9], np.float32)       # BGR: blue-grey
    f = f * .6 + steel * .4
    shadow = np.clip(1 - lum * 2.2, 0, 1)[..., None]
    f = f + shadow * np.array([.03, .012, -.004], np.float32)           # cold shadows
    f = np.clip(f * dark, 0, 1) ** 1.04
    return (f * 255).astype(np.uint8)


def save(path, im, w, h=None, q=74):
    hh = h or round(im.shape[0] * w / im.shape[1])
    interp = cv2.INTER_AREA if w < im.shape[1] else cv2.INTER_LANCZOS4
    r = cv2.resize(im, (w, hh), interpolation=interp)
    soft = cv2.GaussianBlur(r, (0, 0), 1.1)
    r = cv2.addWeighted(r, 1.55, soft, -.55, 0)                         # the frames are soft: a careful unsharp mask
    cv2.imwrite(path, r, [cv2.IMWRITE_WEBP_QUALITY, q])


scenes = {
    'dusk': ('bg-dusk.webp', None),
    'spires': ('bg-spires.webp', None),
    'walls': ('bg-walls.webp', None),
    'clouds': ('s-clouds.webp', None),
    'peaks': ('s-peaks.webp', None),
    'dawn': ('s-dawn.webp', (560, 0, 2400, 1371)),                       # the left edge still shows an old glass letter
    'eagle': ('hero-plate.webp', None),
}
for name, (f, crop) in scenes.items():
    im = cv2.imread(os.path.join(SRC, f))
    if crop: x0, y0, x1, y1 = crop; im = im[y0:y1, x0:x1]
    im = grade(im)
    for w in (1280, 1920):
        save(f'media/world/{name}-{w}.webp', im, w)
    print('scene', name, im.shape[1], 'x', im.shape[0])

# tall stills from the flight (540 x 960): cards and the stations of the path
for n in (1, 12, 60, 96, 108, 132):
    im = cv2.imread(f'media/flight2/frames-portrait/f{n:03d}.webp')
    save(f'media/stills/f{n:03d}.webp', grade(im), 540, 960, q=80)
    print('still', n)
