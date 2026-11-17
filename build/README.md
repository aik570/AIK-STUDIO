# AIK Studio website

Plain HTML, CSS and JavaScript. No framework, no build step at runtime, no third-party requests.
English at `/`, German at `/de/`.

## Edit and rebuild

All copy for both languages lives in one table in `tools/build_site.py`. After editing it:

```
python3 tools/build_site.py .
python3 -m http.server 8765        # then open http://localhost:8765
```

| File | What it does |
|---|---|
| `tools/build_site.py` | writes `index.html` and `de/index.html` (all sections, the enquiry, header, footer) |
| `tools/partials/loader.html` | the ~0.6 s loader markup, shared by both pages |
| `css/aik.css` | the whole design system: one mountain world behind the page, frosted glass, Jost + Inter (loader keeps `css/loader.css`) |
| `js/hero4.js` | Hero: photo in three depths, glass AIK in WebGL, eagle flight on desktop |
| `js/aik.js` | menu, reveals, word highlight, stacked cards, work rail, process, calculator, six-step enquiry |
| `js/loader.js`, `js/loader-gl.js` | the loader |
| `tools/hero_plate.py` | builds `media/hero4/*` from one landscape photo + its traced skyline (`media/hero4/ridge.json`) |
| `tools/make_world.py` | the landscapes behind the sections (`media/world/*`) and the tall stills (`media/stills/*`), all AIK's own frames, graded to one palette |

## Replace the Hero photo

1. Put the original file in `../sources/`.
2. Trace its skyline into `media/hero4/ridge.json` (points in the photo's pixels, left to right).
3. `python3 tools/hero_plate.py ../sources/<photo> media/hero4/ridge.json media/hero4`
4. `python3 tools/build_site.py .`

## Enquiry form

Six steps (need, goal, start, budget, call or request, contact). On Netlify it is sent with
Netlify Forms (`data-netlify`, form name `project`); the notification e-mail is set in the
Netlify dashboard, so no address is in the code. If sending fails (or locally, where there is
no form backend) the visitor gets the same answers as a ready WhatsApp message to +49 1522 1595565.

## Open before launch

- Impressum and Datenschutz: address, e-mail, VAT status (marked in the pages).
- Founder photo for "Why AIK" (now the eagle still).
- Handy-Chirurg: a screenshot for its card (now a text card linking to handychirurg.de).
- Original Hero photo in full resolution (the current one is 1672 px wide).
- Domain: canonical URL, sitemap, absolute og:image.
