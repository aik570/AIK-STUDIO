"""AIK Studio — flight edit v3 (storyboard frames 04–09) + hero loop.

intro:  A (dusk entry) → cloud pass → C (canyon) → cloud pass → E (sea of clouds,
        the Hero composition). E is cleaned of the baked UI.
loop:   E as a seamless "breathing" loop for the Hero: plays E backwards then
        forwards with cosine easing, so the turns are slow glides, never jumps.
matte:  foreground (summit + eagle) per E frame from u2net, stored under the
        picture in the same video (1280x1440: picture on top, matte below), so
        the WebGL glass letters can sit between the sky and the summit/eagle in
        perfect sync.

Usage: python3 -I edit_flight2.py SRC OUTDIR
"""
import os, sys, json, subprocess
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "edit_flight.py")).read()
src = src.rsplit("\nmain()", 1)[0]
ns = {"__name__": "lib", "sys": sys}
sys_argv = sys.argv
exec(compile(src, "edit_flight.py", "exec"), ns)   # read_unique, lab_stats, transfer, ui_mask, cloud_pass, finish, W, H, XF
read_unique, lab_stats, transfer, ui_mask = ns["read_unique"], ns["lab_stats"], ns["transfer"], ns["ui_mask"]
cloud_pass, finish, W, H, XF = ns["cloud_pass"], ns["finish"], ns["W"], ns["H"], ns["XF"]
OUT = sys_argv[2]
os.makedirs(OUT, exist_ok=True)

# short cut (14.11 evening): the eagle comes in, one pass through the cloud, the Hero.
A = read_unique(0.00, 4.40)
E = read_unique(18.20, 20.21)
C = []
print("A E", len(A), len(E), flush=True)
E = [cv2.inpaint(f, ui_mask(f), 6, cv2.INPAINT_TELEA) for f in E]
XF2 = 16
seq = A[:-XF2] + cloud_pass(A[-XF2:], E[:XF2]) + E[XF2:]
seq = [finish(f) for f in seq]
e_start = len(seq) - (len(E) - XF2)            # first pure E frame in the intro
Ef = [finish(f) for f in E]                    # graded E frames for the loop

# ---------------------------------------------------------------- matte (u2net)
os.environ.setdefault("U2NET_HOME", "/home/claude/models")
from rembg import remove, new_session
from PIL import Image
sess = new_session("u2net")

def matte(f):
    m = remove(Image.fromarray(f), session=sess, only_mask=True)
    m = np.asarray(m.convert("L"), np.float32) / 255
    m = cv2.GaussianBlur(m, (0, 0), 1.2)
    return np.clip((m - 0.08) / 0.84, 0, 1)

Em = []
for i, f in enumerate(Ef):
    Em.append(matte(f))
    if i % 8 == 0:
        print("matte", i, flush=True)
Em = [cv2.GaussianBlur(m, (0, 0), 0.6) for m in Em]
# temporal smoothing: kills flicker of the edges between frames
Em2 = []
for i in range(len(Em)):
    acc = Em[i] * 0.5 + Em[max(0, i - 1)] * 0.25 + Em[min(len(Em) - 1, i + 1)] * 0.25
    Em2.append(acc)
Em = Em2

# eagle only: isnet on a tight crop that follows the bird (from the last frame back)
sess_e = new_session("isnet-general-use")
BW, BH = 380, 160
cx, cy = 625.0, 415.0
Eg = [None] * len(Ef)
for i in range(len(Ef) - 1, -1, -1):
    x0 = int(np.clip(cx - BW / 2, 0, W - BW)); y0 = int(np.clip(cy - BH / 2, 0, H - BH))
    crop = Image.fromarray(Ef[i][y0:y0 + BH, x0:x0 + BW])
    mk = np.asarray(remove(crop, session=sess_e, only_mask=True).convert("L"), np.float32) / 255
    mk = np.clip((mk - 0.12) * 1.9, 0, 1)
    full = np.zeros((H, W), np.float32); full[y0:y0 + BH, x0:x0 + BW] = mk
    full = np.minimum(full, np.clip(Em[i] * 1.3, 0, 1))          # never outside the salient matte
    Eg[i] = cv2.GaussianBlur(full, (0, 0), 0.8)
    ys, xs = np.nonzero(mk > 0.35)
    if len(xs) > 50:
        cx = 0.7 * cx + 0.3 * (x0 + xs.mean()); cy = 0.7 * cy + 0.3 * (y0 + ys.mean())
    if i % 8 == 0:
        print("eagle", i, round(cx), round(cy), flush=True)
