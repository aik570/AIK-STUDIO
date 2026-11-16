/* Craft pass: the world behind the page, the depth Hero and pointer tilt. */
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const base = (document.querySelector('.hx, .hero3') || {}).dataset?.media?.replace(/hero\d?\/$/, '') || './media/';

  /* ---------------------------------------------------------- one world
     One fixed scene behind every section. It changes as you travel down the page:
     peaks, sea of clouds, open sky, and dawn at the contact block. */
  const SCENES = { work: 'peaks', offer: 'clouds', system: 'sky', process: 'peaks', services: 'sky', why: 'clouds', faq: 'sky', contact: 'dawn' };
  const world = document.createElement('div');
  world.className = 'world'; world.setAttribute('aria-hidden', 'true');
  const layers = {};
  ['peaks', 'clouds', 'sky', 'dawn'].forEach((n) => {
    const im = new Image(); im.decoding = 'async'; im.alt = '';
    im.dataset.src = `${base}bg/s-${n}.webp`;
    layers[n] = im; world.appendChild(im);
  });
  document.body.prepend(world);
  const use = (n) => {
    const im = layers[n]; if (!im) return;
    if (!im.src) im.src = im.dataset.src;
    Object.values(layers).forEach((l) => l.classList.toggle('on', l === im));
  };
  const secs = Object.keys(SCENES).map((id) => document.getElementById(id)).filter(Boolean);
  let scene = '';
  const pick = () => {
    const mid = innerHeight * 0.55; let cur = secs[0];
    for (const s of secs) if (s.getBoundingClientRect().top <= mid) cur = s;
    const n = SCENES[cur.id];
    if (n !== scene) { scene = n; use(n); }
    if (!reduce) world.style.setProperty('--wy', `${(-(scrollY % 4000) / 4000 * 30).toFixed(1)}px`);
  };

  /* ---------------------------------------------------------- depth Hero
     The frame is one photo plus a depth map: near clouds and the main peak move more
     than the far sky. Pointer = parallax; scroll = a dive into the scene. */
  const hero = document.querySelector('.hero3');
  const plate = hero && hero.querySelector('.hero3__plate');
  const img = plate && plate.querySelector('img');
  let draw = null;
  const initGL = () => {
    const cv = document.createElement('canvas'); cv.className = 'hero3__gl';
    const gl = cv.getContext('webgl', { antialias: false, alpha: false, powerPreference: 'high-performance' });
    if (!gl) return;
    const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); return o; };
    const pr = gl.createProgram();
    gl.attachShader(pr, sh(gl.VERTEX_SHADER, 'attribute vec2 p;varying vec2 v;void main(){v=p*.5+.5;v.y=1.-v.y;gl_Position=vec4(p,0.,1.);}'));
    gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, `precision highp float;varying vec2 v;uniform sampler2D T,D;uniform vec2 M,S,O,F;uniform float Z;
      void main(){
        vec2 uv=v*S+O;
        float d=texture2D(D,uv).r;
        vec2 q=F+(uv-F)*(1.-Z*(.06+.34*d));          // dive: near things rush past faster
        q-=M*(d-.42)*vec2(.016,.011);                 // pointer parallax
        d=texture2D(D,q).r;
        q=F+(uv-F)*(1.-Z*(.06+.34*d))-M*(d-.42)*vec2(.016,.011);
        vec3 c=texture2D(T,clamp(q,0.,1.)).rgb;
        c=mix(c,vec3(.043,.055,.071),smoothstep(.15,1.,Z)*.85*(1.-d*.35));   // far fades into the night first
        gl_FragColor=vec4(c,1.);}`));
    gl.linkProgram(pr);
    if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) return;
    gl.useProgram(pr);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const a = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(a); gl.vertexAttribPointer(a, 2, gl.FLOAT, false, 0, 0);
    const U = (n) => gl.getUniformLocation(pr, n);
    const tex = (unit, src) => {
      const t = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, t);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src);
      [gl.TEXTURE_WRAP_S, gl.TEXTURE_WRAP_T].forEach((k) => gl.texParameteri(gl.TEXTURE_2D, k, gl.CLAMP_TO_EDGE));
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    };
    const dimg = new Image();
    dimg.onload = () => {
      const max = gl.getParameter(gl.MAX_TEXTURE_SIZE);
      let src = img;
      if (img.naturalWidth > max) { const c = document.createElement('canvas'); c.width = max; c.height = Math.round(max * img.naturalHeight / img.naturalWidth); c.getContext('2d').drawImage(img, 0, 0, c.width, c.height); src = c; }
      try { tex(0, src); tex(1, dimg); } catch (e) { return; }
      gl.uniform1i(U('T'), 0); gl.uniform1i(U('D'), 1);
      plate.appendChild(cv);
      const ar = img.naturalWidth / img.naturalHeight;
      let mx = 0, my = 0, tx = 0, ty = 0, z = 0, raf = 0, w = 0, h = 0;
      const size = () => {
        const dpr = Math.min(devicePixelRatio || 1, 2);
        w = Math.round(plate.offsetWidth * dpr); h = Math.round(plate.offsetHeight * dpr);
        if (!w || !h) return;
        cv.width = w; cv.height = h; gl.viewport(0, 0, w, h);
        const car = w / h; let sx = 1, sy = 1;
        if (car > ar) sy = ar / car; else sx = car / ar;                 // object-fit: cover
        const ox = (parseFloat(getComputedStyle(img).objectPosition) || 50) / 100;
        gl.uniform2f(U('S'), sx, sy); gl.uniform2f(U('O'), (1 - sx) * ox, (1 - sy) * 0.5);
        gl.uniform2f(U('F'), 0.40, 0.47);
      };
      const frame = (t) => {
        raf = 0;
        mx += (tx - mx) * 0.07; my += (ty - my) * 0.07;
        let ax = mx, ay = my;
        if (!fine && !reduce) { ax = Math.sin(t / 3800) * 0.55; ay = Math.cos(t / 5200) * 0.4; }   // phones: slow drift
        gl.uniform2f(U('M'), ax, ay); gl.uniform1f(U('Z'), z);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        const moving = Math.abs(tx - mx) + Math.abs(ty - my) > 0.002;
        if ((moving || (!fine && !reduce)) && z < 1 && !document.hidden) kick();
      };
      const kick = () => { if (!raf) raf = requestAnimationFrame(frame); };
      draw = (p) => { z = p; hero.style.setProperty('--dive', p.toFixed(3)); if (p < 1) kick(); };
      if (fine && !reduce) addEventListener('pointermove', (e) => { tx = e.clientX / innerWidth * 2 - 1; ty = e.clientY / innerHeight * 2 - 1; kick(); }, { passive: true });
      addEventListener('resize', () => { size(); kick(); });
      document.addEventListener('visibilitychange', kick);
      size(); frame(0);
      hero.classList.add('has-depth');
      setTimeout(() => { size(); kick(); }, 3000);   // after the entrance scale settles
      onScroll();
    };
    dimg.src = hero.dataset.media + 'hero3-depth.webp';
  };
  if (img) { if (img.complete && img.naturalWidth) initGL(); else img.addEventListener('load', initGL, { once: true }); }

  /* ---------------------------------------------------------- scroll */
  let tick = 0;
  const onScroll = () => {
    tick = 0; pick();
    const hd0 = document.querySelector('.site-header'); if (hd0) hd0.classList.toggle('is-past', scrollY > innerHeight * 0.85);
    const hd = document.querySelector('.site-header'); if (hd) hd.style.setProperty('--read', (scrollY / Math.max(1, document.documentElement.scrollHeight - innerHeight)).toFixed(4));
    if (hero) { const p = Math.min(1, Math.max(0, scrollY / (hero.offsetHeight * 0.9))); if (draw) draw(reduce ? 0 : p); else hero.style.setProperty('--dive', reduce ? 0 : p.toFixed(3)); }
  };
  addEventListener('scroll', () => { if (!tick) tick = requestAnimationFrame(onScroll); }, { passive: true });
  addEventListener('resize', onScroll);
  onScroll();

  /* ---------------------------------------------------------- pointer tilt on the price cards */
  if (fine && !reduce) document.querySelectorAll('.pack').forEach((el) => {
    el.addEventListener('pointermove', (e) => {
      const r = el.getBoundingClientRect(); const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      el.style.setProperty('--ry', `${((x - 0.5) * 5).toFixed(2)}deg`); el.style.setProperty('--rx', `${((0.5 - y) * 4).toFixed(2)}deg`);
      el.style.setProperty('--mx', `${(x * 100).toFixed(1)}%`); el.style.setProperty('--my', `${(y * 100).toFixed(1)}%`);
    });
    el.addEventListener('pointerleave', () => { el.style.setProperty('--rx', '0deg'); el.style.setProperty('--ry', '0deg'); });
  });
})();

