"""Build the Hero 4 media from one clean landscape photo (no letters, no eagle).

  python3 tools/hero_plate.py <photo> <ridge.json> [out_dir=media/hero4]

ridge.json: {"w": <width the points were measured on>, "pts": [[x, y], ...]} - the skyline of
everything that stands in front of the glass AIK (peaks, near clouds), left to right.
For a new photo: trace its skyline, run this, done. The glass letters themselves come from
media/hero/aik-glass-mark.webp and are drawn in WebGL (js/hero4.js).

Writes
  plate-{1280,1920,2880,3840}.webp   the photo
  plate-portrait-{900,1400}.webp     a 9:16 crop around --focus for phones
  depth.png                          R = depth (0 far .. 1 near), G = front mask (in front of the glass)
  glass.png                          R = letter shape, G = soft height (for the refraction normal), B = facet light
"""
import json, os, sys
import cv2, numpy as np

src, ridge_p = sys.argv[1], sys.argv[2]
out = sys.argv[3] if len(sys.argv) > 3 else 'media/hero4'
FOCUS_X = float(os.environ.get('FOCUS_X', '0.40'))   # where the phone crop is centred (fraction of width)
os.makedirs(out, exist_ok=True)

im = cv2.imread(src, cv2.IMREAD_COLOR)
H, W = im.shape[:2]
R = json.load(open(ridge_p)); k = W / R['w']
pts = (np.array(R['pts'], np.float32) * k)

def webp(path, img, q=86):
    soft = cv2.GaussianBlur(img, (0, 0), 1.0)
    img = cv2.addWeighted(img, 1.5, soft, -.5, 0)                       # a careful unsharp mask: the source is soft
    cv2.imwrite(path, img, [cv2.IMWRITE_WEBP_QUALITY, q])

sizes = [w for w in (1280, 1920, 2880, 3840) if w <= max(W, 1920)]
for w in (1280, 1920, 2880, 3840):
    f = f'{out}/plate-{w}.webp'
    if w not in sizes:
        if os.path.exists(f): os.remove(f)                      # stale file from a bigger source
        continue
    h = round(H * w / W)
    r = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA if w <= W else cv2.INTER_LANCZOS4)
    webp(f, r, 84 if w > 2000 else 88)

# phones: 9:16 crop, full height, centred on the main peak
cw = round(H * 9 / 16); cx = int(np.clip(FOCUS_X * W - cw / 2, 0, W - cw))
crop = im[:, cx:cx + cw]
for w in (900, 1400):
    webp(f'{out}/plate-portrait-{w}.webp', cv2.resize(crop, (w, round(w * 16 / 9)), interpolation=cv2.INTER_AREA), 84)
json.dump({'portrait_x0': cx / W, 'portrait_w': cw / W, 'aspect': W / H, 'sizes': sizes}, open(f'{out}/plate.json', 'w'))

# depth + front mask, at 1920 px
dw = 1920; dh = round(H * dw / W); s = dw / W
front = np.zeros((dh, dw), np.uint8)
poly = np.vstack([pts * s, [[dw, pts[-1, 1] * s], [dw, dh], [0, dh], [0, pts[0, 1] * s]]])
cv2.fillPoly(front, [np.int32(poly)], 255, lineType=cv2.LINE_AA)
frontf = front.astype(np.float32) / 255
y = np.linspace(0, 1, dh, dtype=np.float32)[:, None] * np.ones((1, dw), np.float32)
# the ridge height at each column, to grade the near layer from the ridge down to the bottom
ridge_y = np.interp(np.arange(dw), np.r_[0, pts[:, 0] * s, dw], np.r_[pts[0, 1], pts[:, 1], pts[-1, 1]] * s) / dh
near = np.clip((y - ridge_y[None, :]) / np.maximum(1 - ridge_y[None, :], 1e-3), 0, 1)
depth = (.12 + .2 * y) * (1 - frontf) + (.55 + .45 * near) * frontf
depth = cv2.GaussianBlur(depth, (0, 0), 3)
d = np.dstack([np.zeros_like(depth), cv2.GaussianBlur(frontf, (0, 0), .8), depth])   # BGR
cv2.imwrite(f'{out}/depth.png', np.clip(d * 255, 0, 255).astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 9])

# glass letters A, I, K from the approved mark (media/hero/aik-glass-mark.webp, 1914 x 852).
# The mountains of the mark are left out: the photo is the mountains. A and I are taken from the
# mark's own outline (holes filled); K is joined to a mountain stroke there, so it is redrawn
# from measurements of the mark.
g = cv2.imread('media/hero/aik-glass-mark.webp', cv2.IMREAD_UNCHANGED)
solid = cv2.morphologyEx((g[..., 3] > 20).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(solid, connectivity=4)
L = np.zeros_like(solid)
for i in range(1, n):
    x, y, w, h, area = st[i]
    if area > 20000 and y > 260 and x < 1090 and y + h > 760: L[lab == i] = 1      # A and I
L = cv2.morphologyEx(L, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
cs, _ = cv2.findContours(L, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
L2 = np.zeros_like(L)
for c in cs:
    if cv2.contourArea(c) > 2500: cv2.drawContours(L2, [c], -1, 1, -1)              # keep A's counter, drop glass speckle
cs, hier = cv2.findContours(L, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
for c, hh in zip(cs, hier[0]):
    if hh[3] >= 0 and cv2.contourArea(c) > 6000: cv2.drawContours(L2, [c], -1, 0, -1)
cv2.fillPoly(L2, [np.int32([(1095, 412), (1177, 412), (1177, 800), (1095, 800)])], 1)             # K stem
cv2.fillPoly(L2, [np.int32([(1175, 597), (1395, 408), (1497, 408), (1305, 572), (1605, 800), (1470, 800)])], 1)
L2[801:] = 0                                                                                      # one baseline
x0, y0, x1, y1 = 262, 274, 1616, 808
up = 1600 / (x1 - x0)
shape = cv2.resize(L2[y0:y1, x0:x1].astype(np.float32), (1600, round((y1 - y0) * up)), interpolation=cv2.INTER_CUBIC)
shape = np.clip(cv2.GaussianBlur(shape, (0, 0), .8), 0, 1)
gh, gw = shape.shape
# a glass slab with a bevel: flat face, the edge rounds over in ~14 px
dist = cv2.distanceTransform((shape > .5).astype(np.uint8), cv2.DIST_L2, 5)
bevel = np.clip(dist / 16, 0, 1)
height = cv2.GaussianBlur(np.sqrt(bevel) * shape, (0, 0), 2.2)
facet = np.clip(1 - dist / 6, 0, 1) * shape                      # thin inner rim that catches the light
pad = 40
G = np.zeros((gh + 2 * pad, gw + 2 * pad, 3), np.float32)
G[pad:-pad, pad:-pad] = np.dstack([facet, height, shape])        # BGR
cv2.imwrite(f'{out}/glass.png', np.clip(G * 255, 0, 255).astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 9])
json.dump({'w': G.shape[1], 'h': G.shape[0], 'pad': pad, 'inner': [gw, gh]}, open(f'{out}/glass.json', 'w'))
# without WebGL: the same letters as a frosted image
fb = np.dstack([np.full_like(shape, 255)] * 3 + [np.clip(shape * 70 + facet * 150, 0, 255)]).astype(np.uint8)
cv2.imwrite(f'{out}/glass-fallback.webp', cv2.resize(fb, (800, round(800 * gh / gw)), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_WEBP_QUALITY, 90])
print('ok', W, H, '->', out, 'glass', gw, gh)
