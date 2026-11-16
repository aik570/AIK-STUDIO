"""AIK Studio — flight edit.

Source: eagle-flight-raw.mov (1280x720, 30 fps container, 24 fps content with
a duplicated frame roughly every 5th frame). Output: 24 fps master without
duplicates, three shots joined by "cloud pass" transitions, the middle shot
graded towards the warm dusk of the first and last, the baked UI (logo,
menu circle, SCROLL) removed from the last shot.

Usage: python3 -I edit_flight.py SRC OUTDIR
"""
import sys, os, subprocess, json
import numpy as np, cv2

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
W, H = 1280, 720

SHOTS = [  # (name, start, end) in source seconds
    ("A_dusk_entry", 0.00, 7.15),
    ("C_canyon", 9.53, 15.33),
]
PAGE = np.array([16, 20, 25], np.float32)   # site background, --obsidian #101419
FADE = 26                                     # frames: the flight settles into the page (1.08 s)
XF = 20  # transition length in frames (24 fps) = 0.83 s


def read_unique(t0, t1):
    """Decode [t0, t1) at the container rate and drop duplicated frames."""
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{t0}", "-to", f"{t1}", "-i", SRC,
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    frames, prev = [], None
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        small = cv2.resize(f, (160, 90), interpolation=cv2.INTER_AREA).astype(np.float32)
        if prev is not None and np.abs(small - prev).mean() < 0.2:
            continue  # duplicate from 24→30 conversion
        frames.append(f.copy())
        prev = small
    p.wait()
    return frames


def lab_stats(frames, step=6):
    ls = [cv2.cvtColor(f[::4, ::4], cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32) for f in frames[::step]]
    a = np.concatenate(ls)
    return a.mean(0), a.std(0)


def transfer(f, src, dst, k):
    lab = cv2.cvtColor(f, cv2.COLOR_RGB2LAB).astype(np.float32)
    (ms, ss), (md, sd) = src, dst
    t = (lab - ms) / np.maximum(ss, 1e-3) * sd + md
    out = lab * (1 - k) + t * k
    return cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)


def ui_mask(f):
    """Bright UI marks on the darker sky inside three known boxes."""
    g = cv2.cvtColor(f, cv2.COLOR_RGB2GRAY).astype(np.float32)
    m = np.zeros((H, W), np.uint8)
    for x0, y0, x1, y1 in [(52, 10, 168, 72), (1180, 8, 1240, 64), (600, 632, 680, 700)]:
        roi = g[y0:y1, x0:x1]
        bg = cv2.medianBlur(roi.astype(np.uint8), 21).astype(np.float32)
        m[y0:y1, x0:x1] = ((roi - bg) > 10).astype(np.uint8) * 255
    return cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2)


def zoom(f, z, cx=0.5, cy=0.45):
    if abs(z - 1) < 1e-4:
        return f
    M = np.float32([[z, 0, (1 - z) * W * cx], [0, z, (1 - z) * H * cy]])
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def radial_blur(f, amount, cx=0.5, cy=0.45):
    if amount < 0.002:
        return f
    acc = np.zeros_like(f, np.float32)
    for i in range(5):
        acc += zoom(f, 1 + amount * i / 4, cx, cy).astype(np.float32)
    return (acc / 5).astype(np.uint8)


HAZE = np.array([182, 174, 167], np.float32)   # warm-grey cloud body
HAZE_LIT = np.array([228, 212, 192], np.float32)  # sunlit cloud tops

