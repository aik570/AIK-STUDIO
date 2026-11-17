"""Make the folder that goes online: the pages, the files they reference, _headers, robots.txt.
Nothing else (no tools, tests, README, package files, video masters, sources).

    python3 tools/dist.py . dist          # refuses while legal gaps are left
    ALLOW_DRAFT=1 python3 tools/dist.py . dist

Checks before copying:
  - Impressum / Datenschutz have no marked gaps (class="todo")
  - the price note (TAX in tools/build_site.py) is set
  - no inline <script> without src (except JSON-LD) and no inline event handlers (CSP)
  - every link that opens a new tab has rel="noopener"
"""
import os, re, shutil, sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
DST = Path(sys.argv[2] if len(sys.argv) > 2 else 'dist')
DRAFT = os.environ.get('ALLOW_DRAFT') == '1'
PAGES = ['index.html', 'de/index.html', 'impressum.html', 'datenschutz.html']
REF = re.compile(r'(?:\./|\.\./)?((?:media|css|js|fonts)/[A-Za-z0-9_./-]+\.(?:webp|png|jpg|jpeg|mp4|css|js|woff2|svg|json))')

problems, blockers = [], []
for p in PAGES:
    t = (SRC / p).read_text()
    if 'class="todo"' in t: blockers.append(f'{p}: legal gaps left (fill OWNER in tools/build_legal.py)')
    if 'data-tax="missing"' in t: blockers.append(f'{p}: price note missing (set TAX in tools/build_site.py)')
    for m in re.finditer(r'<script(?![^>]*\bsrc=)(?![^>]*application/ld\+json)[^>]*>', t): problems.append(f'{p}: inline script {m.group(0)}')
    for m in re.finditer(r'\son[a-z]+="', t): problems.append(f'{p}: inline handler near {t[max(0, m.start() - 40):m.start() + 20]!r}')
    for m in re.finditer(r'<a\b[^>]*target="_blank"[^>]*>', t):
        if 'noopener' not in m.group(0): problems.append(f'{p}: target=_blank without noopener: {m.group(0)[:80]}')

if problems:
    print('\n'.join('ERROR ' + x for x in problems)); sys.exit(1)
if blockers:
    print('\n'.join(('WARN ' if DRAFT else 'BLOCKED ') + x for x in blockers))
    if not DRAFT:
        print('Not publishing. Fill the gaps, or set ALLOW_DRAFT=1 for a private preview.'); sys.exit(2)

files = set(PAGES) | {'_headers', 'media/hero/intro-first.webp', 'media/hero4/depth.png'}
texts = PAGES + ['css/aik.css', 'css/legal.css', 'css/loader.css', 'js/hero4.js', 'js/aik.js', 'js/loader.js', 'js/loader-gl.js', 'js/boot.js']
for p in texts:
    for m in REF.finditer((SRC / p).read_text()):
        files.add(m.group(1).lstrip('./'))
files |= {str(p.relative_to(SRC)) for p in (SRC / 'media/world').glob('*.webp')}
missing = [f for f in sorted(files) if not (SRC / f).is_file()]
if missing:
    print('\n'.join('ERROR missing ' + f for f in missing)); sys.exit(1)

if DST.exists(): shutil.rmtree(DST)
for f in sorted(files):
    (DST / f).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC / f, DST / f)
(DST / 'robots.txt').write_text('User-agent: *\nAllow: /\n')
size = sum(p.stat().st_size for p in DST.rglob('*') if p.is_file())
print(f'dist: {len(files) + 1} files, {size / 1e6:.1f} MB{" (DRAFT)" if blockers else ""}')
