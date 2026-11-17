"""Hero 4 in EN and DE: replaces the Hero section, wires hero4.css / hero4.js, preloads.
Run after tools/build_sections.py (which writes everything below the Hero):

    python3 tools/build_hero4.py .
"""
import json, re, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
PLATE = json.load(open(f'{ROOT}/media/hero4/plate.json'))
GLASS = json.load(open(f'{ROOT}/media/hero4/glass.json'))
from PIL import Image
LOGO = Image.open(f'{ROOT}/media/logo/aik-lockup-white.png').size
ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 8h11M9 3.5 13.5 8 9 12.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
T = {
 "en": dict(b="./",
   kicker="AIK Studio · Berlin / Potsdam",
   h=["Websites that", "bring you clients."],
   lead="Premium websites for ambitious businesses. Planned, written, designed and built for you, from the first call to launch.",
   cta1="Get a quote", cta2="See the work", skip="Skip intro",
   why=[("One contact", "You talk directly to the person who builds your site."),
        ("Everything included", "Copy, design, build, SEO, Impressum and Datenschutz."),
        ("Prices up front", "From 900 €, listed on this page.")],
   alt="Snowy peaks above a sea of clouds at sunset"),
 "de": dict(b="../",
   kicker="AIK Studio · Berlin / Potsdam",
   h=["Websites, die", "Kunden bringen."],
   lead="Premium-Websites für Unternehmen mit Anspruch. Geplant, getextet, gestaltet und gebaut, vom ersten Gespräch bis zum Start.",
   cta1="Angebot anfragen", cta2="Arbeiten ansehen", skip="Intro überspringen",
   why=[("Ein Ansprechpartner", "Sie sprechen direkt mit dem, der Ihre Website baut."),
        ("Alles inklusive", "Texte, Design, Entwicklung, SEO, Impressum und Datenschutz."),
        ("Offene Preise", "Ab 900 €, hier auf der Seite.")],
   alt="Verschneite Gipfel über einem Wolkenmeer bei Sonnenuntergang"),
}

def hero(c):
    b = c["b"]; m = b + "media/hero4/"
    lines = "".join(f'<span class="hx__line"><span style="--d:{160 + 110 * i}">{t}</span></span>' for i, t in enumerate(c["h"]))
    plate = json.dumps(PLATE, separators=(',', ':')).replace('"', '&quot;')
    glass = json.dumps(GLASS, separators=(',', ':')).replace('"', '&quot;')
    gw, gh = GLASS['inner']
    why = "".join(f'<li data-in style="--d:{640 + 80 * i}"><b>0{i + 1}</b><span><strong>{t}</strong> {d}</span></li>' for i, (t, d) in enumerate(c["why"]))
    srcset = ", ".join(f'{m}plate-{w}.webp {w}w' for w in PLATE['sizes'])
    return f'''<section class="hx" id="top" aria-labelledby="hero-title" data-media="{m}" data-plate="{plate}" data-glass="{glass}" data-film="{b}media/hero/flight-1920.mp4">
    <div class="hx__stage">
      <div class="hx__scene">
        <picture class="hx__plate">
          <source media="(max-width: 760px) and (orientation: portrait)" srcset="{m}plate-portrait-900.webp 900w, {m}plate-portrait-1400.webp 1400w" sizes="100vw">
          <img src="{m}plate-1920.webp" srcset="{srcset}" sizes="(min-aspect-ratio: 16/9) 100vw, 112vw" alt="{c["alt"]}" width="1920" height="1060" fetchpriority="high" decoding="async">
        </picture>
        <div class="hx__mark" aria-hidden="true" style="aspect-ratio: {gw} / {gh}"><img class="hx__glassimg" src="{m}glass-fallback.webp" alt="" width="{gw}" height="{gh}" decoding="async"></div>
        <div class="hx__shade" aria-hidden="true"></div>
      </div>
      <div class="hx__copy">
        <div class="hx__main">
          <p class="hx__kicker" data-in style="--d:60"><i aria-hidden="true"></i>{c["kicker"]}</p>
          <h1 class="hx__title" id="hero-title"><span class="visually-hidden">AIK Studio: </span>{lines}</h1>
        </div>
        <div class="hx__side">
          <p class="hx__lead" data-in style="--d:420">{c["lead"]}</p>
          <div class="hx__ctas" data-in style="--d:520">
            <a class="hx__btn hx__btn--solid" href="#contact">{c["cta1"]} {ARROW}</a>
            <a class="hx__btn hx__btn--ghost" href="#work">{c["cta2"]}</a>
          </div>
        </div>
        <ul class="hx__why">{why}</ul>
      </div>
      <button class="hx__skip" type="button">{c["skip"]}</button>
    </div>
  </section>'''

for lang, path in [("en", "index.html"), ("de", "de/index.html")]:
    c = T[lang]; b = c["b"]; fp = f"{ROOT}/{path}"; s = open(fp).read()
    m = re.search(r'<section class="(?:hero[234]|hx)".*?</section>', s, re.S)
    s = s[:m.start()] + hero(c) + s[m.end():]
    # preloads: the plate the Hero opens on (landscape or portrait), then the headline face
    s = re.sub(r'<link rel="preload" as="image" href="[^"]*(?:hero3-plate|hero4/plate)[^>]*>\n?', '', s)
    pre = (f'<link rel="preload" as="image" href="{b}media/hero4/plate-1920.webp" imagesrcset="{', '.join(f'{b}media/hero4/plate-{w}.webp {w}w' for w in PLATE['sizes'])}" imagesizes="(min-aspect-ratio: 16/9) 100vw, 112vw" media="(min-width: 761px), (orientation: landscape)" fetchpriority="high">\n'
           f'<link rel="preload" as="image" href="{b}media/hero4/plate-portrait-900.webp" imagesrcset="{b}media/hero4/plate-portrait-900.webp 900w, {b}media/hero4/plate-portrait-1400.webp 1400w" imagesizes="100vw" media="(max-width: 760px) and (orientation: portrait)" fetchpriority="high">\n')
    s = s.replace('<link rel="stylesheet"', pre + '<link rel="stylesheet"', 1)
    s = re.sub(r'<link rel="preload" href="[^"]*fonts/(?:outfit|bowlby)[^"]*" as="font" type="font/woff2" crossorigin>',
               f'<link rel="preload" href="{b}fonts/bowlby-one-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>', s)
    if 'hero4.css' not in s:
        s = s.replace(f'<link rel="stylesheet" href="{b}css/v4.css">', f'<link rel="stylesheet" href="{b}css/v4.css">\n<link rel="stylesheet" href="{b}css/hero4.css">')
    s = re.sub(r'(<a class="brand"[^>]*>\s*<img src=")[^"]*(" )width="\d+" height="\d+"', rf'\g<1>{b}media/logo/aik-lockup-white.png\g<2>width="{LOGO[0]}" height="{LOGO[1]}"', s, count=1)
    s = s.replace(f'<script src="{b}js/hero3.js" defer></script>', f'<script src="{b}js/hero4.js" defer></script>')
    s = s.replace('<meta name="theme-color" content="#101419">\n', '').replace('<meta name="theme-color" content="#0d1116">', '<meta name="theme-color" content="#0a0a0a">')
    open(fp, "w").write(s)
    print(lang, "ok", "hero4.js" in s, "hero4.css" in s)
