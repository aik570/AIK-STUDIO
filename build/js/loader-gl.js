/* AIK Studio — loader scene ("Dawn"), WebGL2. Driven by js/loader.js.

   One full-screen pass:
     darkness  near-black with slow fog and film grain
     light     a warm point light travels over the metal as the page loads,
               so the logo is revealed by light, not drawn; the polished
               relief comes from the metal's own luminance (pseudo normals)
     dawn      a golden backlight grows behind the peaks with the progress
     ready     full exposure, a specular band runs across, STUDIO is set
     exit      the camera pushes into the light; the frame floods warm and
               fades into the first frame of the flight

   Returns null when WebGL2 is not available; loader.js then keeps the SVG
   version (css/loader.css). */
window.AIK_LOADER_GL = (el, texSrc) => {
  const canvas = document.createElement('canvas');
  canvas.className = 'aik-loader__gl';
  canvas.setAttribute('aria-hidden', 'true');
  const gl = canvas.getContext('webgl2', { alpha: true, premultipliedAlpha: true, antialias: false, powerPreference: 'high-performance' });
  if (!gl) return null;

  const VS = `#version 300 es
  in vec2 a; void main(){ gl_Position = vec4(a, 0., 1.); }`;

  const FS = `#version 300 es
  precision highp float;
  uniform sampler2D u_logo;
  uniform vec2  u_res;      // canvas px
  uniform vec4  u_rect;     // logo rect, canvas px, top-left origin
  uniform float u_p;        // load progress 0..1
  uniform float u_t;        // seconds
  uniform float u_ready;    // seconds since ready (-1 before)
  uniform float u_exit;     // 0..1
  uniform float u_portrait;
  out vec4 o;

  float hash(vec2 p){ p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
  float noise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.-2.*f);
    return mix(mix(hash(i), hash(i+vec2(1,0)), f.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y); }
  float fbm(vec2 p){ float v = 0., a = .5; for (int k = 0; k < 4; k++){ v += a*noise(p); p = p*2.03 + 7.1; a *= .5; } return v; }
  float ease(float x){ x = clamp(x, 0., 1.); return x*x*(3.-2.*x); }
  float lum(vec3 c){ return dot(c, vec3(.299,.587,.114)); }

  vec4 logo(vec2 uv, float lod){
    if (uv.x < 0. || uv.y < 0. || uv.x > 1. || uv.y > 1.) return vec4(0);
    return textureLod(u_logo, uv, lod);
  }

  void main(){
    vec2 px = vec2(gl_FragCoord.x, u_res.y - gl_FragCoord.y);
    float ex = u_exit;
    float rd = u_ready < 0. ? 0. : u_ready;
    float isReady = u_ready < 0. ? 0. : 1.;
    float expo = ease(rd / .9);                          // full exposure after ready
    float hy = u_rect.y + u_rect.w * .826;                // the line, canvas px

    // the logo steps back a touch and fades as the line takes over
    float lout = ease(ex / .35);
    vec2 zc = u_rect.xy + u_rect.zw * vec2(.5, .45);
    vec2 lpx = zc + (px - zc) / (1. + .06 * lout);
    vec2 uv = (lpx - u_rect.xy) / u_rect.zw;
    vec2 suv = px / u_res;

    /* black */
    vec3 col = vec3(.008, .009, .011);

    /* the lockup, revealed by a cold light passing over the metal */
    float markZone = step(uv.y, .826);
    vec4 L = logo(uv, 0.);
    vec3 alb = L.a > 0. ? L.rgb / L.a : vec3(0);

    vec2 e = vec2(1.5) / vec2(1914., 1032.);
    float hx = lum(logo(uv + vec2(e.x, 0.), 1.).rgb) - lum(logo(uv - vec2(e.x, 0.), 1.).rgb);
    float hz = lum(logo(uv + vec2(0., e.y), 1.).rgb) - lum(logo(uv - vec2(0., e.y), 1.).rgb);
    vec3 n = normalize(vec3(-hx * 7., -hz * 7., 1.));

    float lp = ease(u_p);
    vec3 lpos = vec3(mix(-.3, .6, lp), mix(.75, -.15, lp), .35);
    vec3 ld = lpos - vec3(uv, 0.);
    float fall = 1. / (1. + 3.5 * dot(ld.xy, ld.xy));
    ld = normalize(ld);
    float diff = max(dot(n, ld), 0.);
    float spec = pow(max(dot(reflect(-ld, n), vec3(0, 0, 1)), 0.), 40.);

    float amb = mix(.0, .22, pow(u_p, 1.8));
    amb = mix(amb, 1., expo);
    vec3 lit = alb * (amb + diff * fall * 1.3 * (1. - .6 * expo)) + vec3(spec * fall * (1. - .5 * expo));

    // one clean glint across the metal when it is fully lit
    float s = -.35 + 1.75 * ease((rd - .25) / 1.0);
    float band = exp(-pow((uv.x + (uv.y - .4) * .45) - s, 2.) / .003) * isReady * markZone;
    lit += vec3(band * .8 * smoothstep(.05, .5, lum(alb)));

    // STUDIO, left to right
    float sp = ease((rd - .35) / .9) * 1.25 - .1;
    float studio = (1. - smoothstep(sp - .06, sp, uv.x)) * isReady;
    if (markZone < .5) lit = alb * (.45 + .55 * expo);
    float a = L.a * (markZone + (1. - markZone) * studio) * (1. - lout);
    col = mix(col, lit, a);

    // a single star on the top summit
    vec2 q = (uv - vec2(.509, .02)) * vec2(u_rect.z / u_rect.w, 1.) * 18.;
    float tw = ease((rd - .55) / .2) * (1. - ease((rd - 1.0) / .45)) * (1. - lout);
    col += vec3(exp(-dot(q, q) * 6.) + .55 * exp(-abs(q.x) * 12. - q.y * q.y * 240.) + .55 * exp(-abs(q.y) * 12. - q.x * q.x * 240.)) * tw;

    /* the line: flares, then opens into a slit onto the film */
    float dy = abs(px.y - hy);
    float flare = ease((ex - .15) / .2);
    float open = ease((ex - .33) / .67);
    float slit = open * open * u_res.y * .62;            // half height of the opening
    float halfW = mix(min(u_res.x * .35, u_rect.z * .55), u_res.x * .75, ease((ex - .1) / .4));
    float xin = 1. - smoothstep(halfW * .7, halfW, abs(px.x - u_res.x * .5));
    float core = exp(-pow(max(dy - slit, 0.) / (1.2 + 3. * flare), 2.)) * xin;
    float glow = exp(-max(dy - slit, 0.) / (18. + 60. * flare)) * xin;
    col += vec3(.95, .97, 1.) * (core * (.6 + 1.6 * flare) + glow * .5 * flare) * step(.001, ex);

    /* finish */
    float vig = 1. - .45 * pow(length((suv - .5) * vec2(1., .85)) * 1.35, 2.2);
    col *= clamp(vig, 0., 1.);
    col += (hash(gl_FragCoord.xy + fract(u_t * 13.) * 400.) - .5) * .018;

    float hole = 1. - smoothstep(slit - 6., slit + 1., dy);   // inside the slit: the page beneath
    float alpha = (1. - hole * step(.001, open)) ;
    alpha *= 1. - ease((ex - .85) / .15);
    o = vec4(col * alpha, alpha);
  }`;

  const sh = (type, src) => {
    const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) { console.error('[AIK loader]', gl.getShaderInfoLog(s)); return null; }
    return s;
  };
  const vs = sh(gl.VERTEX_SHADER, VS), fs = sh(gl.FRAGMENT_SHADER, FS);
  if (!vs || !fs) return null;
  const prog = gl.createProgram();
  gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { console.error('[AIK loader]', gl.getProgramInfoLog(prog)); return null; }
  gl.useProgram(prog);

  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, 'a');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

  const U = {};
  ['u_logo', 'u_res', 'u_rect', 'u_p', 'u_t', 'u_ready', 'u_exit', 'u_portrait'].forEach((n) => { U[n] = gl.getUniformLocation(prog, n); });

  const tex = gl.createTexture();
  let texReady = false;
  const texLoaded = new Promise((resolve) => {
    const img = new Image();
    img.decoding = 'async';
    img.onload = () => {
      gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
      gl.generateMipmap(gl.TEXTURE_2D);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      texReady = true; resolve();
    };
    img.onerror = () => resolve();
    img.src = texSrc;
  });
  gl.uniform1i(U.u_logo, 0);

  let dpr = 1;
  const resize = () => {
    dpr = Math.min(devicePixelRatio || 1, 1.75);
    canvas.width = Math.round(innerWidth * dpr);
    canvas.height = Math.round(innerHeight * dpr);
    gl.viewport(0, 0, canvas.width, canvas.height);
  };
  resize();
  addEventListener('resize', resize);

  // Logo box = the same box the SVG version uses (css/loader.css, .aik-loader__mark).
  const rect = () => {
    const vw = innerWidth, vh = innerHeight, portrait = vw / vh <= 0.8;
    const w = portrait ? vw * 0.86 : Math.min(vw * 0.6, 820, vh * 1.18);
    const h = w * 1032 / 1914;
    const x = (vw - w) / 2, y = (vh - h) / 2 - h * 0.04;
    return { x, y, w, h, portrait };
  };

  el.classList.add('is-gl');
  el.prepend(canvas);

  return {
    texLoaded,
    rect,
    draw(p, t, ready, exit) {
      if (!texReady) { gl.clearColor(0.022, 0.025, 0.032, 1); gl.clear(gl.COLOR_BUFFER_BIT); return; }
      const r = rect();
      gl.uniform2f(U.u_res, canvas.width, canvas.height);
      gl.uniform4f(U.u_rect, r.x * dpr, r.y * dpr, r.w * dpr, r.h * dpr);
      gl.uniform1f(U.u_p, p);
      gl.uniform1f(U.u_t, t);
      gl.uniform1f(U.u_ready, ready);
      gl.uniform1f(U.u_exit, exit);
      gl.uniform1f(U.u_portrait, r.portrait ? 1 : 0);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    },
  };
};
