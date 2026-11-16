"""One-off: remove the glass letters that the old AI frame had baked in, so the code-drawn
glass AIK can sit on a clean plate. Only needed for the temporary plate; a real photo
goes straight into tools/hero_plate.py.

usage: python3 tools/unbake_letters.py in.webp out.png [debug_dir]
"""
import sys, cv2, numpy as np

src, dst = sys.argv[1], sys.argv[2]
dbg = sys.argv[3] if len(sys.argv) > 3 else None
im = cv2.imread(src, cv2.IMREAD_COLOR).astype(np.float32)
H, W = im.shape[:2]
s = W / 3840.0
P = {  # letter outlines measured on the 3840 px frame
  'A': [(1005,486),(1340,840),(1240,920),(1005,676),(818,872),(686,790)],
  'I1': [(1346,490),(1534,312),(1534,1260),(1346,1260)],
  'I2': [(1628,400),(1786,551),(1786,1320),(1628,1320)],
  'K': [(1778,780),(2072,498),(2295,496),(1974,800),(2370,1190),(2300,1260),(1778,834)],
}
M = np.zeros((H, W), np.uint8)
for p in P.values():
    cv2.fillPoly(M, [np.int32(np.array(p) * s)], 255)
M = cv2.dilate(M, np.ones((int(9*s)|1, int(9*s)|1), np.uint8))

# what is mountain (opaque, in front of the letters): the ridge, traced on the 3840 px frame
RIDGE = [(560,1060),(600,1015),(640,980),(690,925),(730,890),(760,875),(800,855),(840,890),(890,940),(930,990),
  (970,1040),(1020,1070),(1050,1060),(1080,1030),(1140,990),(1180,950),(1210,900),(1250,840),(1290,800),(1320,760),
  (1360,730),(1390,712),(1430,760),(1460,820),(1500,880),(1540,930),(1570,930),(1610,1010),(1640,1070),(1680,1120),
  (1720,1150),(1780,1180),(1830,1165),(1880,1150),(1930,1090),(1970,1030),(1990,1000),(2020,980),(2040,965),
  (2060,1000),(2090,1020),(2130,1070),(2170,1110),(2210,1140),(2270,1190),(2310,1230),(2350,1250),(2400,1300)]
rock = np.zeros((H, W), np.uint8)
cv2.fillPoly(rock, [np.int32(np.array(RIDGE + [(2400, 2120), (560, 2120)]) * s)], 1)
rock = cv2.dilate(rock, np.ones((int(7*s)|1,)*2, np.uint8))
Msky = (M > 0) & (rock == 0)
m = Msky.astype(np.float32)

