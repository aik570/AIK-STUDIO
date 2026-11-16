import sys, os, subprocess
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "edit_flight.py")).read().rsplit("\nmain()", 1)[0]
sys.argv = ["x", "/home/claude/src/v2/eagle-flight-raw.mov", "/home/claude/flightA"]
ns = {"__name__": "lib"}; exec(compile(src, "edit_flight.py", "exec"), ns)
A = ns["read_unique"](0.90, 6.95)
print("frames", len(A), len(A) / 24)
os.makedirs("/home/claude/flightA", exist_ok=True)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1280x720", "-r", "24", "-i", "-",
                      "-c:v", "libx264", "-preset", "slow", "-crf", "8", "-pix_fmt", "yuv420p", "/home/claude/flightA/A-master-720p24.mp4"], stdin=subprocess.PIPE)
for f in A: p.stdin.write(f.tobytes())
p.stdin.close(); p.wait()
