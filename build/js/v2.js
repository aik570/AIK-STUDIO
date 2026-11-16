/* AIK Studio — behaviour for the sections below the Hero (css/v2.css):
   word-mask reveals, background parallax, cursor + magnetic buttons, work
   preview that follows the pointer, the "climb" progress, the pinned
   horizontal process, the price calculator and the enquiry form. */
(() => {
  const root = document.documentElement;
  root.classList.add('js');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lang = (document.documentElement.lang || 'en').slice(0, 2);

  /* ---------------------------------------------------- split words */
  document.querySelectorAll('[data-split]').forEach((el) => {
    let i = 0;
    const walk = (node) => {
      [...node.childNodes].forEach((n) => {
        if (n.nodeType === 3) {
          const parts = n.textContent.split(/(\s+)/);
          const frag = document.createDocumentFragment();
          parts.forEach((p) => {
            if (!p) return;
            if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(p)); return; }
            const w = document.createElement('span'); w.className = 'w';
            const s = document.createElement('span'); s.textContent = p; s.style.setProperty('--wi', i++);
            w.appendChild(s); frag.appendChild(w);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1 && !n.classList.contains('w')) walk(n);
      });
    };
    walk(el);
  });

  /* ---------------------------------------------------- reveal on view */
  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { rootMargin: '0px 0px -12% 0px' });
  document.querySelectorAll('[data-split], [data-fade]').forEach((el) => io.observe(el));

  /* ---------------------------------------------------- parallax backgrounds */
  const bgs = [...document.querySelectorAll('.v2__bg')];
  const par = () => {
    bgs.forEach((b) => {
      const r = b.parentElement.getBoundingClientRect();
      if (r.bottom < -200 || r.top > innerHeight + 200) return;
      const c = (r.top + r.height / 2 - innerHeight / 2) / innerHeight;
      b.style.setProperty('--py', `${(c * -60).toFixed(1)}px`);
    });
  };

  /* ---------------------------------------------------- climb (system) */
  const climb = document.querySelector('.climb');
  const climbSteps = climb ? [...climb.querySelectorAll('li')] : [];
  const doClimb = () => {
    if (!climb) return;
    const r = climb.getBoundingClientRect();
    const p = clamp((innerHeight * 0.75 - r.top) / (r.height + innerHeight * 0.2));
    climb.style.setProperty('--climb', p.toFixed(3));
    climbSteps.forEach((li, i) => li.classList.toggle('on', p >= i / climbSteps.length + 0.02));
  };

  /* ---------------------------------------------------- pinned horizontal process */
  const pin = document.querySelector('.process__pin--horizontal');  /* retired: the process is a vertical stack now */
  const steps = pin && pin.querySelector('.steps');
  const horiz = () => pin && innerWidth > 960 && !reduce;
  const sizePin = () => {
    if (!pin) return;
    if (!horiz()) { pin.style.removeProperty('--pin-h'); steps.style.removeProperty('--px'); return; }
    const extra = steps.scrollWidth - innerWidth + parseFloat(getComputedStyle(steps).paddingLeft || 0) + 120;
    pin.style.setProperty('--pin-h', `${innerHeight + Math.max(0, extra)}px`);
    pin.dataset.extra = Math.max(0, extra);
  };
  const doPin = () => {
    if (!horiz()) return;
    const r = pin.getBoundingClientRect();
    const total = pin.offsetHeight - innerHeight;
    const p = clamp(-r.top / Math.max(1, total));
    steps.style.setProperty('--px', `${(-p * (+pin.dataset.extra || 0)).toFixed(1)}px`);
  };

  /* ---------------------------------------------------- frame loop */
  let ticking = false;
  const onScroll = () => {
    if (ticking) return; ticking = true;
    requestAnimationFrame(() => { ticking = false; if (!reduce) par(); doClimb(); doPin(); });
  };
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', () => { sizePin(); onScroll(); });
  if (document.fonts) document.fonts.ready.then(() => { sizePin(); onScroll(); });
  sizePin(); onScroll();

  /* ---------------------------------------------------- cursor + magnetic + peek */
  if (fine && !reduce) {
    root.classList.add('has-cursor');
    const cur = document.createElement('div');
    cur.className = 'cursor'; cur.setAttribute('aria-hidden', 'true');
    cur.innerHTML = '<div class="cursor__ring"><span></span></div><div class="cursor__dot"></div>';
    document.body.appendChild(cur);
    const ring = cur.querySelector('.cursor__ring'), dot = cur.querySelector('.cursor__dot'), label = ring.querySelector('span');
    let x = innerWidth / 2, y = innerHeight / 2, rx = x, ry = y;
    addEventListener('pointermove', (e) => { x = e.clientX; y = e.clientY; }, { passive: true });

    const peek = document.createElement('div'); peek.className = 'peek'; peek.setAttribute('aria-hidden', 'true');
    document.body.appendChild(peek);
    const imgs = {};
    document.querySelectorAll('.case[data-img]').forEach((c) => {
      const im = new Image(); im.src = c.dataset.img; im.alt = ''; peek.appendChild(im); imgs[c.dataset.img] = im;
      c.addEventListener('pointerenter', () => { peek.classList.add('on'); Object.values(imgs).forEach((i) => i.classList.toggle('on', i === im)); });
      c.addEventListener('pointerleave', () => peek.classList.remove('on'));
    });
    let px = x, py = y;

    const tick = () => {
      rx += (x - rx) * 0.18; ry += (y - ry) * 0.18;
      px += (x - px) * 0.1; py += (y - py) * 0.1;
      dot.style.transform = `translate(${x}px, ${y}px)`;
      ring.style.transform = `translate(${rx}px, ${ry}px)`;
      peek.style.left = `${px}px`; peek.style.top = `${py}px`;
      requestAnimationFrame(tick);
    };
    tick();
    document.addEventListener('pointerover', (e) => {
      const v = e.target.closest('[data-cursor]');
      const l = e.target.closest('a, button, summary, label, input, select, textarea');
      cur.classList.toggle('is-view', !!v);
      cur.classList.toggle('is-link', !v && !!l);
      label.textContent = v ? v.dataset.cursor : '';
    });
    document.querySelectorAll('.cta, .site-header .btn').forEach((b) => {
      b.addEventListener('pointermove', (e) => {
        const r = b.getBoundingClientRect();
        const dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
        b.style.transform = `translate(${dx * 0.18}px, ${dy * 0.3}px)`;
      });
      b.addEventListener('pointerleave', () => { b.style.transform = ''; });
    });
  }

  /* ---------------------------------------------------- calculator */
  const calc = document.querySelector('.calc');
  const fmt = (n) => new Intl.NumberFormat(lang === 'de' ? 'de-DE' : 'en-GB').format(Math.round(n / 50) * 50);
  let estimateText = '';
  if (calc) {
    const T = JSON.parse(calc.dataset.t);
    const state = { type: 'site', pages: 6, cms: false, care: 'none' };
    const pages = calc.querySelector('#c-pages'), pagesOut = calc.querySelector('.pages-out');
    const priceOut = calc.querySelector('.calc__price'), monthOut = calc.querySelector('.calc__monthly');
    const pagesField = calc.querySelector('.f-pages');
    calc.querySelectorAll('[data-type]').forEach((b) => b.addEventListener('click', () => {
      state.type = b.dataset.type;
      calc.querySelectorAll('[data-type]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      render();
    }));
    calc.querySelectorAll('[data-care]').forEach((b) => b.addEventListener('click', () => {
      state.care = b.dataset.care;
      calc.querySelectorAll('[data-care]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      render();
    }));
    pages.addEventListener('input', () => { state.pages = +pages.value; render(); });
    calc.querySelector('#c-cms').addEventListener('change', (e) => { state.cms = e.target.checked; render(); });

    // From the business plan: landing 900–1 400 €, website 2 400–4 600 €,
    // larger projects above that, admin panel +600 €, care 150–300 €/month.
    const render = () => {
      let lo, hi, plus = false;
      pagesField.hidden = state.type !== 'site';
      if (state.type === 'landing') { lo = 900; hi = 1400; }
      else if (state.type === 'site') {
        const k = clamp((state.pages - 3) / 9);
        lo = 2400 + k * 1400; hi = 3000 + k * 1600;
      } else { lo = 4600; hi = 0; plus = true; }
      if (state.cms) { lo += 600; if (hi) hi += 600; }
      pagesOut.textContent = state.pages >= 12 ? '12+' : state.pages;
      const range = plus ? `${T.from} ${fmt(lo)} €` : `${fmt(lo)} – ${fmt(hi)} €`;
      priceOut.textContent = range;
      const care = state.care === 'basic' ? 150 : state.care === 'full' ? 300 : 0;
      monthOut.textContent = care ? `+ ${care} € ${T.month}` : T.noCare;
      estimateText = `${T.types[state.type]}${state.type === 'site' ? `, ${pagesOut.textContent} ${T.pages}` : ''}${state.cms ? `, ${T.cms}` : ''}${care ? `, ${T.care} ${care} €/${T.mo}` : ''} — ${range}`;
    };
    render();
    calc.querySelector('.to-form').addEventListener('click', () => {
      const msg = document.querySelector('#f-msg');
      if (msg) msg.value = `${T.prefill}: ${estimateText}\n\n` + msg.value.replace(/^.*?\n\n/s, '');
    });
  }

  /* ---------------------------------------------------- form */
  const form = document.querySelector('.form');
  if (form) {
    form.addEventListener('submit', (e) => {
      // Live on Netlify the form posts to Netlify Forms; anywhere else (preview)
      // nothing is sent, and the page says so instead of pretending.
      if (/netlify\.app$|aikstudio\./.test(location.hostname)) return;
      e.preventDefault();
      form.classList.add('sent');
    });
  }
})();
