/* Hero 3: desktop plays the eagle flight, then dissolves into the Hero frame.
   Phones (and reduced motion / save-data) go straight to the frame. */
(() => {
  // EN | DE switch: slide the knob, then go
  document.querySelectorAll('.site-header .lang a').forEach((a, i) => a.addEventListener('click', (e) => {
    if (a.getAttribute('aria-current') === 'true' || e.metaKey || e.ctrlKey) return;
    e.preventDefault();
    a.parentElement.classList.add(i ? 'go-right' : 'go-left');
    setTimeout(() => { location.href = a.href; }, 320);
  }));

  const sec = document.querySelector('.hero3');
  if (!sec) return;
  const root = document.documentElement;
  const header = document.querySelector('.site-header');
  const loader = window.AIK_LOADER;
  const conn = navigator.connection || {};
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const phone = Math.min(screen.width, screen.height) < 760 || innerWidth < 760;
  const midPage = scrollY > 10 || (location.hash && location.hash !== '#top');
  const film = !(reduce || phone || midPage || conn.saveData);

  const showNav = () => header && header.classList.remove('is-cine-hidden');
  const reveal = () => { sec.classList.add('is-in'); setTimeout(showNav, 700); };

  // mouse parallax on the plate (desktop only)
  if (!phone && !reduce) {
    let tx = 0, ty = 0, x = 0, y = 0, raf = 0;
    const tick = () => {
      x += (tx - x) * 0.06; y += (ty - y) * 0.06;
      sec.style.setProperty('--px', (x * -14).toFixed(2) + 'px');
      sec.style.setProperty('--py', (y * -9).toFixed(2) + 'px');
      raf = Math.abs(tx - x) + Math.abs(ty - y) > 0.001 ? requestAnimationFrame(tick) : 0;
    };
    addEventListener('pointermove', (e) => {
      tx = e.clientX / innerWidth - 0.5; ty = e.clientY / innerHeight - 0.5;
      if (!raf) raf = requestAnimationFrame(tick);
    }, { passive: true });
  }

  let v = null, box = null, done = false;
  if (film) {
    box = document.createElement('div');
    box.className = 'hero3__film';
    v = document.createElement('video');
    v.muted = true; v.playsInline = true; v.preload = 'auto';
    v.setAttribute('muted', ''); v.setAttribute('playsinline', '');
    v.poster = sec.dataset.media + 'intro-first.webp';
    v.src = sec.dataset.media + 'flight-1920.mp4';
    box.appendChild(v);
    sec.querySelector('.hero3__stage').appendChild(box);
    sec.classList.add('is-film');
    root.classList.add('hero-lock');
  }

  const finish = (fast) => {
    if (done) return; done = true;
    sec.classList.remove('is-film');
    root.classList.remove('hero-lock');
    if (box) {
      if (fast) box.style.transitionDuration = '600ms';
      box.classList.add('is-out');
      setTimeout(() => { if (v) v.pause(); box.remove(); }, 1400);
    }
    setTimeout(reveal, fast ? 150 : 260);
  };

  const start = () => {
    if (!film) { reveal(); return; }
    const p = v.play();
    if (p && p.catch) p.catch(() => finish(true));
    // ~3 s in total: the flight starts fast and settles to real time as the peaks arrive,
    // then the camera pushes through the last frame into the Hero.
    const ramp = () => {
      if (done) return;
      const d = v.duration || 6.08, k = Math.min(1, v.currentTime / d);
      try { v.playbackRate = 2.8 - 1.8 * k; } catch (e) {}
      if (v.currentTime > d - 0.75) return finish(false);
      requestAnimationFrame(ramp);
    };
    requestAnimationFrame(ramp);
    v.addEventListener('ended', () => finish(false), { once: true });
    v.addEventListener('error', () => finish(true), { once: true });
    // slow network: give it time; a dead one falls back to the frame
    const t0 = performance.now();
    const dog = setInterval(() => {
      if (done || v.currentTime > 0.05) return clearInterval(dog);
      if (performance.now() - t0 > 6000) { clearInterval(dog); finish(true); }
    }, 250);
    // scroll / key / skip = go to the frame now
    const skip = () => finish(true);
    sec.querySelector('.hero3__skip').addEventListener('click', skip);
    addEventListener('wheel', (e) => { if (!done) { e.preventDefault(); if (e.deltaY > 0) skip(); } }, { passive: false });
    addEventListener('keydown', (e) => { if (!done && /^(ArrowDown|PageDown|Space|Escape|Enter)$/.test(e.code)) skip(); });
  };

  Promise.resolve(loader ? loader.done : null).then(start);
})();
