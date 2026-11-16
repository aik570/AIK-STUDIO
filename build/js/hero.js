/* AIK Studio — Hero (storyboard frames 04–12). Styles: css/hero.css.
   Media: media/hero/ (tools/edit_flight2.py). Each video holds the picture on
   top and the foreground matte (summit + eagle) below, so they stay in sync.

   States
     intro   the flight plays by itself after the loader; scrolling down speeds
             it up, scrolling up winds it back; "Skip" or a key jumps ahead.
             The page does not move while the intro runs.
     hero    the flight ends on the sea of clouds and hands over to a seamless
             loop. Glass AIK letters rise behind the summit, the eagle flies in
             front of STUDIO, the navigation follows.
     dive    scrolling pushes the camera down into the dark; the letters fly
             past; "01 — Selected Work" comes out of the fog.

   One WebGL2 canvas draws the film, the glass and the dive. Without WebGL2, or
   with reduced motion: the Hero still with the letters as an image. */
(() => {
  const root = document.documentElement;
  const sec = document.querySelector('.hero2');
  if (!sec) return;
  const header = document.querySelector('.site-header');
  const loader = window.AIK_LOADER;
  const stage = sec.querySelector('.hero2__stage');
  const MEDIA = sec.dataset.media;
  const reduce = !root.classList.contains('cine-on');
  const showNav = () => header && header.classList.remove('is-cine-hidden');

  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const smooth = (a, b, v) => { const t = clamp((v - a) / (b - a)); return t * t * (3 - 2 * t); };

  /* ------------------------------------------------------------ layout */
  // The glass lockup (mountains + AIK, 1914 x 852) and STUDIO below it.
  const layout = () => {
    const vw = innerWidth, vh = innerHeight, portrait = vw / vh <= 0.8;
    const w = portrait ? vw * 0.9 : Math.min(vw * 0.5, vh * 1.02);
    const h = w * 852 / 1914;
    const top = portrait ? vh * 0.21 : vh * 0.115;
    return { x: (vw - w) / 2, y: top, w, h, portrait };
  };
  const place = () => {
    const L = layout();
    sec.style.setProperty('--mark-x', `${L.x}px`);
    sec.style.setProperty('--mark-y', `${L.y}px`);
    sec.style.setProperty('--mark-w', `${L.w}px`);
    sec.style.setProperty('--mark-h', `${L.h}px`);
  };
  place();
  addEventListener('resize', place);

  if (reduce) { sec.classList.add('is-static', 'is-hero'); showNav(); return; }

  /* ------------------------------------------------------------ WebGL */
  const canvas = sec.querySelector('.hero2__gl');
  const gl = canvas.getContext('webgl2', { alpha: false, antialias: false, premultipliedAlpha: false, powerPreference: 'high-performance' });
  if (!gl) { sec.classList.add('is-static', 'is-hero'); showNav(); return; }

  const VS = `#version 300 es
  in vec2 a; void main(){ gl_Position = vec4(a, 0., 1.); }`;
  const FS = `#version 300 es
  precision highp float;
  uniform sampler2D u_vid;      // picture (top half) + matte (bottom half)
  uniform sampler2D u_mark;     // glass lockup, premultiplied
  uniform vec2  u_res;          // canvas px
  uniform vec2  u_vsize;        // picture size (1280, 720)
  uniform vec4  u_rect;         // lockup rect, canvas px, top-left origin
  uniform float u_letters;      // 0..1 letters risen
  uniform float u_sweep;        // light run across the glass, -1..2
  uniform float u_dive;         // 0..1
  uniform float u_fg;           // 1 when the matte is meaningful
  uniform float u_t;
  uniform vec2  u_sun;          // sun in picture uv
  uniform vec2  u_mouse;        // pointer, -0.5..0.5 (parallax)
  uniform sampler2D u_studio;   // STUDIO + light rule, white on transparent
  uniform vec4  u_srect;        // its rect, canvas px
  uniform float u_studioA;      // 0..1
  out vec4 o;

  float hash(vec2 p){ p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
  float noise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.-2.*f);
    return mix(mix(hash(i), hash(i+vec2(1,0)), f.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y); }
  float fbm(vec2 p){ float v = 0., a = .5; for (int k = 0; k < 4; k++){ v += a*noise(p); p = p*2.03 + 7.1; a *= .5; } return v; }
  float lum(vec3 c){ return dot(c, vec3(.299,.587,.114)); }

  // screen px → picture uv (cover, focus slightly above centre)
  float S; vec2 OFF;
  vec2 toUV(vec2 px){ return (px - OFF) / (u_vsize * S); }
  // texture: picture 1280x720 on top (2/3), two half-size mattes below: summit+eagle | eagle
  vec3 pic(vec2 uv){ uv = clamp(uv, vec2(.001), vec2(.999)); return texture(u_vid, vec2(uv.x, uv.y * (2. / 3.))).rgb; }
  float mat(vec2 uv){ uv = clamp(uv, vec2(.002), vec2(.998)); return texture(u_vid, vec2(uv.x * .5, 2. / 3. + uv.y / 3.)).r; }
  vec4 mark(vec2 m, float lod){ if (any(lessThan(m, vec2(0))) || any(greaterThan(m, vec2(1)))) return vec4(0); return textureLod(u_mark, m, lod); }

  void main(){
    vec2 px = vec2(gl_FragCoord.x, u_res.y - gl_FragCoord.y);
    S = max(u_res.x / u_vsize.x, u_res.y / u_vsize.y);
    OFF = (u_res - u_vsize * S) * vec2(.5, .42);

    // the dive: push towards the summit, letters fly past faster than the land
    vec2 zc = OFF + u_vsize * S * vec2(.5, .40);
    float d = u_dive;
    float breathe = .018 * u_letters * (.5 - .5 * cos(u_t * .16));   // slow push while the Hero rests
    float zl = 1. + 2.2 * d * d + breathe;       // land
    float zm = 1. + 5.5 * pow(d, 1.6);           // letters (closer to camera)
    vec2 par = u_mouse * u_res.y;                // pointer parallax: land moves less than the glass
    vec2 p = zc + (px - zc) / zl - par * .006;
    vec2 uv = toUV(p);
    vec3 bg = pic(uv);
    float m = mat(uv) * u_fg;

    /* glass lockup */
    vec2 pm = zc + (px - zc) / zm - par * .018;
    float rise = (1. - u_letters) * u_rect.w * .10;
    vec2 luv = (pm - u_rect.xy - vec2(0., rise)) / u_rect.zw;
    vec4 M = mark(luv, 0.);
    float a = M.a * smoothstep(0., 1., u_letters) * (1. - smoothstep(.35, .7, d));
    vec3 col = bg;
    if (a > .001) {
      vec3 metal = M.rgb / max(M.a, .001);
      vec2 e = 1.6 / vec2(1914., 852.);
      float hx = lum(mark(luv + vec2(e.x, 0.), 1.).rgb) - lum(mark(luv - vec2(e.x, 0.), 1.).rgb);
      float hy = lum(mark(luv + vec2(0., e.y), 1.).rgb) - lum(mark(luv - vec2(0., e.y), 1.).rgb);
      vec3 n = normalize(vec3(-hx * 6., -hy * 6., 1.));
      // refraction: the land seen through thick glass, slightly magnified and bent
      vec2 q = p + n.xy * u_rect.z * .045 - (p - (u_rect.xy + u_rect.zw * .5)) * .06;
      vec2 r = 1.6 / (u_vsize * S);
      vec2 uq = toUV(q);
      vec3 through = (pic(uq) * .4 + pic(uq + vec2(r.x, 0.)) * .15 + pic(uq - vec2(r.x, 0.)) * .15
                    + pic(uq + vec2(0., r.y)) * .15 + pic(uq - vec2(0., r.y)) * .15);
      through = through * 1.32 + vec3(.05, .055, .065);           // glass gathers light
      // light from the sun, a slow sheen, and the metal's own bevels as chrome edges
      vec2 sunPx = OFF + u_vsize * S * u_sun;
      vec3 L = normalize(vec3((sunPx - px) / u_res.y, .55));
      float spec = pow(max(dot(reflect(-L, n), vec3(0, 0, 1)), 0.), 28.);
      float bevel = smoothstep(.45, .95, lum(metal));
      float sheen = exp(-pow((luv.x + luv.y * .35) - u_sweep, 2.) / .004);
      float slow = exp(-pow((luv.x + luv.y * .35) - (fract(u_t / 9.) * 2.6 - .5), 2.) / .01) * .35;
      vec3 glass = through * (.86 + .12 * (1. - lum(metal)))
                 + vec3(1., .96, .9) * (spec * .75 + bevel * .38 + (sheen + slow) * .6 * bevel + sheen * .2);
      // a thin bright rim where the glass ends
      float rim = smoothstep(.15, .5, M.a) * (1. - smoothstep(.5, .95, M.a));
      glass += vec3(.92, .94, .97) * rim * .6;
      col = mix(bg, glass, a * .97);
    }
    // STUDIO and its light rule, under the eagle
    vec2 suvS = (pm - u_srect.xy) / u_srect.zw;
    if (all(greaterThan(suvS, vec2(0))) && all(lessThan(suvS, vec2(1)))) {
      float sa = texture(u_studio, suvS).a * u_studioA * (1. - smoothstep(.2, .5, d));
      col = mix(col, vec3(.95, .965, .975), sa);
    }
    // the eagle (and summit, when in the matte) stays in front of the glass and STUDIO
    col = mix(col, bg, m * smoothstep(.0, .25, u_letters) * (1. - d));

    /* the dive: darkness and fog come up from below */
    float fog = fbm(vec2(px.x / u_res.y, px.y / u_res.y) * 2.2 + vec2(u_t * .02, -d * 1.5));
    float dark = smoothstep(.15, .85, d);
    col = mix(col, vec3(.045, .055, .068), dark * .92);
    col += vec3(.55, .58, .62) * fog * fog * smoothstep(.1, .5, d) * (1. - smoothstep(.75, 1., d)) * .35;
    col = mix(col, vec3(.063, .078, .098), smoothstep(.85, 1., d));   // --obsidian

    // finish
    vec2 s = px / u_res;
    col *= 1. - .28 * pow(length((s - .5) * vec2(1., .9)) * 1.25, 2.4);
    col += (hash(gl_FragCoord.xy + fract(u_t * 7.) * 300.) - .5) * .02;
    o = vec4(col, 1.);
  }`;

  const sh = (t, s) => { const x = gl.createShader(t); gl.shaderSource(x, s); gl.compileShader(x);
    if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) { console.error('[AIK hero]', gl.getShaderInfoLog(x)); return null; } return x; };
  const vs = sh(gl.VERTEX_SHADER, VS), fs = sh(gl.FRAGMENT_SHADER, FS);
  const prog = gl.createProgram();
  gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
  if (!vs || !fs || !gl.getProgramParameter(prog, gl.LINK_STATUS)) { sec.classList.add('is-static', 'is-hero'); showNav(); return; }
  gl.useProgram(prog);
  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, 'a');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  const U = {};
  ['u_vid', 'u_mark', 'u_res', 'u_vsize', 'u_rect', 'u_letters', 'u_sweep', 'u_dive', 'u_fg', 'u_t', 'u_sun', 'u_mouse', 'u_studio', 'u_srect', 'u_studioA'].forEach((n) => { U[n] = gl.getUniformLocation(prog, n); });
  gl.uniform1i(U.u_vid, 0);
  gl.uniform1i(U.u_mark, 1);
  gl.uniform2f(U.u_vsize, 1920, 1080);
  gl.uniform2f(U.u_sun, 0.17, 0.40);
  gl.uniform1i(U.u_studio, 2);

  const mkTex = (unit) => {
    const t = gl.createTexture();
    gl.activeTexture(gl.TEXTURE0 + unit);
    gl.bindTexture(gl.TEXTURE_2D, t);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    return t;
  };
  const vidTex = mkTex(0);
  const markTex = mkTex(1);
  let markReady = false;
  const markImg = new Image();
  const markLoaded = new Promise((res) => {
    markImg.onload = () => {
      gl.activeTexture(gl.TEXTURE1);
      gl.bindTexture(gl.TEXTURE_2D, markTex);
      gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, markImg);
      gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
      gl.generateMipmap(gl.TEXTURE_2D);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
      markReady = true; res();
    };
    markImg.onerror = res;
  });
  markImg.src = sec.dataset.mark;
  if (loader) loader.track(markLoaded, 1);

  // STUDIO as a texture, so the eagle can fly in front of it
  const studioTex = mkTex(2);
  const drawStudio = () => {
    const c = document.createElement('canvas'); c.width = 2048; c.height = 256;
    const x = c.getContext('2d');
    const g = x.createLinearGradient(80, 0, 1968, 0);
    g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(0.2, 'rgba(255,255,255,.55)');
    g.addColorStop(0.5, 'rgba(255,255,255,1)'); g.addColorStop(0.8, 'rgba(255,255,255,.55)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    x.fillStyle = g; x.fillRect(80, 30, 1888, 2);
    x.shadowColor = 'rgba(255,255,255,.6)'; x.shadowBlur = 14; x.fillRect(560, 30, 928, 2); x.shadowBlur = 0;
    x.fillStyle = '#fff'; x.font = '300 132px "Space Grotesk", system-ui, sans-serif'; x.textBaseline = 'alphabetic';
    const word = 'STUDIO', track = 132 * 0.9;
    const widths = [...word].map((ch) => x.measureText(ch).width);
    const total = widths.reduce((a, b) => a + b, 0) + track * (word.length - 1);
    let cx = (2048 - total) / 2;
    [...word].forEach((ch, i) => { x.fillText(ch, cx, 200); cx += widths[i] + track; });
    gl.activeTexture(gl.TEXTURE2);
    gl.bindTexture(gl.TEXTURE_2D, studioTex);
    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, c);
  };
  drawStudio();
  if (document.fonts) document.fonts.load('300 132px "Space Grotesk"').then(drawStudio).catch(() => {});

  let dpr = 1;
  const resize = () => {
    dpr = Math.min(devicePixelRatio || 1, 2, 2400 / innerWidth);
    canvas.width = Math.round(innerWidth * dpr);
    canvas.height = Math.round(innerHeight * dpr);
    gl.viewport(0, 0, canvas.width, canvas.height);
  };
  resize();
  addEventListener('resize', resize);

  /* ------------------------------------------------------------ videos */
  const mkVideo = (loop) => {
    const v = document.createElement('video');
    v.muted = true; v.playsInline = true; v.loop = loop; v.preload = 'auto';
    v.setAttribute('muted', ''); v.setAttribute('playsinline', '');
    return v;
  };
  const intro = mkVideo(false);
  // Phones and slow links get the 1280 cut (2 MB instead of 7 MB): same shot, same layout.
  const conn = navigator.connection || {};
  const small = Math.min(screen.width, screen.height) < 900 || conn.saveData || /(^|-)(2g|3g)$/.test(conn.effectiveType || '');
  // Phones skip the film: straight into the Hero frame (living glass, fog, tilt). Desktop gets the flight.
  const noFilm = Math.min(screen.width, screen.height) < 760 || conn.saveData;
  const introSrc = MEDIA + (small ? 'intro-1280.mp4' : 'intro-1920.mp4');
  // Stream, never block the loader on the film: the poster (its first frame) covers buffering.
  if (!noFilm) { intro.src = introSrc; intro.load(); }
  else { const po = sec.querySelector('.hero2__poster'); if (po) po.src = MEDIA + 'hero-plate.webp'; }

  // Still fallback (autoplay refused, e.g. in-app browsers / low-power mode):
  // the last frame + its matte, same layout as the videos, so the glass still works.
  const still = new Image();
  still.decoding = 'async';
  still.src = MEDIA + 'hero-still-stack.webp';
  const isReady = (v) => (v instanceof HTMLImageElement ? v.complete && v.naturalWidth > 0 : v.readyState >= 2);

  let src = intro;            // the video (or still) currently on screen
  let lastUpload = -1;
  let mx = 0, my = 0, mxT = 0, myT = 0;
  addEventListener('pointermove', (e) => { mxT = e.clientX / innerWidth - 0.5; myT = e.clientY / innerHeight - 0.5; }, { passive: true });
  let fg = 0;

  /* ------------------------------------------------------------ state */
  let state = 'wait', tHero = 0, t0 = performance.now();
  const lockScroll = (on) => root.classList.toggle('hero-lock', on);

  const useStill = () => { src = still; lastUpload = -1; };
  const toHero = (opts = {}) => {
    if (state === 'hero') return;
    state = 'hero';
    tHero = performance.now();
    lockScroll(false);
    if (opts.still) intro.pause();
    if (opts.still) { useStill(); }
    // otherwise the film keeps running and glides to a stop on its last frame
    fg = 1;
    sec.classList.add('is-hero');
    setTimeout(showNav, 1500);
  };

  const startIntro = () => {
    state = 'intro';
    lockScroll(true);
    sec.classList.add('is-intro');
    intro.addEventListener('ended', () => toHero(), { once: true });
    const t0i = performance.now();
    const p = intro.play();
    if (p && p.catch) p.catch(() => {
      // Autoplay refused (low-power mode, some in-app browsers): the first touch starts the flight.
      lockScroll(false);
      const go = () => {
        ['pointerup', 'touchend', 'keydown'].forEach((e) => removeEventListener(e, go));
        if (state !== 'intro' || scrollY > 10) return;
        lockScroll(true);
        intro.play().catch(() => toHero({ still: true }));
      };
      ['pointerup', 'touchend', 'keydown'].forEach((e) => addEventListener(e, go, { passive: true }));
      setTimeout(() => { if (state === 'intro' && intro.paused) { go(); toHero({ still: true }); } }, 3500);
    });
    // Watchdog: a slow network gets time to buffer (poster stays up); only a dead one falls back.
    const dog = setInterval(() => {
      if (state !== 'intro') return clearInterval(dog);
      if ((intro.currentTime || 0) > 0.05) return clearInterval(dog);
      if (performance.now() - t0i > 8000 || intro.error) { clearInterval(dog); toHero({ still: true }); }
    }, 250);
  };

  // scroll gestures during the intro: down = faster, up = wind back
  let push = 0;
  const nudge = (dy) => {
    if (state !== 'intro') return;
    push = clamp(push + dy * 0.004, -3, 3);
  };
  addEventListener('wheel', (e) => { if (state === 'intro') { e.preventDefault(); nudge(e.deltaY); } }, { passive: false });
  let ty = null;
  addEventListener('touchstart', (e) => { ty = e.touches[0].clientY; }, { passive: true });
  addEventListener('touchmove', (e) => {
    if (state !== 'intro' || ty == null) return;
    e.preventDefault();
    const y = e.touches[0].clientY; nudge((ty - y) * 2.2); ty = y;
  }, { passive: false });
  addEventListener('keydown', (e) => {
    if (state === 'intro' && ['ArrowDown', 'PageDown', ' ', 'End', 'Escape', 'Enter'].includes(e.key)) { e.preventDefault(); skipIntro(); }
  });
  const skipBtn = sec.querySelector('.hero2__skip');
  const skipIntro = () => {
    if (state !== 'intro') return;
    const d = intro.duration || 6.08;
    intro.currentTime = Math.max(0, d - 1.6);   // land on the sea of clouds, not a cut
  };
  if (skipBtn) skipBtn.addEventListener('click', skipIntro);

  /* ------------------------------------------------------------ scroll (dive) */
  let top = 0, len = 1, dive = 0, diveNow = 0;
  const measure = () => { const r = sec.getBoundingClientRect(); top = r.top + scrollY; len = Math.max(1, sec.offsetHeight - innerHeight); };
  const read = () => { dive = clamp((scrollY - top) / len); };
  measure(); read();
  addEventListener('resize', () => { measure(); read(); });
  addEventListener('scroll', read, { passive: true });

  /* ------------------------------------------------------------ frame */
  const frame = (now) => {
    const t = (now - t0) / 1000;

    if (state === 'intro') {
      // forward: playbackRate; backward: small seeks (every frame is a keyframe every 6)
      push *= 0.9;
      if (push > 0.05) { intro.playbackRate = clamp(1 + push * 1.6, 1, 6); if (intro.paused) intro.play().catch(() => {}); }
      else if (push < -0.05) { intro.pause(); intro.currentTime = Math.max(0, intro.currentTime + push * 0.06); }
      else { intro.playbackRate = 1; if (intro.paused && !intro.ended) intro.play().catch(() => {}); }
      const dur = intro.duration || 6.08, ct = intro.currentTime || 0;
      sec.style.setProperty('--intro', (ct / dur).toFixed(3));
      // the matte only exists on the last shot
      const e0 = 102 / 24;
      fg = smooth(e0 - 0.3, e0, ct);
      if (ct > dur - 1.4) toHero();             // letters rise while the film slows down
    }
    if (state === 'hero' && src === intro && !intro.paused) {
      const dur = intro.duration || 6.08, left = dur - intro.currentTime;
      intro.playbackRate = clamp(left / 1.4, 0.12, 1);
    }
    mx += (mxT - mx) * 0.05; my += (myT - my) * 0.05;

    diveNow += (dive - diveNow) * 0.12;
    sec.style.setProperty('--dive', diveNow.toFixed(4));

    const letters = state === 'hero' ? smooth(0.15, 2.2, (now - tHero) / 1000) : 0;
    const sweep = state === 'hero' ? -0.6 + 2.8 * smooth(1.1, 3.4, (now - tHero) / 1000) : -1;

    if (isReady(src)) {
      const ct = src instanceof HTMLImageElement ? 1e9 : src.currentTime;
      if (ct !== lastUpload) {
        gl.activeTexture(gl.TEXTURE0);
        gl.bindTexture(gl.TEXTURE_2D, vidTex);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src);
        lastUpload = ct;
      }
    }
    if (markReady && lastUpload !== -1) {
      const L = layout();
      gl.uniform2f(U.u_res, canvas.width, canvas.height);
      gl.uniform4f(U.u_rect, L.x * dpr, L.y * dpr, L.w * dpr, L.h * dpr);
      gl.uniform1f(U.u_letters, letters);
      gl.uniform1f(U.u_sweep, sweep);
      gl.uniform1f(U.u_dive, diveNow);
      gl.uniform1f(U.u_fg, fg);
      gl.uniform1f(U.u_t, t);
      const sw = L.w * 1.0, sh = sw * 256 / 2048;
      gl.uniform4f(U.u_srect, (L.x + (L.w - sw) / 2) * dpr, (L.y + L.h + L.w * 0.01) * dpr, sw * dpr, sh * dpr);
      gl.uniform1f(U.u_studioA, state === 'hero' ? smooth(1.0, 2.6, (now - tHero) / 1000) : 0);
      gl.uniform2f(U.u_mouse, mx, my);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      canvas.classList.add('is-on');
    }
    requestAnimationFrame(frame);
  };

  /* ------------------------------------------------------------ go */
  // Arriving mid-page (reload, anchor): no intro.
  const midPage = () => scrollY > 10 || (location.hash && location.hash !== '#top');
  Promise.resolve(loader ? loader.done : null).then(() => {
    requestAnimationFrame(frame);
    if (midPage() || noFilm) { toHero({ still: true }); return; }
    startIntro();
  });
})();