def _fbm(seed, w=W, h=H):
    """Soft cloud texture: large forms first, finer detail on top."""
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32); tot = 0
    for s, amp in ((360, 1.0), (180, .55), (90, .3), (45, .16)):
        n = rng.random((h // s + 3, w // s + 3)).astype(np.float32)
        big = cv2.resize(n, ((w // s + 3) * s, (h // s + 3) * s), interpolation=cv2.INTER_CUBIC)
        acc += amp * big[s:s + h, s:s + w]; tot += amp
    acc = cv2.GaussianBlur(acc / tot, (0, 0), 4)
    return (acc - acc.min()) / (acc.max() - acc.min())

FOG = [_fbm(7), _fbm(11)]


def cloud_pass(a_frames, b_frames):
    """Fly into a cloud at the end of A and out of it at the start of B.
    Two layers of cloud texture rush past the camera (they scale up as we move
    through them); density follows a bell over the transition, so the cut sits
    inside the thickest part and is never seen."""
    out = []
    n = len(a_frames)
    for i in range(n):
        t = (i + 0.5) / n
        za = 1 + 0.20 * t ** 1.6
        zb = 1.18 - 0.18 * t ** 0.7
        fa = radial_blur(zoom(a_frames[i], za), 0.06 * t)
        fb = radial_blur(zoom(b_frames[i], zb), 0.06 * (1 - t))
        m = np.clip((t - 0.38) / 0.24, 0, 1); m = m * m * (3 - 2 * m)   # the cut hides at the densest moment
        img = fa.astype(np.float32) * (1 - m) + fb.astype(np.float32) * m
        dens = np.sin(np.pi * t) ** 1.8
        layers = 0
        for k, fog in enumerate(FOG):
            z = 1 + (0.8 + 0.6 * k) * t                # the cloud comes at us
            f = zoom(fog, z, 0.5 + 0.08 * (k - 0.5), 0.45)
            layers = layers + f * (0.6 if k == 0 else 0.4)
        cover = np.clip((layers - (0.62 - 0.55 * dens)) / 0.28, 0, 1) * min(1.0, dens * 1.25)
        cover = np.maximum(cover * (0.55 + 0.45 * dens), 0.93 * dens ** 1.5)   # no dark holes in the thick of it
        col = HAZE[None, None] * (1 - layers[..., None] * 0.6) + HAZE_LIT[None, None] * (layers[..., None] * 0.6)
        img = img * (1 - cover[..., None]) + col * cover[..., None]
        out.append(np.clip(img, 0, 255).astype(np.uint8))
    return out


def finish(f):
    """Shared final look: gentle S-curve, a touch of vignette."""
    x = f.astype(np.float32) / 255
    x = x + (x - 0.5) * 0.12 * (1 - np.abs(2 * x - 1))      # soft S-curve
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    vig = 1 - 0.18 * np.clip(r - 0.55, 0, None) ** 1.5
    return np.clip(x * vig[..., None] * 255, 0, 255).astype(np.uint8)


def main():
    shots = {}
    for name, a, b in SHOTS:
        fr = read_unique(a, b)
        shots[name] = fr
        print(name, len(fr), "frames", f"{len(fr) / 24:.2f}s", flush=True)

    A, C = shots["A_dusk_entry"], shots["C_canyon"]

    # grade C towards the dusk of A
    dst, src = lab_stats(A), lab_stats(C)
    C = [transfer(f, src, dst, 0.72) for f in C]

    seq = A[:-XF] + cloud_pass(A[-XF:], C[:XF]) + C[XF:]
    seq = [finish(f) for f in seq]

    # ending: the eagle flies on towards the peaks while the frame settles into the page colour
    n = len(seq)
    for k in range(FADE):
        i = n - FADE + k
        t = (k + 1) / FADE
        e = t * t * (3 - 2 * t)
        f = zoom(seq[i], 1 + 0.04 * e).astype(np.float32)
        seq[i] = np.clip(f * (1 - e) + PAGE * e, 0, 255).astype(np.uint8)
    print("total", len(seq), "frames", f"{len(seq) / 24:.2f}s", flush=True)

    marks = {"A_end": len(A) - XF, "C_start": len(A), "fade_start": len(seq) - FADE, "frames": len(seq)}
    json.dump(marks, open(os.path.join(OUT, "edit-marks.json"), "w"), indent=1)

    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "24", "-i", "-",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                            os.path.join(OUT, "aik-flight-master-720p24.mp4")], stdin=subprocess.PIPE)
    for f in seq:
        enc.stdin.write(f.tobytes())
    enc.stdin.close(); enc.wait()
    print("done", flush=True)


main()
