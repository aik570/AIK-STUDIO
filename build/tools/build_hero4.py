"""Hero 4 in EN and DE: replaces the Hero section, wires hero4.css / hero4.js, preloads.
Run after tools/build_sections.py (which writes everything below the Hero):

    python3 tools/build_hero4.py .
"""
import json, re, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
PLATE = json.load(open(f'{ROOT}/media/hero4/plate.json'))
GLASS = json.load(open(f'{ROOT}/media/hero4/glass.json'))
ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 8h11M9 3.5 13.5 8 9 12.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
T = {
 "en": dict(b="./",
   kicker="Premium websites for ambitious businesses",
   h=["Websites that", "bring you clients."],
   lead="Redesign, copy, development, SEO, Impressum and privacy policy. One studio does all of it, from Berlin and Potsdam.",
   cta1="Get a quote", cta2="See the work", skip="Skip intro",
   alt="Snowy peaks above a sea of clouds at sunset"),
 "de": dict(b="../",
   kicker="Premium-Websites für Unternehmen mit Anspruch",
   h=["Websites, die", "Kunden bringen."],
   lead="Redesign, Texte, Entwicklung, SEO, Impressum und Datenschutz. Ein Studio macht alles, aus Berlin und Potsdam.",
   cta1="Angebot anfragen", cta2="Arbeiten ansehen", skip="Intro überspringen",
   alt="Verschneite Gipfel über einem Wolkenmeer bei Sonnenuntergang"),
}

def hero(c):
    b = c["b"]; m = b + "media/hero4/"
    lines = "".join(f'<span class="hx__line"><span style="--d:{160 + 110 * i}">{t}</span></span>' for i, t in enumerate(c["h"]))
    plate = json.dumps(PLATE, separators=(',', ':')).replace('"', '&quot;')
    glass = json.dumps(GLASS, separators=(',', ':')).replace('"', '&quot;')
    gw, gh = GLASS['inner']
    return f'''<section class="hx" id="top" aria-labelledby="hero-title" data-media="{m}" data-plate="{plate}" data-glass="{glass}" data-film="{b}media/hero/flight-1920.mp4">
    <div class="hx__stage">
      <div class="hx__scene">
        <picture class="hx__plate">
          <source media="(max-width: 760px) and (orientation: portrait)" srcset="{m}plate-portrait-900.webp 900w, {m}plate-portrait-1400.webp 1400w" sizes="100vw">
          <img src="{m}plate-1920.webp" srcset="{m}plate-1280.webp 1280w, {m}plate-1920.webp 1920w, {m}plate-2880.webp 2880w, {m}plate-3840.webp 3840w" sizes="(min-aspect-ratio: 16/9) 100vw, 112vw" alt="{c["alt"]}" width="1920" height="1060" fetchpriority="high" decoding="async">
        </picture>
        <div class="hx__mark" aria-hidden="true" style="aspect-ratio: {gw} / {gh}"><img class="hx__glassimg" src="{m}glass-fallback.webp" alt="" width="{gw}" height="{gh}" decoding="async"></div>
        <div class="hx__shade" aria-hidden="true"></div>
      </div>
      <div class="hx__copy">
        <p class="hx__kicker" data-in style="--d:60"><i aria-hidden="true"></i>{c["kicker"]}</p>
        <h1 class="hx__title" id="hero-title"><span class="visually-hidden">AIK Studio: </span>{lines}</h1>
        <div class="hx__side">
          <p class="hx__lead" data-in style="--d:420">{c["lead"]}</p>
          <div class="hx__ctas" data-in style="--d:520">
            <a class="hx__btn hx__btn--solid" href="#contact">{c["cta1"]} {ARROW}</a>
            <a class="hx__btn hx__btn--ghost" href="#work">{c["cta2"]}</a>
          </div>
        </div>
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
    pre = (f'<link rel="preload" as="image" href="{b}media/hero4/plate-1920.webp" imagesrcset="{b}media/hero4/plate-1280.webp 1280w, {b}media/hero4/plate-1920.webp 1920w, {b}media/hero4/plate-2880.webp 2880w, {b}media/hero4/plate-3840.webp 3840w" imagesizes="(min-aspect-ratio: 16/9) 100vw, 112vw" media="(min-width: 761px), (orientation: landscape)" fetchpriority="high">\n'
           f'<link rel="preload" as="image" href="{b}media/hero4/plate-portrait-900.webp" imagesrcset="{b}media/hero4/plate-portrait-900.webp 900w, {b}media/hero4/plate-portrait-1400.webp 1400w" imagesizes="100vw" media="(max-width: 760px) and (orientation: portrait)" fetchpriority="high">\n')
    s = s.replace('<link rel="stylesheet"', pre + '<link rel="stylesheet"', 1)
    s = re.sub(r'<link rel="preload" href="[^"]*fonts/(?:outfit|bowlby)[^"]*" as="font" type="font/woff2" crossorigin>',
               f'<link rel="preload" href="{b}fonts/bowlby-one-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>', s)
    if 'hero4.css' not in s:
        s = s.replace(f'<link rel="stylesheet" href="{b}css/v4.css">', f'<link rel="stylesheet" href="{b}css/v4.css">\n<link rel="stylesheet" href="{b}css/hero4.css">')
    s = s.replace(f'<script src="{b}js/hero3.js" defer></script>', f'<script src="{b}js/hero4.js" defer></script>')
    s = s.replace('<meta name="theme-color" content="#101419">\n', '').replace('<meta name="theme-color" content="#0d1116">', '<meta name="theme-color" content="#0a0a0a">')
    open(fp, "w").write(s)
    print(lang, "ok", "hero4.js" in s, "hero4.css" in s)
