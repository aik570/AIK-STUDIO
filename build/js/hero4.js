/* Hero 4: one real photo, three depths, glass AIK drawn in code.

   Layers (back → front), all in one WebGL pass so they move together:
     sky and far range  → slow
     glass AIK          → between: refracts and frosts what is behind it
     near peaks, clouds → fast, and they stand in front of the glass (media/hero4/depth.png, G)
     drifting mist      → fastest
   Pointer = parallax (desktop), slow drift (phones). Scroll = the camera flies through the letters.

   Desktop: loader → eagle flight (~3 s) → Hero. Phones, reduced motion, save-data: loader → Hero.
   No WebGL: the photo and the glass mark as plain images, same layout. */
(() => {
  // EN | DE switch: slide the knob, then go
  document.querySelectorAll('.site-header .lang a').forEach((a, i) => a.addEventListener('click', (e) => {
    if (a.getAttribute('aria-current') === 'true' || e.metaKey || e.ctrlKey) return;
    e.preventDefault();
    a.parentElement.classList.add(i ? 'go-right' : 'go-left');
    setTimeout(() => { location.href = a.href; }, 320);
  }));

  const sec = document.querySelector('.hx');
  if (!sec) return;
  const root = document.documentElement;
  const header = document.querySelector('.site-header');
  const stage = sec.querySelector('.hx__stage');
  const scene = sec.querySelector('.hx__scene');
  const img = sec.querySelector('.hx__plate img');
  const markBox = sec.querySelector('.hx__mark');
  const media = sec.dataset.media;
  const loader = window.AIK_LOADER;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const phone = Math.min(screen.width, screen.height) < 760 || innerWidth < 760;
  const midPage = scrollY > 10 || (location.hash && location.hash !== '#top');
  const conn = navigator.connection || {};
  const film = !(reduce || phone || midPage || conn.saveData) && sec.dataset.film;
  const ease = (t) => 1 - Math.pow(1 - Math.min(1, Math.max(0, t)), 4);   // ≈ cubic-bezier(.23,1,.32,1)

  /* ------------------------------------------------------------ state shared by GL and CSS */
  let intro = 0, introT0 = 0, dive = 0, kick = () => {};
  const setDive = (p) => { dive = p; sec.style.setProperty('--dive', p.toFixed(4)); kick(); };

  /* ------------------------------------------------------------ WebGL scene */
  const VS = 'attribute vec2 p;varying vec2 v;void main(){v=p*.5+.5;v.y=1.-v.y;gl_Position=vec4(p,0.,1.);}';
  const FS = `precision highp float;
  varying vec2 v;
  uniform sampler2D T,D,G;
  uniform vec2 S,O,M,R,CR;        // cover scale/offset, pointer, canvas px, portrait crop (x0,w) into the depth map
  uniform vec4 B,GP;              // mark box in screen uv; glass texture inner rect
  uniform vec2 GS;                // glass texel
  uniform float Z,I,t,SW;         // dive, intro, time, light sweep
  float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
  float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
    return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
  float fbm(vec2 p){float a=.5,s=0.;for(int k=0;k<4;k++){s+=a*n(p);p=p*2.03+vec2(1.7,9.2);a*=.5;}return s;}
  vec4 dm(vec2 q){return texture2D(D,vec2(CR.x+q.x*CR.y,q.y));}
  vec2 move(vec2 u,float d){
    float zoom=1.+.075*(1.-I)*(1.-d*.4);                         // entrance: the scene settles
    u=vec2(.42,.5)+(u-vec2(.42,.5))/zoom;
    u=vec2(.42,.46)+(u-vec2(.42,.46))*(1.-Z*(.06+.32*d));       // dive: near things rush past faster
    return u-M*(d-.36)*vec2(.018,.012);                          // parallax around the glass plane
  }
  void main(){
    vec2 u=v*S+O;
    float d=dm(u).r; vec2 q=move(u,d); d=dm(q).r; q=move(u,d);
    vec3 c=texture2D(T,clamp(q,0.,1.)).rgb;
    c=mix(vec3(.04),c,smoothstep(-.02,.16,q.y));                 // above the photo: night sky
    float front=dm(q).g;

    // ---- glass AIK: lives on its own plane between the far sky and the near peaks
    float fly=1.+Z*Z*7.;                                          // scroll: fly through the letters
    vec2 bc=B.xy+B.zw*.5;
    vec2 sv=bc+(v-bc)/fly-M*vec2(.006,.004);
    vec2 g=(sv-B.xy)/B.zw;
    float inside=step(0.,g.x)*step(g.x,1.)*step(0.,g.y)*step(g.y,1.);
    vec2 gt=GP.xy+g*GP.zw;
    vec3 gs=texture2D(G,gt).rgb*inside;
    float shape=gs.r;
    if(shape>.002){
      vec2 e=GS*1.5;
      vec2 nr=vec2(texture2D(G,gt+vec2(e.x,0)).g-texture2D(G,gt-vec2(e.x,0)).g,
                    texture2D(G,gt+vec2(0,e.y)).g-texture2D(G,gt-vec2(0,e.y)).g)*inside;
      float steep=clamp(length(nr)*5.,0.,1.);
      vec2 nd=nr/(length(nr)+1e-4);
      vec2 off=-nr*vec2(1.2,1.7)*(.4+.6*I)+(sv-bc)*-.018;         // the bevel bends the light; the face is a weak lens
      vec3 r=vec3(0.);
      for(int k=0;k<10;k++){                                      // frosted face: average around the bent ray
        float a=float(k)*2.39996, rr=.0022*sqrt(float(k)+.5);
        vec2 rq=q+off+vec2(cos(a),sin(a))*rr*vec2(1.,S.x/S.y);
        r+=mix(vec3(.04),texture2D(T,clamp(rq,0.,1.)).rgb,smoothstep(-.02,.16,rq.y));
      }
      r/=10.;
      vec3 gl=mix(r,vec3(dot(r,vec3(.3,.59,.11))),.1)*1.16+vec3(1.,.86,.7)*(.05+.13*(1.-g.y));   // warm light falls in from above
      float lit=dot(-nd,normalize(vec2(-.55,-.85)));              // outward normal · light from the upper left
      gl+=vec3(1.,.95,.88)*gs.b*(.18+.82*max(lit,0.))*.9;         // the rim that faces the light
      gl*=1.-gs.b*.35*max(-lit,0.);                               // the rim that turns away
      gl+=vec3(1.,.9,.78)*steep*.12;
      float band=(g.x*.75+g.y*.55)-SW;                            // a slow sheet of light across the letters
      gl+=vec3(1.,.92,.82)*exp(-band*band*60.)*(.16+.5*gs.b+.3*steep);
      float occ=front*(1.-smoothstep(.04,.32,Z));                 // the near ridge hides the glass… until we fly through
      float a=shape*(1.-occ)*smoothstep(0.,.55,I)*(1.-smoothstep(.55,.92,Z))*mix(1.,.42,smoothstep(.5,1.,g.y)*(1.-Z));   // poster: the letters thin out into the haze
      c=mix(c,gl,a);
    }

    // ---- mist in front of everything, drifting
    if(v.y>.5){
      float m=fbm(vec2(v.x*2.6+t*.018-M.x*.08,v.y*5.-t*.006))*smoothstep(.5,1.,v.y);
      c=mix(c,vec3(.80,.74,.70)*.55,clamp(m*m*1.1,0.,.5)*(1.-Z*.6));
    }

    // ---- dive: the far world sinks into the dark first
    c=mix(c,vec3(.039),smoothstep(.12,1.,Z)*.9*(1.-d*.3));
    c*=mix(.0,1.,smoothstep(0.,.35,I+.08));                       // fade up from black
    gl_FragColor=vec4(c,1.);
  }`;

  const initGL = (glassImg, depthImg) => {
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
    const U = {}; ['T', 'D', 'G', 'S', 'O', 'M', 'R', 'CR', 'B', 'GP', 'GS', 'Z', 'I', 't', 'SW'].forEach((k) => { U[k] = gl.getUniformLocation(pr, k); });
    const max = gl.getParameter(gl.MAX_TEXTURE_SIZE);
    const tex = (unit, src) => {
      if ((src.naturalWidth || 0) > max) {
        const c = document.createElement('canvas'); c.width = max; c.height = Math.round(max * src.naturalHeight / src.naturalWidth);
        c.getContext('2d').drawImage(src, 0, 0, c.width, c.height); src = c;
      }
      const tx = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, tx);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, src);
      [gl.TEXTURE_WRAP_S, gl.TEXTURE_WRAP_T].forEach((k) => gl.texParameteri(gl.TEXTURE_2D, k, gl.CLAMP_TO_EDGE));
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    };
    tex(0, img); tex(1, depthImg);
    const pot = document.createElement('canvas'); pot.width = 2048; pot.height = 1024;
    pot.getContext('2d').drawImage(glassImg, 0, 0, 2048, 1024);
    tex(2, pot); gl.generateMipmap(gl.TEXTURE_2D);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
    gl.uniform1i(U.T, 0); gl.uniform1i(U.D, 1); gl.uniform1i(U.G, 2);
    const gj = { w: glassImg.naturalWidth, h: glassImg.naturalHeight, pad: JSON.parse(sec.dataset.glass || '{}').pad || 40 };
    gl.uniform2f(U.GS, 1 / 2048, 1 / 1024);
    gl.uniform4f(U.GP, gj.pad / gj.w, gj.pad / gj.h, 1 - 2 * gj.pad / gj.w, 1 - 2 * gj.pad / gj.h);
    const portrait = /portrait/.test(img.currentSrc || img.src);
    const pj = JSON.parse(sec.dataset.plate || '{}');
    gl.uniform2f(U.CR, portrait ? pj.portrait_x0 || 0 : 0, portrait ? pj.portrait_w || 1 : 1);
    scene.appendChild(cv);

    const ar = img.naturalWidth / img.naturalHeight;
    let w = 0, h = 0;
    const size = () => {
      const dpr = Math.min(devicePixelRatio || 1, phone ? 1.75 : 2);
      w = Math.round(scene.offsetWidth * dpr); h = Math.round(scene.offsetHeight * dpr);
      if (!w || !h) return;
      cv.width = w; cv.height = h; gl.viewport(0, 0, w, h);
      const car = w / h; let sx = 1, sy = 1;
      if (car > ar) sy = ar / car; else sx = car / ar;                  // object-fit: cover
      const cs = getComputedStyle(sec);
      const fx = parseFloat(cs.getPropertyValue('--focus-x')) || .5;
      const fy = parseFloat(cs.getPropertyValue('--focus-y')) || .5;
      const sh = parseFloat(cs.getPropertyValue('--plate-shift')) || 0;  // move the photo down (fraction of the screen); the sky above fades to black
      gl.uniform2f(U.S, sx, sy); gl.uniform2f(U.O, (1 - sx) * fx, (1 - sy) * fy - sh * sy); gl.uniform2f(U.R, w, h);
      const sr = scene.getBoundingClientRect(), br = markBox.getBoundingClientRect();
      gl.uniform4f(U.B, (br.left - sr.left) / sr.width, (br.top - sr.top) / sr.height, br.width / sr.width, br.height / sr.height);
    };
    let mx = 0, my = 0, tx = 0, ty = 0;
    if (fine && !reduce) addEventListener('pointermove', (e) => { tx = e.clientX / innerWidth * 2 - 1; ty = e.clientY / innerHeight * 2 - 1; kick(); }, { passive: true });
    let raf = 0, visible = true, t0 = performance.now();
    const frame = (now) => {
      raf = 0;
      const t = (now - t0) / 1000;
      if (introT0) intro = reduce ? 1 : ease((now - introT0) / 1700);
      mx += (tx - mx) * .06; my += (ty - my) * .06;
      let ax = mx, ay = my;
      if (!fine && !reduce) { ax = Math.sin(t / 4.2) * .5; ay = Math.cos(t / 5.6) * .35; }
      const sw = reduce ? .55 : introT0 ? -.35 + 1.9 * ease((now - introT0 - 250) / 2600) + Math.max(0, (now - introT0 - 2850) / 1000 % 9 - 7.5) * 1.3 : -1;
      gl.uniform2f(U.M, ax, ay); gl.uniform1f(U.Z, dive); gl.uniform1f(U.I, introT0 ? intro : 0);
      gl.uniform1f(U.t, reduce ? 0 : t); gl.uniform1f(U.SW, sw);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      if (!cv.classList.contains('is-on')) { cv.classList.add('is-on'); sec.classList.add('has-gl'); }
      if (visible && !document.hidden && dive < 1 && !reduce) raf = requestAnimationFrame(frame);
    };
    kick = () => { if (!raf) raf = requestAnimationFrame(frame); };
    new IntersectionObserver(([en]) => { visible = en.isIntersecting; kick(); }).observe(stage);
    document.addEventListener('visibilitychange', kick);
    addEventListener('resize', () => { size(); kick(); });
    size(); kick();
    return { size };
  };

  const load = (src) => new Promise((res, rej) => { const i = new Image(); i.decoding = 'async'; i.onload = () => res(i); i.onerror = rej; i.src = src; });
  const ready = (im) => (im.complete && im.naturalWidth ? Promise.resolve() : new Promise((r, j) => { im.addEventListener('load', r, { once: true }); im.addEventListener('error', j, { once: true }); }));
  const glReady = Promise.all([ready(img), load(media + 'glass.png'), load(media + 'depth.png')])
    .then(([, g, d]) => { try { return initGL(g, d); } catch (e) { console.warn('hero4: WebGL off,', e.message); return null; } })
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
