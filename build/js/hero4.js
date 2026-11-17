/* Hero: one real photo in three depths and the word AIK as a window into it.

   Around the letters the sky is cold mist; inside them the same sky is clear and warm,
   as if the fog had opened in the shape of the name. The near peaks stand in front of the
   letters (media/hero4/depth.png, G), the lower part of the letters dissolves into drifting
   mist, and S T U D I O sits underneath as in the logo (HTML, see .hx__studio).
   Type: Big Shoulders Display 900, rasterised at screen resolution.

   Desktop: loader → eagle flight (~3 s) → Hero. Phones, reduced motion, save-data: loader → Hero.
   "Pause motion" (html.is-still) freezes mist, drift and the light sweep. */
(() => {
  const sec = document.querySelector('.hx');
  if (!sec) return;
  const root = document.documentElement;
  const header = document.querySelector('.site-header');
  const stage = sec.querySelector('.hx__stage');
  const scene = sec.querySelector('.hx__scene');
  const img = sec.querySelector('.hx__plate img');
  const markBox = sec.querySelector('.hx__mark');
  const WORD = (markBox.dataset.word || 'AIK').toUpperCase();
  const FACE = '900 100px "Big Shoulders Display"';
  const media = sec.dataset.media;
  const loader = window.AIK_LOADER;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const phone = Math.min(screen.width, screen.height) < 760 || innerWidth < 760;
  const midPage = scrollY > 10 || (location.hash && location.hash !== '#top');
  const conn = navigator.connection || {};
  const film = !(reduce || phone || midPage || conn.saveData) && sec.dataset.film;
  const still = () => reduce || root.classList.contains('is-still');
  const ease = (t) => 1 - Math.pow(1 - Math.min(1, Math.max(0, t)), 4);   // ≈ cubic-bezier(.23,1,.32,1)

  let introT0 = 0, dive = 0, kick = () => {};
  const setDive = (p) => { dive = p; sec.style.setProperty('--dive', p.toFixed(4)); kick(); };

  /* ------------------------------------------------------------ the word → texture
     R: the letters, G: a fine edge inside them */
  const letters = (w, h) => {
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    const x = c.getContext('2d');
    x.font = FACE; x.textBaseline = 'alphabetic'; x.textAlign = 'center';
    const m = x.measureText(WORD);
    const cap = m.actualBoundingBoxAscent || 80;
    const k = Math.min(w / m.width, h / cap);
    x.font = `900 ${100 * k}px "Big Shoulders Display"`;
    x.fillStyle = '#fff';
    x.fillText(WORD, w / 2, h / 2 + cap * k / 2);
    const fill = x.getImageData(0, 0, w, h).data;
    x.globalCompositeOperation = 'source-atop';
    x.fillStyle = '#000'; x.fillRect(0, 0, w, h);
    x.globalCompositeOperation = 'source-over';
    x.strokeStyle = '#fff'; x.lineWidth = Math.max(1.5, w / 700);
    x.save(); x.beginPath(); x.rect(0, 0, w, h); x.clip();
    x.strokeText(WORD, w / 2, h / 2 + cap * k / 2);
    x.restore();
    const edge = x.getImageData(0, 0, w, h).data;
    const out = new Uint8Array(w * h * 4);
    for (let i = 0; i < out.length; i += 4) { out[i] = fill[i + 3]; out[i + 1] = Math.min(fill[i + 3], edge[i]); out[i + 3] = 255; }
    return out;
  };

  /* ------------------------------------------------------------ WebGL scene */
  const VS = 'attribute vec2 p;varying vec2 v;void main(){v=p*.5+.5;v.y=1.-v.y;gl_Position=vec4(p,0.,1.);}';
  const FS = `precision highp float;
  varying vec2 v;
  uniform sampler2D T,D,G;
  uniform vec2 S,O,M,CR,GS;       // cover scale/offset, pointer, portrait crop into the depth map, letter texel
  uniform vec4 B;                 // letter box in screen uv
  uniform float Z,I,t,SW;         // dive, intro, time, light sweep
  float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
  float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
    return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
  float fbm(vec2 p){float a=.5,s=0.;for(int k=0;k<4;k++){s+=a*n(p);p=p*2.03+vec2(1.7,9.2);a*=.5;}return s;}
  vec4 dm(vec2 q){return texture2D(D,vec2(CR.x+q.x*CR.y,q.y));}
  vec3 photo(vec2 q){return mix(vec3(.04),texture2D(T,clamp(q,0.,1.)).rgb,smoothstep(-.02,.16,q.y));}  // night above the photo
  vec2 move(vec2 u,float d){
    float zoom=1.+.075*(1.-I)*(1.-d*.4);                         // entrance: the scene settles
    u=vec2(.46,.5)+(u-vec2(.46,.5))/zoom;
    u=vec2(.46,.46)+(u-vec2(.46,.46))*(1.-Z*(.06+.32*d));       // dive: near things rush past faster
    return u-M*(d-.36)*vec2(.018,.012);                          // parallax around the letter plane
  }
  void main(){
    vec2 u=v*S+O;
    float d=dm(u).r; vec2 q=move(u,d); d=dm(q).r; q=move(u,d);
    vec3 c=photo(q);
    float front=dm(q).g;

    // ---- the world outside the letters: cold mist over the sky, the near peaks clear but cool
    float L=dot(c,vec3(.299,.587,.114));
    vec3 cool=mix(c,vec3(L)*vec3(.86,.94,1.06),.5)*.94;
    float up=smoothstep(.95,.05,v.y);                              // the higher, the thicker the mist
    vec3 mist=mix(vec3(.2,.24,.29),vec3(.46,.52,.58),up)+vec3(.3,.34,.38)*(L-.35)*.55;
    vec3 base=mix(cool,mist,(1.-front)*(.72+.22*up));

    // ---- AIK: a window through the mist, on its own plane between the far sky and the near peaks
    float fly=1.+Z*Z*7.;                                          // scroll: fly through the letters
    vec2 bc=B.xy+B.zw*.5;
    vec2 sv=bc+(v-bc)/fly-M*vec2(.006,.004);
    vec2 g=(sv-B.xy)/B.zw;
    float inside=step(0.,g.x)*step(g.x,1.)*step(0.,g.y)*step(g.y,1.);
    vec3 gs=texture2D(G,g).rgb*inside;
    float a=0.;
    if(gs.r>.002){
      float occ=front*(1.-smoothstep(.04,.32,Z));                 // the near ridge hides them… until we fly through
      a=gs.r*(1.-occ)*smoothstep(0.,.6,I)*(1.-smoothstep(.55,.92,Z));
      float fm=fbm(vec2(g.x*3.2+t*.03,g.y*2.2-t*.012));
      a*=1.-smoothstep(.5,1.08,g.y+(fm-.5)*.4)*.8*(1.-Z);         // the feet of the letters stand in the fog
    }
    vec3 win=clamp((c*vec3(1.1,1.04,.98)*1.1-.5)*1.08+.5,0.,1.);  // inside: the sky as it is, a touch richer
    win+=vec3(1.,.96,.9)*gs.g*.18;
    float band=(g.x*.75+g.y*.55)-SW;                              // a slow sheet of light across the letters
    win+=vec3(1.,.93,.84)*exp(-band*band*60.)*.14*gs.r;
    c=mix(base,win,a);

    // ---- mist in front of everything, drifting
    if(v.y>.45){
      float m=fbm(vec2(v.x*2.6+t*.018-M.x*.08,v.y*5.-t*.006))*smoothstep(.45,1.,v.y);
      c=mix(c,vec3(.55,.61,.68)*.55,clamp(m*m*1.2,0.,.55)*(1.-Z*.6));
    }
    c=mix(c,vec3(.039),smoothstep(.12,1.,Z)*.9*(1.-d*.3));       // dive: the far world sinks into the dark first
    c*=smoothstep(0.,.35,I+.08);                                  // fade up from black
    gl_FragColor=vec4(c,1.);
  }`;

  const initGL = (depthImg) => {
    const cv = document.createElement('canvas');
    cv.className = 'hx__gl'; cv.setAttribute('aria-hidden', 'true');
    const gl = cv.getContext('webgl', { antialias: false, alpha: false, powerPreference: 'high-performance' });
    if (!gl) return null;
    const sh = (ty, s) => { const o = gl.createShader(ty); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
    const pr = gl.createProgram();
    gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS));
    gl.linkProgram(pr);
    if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(pr));
    gl.useProgram(pr);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const ap = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(ap); gl.vertexAttribPointer(ap, 2, gl.FLOAT, false, 0, 0);
    const U = {}; ['T', 'D', 'G', 'S', 'O', 'M', 'CR', 'GS', 'B', 'Z', 'I', 't', 'SW'].forEach((k) => { U[k] = gl.getUniformLocation(pr, k); });
    const max = gl.getParameter(gl.MAX_TEXTURE_SIZE);
    const mk = (unit) => {
      const tx = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, tx);
      [gl.TEXTURE_WRAP_S, gl.TEXTURE_WRAP_T].forEach((k) => gl.texParameteri(gl.TEXTURE_2D, k, gl.CLAMP_TO_EDGE));
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      return tx;
    };
    const upload = (unit, src) => {
      if ((src.naturalWidth || 0) > max) {
        const c = document.createElement('canvas'); c.width = max; c.height = Math.round(max * src.naturalHeight / src.naturalWidth);
        c.getContext('2d').drawImage(src, 0, 0, c.width, c.height); src = c;
      }
      mk(unit); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, src);
    };
    upload(0, img); upload(1, depthImg);
    const gtex = mk(2);
    gl.uniform1i(U.T, 0); gl.uniform1i(U.D, 1); gl.uniform1i(U.G, 2);
    const portrait = /portrait/.test(img.currentSrc || img.src);
    const pj = JSON.parse(sec.dataset.plate || '{}');
    gl.uniform2f(U.CR, portrait ? pj.portrait_x0 || 0 : 0, portrait ? pj.portrait_w || 1 : 1);
    scene.appendChild(cv);

    const ar = img.naturalWidth / img.naturalHeight;
    let lw = 0;
    const size = () => {
      const dpr = Math.min(devicePixelRatio || 1, phone ? 1.75 : 2);
      const w = Math.round(scene.offsetWidth * dpr), h = Math.round(scene.offsetHeight * dpr);
      if (!w || !h) return;
      cv.width = w; cv.height = h; gl.viewport(0, 0, w, h);
      const car = w / h; let sx = 1, sy = 1;
      if (car > ar) sy = ar / car; else sx = car / ar;                  // object-fit: cover
      const cs = getComputedStyle(sec);
      const fx = parseFloat(cs.getPropertyValue('--focus-x')) || .5;
      const fy = parseFloat(cs.getPropertyValue('--focus-y')) || .5;
      const shift = parseFloat(cs.getPropertyValue('--plate-shift')) || 0;  // photo moved down; night sky above
      const zm = parseFloat(cs.getPropertyValue('--plate-zoom')) || 1;      // >1: the mountains come closer
      sx /= zm; sy /= zm;
      gl.uniform2f(U.S, sx, sy); gl.uniform2f(U.O, (1 - sx) * fx, (1 - sy) * fy - shift * sy);
      const sr = scene.getBoundingClientRect(), br = markBox.getBoundingClientRect();
      gl.uniform4f(U.B, (br.left - sr.left) / sr.width, (br.top - sr.top) / sr.height, br.width / sr.width, br.height / sr.height);
      // the letters at the size they are shown
      const tw = Math.min(max, 2400, Math.round(br.width * dpr)), th = Math.max(1, Math.round(tw * br.height / br.width));
      if (tw && tw + th * 1e-4 !== lw) {
        lw = tw + th * 1e-4;
        gl.activeTexture(gl.TEXTURE2); gl.bindTexture(gl.TEXTURE_2D, gtex);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, tw, th, 0, gl.RGBA, gl.UNSIGNED_BYTE, letters(tw, th));
        gl.uniform2f(U.GS, 1 / tw, 1 / th);
      }
    };
    let mx = 0, my = 0, tx = 0, ty = 0, raf = 0, visible = true, tt = 0, last = performance.now();
    if (fine && !reduce) addEventListener('pointermove', (e) => { tx = e.clientX / innerWidth * 2 - 1; ty = e.clientY / innerHeight * 2 - 1; kick(); }, { passive: true });
    const frame = (now) => {
      raf = 0;
      const dt = Math.min(64, now - last) / 1000; last = now;
      if (!still()) tt += dt;
      const intro = introT0 ? (reduce ? 1 : ease((now - introT0) / 1700)) : 0;
      mx += (tx - mx) * .06; my += (ty - my) * .06;
      let ax = still() ? 0 : mx, ay = still() ? 0 : my;
      if (!fine && !still()) { ax = Math.sin(tt / 4.2) * .5; ay = Math.cos(tt / 5.6) * .35; }
      const since = now - introT0;
      const sw = still() ? -1 : introT0 ? -.35 + 1.9 * ease((since - 250) / 2600) + Math.max(0, since / 1000 % 9 - 7.5) * 1.3 * (since > 2850) : -1;
      gl.uniform2f(U.M, ax, ay); gl.uniform1f(U.Z, dive); gl.uniform1f(U.I, intro);
      gl.uniform1f(U.t, tt); gl.uniform1f(U.SW, sw);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      if (!cv.classList.contains('is-on')) { cv.classList.add('is-on'); sec.classList.add('has-gl'); }
      const settling = introT0 && now - introT0 < 3200;
      if (visible && !document.hidden && dive < 1 && (!still() || settling || Math.abs(tx - mx) + Math.abs(ty - my) > .002)) raf = requestAnimationFrame(frame);
    };
    kick = () => { if (!raf) raf = requestAnimationFrame(frame); };
    new IntersectionObserver(([en]) => { visible = en.isIntersecting; kick(); }).observe(stage);
    document.addEventListener('visibilitychange', kick);
    document.addEventListener('aik:motion', kick);
    let rt = 0;
    addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => { size(); kick(); }, 120); });
    size(); kick();
    return { size };
  };

  const load = (src) => new Promise((res, rej) => { const i = new Image(); i.decoding = 'async'; i.onload = () => res(i); i.onerror = rej; i.src = src; });
  const ready = (im) => (im.complete && im.naturalWidth ? Promise.resolve() : new Promise((r, j) => { im.addEventListener('load', r, { once: true }); im.addEventListener('error', j, { once: true }); }));
  const face = document.fonts ? Promise.race([document.fonts.load(FACE), new Promise((r) => setTimeout(r, 2500))]).catch(() => {}) : null;
  const glReady = Promise.all([ready(img), load(media + 'depth.png'), face])
    .then(([, d]) => { try { return initGL(d); } catch (e) { console.warn('hero: WebGL off,', e.message); return null; } })
    .catch(() => null);
  if (loader && loader.track) loader.track(glReady, 3);

  /* ------------------------------------------------------------ entrance */
  const showNav = () => header && header.classList.remove('is-cine-hidden');
  const reveal = () => {
    if (introT0) return;
    introT0 = performance.now(); kick();
    sec.classList.add('is-in');
    setTimeout(showNav, reduce ? 0 : 650);
  };

  let v = null, box = null, done = false;
  if (film) {
    box = document.createElement('div');
    box.className = 'hx__film';
    v = document.createElement('video');
    v.muted = true; v.playsInline = true; v.preload = 'auto';
    v.setAttribute('muted', ''); v.setAttribute('playsinline', ''); v.setAttribute('aria-hidden', 'true');
    v.poster = sec.dataset.film.replace(/[^/]+$/, 'intro-first.webp');
    v.src = sec.dataset.film;
    box.appendChild(v);
    stage.appendChild(box);
    sec.classList.add('is-film');
    root.classList.add('hero-lock');
  }

  const finish = (fast) => {
    if (done) return; done = true;
    sec.classList.remove('is-film');
    root.classList.remove('hero-lock');
    if (box) {
      if (fast) box.style.transitionDuration = '500ms';
      box.classList.add('is-out');
      setTimeout(() => { if (v) v.pause(); box.remove(); }, 1300);
    }
    reveal();
  };

  const start = () => {
    if (!film) { reveal(); return; }
    const p = v.play();
    if (p && p.catch) p.catch(() => finish(true));
    // ~3 s: the flight starts fast and settles to real time as the peaks arrive
    const ramp = () => {
      if (done) return;
      const d = v.duration || 6.08, k = Math.min(1, v.currentTime / d);
      try { v.playbackRate = 2.8 - 1.8 * k; } catch (e) {}
      if (v.currentTime > d - .8) return finish(false);
      requestAnimationFrame(ramp);
    };
    requestAnimationFrame(ramp);
    v.addEventListener('ended', () => finish(false), { once: true });
    v.addEventListener('error', () => finish(true), { once: true });
    const t0 = performance.now();
    const dog = setInterval(() => {
      if (done || v.currentTime > .05) return clearInterval(dog);
      if (performance.now() - t0 > 5000) { clearInterval(dog); finish(true); }
    }, 250);
    const skip = () => finish(true);
    sec.querySelector('.hx__skip').addEventListener('click', skip);
    addEventListener('wheel', (e) => { if (!done) { e.preventDefault(); if (e.deltaY > 0) skip(); } }, { passive: false });
    addEventListener('touchmove', () => { if (!done) skip(); }, { passive: true });
    addEventListener('keydown', (e) => { if (!done && /^(ArrowDown|PageDown|Space|Escape|Enter)$/.test(e.code)) skip(); });
  };

  // wait for the GL scene (or its failure) so the first Hero frame is the finished one
  Promise.all([loader ? loader.done : null, glReady]).then(start);

  /* ------------------------------------------------------------ scroll: fly through the letters */
  let tk = 0;
  const onScroll = () => {
    tk = 0;
    const span = Math.max(1, sec.offsetHeight - innerHeight);
    setDive(reduce ? 0 : Math.min(1, Math.max(0, scrollY / span)));
  };
  addEventListener('scroll', () => { if (!tk) tk = requestAnimationFrame(onScroll); }, { passive: true });
  addEventListener('resize', onScroll);
  onScroll();
})();
