"""AIK Studio — flight v4 (14.11 evening): one continuous shot, no cuts.
Shot A 0.90–7.15 s of eagle-flight-raw.mov: dusk over the range, the eagle rises
from below and glides towards the main summit. Duplicate frames removed (24 fps),
shared finish, upscaled to 1920x1080 (Lanczos + gentle unsharp) and encoded
lightly, because heavy compression was the visible problem.
Matte (summit + eagle, u2net) only for the last 44 frames, where the glass AIK
rises behind the summit. Layout of the video: 1920x1080 picture on top, below a
strip of two 960x540 mattes [summit+eagle | empty] -> 1920x1620.
Usage: python3 -I edit_flight4.py SRC OUTDIR
"""
import os, sys, json, subprocess
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "edit_flight.py")).read().rsplit("\nmain()", 1)[0]
argv = sys.argv
ns = {"__name__": "lib"}; exec(compile(src, "edit_flight.py", "exec"), ns)
read_unique, finish = ns["read_unique"], ns["finish"]
OUT = argv[2]; os.makedirs(OUT, exist_ok=True)

A = [finish(f) for f in read_unique(0.90, 6.95)]   # artefacts of the glitch start at ~7.0 s
N = len(A); print("frames", N, N / 24, flush=True)
MATTE_FROM = N - 44

os.environ.setdefault("U2NET_HOME", "/home/claude/models")
from rembg import remove, new_session
from PIL import Image
sess = new_session("u2net")
M = {}
for i in range(MATTE_FROM, N):
    m = np.asarray(remove(Image.fromarray(A[i]), session=sess, only_mask=True).convert("L"), np.float32) / 255
    M[i] = np.clip((cv2.GaussianBlur(m, (0, 0), 1.2) - 0.08) / 0.84, 0, 1)
for i in range(MATTE_FROM, N):   # temporal smoothing
    a, b = M.get(i - 1, M[i]), M.get(i + 1, M[i])
    M[i] = M[i] * 0.5 + a * 0.25 + b * 0.25
print("mattes", len(M), flush=True)

W2, H2 = 1920, 1080
def up(f):
    g = cv2.resize(f, (W2, H2), interpolation=cv2.INTER_LANCZOS4)
    blur = cv2.GaussianBlur(g, (0, 0), 1.1)
    return cv2.addWeighted(g, 1.35, blur, -0.35, 0)

def frames(stack):
    blank = np.zeros((H2 // 2, W2), np.uint8)
    for i, f in enumerate(A):
        pic = up(f)
        if not stack:
            yield pic; continue
        if i in M:
            mm = (cv2.resize(M[i], (W2 // 2, H2 // 2), interpolation=cv2.INTER_AREA) * 255).astype(np.uint8)
            row = np.hstack([mm, np.zeros_like(mm)])
        else:
            row = blank
        yield np.vstack([pic, np.dstack([row, row, row])])

def encode(it, path, h, crf, g, extra=()):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W2}x{h}", "-r", "24", "-i", "-",
                          "-an", "-c:v", "libx264", "-preset", "slow", "-tune", "film", "-crf", str(crf), "-g", str(g), "-keyint_min", str(g),
                          "-sc_threshold", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart", *extra, path], stdin=subprocess.PIPE)
    for f in it:
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()

encode(frames(True), os.path.join(OUT, "intro-1920.mp4"), H2 + H2 // 2, 19, 12)
encode(frames(False), os.path.join(OUT, "flight-preview-1080p.mp4"), H2, 16, 48)

last = up(A[-1]); first = up(A[0])
mm = (cv2.resize(M[N - 1], (W2 // 2, H2 // 2), interpolation=cv2.INTER_AREA) * 255).astype(np.uint8)
row = np.hstack([mm, np.zeros_like(mm)])
cv2.imwrite(os.path.join(OUT, "hero-still-stack.png"), cv2.cvtColor(np.vstack([last, np.dstack([row, row, row])]), cv2.COLOR_RGB2BGR))
cv2.imwrite(os.path.join(OUT, "hero-plate.png"), cv2.cvtColor(last, cv2.COLOR_RGB2BGR))
cv2.imwrite(os.path.join(OUT, "intro-first.png"), cv2.cvtColor(first, cv2.COLOR_RGB2BGR))
json.dump({"frames": N, "matte_from": MATTE_FROM, "fps": 24, "w": W2, "h": H2}, open(os.path.join(OUT, "marks.json"), "w"), indent=1)
print("done", flush=True)