Eg = [Eg[i] * 0.5 + Eg[max(0, i - 1)] * 0.25 + Eg[min(len(Eg) - 1, i + 1)] * 0.25 for i in range(len(Eg))]

QW, QH = W // 2, H // 2
def stack(color, m, e=None):
    """picture 1280x720 on top; below, two half-size mattes: summit+eagle | eagle."""
    a = cv2.resize(np.clip(m, 0, 1), (QW, QH), interpolation=cv2.INTER_AREA)
    b = cv2.resize(np.clip(e if e is not None else np.zeros_like(m), 0, 1), (QW, QH), interpolation=cv2.INTER_AREA)
    row = (np.hstack([a, b]) * 255).astype(np.uint8)
    return np.vstack([color, np.dstack([row, row, row])])

def encode(frames, path, crf, g, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{h}", "-r", "24", "-i", "-",
                          "-an", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-g", str(g), "-keyint_min", str(g), "-sc_threshold", "0",
                          "-pix_fmt", "yuv420p", "-movflags", "+faststart", path], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()

# intro: matte only where E is on screen (fades in across the cloud pass)
blank = np.zeros((H, W), np.float32)
def intro_frames():
    for i, f in enumerate(seq):
        k = i - (len(seq) - len(E))             # index into E (negative before E)
        m = Em[k] if 0 <= k < len(Em) else blank
        e = Eg[k] if 0 <= k < len(Eg) else blank
        yield stack(f, m, e)
del A, C
encode(intro_frames(), os.path.join(OUT, "intro-1280.mp4"), 22, 6, H + H // 2)
encode(seq, os.path.join(OUT, "intro-preview.mp4"), 18, 48, H)

# loop: start at E's last frame (where the intro ends), glide back, glide forward
n = len(Ef)
T = 6.0
def loop_frames():
  for j in range(int(T * 24)):
    tau = j / (T * 24)
    fpos = (n - 1) * (0.5 + 0.5 * np.cos(2 * np.pi * tau))   # n-1 → 0 → n-1
    i0 = int(np.floor(fpos)); i1 = min(n - 1, i0 + 1); t = fpos - i0
    col = (Ef[i0].astype(np.float32) * (1 - t) + Ef[i1].astype(np.float32) * t).astype(np.uint8)
    mm = Em[i0] * (1 - t) + Em[i1] * t
    ee = Eg[i0] * (1 - t) + Eg[i1] * t
    yield stack(col, mm, ee)
encode(loop_frames(), os.path.join(OUT, "hero-loop-1280.mp4"), 21, 24, H + H // 2)

cv2.imwrite(os.path.join(OUT, "hero-plate.png"), cv2.cvtColor(Ef[-1], cv2.COLOR_RGB2BGR))
cv2.imwrite(os.path.join(OUT, "hero-matte.png"), (Em[-1] * 255).astype(np.uint8))
cv2.imwrite(os.path.join(OUT, "hero-eagle.png"), (Eg[-1] * 255).astype(np.uint8))
cv2.imwrite(os.path.join(OUT, "intro-first.png"), cv2.cvtColor(seq[0], cv2.COLOR_RGB2BGR))
json.dump({"frames": len(seq), "e_start": e_start, "e_len": len(E), "fps": 24, "loop_seconds": T},
          open(os.path.join(OUT, "marks.json"), "w"), indent=1)
print("done", len(seq), "frames", f"{len(seq)/24:.2f}s", "e_start", e_start, flush=True)
