/* AIK Studio — Hero + flight. Styles: css/flight.css. Media: media/flight2/
   (edit: tools/edit_flight.py, frame marks in edit-marks.json).

   Scroll position inside .flight (0..1) drives everything:
     0.00–0.10  the Hero lifts away (--out)
     0.06–0.97  the flight is scrubbed 0..1 (eased towards the target, so a
                flick of the wheel glides instead of jumping)
     captions   fade in and out on fixed parts of the film (CAPTIONS)
   Desktop: an all-intra <video> (every frame a keyframe, exact seeks), loaded
   through the loader so the counter counts it. Phones (portrait): 146 WebP
   frames drawn on a canvas with a cross-fade between neighbours.
   Reduced motion: the Hero on the first frame, nothing else. */
(() => {
  const root = document.documentElement;
  const sec = document.querySelector('.flight');
  if (!sec) return;
  const header = document.querySelector('.site-header');
  const loader = window.AIK_LOADER;
  const showChrome = () => { sec.classList.add('is-on'); header && header.classList.remove('is-cine-hidden'); };

  if (!root.classList.contains('cine-on')) { showChrome(); return; }

  const MEDIA = sec.dataset.media;
  const stage = sec.querySelector('.flight__stage');
  const hero = sec.querySelector('.flight__hero');
  const video = sec.querySelector('.flight__video');
  const canvas = sec.querySelector('.flight__canvas');
  const poster = sec.querySelector('.flight__poster');
  const caps = [...sec.querySelectorAll('.flight__caption')];

  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const smooth = (a, b, v) => { const t = clamp((v - a) / (b - a)); return t * t * (3 - 2 * t); };

  // Caption windows in film progress (0..1). Film: 292 frames, A ends 153,
  // cloud 153–173, canyon 173–266, fade to page 266–292.
  const CAPTIONS = [[0.08, 0.40], [0.48, 0.74], [0.79, 0.95]];
  const FADE_IN = 0.035, FADE_OUT = 0.04;

  const portrait = matchMedia('(max-aspect-ratio: 4/5)').matches;
  const FRAMES = 146;
  let mode = portrait ? 'frames' : 'video';
  let duration = 292 / 24;

  /* ----------------------------------------------------- media */
  let frames = [];
  let lastDrawn = -1;
  const ctx = canvas.getContext('2d', { alpha: false });
  const sizeCanvas = () => {
    const dpr = Math.min(devicePixelRatio || 1, 2);
    canvas.width = Math.round(stage.clientWidth * dpr);
    canvas.height = Math.round(stage.clientHeight * dpr);
    lastDrawn = -1;
  };

  const loadImg = (src) => new Promise((res) => {
    const im = new Image(); im.decoding = 'async';
    im.onload = () => (im.decode ? im.decode().catch(() => {}).then(() => res(im)) : res(im));
    im.onerror = () => res(null);
    im.src = src;
  });

  if (mode === 'frames') {
    video.remove();
    const url = (i) => `${MEDIA}frames-portrait/f${String(i + 1).padStart(3, '0')}.webp`;
    frames = new Array(FRAMES).fill(null);
    // the first second is part of the loading screen, the rest streams in behind it
    const first = 16;
    const head = Promise.all([...Array(first)].map((_, i) => loadImg(url(i)).then((im) => { frames[i] = im; })));
    if (loader) loader.track(head, 4);
    head.then(async () => {
      for (let i = first; i < FRAMES; i += 6) {
        await Promise.all([...Array(Math.min(6, FRAMES - i))].map((_, k) => loadImg(url(i + k)).then((im) => { frames[i + k] = im; })));
      }
    });
    sizeCanvas();
    addEventListener('resize', sizeCanvas);
  } else {
    canvas.remove();
    const src = MEDIA + 'flight-scrub-1280.mp4';
    const attach = (u) => {
      video.src = u;
      video.addEventListener('loadedmetadata', () => { duration = video.duration || duration; }, { once: true });
      video.addEventListener('loadeddata', () => { poster.style.opacity = '0'; }, { once: true });
    };
    if (loader) loader.fetch(src, 8).then(attach, () => attach(src));
    else attach(src);
  }

  /* ----------------------------------------------------- frame drawing (phones) */
  const nearest = (i) => {
    if (frames[i]) return i;
    for (let d = 1; d < FRAMES; d++) {
      if (frames[i - d]) return i - d;
      if (frames[i + d]) return i + d;
    }
    return -1;
  };
  const drawFrames = (v) => {
    const f = v * (FRAMES - 1);
    const key = Math.round(f * 8);
    if (key === lastDrawn) return;
    lastDrawn = key;
    const i0 = nearest(Math.floor(f)), i1 = nearest(Math.min(FRAMES - 1, Math.ceil(f)));
    if (i0 < 0) return;
    const W = canvas.width, H = canvas.height;
    const draw = (im, a) => {
      const s = Math.max(W / im.naturalWidth, H / im.naturalHeight);
      const w = im.naturalWidth * s, h = im.naturalHeight * s;
      ctx.globalAlpha = a;
      ctx.drawImage(im, (W - w) / 2, (H - h) * 0.45, w, h);
    };
    draw(frames[i0], 1);
    const t = f - Math.floor(f);
    if (i1 !== i0 && t > 0.01) draw(frames[i1], t);
    ctx.globalAlpha = 1;
    if (canvas.style.opacity !== '1') canvas.style.opacity = '1';
  };

  /* ----------------------------------------------------- video seeking (desktop) */
  let seekTarget = 0, seeking = false;
  const seek = (t) => {
    seekTarget = t;
    if (seeking || video.readyState < 1) return;
    if (Math.abs(video.currentTime - t) < 1 / 48) return;
    seeking = true;
    video.currentTime = t;
  };
  video.addEventListener('seeked', () => {
    seeking = false;
    if (Math.abs(video.currentTime - seekTarget) >= 1 / 48) seek(seekTarget);
  });

  /* ----------------------------------------------------- scroll → state */
  let top = 0, len = 1, pTarget = 0, vNow = 0;
  const measure = () => {
    const r = sec.getBoundingClientRect();
    top = r.top + scrollY;
    len = Math.max(1, sec.offsetHeight - innerHeight);
  };
  const read = () => { pTarget = clamp((scrollY - top) / len); };

  const render = () => {
    const p = pTarget;
    const out = smooth(0.0, 0.10, p);
    sec.style.setProperty('--out', out.toFixed(3));
    hero.classList.toggle('is-gone', out > 0.98);

    const vTarget = clamp((p - 0.06) / 0.91);
    vNow += (vTarget - vNow) * 0.14;
    if (Math.abs(vTarget - vNow) < 0.0004) vNow = vTarget;

    if (mode === 'frames') drawFrames(vNow);
    else seek(vNow * Math.max(0, duration - 0.01));

    caps.forEach((c, i) => {
      const [a, b] = CAPTIONS[i];
      const op = smooth(a, a + FADE_IN, vNow) * (1 - smooth(b - FADE_OUT, b, vNow));
      c.style.setProperty('--a', op.toFixed(3));
      c.setAttribute('aria-hidden', op < 0.5 ? 'true' : 'false');
    });
    sec.style.setProperty('--v', vNow.toFixed(4));
    sec.style.setProperty('--rail', (smooth(0.08, 0.14, p) * (1 - smooth(0.9, 0.97, p))).toFixed(3));
    requestAnimationFrame(render);
  };

  measure(); read();
  addEventListener('resize', () => { measure(); read(); });
  addEventListener('scroll', read, { passive: true });
  addEventListener('load', measure);

  const start = () => { showChrome(); requestAnimationFrame(render); };
  if (loader) loader.done.then(start); else start();
})();
