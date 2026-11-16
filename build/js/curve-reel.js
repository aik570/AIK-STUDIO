/* AIK Studio — curved reel for the work section.
   Vanilla port of "Tilted Grid Hero" (React original): one row of images
   streams round the inside of a cylinder; the centre faces you flat, the ends
   bend toward you and fade into the page. A box can't bend, so each tile is cut
   into SLICES vertical strips, each a flat facet of the cylinder; the tile
   (preserve-3d) is what moves, with one rotateY about the axis. Transform-only,
   on the compositor; the only JS sizes the loop and hands a tile its next
   image each time it wraps, out of sight.
   Markup: <div class="reel" data-images='["a.webp", …]' data-aspect="0.64"></div> */
(() => {
  const SLICES = 14, CAMERA = 1.6;
  let MAX_WIDTH = 34;                       // tile width cap, % of the reel (bigger on phones)
  const arc = (bend) => (CAMERA - 1 + Math.cos(bend)) / (2 * CAMERA * Math.sin(bend));
  const measure = (width, height, tile, aspect, gap, bend) => {
    const h = Math.min((tile / 100) * height, ((MAX_WIDTH / 100) * width) / aspect);
    const radius = width * arc(bend);
    if (!(h > 0) || !(radius > 0)) return { columns: 2, sweep: 0, unit: 0, limit: 0 };
    const deg = (r) => (r * 180) / Math.PI;
    const unit = deg(h / radius);
    const pitch = (aspect + gap / 100) * unit;
    const limit = deg(bend) + (aspect * unit) / 2;
    const columns = Math.min(40, Math.max(2, Math.ceil((2 * limit) / pitch)));
    const round = (n) => +n.toFixed(4);
    const sweep = round((columns * pitch) / 2);
    return { columns, sweep, unit: round(unit), limit: round(Math.min(sweep, limit)) };
  };

  document.querySelectorAll('.reel').forEach((el, n) => {
    const images = JSON.parse(el.dataset.images || '[]');
    if (!images.length) return;
    const aspect = +el.dataset.aspect || 0.64;
    const tileH = +el.dataset.tile || 80;
    const gap = +el.dataset.gap || 7;
    const speed = +el.dataset.speed || 4.5;
    const fade = +el.dataset.fade || 12;
    const bend = (Math.min(85, Math.max(5, +el.dataset.curve || 62)) * Math.PI) / 180;
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    images.forEach((src) => { new Image().src = src; });

    el.style.containerType = 'size';
    const style = document.createElement('style');
    const band = document.createElement('div');
    band.className = 'reel__band';
    band.setAttribute('aria-hidden', 'true');
    el.append(style, band);
    const orbit = `reel-o-${n}`, tileCls = `reel-t-${n}`;
    const r = 100 * arc(bend);
    const radius = `${+r.toFixed(3)}cqw`;
    const turn = (deg) => `translateZ(${radius}) rotateY(${+deg.toFixed(4)}deg) translateZ(-${radius})`;
    const u = (k) => `calc(${+k.toFixed(4)} * min(${tileH}cqh, ${+(MAX_WIDTH / aspect).toFixed(4)}cqw))`;
    const mask = `linear-gradient(90deg,transparent,#000 ${fade}%,#000 ${100 - fade}%,transparent)`;
    band.style.cssText = `position:absolute;inset:0;pointer-events:none;perspective:${+(r * CAMERA).toFixed(3)}cqw;perspective-origin:50% 50%;-webkit-mask-image:${mask};mask-image:${mask};opacity:0;transition:opacity .8s ease`;

    let last = null;
    const build = (L) => {
      const { columns, sweep, unit, limit } = L;
      const hide = +(((sweep - limit) / (2 * sweep || 1)) * 100).toFixed(4);
      style.textContent = `@keyframes ${orbit}{from{transform:${turn(-sweep)}}to{transform:${turn(sweep)}}`
        + `0%,${hide}%,${100 - hide}%,100%{visibility:hidden}${hide + 0.001}%,${100 - hide - 0.001}%{visibility:visible}}`
        + (reduce ? `.${tileCls}{animation-play-state:paused}` : '');
      const share = aspect / SLICES;
      const duration = columns * speed;
      band.textContent = '';
      for (let t = 0; t < columns; t++) {
        const first = columns - 1 - t;
        const tile = document.createElement('div');
        tile.className = `reel__tile ${tileCls}`;
        tile.style.cssText = `position:absolute;left:calc(50% - ${u(aspect / 2)});top:calc(50% - ${u(0.5)});width:${u(aspect)};height:${u(1)};transform-style:preserve-3d;animation:${orbit} ${duration}s linear ${-t * speed}s infinite`;
        const strips = [];
        for (let k = 0; k < SLICES; k++) {
          const strip = document.createElement('div');
          strip.className = 'reel__strip';
          strip.style.cssText = `position:absolute;top:0;overflow:hidden;left:${u((aspect - share) / 2)};width:${k === SLICES - 1 ? u(share) : `calc(${u(share)} + 1px)`};height:${u(1)};transform:${turn((aspect / 2 - (k + 0.5) * share) * unit)}`
            + (k === 0 ? ';border-radius:10px 0 0 10px' : k === SLICES - 1 ? ';border-radius:0 10px 10px 0' : '');
          const img = document.createElement('img');
          img.alt = ''; img.draggable = false; img.decoding = 'async';
          img.style.cssText = `position:absolute;top:0;max-width:none;object-fit:cover;object-position:50% 0;left:${u(-k * share)};width:${u(aspect)};height:${u(1)}`;
          img.src = images[first % images.length];
          strip.appendChild(img); tile.appendChild(strip); strips.push(img);
        }
        tile.addEventListener('animationiteration', (e) => {
          const lap = Math.round(e.elapsedTime / duration);
          const src = images[(lap * columns + first) % images.length];
          strips.forEach((im) => { if (im.getAttribute('src') !== src) im.src = src; });
        });
        band.appendChild(tile);
      }
      band.style.opacity = '1';
    };

    new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect;
      const mw = width < 640 ? 54 : 34;
      if (mw !== MAX_WIDTH) { MAX_WIDTH = mw; last = null; }
      const L = measure(width, height, tileH, aspect, gap, bend);
      if (last && last.columns === L.columns && last.sweep === L.sweep && last.unit === L.unit) return;
      last = L; build(L);
    }).observe(el);
  });
})();
