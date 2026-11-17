/* AIK Studio — loader. Markup and styles: index.html (.aik-loader), css/loader.css.

   Progress is real: every item the opening needs is registered with a weight,
   and large files report their bytes as they stream in. Other scripts can add
   items before the loader finishes:

     AIK_LOADER.track(promise, weight)      // counts when the promise settles
     AIK_LOADER.fetch(url, weight)          // counts bytes; resolves to a Blob URL
     AIK_LOADER.done                        // resolves when the screen has opened

   The counter never runs ahead of the real progress, and never jumps: it eases
   towards it, so a fast connection still shows the trace (min. ~1.4 s). A
   failed item counts as loaded (the page decides what to do without it);
   after 12 s the loader opens regardless. */
(() => {
  const root = document.documentElement;
  const el = document.querySelector('.aik-loader');
  let resolveDone;
  const done = new Promise((r) => { resolveDone = r; });

  if (!el) {
    window.AIK_LOADER = { track: (p) => p, fetch: (u) => Promise.resolve(u), done: Promise.resolve() };
    return;
  }

  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let quick = false;
  // No storage here: remembering that the intro was seen is not something the visitor asked for (§ 25 TDDDG).
  if (quick) el.classList.add('is-quick');

  const mark = el.querySelector('.aik-loader__mark');
  const count = el.querySelector('.aik-loader__count');

  // WebGL scene (js/loader-gl.js) when available; otherwise the SVG version.
  let glr = null;
  if (!reduce && window.AIK_LOADER_GL) {
    try { glr = window.AIK_LOADER_GL(el, el.dataset.tex); } catch (e) { glr = null; }
  }

  /* ---------------------------------------------------- horizon position */
  // The line sits in the gap between the mountains and STUDIO (82.6% of the lockup).
  const placeHorizon = () => {
    const r = glr ? (({ y, h }) => ({ top: y, height: h }))(glr.rect()) : mark.getBoundingClientRect();
    const y = r.top + r.height * 0.826;
    el.style.setProperty('--horizon', `${Math.round(y)}px`);
  };
  placeHorizon();
  addEventListener('resize', placeHorizon);

  /* ---------------------------------------------------- progress model */
  const items = [];                                   // { w, f }  weight, fraction 0..1
  let finished = false;

  const add = (w) => { const it = { w, f: 0 }; items.push(it); return it; };
  const real = () => {
    const tw = items.reduce((s, i) => s + i.w, 0);
    return tw ? items.reduce((s, i) => s + i.w * i.f, 0) / tw : 0;
  };

  const track = (promise, w = 1) => {
    const it = add(w);
    return Promise.resolve(promise).then(
      (v) => { it.f = 1; return v; },
      (e) => { it.f = 1; throw e; },
    );
  };

  const fetchTracked = async (url, w = 4) => {
    const it = add(w);
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(res.status);
      const total = +res.headers.get('content-length') || 0;
      if (!res.body || !total) { const b = await res.blob(); it.f = 1; return URL.createObjectURL(b); }
      const reader = res.body.getReader();
      const chunks = []; let got = 0;
      for (;;) {
        const { done: d, value } = await reader.read();
        if (d) break;
        chunks.push(value); got += value.length;
        it.f = Math.min(0.999, got / total);
      }
      it.f = 1;
      return URL.createObjectURL(new Blob(chunks, { type: res.headers.get('content-type') || '' }));
    } catch (e) { it.f = 1; throw e; }
  };

  /* ---------------------------------------------------- what the loader waits for */
  const decode = (img) => (img.complete ? (img.decode ? img.decode().catch(() => {}) : 0)
    : new Promise((r) => { img.addEventListener('load', r, { once: true }); img.addEventListener('error', r, { once: true }); }));

  el.querySelectorAll('image').forEach((im) => {                       // the lockup itself
    const img = new Image(); img.src = im.getAttribute('href'); track(decode(img), 2);
  });
  if (glr) track(glr.texLoaded, 3);
  track(document.fonts ? Promise.race([document.fonts.ready, new Promise((r) => setTimeout(r, 400))]) : 0, 1);

  /* ---------------------------------------------------- render loop */
  const t0 = performance.now();
  const MIN_MS = reduce ? 0 : quick ? 150 : 300;                  // short: the site is the show, not the loader
  const MAX_MS = 700;                                            // hard cap: never hold the site hostage
  let shown = 0, last = t0, readyAt = 0, exitAt = 0, gone = false;
  const EXIT_MS = 320;
  const PACE = 4.5;                                              // loader-gl timeline speed-up

  const tick = (now) => {
    const dt = Math.min(64, now - last); last = now;
    const elapsed = now - t0;
    let target = real();
    if (elapsed > MAX_MS) target = 1;
    // never faster than MIN_MS for the full trace, never ahead of reality
    const cap = MIN_MS ? elapsed / MIN_MS : 1;
    target = Math.min(target, cap);
    shown += (target - shown) * (1 - Math.exp(-dt / 40));
    if (target >= 1 && 1 - shown < 0.03) shown = 1;
    el.style.setProperty('--p', shown.toFixed(4));
    if (count) count.textContent = String(Math.round(shown * 100)).padStart(3, '0');
    if (glr) glr.draw(shown, now / 1000, readyAt ? (now - readyAt) / 1000 * PACE : -1, exitAt ? Math.min(1, (now - exitAt) / EXIT_MS) : 0);
    if (shown >= 1 && !finished) ready();
    if (!gone) requestAnimationFrame(tick);
  };

  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const ready = async () => {
    if (finished) return; finished = true;
    el.classList.add('is-ready');
    readyAt = performance.now();
    await wait(reduce ? 150 : quick ? 80 : glr ? 140 : 200);   // exposure, light sweep, glints, STUDIO
    el.classList.add('is-leaving');
    exitAt = performance.now();
    if (glr) await wait(EXIT_MS * 0.35);                // the push into the light, then the page beneath
    root.classList.remove('is-loading');
    root.classList.add('is-loaded');
    resolveDone();
    document.dispatchEvent(new CustomEvent('aik:loaded'));
    await wait(reduce ? 250 : glr ? EXIT_MS * 0.7 : 400);
    gone = true;
    el.hidden = true;
    el.setAttribute('aria-hidden', 'true');
  };

  window.AIK_LOADER = { track, fetch: fetchTracked, done };
  requestAnimationFrame(tick);
})();
