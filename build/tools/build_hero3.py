"""Swap the Hero for Hero 3 (approved frame + live HTML) in EN and DE."""
import re, sys
ROOT = sys.argv[1]
T = {
 "en": dict(b="./", eyebrow="Digital experiences<br>built with intention",
   h=[("", "Your business"), ("dim", "deserves"), ("strong", "a better website.")],
   lead="We turn your business into a digital experience that builds trust, communicates value and moves people to act.",
   cta1="Discuss your project", cta2="Explore our work", scroll="Scroll", skip="Skip intro",
   pillars=["Strategy", "UI/UX Design", "Development", "Growth"],
   nav=[("#work", "Work"), ("#services", "Services"), ("#process", "Approach"), ("#why", "About"), ("#contact", "Contact")],
   alt="Glass AIK letters between snowy peaks above a sea of clouds at sunset"),
 "de": dict(b="../", eyebrow="Digitale Erlebnisse,<br>mit Absicht gebaut",
   h=[("", "Ihr Unternehmen"), ("dim", "verdient"), ("strong", "eine bessere Website.")],
   lead="Wir machen Ihr Unternehmen zu einem digitalen Erlebnis, das Vertrauen schafft, Wert vermittelt und Menschen zum Handeln bewegt.",
   cta1="Projekt besprechen", cta2="Arbeiten ansehen", scroll="Scroll", skip="Intro überspringen",
   pillars=["Strategie", "UI/UX Design", "Entwicklung", "Wachstum"],
   nav=[("#work", "Arbeiten"), ("#services", "Leistungen"), ("#process", "Ablauf"), ("#why", "Über uns"), ("#contact", "Kontakt")],
   alt="Gläserne AIK-Buchstaben zwischen verschneiten Gipfeln über einem Wolkenmeer bei Sonnenuntergang"),
}
def hero(c):
    b = c["b"]; m = b + "media/hero/"
    h = "".join(f'<span><span class="{k}" style="--d:{120*i}">{t}</span></span>' for i, (k, t) in enumerate(c["h"]))
    pil = "".join(f'<li data-in style="--d:{900+i*90}"><b>0{i+1}</b><span>{p}</span></li>' for i, p in enumerate(c["pillars"]))
    return f'''<section class="hero3" id="top" aria-labelledby="hero-title" data-media="{m}">
    <div class="hero3__stage">
      <div class="hero3__plate"><img src="{m}hero3-plate-1920.webp" srcset="{m}hero3-plate-1280.webp 1280w, {m}hero3-plate-1920.webp 1920w, {m}hero3-plate-2880.webp 2880w, {m}hero3-plate-3840.webp 3840w" sizes="104vw" alt="{c["alt"]}" width="1920" height="1060" fetchpriority="high" decoding="async"></div>
      <div class="hero3__sun" aria-hidden="true"></div>
      <div class="hero3__sweep" aria-hidden="true"></div>
      <div class="hero3__veil" aria-hidden="true"></div>
      <div class="hero3__copy">
        <p class="hero3__eyebrow" data-in style="--d:0"><i></i><span>{c["eyebrow"]}</span></p>
        <h1 class="hero3__title" id="hero-title"><span class="visually-hidden">AIK Studio — </span>{h}</h1>
        <p class="hero3__lead" data-in style="--d:420">{c["lead"]}</p>
        <div class="hero3__ctas" data-in style="--d:560">
          <a class="h3btn h3btn--solid" href="#contact">{c["cta1"]} <span aria-hidden="true">→</span></a>
          <a class="h3btn h3btn--play" href="#work"><i aria-hidden="true"></i>{c["cta2"]}</a>
        </div>
      </div>
      <a class="hero3__scroll" href="#work" data-in style="--d:800"><span>{c["scroll"]}<b aria-hidden="true">↓</b></span></a>
      <ol class="hero3__pillars">{pil}</ol>
      <button class="hero3__skip" type="button">{c["skip"]}</button>
    </div>
  </section>'''