/* Design system v3: second marquee row + paragraphs that light up word by word. */
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const mq = document.querySelector('.work2 > .marquee .marquee__track');
  if (mq) { const b = mq.cloneNode(true); b.classList.add('marquee__track--b'); [...b.children].reverse().forEach((n) => b.appendChild(n)); mq.parentElement.appendChild(b); }

  const els = [...document.querySelectorAll('.answer .lead, .process__intro .lead, .system__foot p, .contact2 .lead')];
  els.forEach((el) => {
    if (el.children.length) return;
    el.removeAttribute('data-fade'); el.dataset.read = '';
    el.innerHTML = el.textContent.trim().split(/\s+/).map((w) => `<span class="w">${w}</span>`).join(' ');
  });
  if (reduce || !els.length) return;
  let t = 0;
  const read = () => {
    t = 0;
    els.forEach((el) => {
      const r = el.getBoundingClientRect(); if (r.bottom < 0 || r.top > innerHeight) return;
      const p = Math.min(1, Math.max(0, (innerHeight * 0.88 - r.top) / (innerHeight * 0.42 + r.height)));
      const ws = el.children, n = Math.round(p * ws.length);
      for (let i = 0; i < ws.length; i++) ws[i].classList.toggle('on', i < n);
    });
  };
  addEventListener('scroll', () => { if (!t) t = requestAnimationFrame(read); }, { passive: true });
  read();
})();

/* v4: plain pill nav — mark the section in view. */
(() => {
  const links = [...document.querySelectorAll('.site-header .nav__list a[href^="#"]')];
  const secs = links.map((a) => document.querySelector(a.getAttribute('href')));
  if (!links.length) return;
  let t = 0;
  const spy = () => {
    t = 0; const mid = innerHeight * 0.4; let best = -1, top = -Infinity;
    secs.forEach((s, i) => { if (!s) return; const r = s.getBoundingClientRect(); if (r.top <= mid && r.top > top) { top = r.top; best = i; } });
    links.forEach((a, i) => a.classList.toggle('is-here', i === best));
  };
  addEventListener('scroll', () => { if (!t) t = requestAnimationFrame(spy); }, { passive: true });
  spy();
})();
