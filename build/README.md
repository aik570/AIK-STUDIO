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

## Legal (researched Nov 2026, not legal advice)

`tools/build_legal.py` writes Impressum and Datenschutz from one table (`OWNER`). Fill in:
name exactly as registered, a serviceable postal address (no P.O. box), e-mail, USt-IdNr. or
Wirtschafts-IdNr. if one exists, and the host. Gaps show on the pages and block publishing.
Set `TAX` in `tools/build_site.py` (`'kleinunternehmer'` or `'ust'`) for the price note (PAngV).

Already handled: no OS-platform link (platform closed 20 Jul 2025); voluntary VSBG sentence;
no cookies, no tracking, no third-party fonts or scripts; the only browser storage is the
"pause motion" choice, written only when the visitor presses it (§ 25 Abs. 2 Nr. 2 TDDDG);
"Recommended" instead of an unverifiable "Most chosen" (UWG § 5); the studio sets up legal
pages, the texts come from a generator or a lawyer (RDG); softer wording in the comparison.
Still to check: Netlify DPF status and the signed DPA; rights to show MA’LOA / Architekturcontor
logos and photos in the portfolio; both texts once with a legal-text generator or a lawyer.

## Deploy and security

`netlify.toml` (repo root) builds `build/dist` with `tools/dist.py`: only the pages and the files
they use, plus `_headers` and `robots.txt`. `dist.py` refuses to publish while legal gaps or the
price note are open (`ALLOW_DRAFT=1` for a private preview) and fails on inline scripts, inline
event handlers or `target=_blank` links without `rel="noopener"`.

`_headers`: strict Content-Security-Policy (only own files, no inline script), no framing,
nosniff, referrer policy, permissions policy, COOP/CORP, HSTS. Checked locally with the same
headers: 0 policy violations on all pages at 1440 and 390 px.

Accounts: turn on two-factor login for GitHub, Netlify and the domain registrar.
The dev test kit (`package.json`, `tests/`) is never deployed; it targets the old markup and its
lighthouse dependency has open advisories, so don't run `npm install` there without updating it.

## Open before launch

- Impressum and Datenschutz: address, e-mail, VAT status (marked in the pages).
- Founder photo: media/founder/nikolay-riabov.webp (source in ../sources/founder-original.png; the supplied file is about 640 px wide, a larger original would look sharper on Retina).
- Handy-Chirurg: a screenshot for its card (now a text card linking to handychirurg.de).
- Original Hero photo in full resolution (the current one is 1672 px wide).
- Domain: canonical URL, sitemap, absolute og:image.
