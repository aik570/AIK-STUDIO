"""Section backgrounds from the owner's own Hero photo (no third-party images):
  media/bg/peak-gold.webp     monochrome world, gold only where the sun hits the rock (System)
  media/bg/mist-ridges.webp   layered ridges in haze, far = lighter (Contact)
  media/bg/founder-peaks.webp portrait crop of the haze version (Why AIK, until the founder photo arrives)
    python3 tools/make_backgrounds.py ../sources/hero-photo-1672.jpg media/hero4/depth.png"""
import sys, cv2, numpy as np
src, dep = sys.argv[1], sys.argv[2]
im = cv2.imread(src).astype(np.float32) / 255
H, W = im.shape[:2]
d = cv2.resize(cv2.imread(dep), (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
depth, front = d[..., 2], d[..., 1]
lum = (im @ np.array([.114, .587, .299], np.float32))[..., None]
hsv = cv2.cvtColor((im * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
hue, sat, val = hsv[..., 0], hsv[..., 1] / 255, hsv[..., 2] / 255
y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]

def save(name, img, w, h=None, crop=None):
    out = np.clip(img * 255, 0, 255).astype(np.uint8)
    if crop: x0, y0, x1, y1 = crop; out = out[y0:y1, x0:x1]
    hh = h or round(out.shape[0] * w / out.shape[1])
    out = cv2.resize(out, (w, hh), interpolation=cv2.INTER_AREA if w < out.shape[1] else cv2.INTER_LANCZOS4)
    cv2.imwrite(f'media/bg/{name}.webp', out, [cv2.IMWRITE_WEBP_QUALITY, 80])
    print(name, out.shape)

# 1) gold on monochrome: warm, lit pixels keep their colour (pushed to gold), the rest goes grey
warm = ((hue > 5) & (hue < 28)).astype(np.float32) * np.clip((sat - .18) / .25, 0, 1) * np.clip((val - .38) / .25, 0, 1)
warm = cv2.GaussianBlur(warm, (0, 0), 2)[..., None]
grey = np.repeat(lum, 3, 2)
grey = np.clip((grey - .04) * 1.12, 0, 1) ** 1.1
gold = np.clip(lum * np.array([.42, .78, 1.22], np.float32) * 1.25, 0, 1)        # BGR: amber
g1 = grey * (1 - warm * .9) + gold * warm * .9
g1 *= (.55 + .45 * np.clip(y * 1.6, 0, 1))                                         # darker sky
save('peak-gold', g1, 1600)

# 2) haze: far things fade into a soft grey, near ridges stay crisp; dark at the top for the page
fog = np.clip((1 - depth) * 1.15 - .05, 0, 1)[..., None]
fog = fog * (1 - front[..., None] * .55)
fogc = (.30 + .30 * y)                                                             # sky grey, lighter towards the horizon
g2 = np.repeat(np.clip(lum * 1.08, 0, 1) ** 1.15, 3, 2)
g2 = g2 * (1 - fog * .8) + fogc * fog * .8
g2 *= (.45 + .55 * np.clip(y * 1.4, 0, 1))
save('mist-ridges', g2, 1920)
save('founder-peaks', g2, 900, 1100, crop=(560, 120, 560 + 600, 120 + 733))