# low frequencies: inside the letters (hazed) vs the sky around them (inpainted). Work in Lab:
# lightness keeps the real cloud detail, colour comes from the sky around the letters.
lab = cv2.cvtColor(np.clip(im, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
sig = 26 * s
def nblur(a, w):
    return cv2.GaussianBlur(a * w[..., None], (0, 0), sig) / np.maximum(cv2.GaussianBlur(w, (0, 0), sig), 1e-4)[..., None]
# each flat facet of the old glass had its own light: estimate the haze per facet
FACETS = [
  [(1005,486),(1005,676),(818,872),(686,790)], [(1005,486),(1340,840),(1240,920),(1005,676)],     # A left / right
  P['I1'], P['I2'],
  [(1778,780),(2072,498),(2295,496),(1974,800),(1876,812)], [(1778,834),(1876,812),(1974,800),(2370,1190),(2300,1260)],  # K arm / leg
]
lowIn = nblur(lab, m)
for f in FACETS:
    F = np.zeros((H, W), np.uint8); cv2.fillPoly(F, [np.int32(np.array(f) * s)], 1)
    F = cv2.dilate(F, np.ones((int(9*s)|1,)*2, np.uint8)).astype(np.float32) * m
    if F.sum() < 10: continue
    lowIn = np.where(F[..., None] > 0, nblur(lab, F), lowIn)
k = 8
hole = cv2.dilate((M > 0).astype(np.uint8) * 255, np.ones((int(24*s)|1,)*2, np.uint8))
small = cv2.resize(np.clip(im, 0, 255).astype(np.uint8), (W//k, H//k), interpolation=cv2.INTER_AREA)
msmall = cv2.resize(hole, (W//k, H//k), interpolation=cv2.INTER_NEAREST)
fill = cv2.inpaint(small, msmall, 14, cv2.INPAINT_TELEA)
fill = cv2.cvtColor(cv2.resize(fill, (W, H), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2LAB).astype(np.float32)
lowOut = cv2.GaussianBlur(fill, (0, 0), sig)
# the two upright strokes: rebuild their sky row by row from the sky either side (no fake glow column)
for nm in ('I1', 'I2'):
    q = np.array(P[nm]) * s
    xl, xr = int(q[:, 0].min() - 26 * s), int(q[:, 0].max() + 26 * s)
    y0, y1 = int(q[:, 1].min()), int(q[:, 1].max())
    xs = np.linspace(0, 1, xr - xl, dtype=np.float32)[None, :, None]
    L_, R_ = lowOut[y0:y1, xl - 1:xl], lowOut[y0:y1, xr:xr + 1]
    lowOut[y0:y1, xl:xr] = L_ * (1 - xs) + R_ * xs
lowOut = cv2.GaussianBlur(lowOut, (0, 0), 6 * s)
ring = (cv2.dilate((M > 0).astype(np.uint8), np.ones((int(80*s)|1,)*2, np.uint8)) > 0) & ~(hole > 0) & (rock == 0)
lowAll = cv2.GaussianBlur(lab, (0, 0), sig)
hi = lab - lowIn
kc = float(np.clip(np.std((lab - lowAll)[..., 0][ring]) / max(np.std(hi[..., 0][Msky]), 1e-3), .45, 1.6))
out = lowOut.copy()
out[..., 0] += hi[..., 0] * kc
out[..., 1:] += hi[..., 1:] * .35
out = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
feather = cv2.GaussianBlur(m, (0, 0), 5*s)[..., None]
res = im * (1 - feather) + out * feather
res = np.clip(res, 0, 255).astype(np.uint8)

# the bright rims of the old glass: thin band along every outline, inpainted at full res
E = np.zeros((H, W), np.uint8)
for p in P.values():
    cv2.polylines(E, [np.int32(np.array(p) * s)], True, 255, max(2, int(26*s)))
cv2.line(E, (int(1005*s), int(470*s)), (int(1005*s), int(690*s)), 255, max(2, int(18*s)))   # the old A's centre seam
E = cv2.dilate(E, np.ones((3, 3), np.uint8))
res = cv2.inpaint(res, E, max(3, int(7*s)), cv2.INPAINT_TELEA)
# where the old glass crossed a peak: undo the haze with a per-letter level match against the
# same rock just outside that letter
base = im.astype(np.float32)
fixed = base.copy()
for name, p in P.items():
    L = np.zeros((H, W), np.uint8); cv2.fillPoly(L, [np.int32(np.array(p) * s)], 1)
    R = (L > 0) & (rock > 0)
    if R.sum() < 500: continue
    ringL = (cv2.dilate(L, np.ones((int(70*s)|1,)*2, np.uint8)) > 0) & ~(cv2.dilate(L, np.ones((int(9*s)|1,)*2, np.uint8)) > 0) & (rock > 0)
    if ringL.sum() < 500: continue
    for c in range(3):
        a_, b_ = base[..., c][R], base[..., c][ringL]
        k = np.std(b_) / max(np.std(a_), 1e-3)
        fixed[..., c] = np.where(R, (base[..., c] - a_.mean()) * k + b_.mean(), fixed[..., c])
    print(name, 'rock fixed', int(R.sum()))
Rall = np.zeros((H, W), np.float32)
for p in P.values(): cv2.fillPoly(Rall, [np.int32(np.array(p) * s)], 1)
Rall = .55 * cv2.GaussianBlur(Rall * (rock > 0), (0, 0), 18*s)[..., None]
res = np.clip(res.astype(np.float32) * (1 - Rall) + fixed * Rall, 0, 255).astype(np.uint8)
cv2.imwrite(dst, res)
print('kc', round(float(kc), 3))
if dbg:
    cv2.imwrite(f'{dbg}/mask.png', (Msky * 255).astype(np.uint8))
    cv2.imwrite(f'{dbg}/rock.png', rock * 255)
