/* AIK Studio — cinematic opening (homepage only).

   Part A plays once, on one canvas:
     logo      the approved logo animation (media/intro), untouched
     reveal    a band of light crosses the letters; the empty mountain plate
               appears inside the metal
     through   the letters open up into that landscape
     film      the clips listed in flight.json → "film", chained on matching
               frames (eagle flies in, eagle shot, recedes into the valley,
               settles on the Hero). Replacing the eagle footage means editing
               that list only: nothing here depends on a clip's length or size.
     pullback  phones only: the camera eases back from the last film frame to
               the full-screen portrait Hero
     hero      the Hero still; STUDIO, then the nav
   Part B: scrolling pushes gently into the Hero while two layers of real fog
   drift past at different speeds, and the scene darkens into the next block.

   If the logo video cannot be played the opening says so (console error,
   data-intro="logo-failed") and starts at the film; it never fakes the logo.
   Reduced motion or no script: the Hero still with STUDIO and the nav. */
(() => {
  const root = document.documentElement;
  const cine = document.querySelector('.cine');
  if (!cine || !root.classList.contains('cine-on')) return;

  const stage = cine.querySelector('.cine__stage');
  const canvas = cine.querySelector('.cine__canvas');
  const studio = cine.querySelector('.cine__studio');
  const skip = cine.querySelector('.cine__skip');
  const header = document.querySelector('.site-header');
  const ctx = canvas.getContext('2d', { alpha: false });
  const MEDIA = cine.dataset.media;                    // "./media/" or "../media/"

  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const smooth = (a, b, v) => { const t = clamp((v - a) / (b - a)); return t * t * (3 - 2 * t); };
  const easeInOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const isPortrait = innerWidth / innerHeight < 0.8;

  /* ------------------------------------------------------------ canvas */
  let W = 0, H = 0, dpr = 1;
  const fx = document.createElement('canvas');          // reveal compositing
  const fxc = fx.getContext('2d');
  const resize = () => {
    const cw = stage.clientWidth, ch = stage.clientHeight;
    dpr = Math.min(devicePixelRatio || 1, 2, 2560 / cw);
    W = Math.round(cw * dpr);
    H = Math.round(ch * dpr);
    canvas.width = fx.width = W;
    canvas.height = fx.height = H;
  };

  const sizeOf = (src) => ({
    w: src.videoWidth || src.naturalWidth || src.width,
    h: src.videoHeight || src.naturalHeight || src.height,
  });

  // Full-screen cover, with the point focusX (fraction of the source width)
  // kept as close to the centre of the screen as the edges allow.
  const cover = (w, h, zoom = 1, focusX = 0.5) => {
    const s = Math.max(W / w, H / h) * zoom;
    const dw = w * s, dh = h * s;
    return { dx: clamp(W / 2 - focusX * dw, W - dw, 0), dy: (H - dh) / 2, dw, dh };
  };
  const drawAt = (c, src, r, alpha = 1) => {
    if (alpha <= 0) return;
    c.globalAlpha = alpha;
    c.drawImage(src, r.dx, r.dy, r.dw, r.dh);
    c.globalAlpha = 1;
  };
  const drawScene = (c, src, alpha = 1, zoom = 1, focusX = 0.5) => {
    const { w, h } = sizeOf(src);
    if (w && h) drawAt(c, src, cover(w, h, zoom, focusX), alpha);
  };

  /* ------------------------------------------------------------ logo geometry */
  // The logo video is 1920 x 1080 on a flat rgb(29 33 37) ground; the lockup
  // sits inside LOGO_BOX. It reads at about 62% of the width on landscape and
  // 84% on a phone.
  const LOGO_BG = 'rgb(29 33 37)';
  const LOGO_BOX = { x: 405, y: 250, w: 1260, h: 575 };
  const logoTransform = (zoom = 1) => {
    let s = (W * (isPortrait ? 0.84 : 0.62)) / LOGO_BOX.w;
    s = Math.min(s, (H * 0.5) / LOGO_BOX.h) * zoom;
    const cx = LOGO_BOX.x + LOGO_BOX.w / 2;
    const cy = LOGO_BOX.y + LOGO_BOX.h * 0.42;            // zoom toward the I of AIK
    return { s, dx: W / 2 - cx * s, dy: H / 2 - cy * s };
  };
  const drawLogo = (c, src, zoom = 1) => {
    const t = logoTransform(zoom);
    c.drawImage(src, t.dx, t.dy, 1920 * t.s, 1080 * t.s);
  };

  // The logo's last frame, keyed off its ground: on black (for multiply and
  // screen) and as alpha (to clip the landscape to the letters).
  let logoKey = null, logoAlpha = null;
  const keyLogo = (video) => {
    const k = document.createElement('canvas');
    k.width = 1920; k.height = 1080;
    const kc = k.getContext('2d', { willReadFrequently: true });
    kc.drawImage(video, 0, 0, 1920, 1080);
    let img;
    try { img = kc.getImageData(0, 0, 1920, 1080); } catch (e) { return false; }
    const d = img.data;
    const a = document.createElement('canvas');
    a.width = 1920; a.height = 1080;
    const ac = a.getContext('2d');
    const al = ac.createImageData(1920, 1080);
    const o = al.data;
    for (let i = 0; i < d.length; i += 4) {
      const r = Math.max(0, (d[i] - 29) / 226);
      const g = Math.max(0, (d[i + 1] - 33) / 222);
      const b = Math.max(0, (d[i + 2] - 37) / 218);
      d[i] = r * 255; d[i + 1] = g * 255; d[i + 2] = b * 255;
      o[i] = o[i + 1] = o[i + 2] = 255;
      o[i + 3] = Math.min(1, Math.max(r, g, b) * 1.6) * 255;
    }
    kc.putImageData(img, 0, 0);
    ac.putImageData(al, 0, 0);
    logoKey = k; logoAlpha = a;
    return true;
  };

  // The landscape inside the letters, with the letters' own metal shading kept.
  const drawLettersWithScene = (scene, zoom, wipe, alpha) => {
    if (!logoKey || alpha <= 0) return;
    const t = logoTransform(zoom);
    fxc.globalCompositeOperation = 'source-over';
    fxc.clearRect(0, 0, W, H);
    fxc.filter = 'brightness(1.45) contrast(1.05)';
    drawScene(fxc, scene);
    fxc.filter = 'none';
    fxc.globalCompositeOperation = 'multiply';
    fxc.drawImage(logoKey, t.dx, t.dy, 1920 * t.s, 1080 * t.s);
    fxc.globalCompositeOperation = 'destination-in';
    fxc.drawImage(logoAlpha, t.dx, t.dy, 1920 * t.s, 1080 * t.s);
    if (wipe < 1) {
      const g = fxc.createLinearGradient(0, H * 0.2, W, H * 0.8);
      const e = -0.25 + wipe * 1.5;
      g.addColorStop(clamp(e - 0.25), 'rgba(0,0,0,1)');
      g.addColorStop(clamp(e), 'rgba(0,0,0,1)');
      g.addColorStop(clamp(e + 0.2), 'rgba(0,0,0,0)');
      fxc.fillStyle = g;
      fxc.fillRect(0, 0, W, H);
    }
    fxc.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = alpha;
    ctx.drawImage(fx, 0, 0);
    ctx.globalAlpha = 1;
  };

  /* ------------------------------------------------------------ media */
  const makeVideo = (src) => {
    const v = document.createElement('video');
    v.muted = true; v.defaultMuted = true;
    v.playsInline = true;
    v.setAttribute('playsinline', '');
    v.setAttribute('muted', '');
    v.preload = 'auto';
    v.src = src;
    return v;
  };
  const loadImage = (src) => new Promise((res, rej) => {
    const i = new Image();
    i.decoding = 'async';
    i.onload = () => res(i);
    i.onerror = rej;
    i.src = src;
  });
  const canDraw = (v) => v && v.readyState >= 2 && !v.error;
  const playSafe = (v) => {
    try { const p = v.play(); return p && p.catch ? p.then(() => true, () => false) : Promise.resolve(true); }
    catch (e) { return Promise.resolve(false); }
  };
  const seekTo = (v, t) => new Promise((res) => {
    if (Math.abs(v.currentTime - t) < 0.01 && v.readyState >= 2) return res();
    v.addEventListener('seeked', () => res(), { once: true });
    v.currentTime = t;
  });

  let logoV = null, plate = null, chain = [];

  /* ------------------------------------------------------------ the Hero frame */
  // Landscape: the 16:9 Hero still. Phones: the portrait Hero, whose `inner`
  // rectangle (fractions) holds the original 16:9 frame pixel for pixel, so
  // the film's last frame lines up with it. Positions given in Hero-frame
  // fractions (focus, STUDIO) are mapped through `inner`.
  let hero = null;            // { img, inner: [x0, y0, x1, y1], focusX }
  let STUDIO = { x: 0.372, y: 0.535, size: 0.0405 };
  const LETTERS_X = isPortrait ? 0.348 : 0.372;          // centre of A…K in the Hero frame

  const heroInPx = () => {
    const { w, h } = sizeOf(hero.img);
    const [x0, y0, x1, y1] = hero.inner;
    return { x: x0 * w, y: y0 * h, w: (x1 - x0) * w, h: (y1 - y0) * h, iw: w, ih: h };
  };
  const heroRect = (zoom = 1) => {
    const r = heroInPx();
    const focus = (r.x + LETTERS_X * r.w) / r.iw;
    return cover(r.iw, r.ih, zoom, focus);
  };
  // Map a point of the original 16:9 frame (fractions) onto the screen.
  const heroPoint = (rect, fxp, fyp) => {
    const r = heroInPx();
    const s = rect.dw / r.iw;
    return { x: rect.dx + (r.x + fxp * r.w) * s, y: rect.dy + (r.y + fyp * r.h) * s, s: r.w * s };
  };
  const placeTitle = (rect) => {
    if (!hero || !rect) return;
    const p = heroPoint(rect, STUDIO.x, STUDIO.y);
    const st = studio.style;
    st.setProperty('--x', (p.x / dpr).toFixed(1) + 'px');
    st.setProperty('--y', (p.y / dpr).toFixed(1) + 'px');
    st.setProperty('--size', ((STUDIO.size * p.s) / dpr).toFixed(1) + 'px');
  };

  /* ------------------------------------------------------------ state */
  // 'logo' → 'reveal' → 'through' → 'film' → ('pullback') → 'hero'
  let state = 'boot', stateAt = performance.now(), clip = 0, logoEndedAt = 0;
  const REVEAL_MS = 1500, THROUGH_MS = 1900, PULLBACK_MS = 1800;
  const setState = (s) => {
    state = s; stateAt = performance.now(); cine.dataset.state = s;
    if (s === 'hero' && skip) skip.hidden = true;
  };

  const showTitle = () => cine.classList.add('is-titled');
  const showNav = () => header && header.classList.remove('is-cine-hidden');

  // Skip, failure or a mid-page arrival: settle straight on the Hero.
  let handoff = null;
  const settle = (reason) => {
    if (state === 'hero') return;
    if (W && H && state !== 'boot') {
      const snap = document.createElement('canvas');
      snap.width = W; snap.height = H;
      snap.getContext('2d').drawImage(canvas, 0, 0);
      handoff = { img: snap, at: performance.now() };
    }
    if (logoV) logoV.pause();
    chain.forEach((c) => c.v.pause());
    setState('hero');
    showTitle();
    setTimeout(showNav, reason === 'scroll' || reason === 'skip' ? 0 : 900);
  };

  const logoFailed = (why) => {
    if (state !== 'logo' && state !== 'boot') return;
    cine.dataset.intro = 'logo-failed';
    console.error(`[AIK intro] The logo video could not be played (${why}): ${MEDIA}${manifest.intro}. Starting at the film without the logo.`);
    startFilm();
  };

  /* ------------------------------------------------------------ scroll */
  let pTarget = 0, p = 0, lastT = performance.now();
  const measure = () => {
    const r = cine.getBoundingClientRect();
    const range = cine.offsetHeight - stage.offsetHeight;
    pTarget = range > 0 ? clamp(-r.top / range) : 0;
  };
  const onScroll = () => {
    measure();
    if (pTarget > 0.002 && state !== 'hero') settle('scroll');
    if (pTarget > 0.002) showNav();
  };

  /* ------------------------------------------------------------ render */
  let filmEndRect = null, filmEndFrame = null;

  const frame = (now) => {
    requestAnimationFrame(frame);
    const dt = Math.min(0.1, (now - lastT) / 1000);
    lastT = now;
    p += (pTarget - p) * (1 - Math.exp(-dt / 0.09));
    if (Math.abs(pTarget - p) < 0.0004) p = pTarget;
    const el = now - stateAt;

    if (state === 'logo') {
      ctx.fillStyle = LOGO_BG; ctx.fillRect(0, 0, W, H);
      if (canDraw(logoV)) drawLogo(ctx, logoV);
      if (logoV.ended || logoV.currentTime >= (logoV.duration || 5) - 0.05) {
        if (!logoEndedAt) logoEndedAt = now;
        if (plate && keyLogo(logoV)) setState('reveal');
        else if (now - logoEndedAt > 3000) startFilm();
      }
    } else if (state === 'reveal') {
      const r = clamp(el / REVEAL_MS);
      ctx.fillStyle = LOGO_BG; ctx.fillRect(0, 0, W, H);
      drawScene(ctx, plate, 0.12 * r, 1.06);
      drawLogo(ctx, logoV);
      drawLettersWithScene(plate, 1, easeInOut(r), 1);
      if (r >= 1) setState('through');
    } else if (state === 'through') {
      const u = clamp(el / THROUGH_MS);
      const e = easeInOut(u);
      const zoom = 1 + 1.9 * Math.pow(e, 1.6);
      ctx.fillStyle = LOGO_BG; ctx.fillRect(0, 0, W, H);
      drawScene(ctx, plate, 0.12 + 0.88 * smooth(0.18, 0.95, u), 1.06 - 0.06 * e);
      const t = logoTransform(zoom);
      ctx.globalCompositeOperation = 'screen';
      ctx.globalAlpha = 0.45 * (1 - smooth(0.35, 0.9, u));
      ctx.drawImage(logoKey, t.dx, t.dy, 1920 * t.s, 1080 * t.s);
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = 'source-over';
      drawLettersWithScene(plate, zoom, 1, 1 - smooth(0.4, 0.92, u));
      if (u >= 1) startFilm();
    } else if (state === 'film') {
      const c = chain[clip];
      const focus = c.framing === 'hero' ? LETTERS_X : 0.5;
      if (canDraw(c.v)) drawScene(ctx, c.v, 1, 1, focus);
      const end = c.to != null ? c.to : (c.v.duration || Infinity) - 0.03;
      // landscape: STUDIO settles in over the end of the film; phones: after the pull-back
      if (!hero.portrait && c.titleBeforeEnd != null && c.v.duration && end - c.v.currentTime <= c.titleBeforeEnd) showTitle();
      if (c.v.ended || c.v.currentTime >= end) {
        if (clip < chain.length - 1) {
          clip++;
          playSafe(chain[clip].v).then((ok) => { if (!ok) settle('fail'); });
          c.v.pause();
        } else if (hero.portrait && canDraw(c.v)) {
          const { w, h } = sizeOf(c.v);
          filmEndRect = cover(w, h, 1, focus);
          filmEndFrame = c.v;
          setState('pullback');
        } else {
          setState('hero');
          showTitle();
          setTimeout(showNav, 900);
        }
      }
    } else if (state === 'pullback') {
      // From the film's last frame (full-screen, letters cropped) back to the
      // portrait Hero: the Hero is placed so its original 16:9 area sits
      // exactly on that frame, then eases out to its own full-screen framing.
      const u = easeInOut(clamp(el / PULLBACK_MS));
      const r = heroInPx();
      const s0 = filmEndRect.dw / r.w;
      const start = { dx: filmEndRect.dx - r.x * s0, dy: filmEndRect.dy - r.y * s0, dw: r.iw * s0, dh: r.ih * s0 };
      const end = heroRect();
      const lerp = (a, b) => a + (b - a) * u;
      const rect = { dx: lerp(start.dx, end.dx), dy: lerp(start.dy, end.dy), dw: lerp(start.dw, end.dw), dh: lerp(start.dh, end.dh) };
      drawAt(ctx, hero.img, rect);
      const s = rect.dw / r.iw;
      drawAt(ctx, filmEndFrame, { dx: rect.dx + r.x * s, dy: rect.dy + r.y * s, dw: r.w * s, dh: r.h * s }, 1 - smooth(0, 0.35, u));
      placeTitle(rect);
      if (u >= 1) { setState('hero'); showTitle(); setTimeout(showNav, 900); }
    }

    if (state === 'hero' && hero) {
      // Part B: a slow push into the Hero, real fog passing, then darkness.
      const rect = heroRect(1 + 0.1 * smooth(0, 1, p));
      drawAt(ctx, hero.img, rect);
      if (handoff) {
        const a = 1 - clamp((now - handoff.at) / 700);
        if (a <= 0) handoff = null;
        else { ctx.globalAlpha = a; ctx.drawImage(handoff.img, 0, 0, W, H); ctx.globalAlpha = 1; }
      }
      placeTitle(rect);
    } else if (state === 'film' && !hero.portrait) {
      placeTitle(heroRect());                             // the settle shot ends on the Hero framing
    }

    const st = cine.style;
    st.setProperty('--title-o', (1 - smooth(0.02, 0.28, p)).toFixed(3));
    st.setProperty('--title-y', (-p * 120).toFixed(1) + 'px');
    st.setProperty('--cue-o', (1 - smooth(0, 0.04, p)).toFixed(3));
    st.setProperty('--fog-far-o', smooth(0.08, 0.6, p).toFixed(3));
    st.setProperty('--fog-far-y', ((1 - p) * 14).toFixed(2) + '%');
    st.setProperty('--fog-near-o', smooth(0.35, 0.85, p).toFixed(3));
    st.setProperty('--fog-near-y', ((1 - p) * 34).toFixed(2) + '%');
    st.setProperty('--shade-o', smooth(0.62, 1, p).toFixed(3));
  };

  const startFilm = async () => {
    if (state === 'film' || state === 'hero') return;
    if (logoV) logoV.pause();
    setState('film');
    clip = 0;
    const ok = await playSafe(chain[0].v);
    if (!ok) settle('fail');
  };

  /* ------------------------------------------------------------ boot */
  let manifest;
  const boot = async () => {
    resize();
    addEventListener('resize', () => { resize(); measure(); });
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('keydown', (e) => {
      if (['ArrowDown', 'PageDown', ' ', 'End', 'Escape'].includes(e.key) && e.target === document.body) settle('scroll');
    });
    if (skip) skip.addEventListener('click', () => { settle('skip'); header.querySelector('a').focus({ preventScroll: true }); });
    measure();

    const staticHero = () => { cine.classList.add('is-static'); showTitle(); showNav(); if (skip) skip.hidden = true; };
    try { manifest = await (await fetch(MEDIA + 'flight/flight.json')).json(); }
    catch (e) { console.error('[AIK intro] flight.json missing; showing the Hero still.'); staticHero(); return; }

    const hp = isPortrait && manifest.heroPortrait;
    try {
      hero = hp
        ? { img: await loadImage(MEDIA + hp.src), inner: hp.inner, portrait: true }
        : { img: await loadImage(MEDIA + manifest.hero), inner: [0, 0, 1, 1], portrait: false };
    } catch (e) { console.error('[AIK intro] Hero image missing; showing the still.'); staticHero(); return; }
    if (manifest.studio) STUDIO = manifest.studio;
    resize();
    requestAnimationFrame(frame);

    // Arriving mid-page (reload, anchor): no opening.
    if (pTarget > 0.002 || location.hash) { settle('scroll'); return; }

    chain = manifest.film.map((c) => ({ ...c, v: makeVideo(MEDIA + c.src) }));
    chain.forEach((c) => {
      if (c.rate) c.v.playbackRate = c.v.defaultPlaybackRate = c.rate;
      if (c.from) seekTo(c.v, c.from);
      c.v.addEventListener('error', () => { console.error('[AIK intro] Film clip failed: ' + c.src); settle('fail'); });
    });

    try { plate = await loadImage(MEDIA + manifest.plate); } catch (e) { plate = null; }

    if (skip) skip.hidden = false;
    logoV = makeVideo(MEDIA + manifest.intro);
    logoV.addEventListener('error', () => logoFailed('load error'));
    setState('logo');
    if (!(await playSafe(logoV))) logoFailed('playback refused');
    setTimeout(() => { if (state === 'logo' && logoV.currentTime === 0) logoFailed('timeout'); }, 4000);
  };

  // The opening starts when the loader opens the screen (js/loader.js).
  const start = () => (window.AIK_LOADER ? window.AIK_LOADER.done.then(boot) : boot());
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