for lang, path in [("en", "index.html"), ("de", "de/index.html")]:
    c = T[lang]; b = c["b"]; m_ = b + "media/hero/"; fp = f"{ROOT}/{path}"; s = open(fp).read()
    m = re.search(r'<section class="hero[23]".*?</section>', s, re.S)
    s = s[:m.start()] + hero(c) + s[m.end():]
    nav = "".join(f'<li><a href="{h}">{x}</a></li>' for h, x in c["nav"])
    s = re.sub(r'<ul class="nav__list">.*?</ul>', f'<ul class="nav__list">{nav}</ul>', s, count=1, flags=re.S)
    s = re.sub(r'<link rel="preload" as="image" href="[^"]*intro-first.webp">', f'<link rel="preload" as="image" href="{b}media/hero/hero3-plate-1920.webp" imagesrcset="{b}media/hero/hero3-plate-1280.webp 1280w, {b}media/hero/hero3-plate-1920.webp 1920w, {b}media/hero/hero3-plate-2880.webp 2880w" imagesizes="104vw" fetchpriority="high">', s)
    if 'hero3.css' not in s:
        s = s.replace(f'<link rel="stylesheet" href="{b}css/hero.css">', f'<link rel="stylesheet" href="{b}css/hero.css">\n<link rel="stylesheet" href="{b}css/hero3.css">')
    if 'polish.css' not in s:
        s = s.replace(f'<link rel="stylesheet" href="{b}css/v2.css">', f'<link rel="stylesheet" href="{b}css/v2.css">\n<link rel="stylesheet" href="{b}css/polish.css">')
    if 'craft.css' not in s:
        s = s.replace(f'<link rel="stylesheet" href="{b}css/polish.css">', f'<link rel="stylesheet" href="{b}css/polish.css">\n<link rel="stylesheet" href="{b}css/craft.css">')
    if 'system3.css' not in s:
        s = s.replace(f'<link rel="stylesheet" href="{b}css/craft.css">', f'<link rel="stylesheet" href="{b}css/craft.css">\n<link rel="stylesheet" href="{b}css/system3.css">')
    if 'v4.css' not in s:
        s = s.replace(f'<link rel="stylesheet" href="{b}css/system3.css">', f'<link rel="stylesheet" href="{b}css/system3.css">\n<link rel="stylesheet" href="{b}css/v4.css">')
    s = s.replace(f'<link rel="stylesheet" href="{b}css/liquid-nav.css">\n', '').replace(f'<script src="{b}js/liquid-nav.js" defer></script>\n', '')
    if 'craft.js' not in s:
        s = s.replace('</body>', f'<script src="{b}js/craft.js" defer></script>\n</body>')
    s = s.replace(f'{b}fonts/inter-latin-wght-normal.woff2', f'{b}fonts/outfit-latin-wght-normal.woff2')
    s = s.replace('hero3-plate-2880.webp 2880w"', 'hero3-plate-2880.webp 2880w, ' + m_ + 'hero3-plate-3840.webp 3840w"')
    s = s.replace(f'<script src="{b}js/hero.js" defer></script>', f'<script src="{b}js/hero3.js" defer></script>')
    if 'icon-48.png' not in s:
        t = re.search(r'<title>(.*?)</title>', s).group(1); d = re.search(r'<meta name="description" content="(.*?)"', s).group(1)
        s = s.replace('</title>', '</title>\n<link rel="icon" type="image/png" sizes="48x48" href="' + b + 'media/logo/icon-48.png">\n<link rel="apple-touch-icon" href="' + b + 'media/logo/icon-180.png">\n<meta name="theme-color" content="#0d1116">\n<meta property="og:type" content="website">\n<meta property="og:title" content="' + t + '">\n<meta property="og:description" content="' + d + '">\n<meta property="og:image" content="' + b + 'media/og.jpg">\n<meta name="twitter:card" content="summary_large_image">', 1)
    open(fp, "w").write(s)
    print(lang, "ok", s.count("hero3"), "hero.js" in s)
