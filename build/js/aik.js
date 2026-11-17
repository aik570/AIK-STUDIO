/* AIK Studio: everything below the Hero.
   Menu · header · pause motion · reveals · words that light up · stacked cards · work rail ·
   process with a rolling number · calculator · floating button · the six-step enquiry. */
(() => {
  const root = document.documentElement;
  root.classList.add('js');
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const lang = (root.lang || 'en').slice(0, 2);
  const fmt = (n) => new Intl.NumberFormat(lang === 'de' ? 'de-DE' : 'en-GB').format(Math.round(n / 50) * 50).replace(/,/g, ' ');
  const onScroll = [];
  let ticking = 0;
  const run = () => { ticking = 0; onScroll.forEach((f) => f()); };
  addEventListener('scroll', () => { if (!ticking) ticking = requestAnimationFrame(run); }, { passive: true });
  addEventListener('resize', () => { if (!ticking) ticking = requestAnimationFrame(run); });

  /* ---------------------------------------------------- menu (phones and tablets) */
  const header = $('.site-header');
  const toggle = $('.menu-toggle');
  const setMenu = (open) => {
    root.classList.toggle('is-menu', open);
    toggle.setAttribute('aria-expanded', String(open));
    const t = $('.menu-toggle__txt', toggle); t.textContent = open ? t.dataset.close : t.dataset.open;
  };
  $$('.nav__list li').forEach((li, i) => li.style.setProperty('--i', i));
  toggle && toggle.addEventListener('click', () => setMenu(!root.classList.contains('is-menu')));
  $$('.nav a').forEach((a) => a.addEventListener('click', () => setMenu(false)));
  addEventListener('keydown', (e) => { if (e.key === 'Escape' && root.classList.contains('is-menu')) setMenu(false); });

  /* ---------------------------------------------------- header: where am I, what is under me */
  const links = $$('.nav__list a[href^="#"]');
  const targets = links.map((a) => $(a.getAttribute('href')));
  const lights = $$('.light');
  onScroll.push(() => {
    const mid = innerHeight * .4; let best = -1, top = -Infinity;
    targets.forEach((s, i) => { if (!s) return; const r = s.getBoundingClientRect(); if (r.top <= mid && r.bottom > mid && r.top > top) { top = r.top; best = i; } });
    links.forEach((a, i) => a.classList.toggle('is-here', i === best));
    const y = 40;
    header.classList.toggle('on-light', !root.classList.contains('is-menu') && lights.some((s) => { const r = s.getBoundingClientRect(); return r.top <= y && r.bottom >= y; }));
  });

  /* ---------------------------------------------------- pause motion */
  const pauses = $$('.pause');
  const setStill = (on) => {
    root.classList.toggle('is-still', on);
    pauses.forEach((b) => { b.setAttribute('aria-pressed', String(on)); b.textContent = on ? b.dataset.play : b.dataset.pause; });
    try { localStorage.setItem('aik-still', on ? '1' : '0'); } catch (e) {}
    document.dispatchEvent(new Event('aik:motion'));
  };
  try { if (localStorage.getItem('aik-still') === '1') setStill(true); } catch (e) {}
  pauses.forEach((b) => b.addEventListener('click', () => setStill(!root.classList.contains('is-still'))));

  /* ---------------------------------------------------- words */
  const split = (el) => {
    let i = 0;
    const walk = (node) => [...node.childNodes].forEach((n) => {
      if (n.nodeType === 3) {
        const frag = document.createDocumentFragment();
        n.textContent.split(/(\s+)/).forEach((p) => {
          if (!p) return;
          if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(p)); return; }
          const w = document.createElement('span'); w.className = 'w'; w.textContent = p; w.style.setProperty('--i', i++);
          frag.appendChild(w);
        });
        n.replaceWith(frag);
      } else if (n.nodeType === 1) walk(n);
    });
    walk(el);
  };
  $$('[data-blur], [data-read]').forEach(split);

  /* ---------------------------------------------------- reveal on view */
  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (!e.isIntersecting) return;
    e.target.classList.add('in'); io.unobserve(e.target);
    const c = $('[data-count]', e.target);
    if (c && !reduce) {
      const to = +c.dataset.count, t0 = performance.now();
      const step = (now) => { const k = clamp((now - t0) / 1400); c.textContent = Math.round(to * (1 - Math.pow(1 - k, 4))); if (k < 1) requestAnimationFrame(step); };
      requestAnimationFrame(step);
    }
  }), { rootMargin: '0px 0px -12% 0px' });
  $$('[data-up], [data-blur]').forEach((el) => io.observe(el));

  /* ---------------------------------------------------- paragraphs light up word by word */
  const reads = $$('[data-read]');
  if (!reduce) onScroll.push(() => reads.forEach((el) => {
    const r = el.getBoundingClientRect(); if (r.bottom < 0 || r.top > innerHeight) return;
    const p = clamp((innerHeight * .86 - r.top) / (innerHeight * .44 + r.height));
    const ws = el.children, n = Math.round(p * ws.length);
    for (let i = 0; i < ws.length; i++) ws[i].classList.toggle('on', i < n);
  }));

  /* ---------------------------------------------------- stacked cards */
  const cards = $$('.stack__card');
  cards.forEach((c, i) => c.style.setProperty('--i', i));
  if (!reduce) onScroll.push(() => cards.forEach((c, i) => {
    const next = cards[i + 1]; if (!next) return;
    const a = c.getBoundingClientRect(), b = next.getBoundingClientRect();
    const p = clamp(1 - (b.top - a.top) / Math.max(1, a.height));
    c.style.setProperty('--s', (1 - p * .06).toFixed(4));
    c.style.setProperty('--b', (1 - p * .4).toFixed(3));
  }));

  /* ---------------------------------------------------- slow background drift */
  const bgs = $$('.system__bg img');
  if (!reduce) onScroll.push(() => bgs.forEach((b) => {
    const r = b.parentElement.getBoundingClientRect(); if (r.bottom < 0 || r.top > innerHeight) return;
    b.style.setProperty('--py', `${((r.top + r.height / 2 - innerHeight / 2) / innerHeight * -70).toFixed(1)}px`);
  }));

  /* ---------------------------------------------------- work: rail */
  const work = $('.work');
  if (work) {
    const rail = $('.work__rail', work), track = $('.work__track', work), bar = $('.work__bar', work);
    const pinMQ = matchMedia('(min-width: 961px) and (hover: hover)');
    let over = 0;
    const layout = () => {
      const pin = pinMQ.matches && !reduce;
      work.classList.toggle('is-pinned', pin);
      if (!pin) { work.style.removeProperty('--h'); return; }
      over = Math.max(0, track.scrollWidth - rail.clientWidth + parseFloat(getComputedStyle(rail).paddingLeft) * 2);
      work.style.setProperty('--h', `${innerHeight + over}px`);
    };
    layout(); addEventListener('resize', layout); pinMQ.addEventListener('change', layout);
    onScroll.push(() => {
      if (work.classList.contains('is-pinned')) {
        const r = work.getBoundingClientRect(); const p = clamp(-r.top / Math.max(1, over));
        work.style.setProperty('--x', (p * over).toFixed(1)); bar.style.setProperty('--p', (.08 + p * .92).toFixed(3));
      }
    });
    rail.addEventListener('scroll', () => bar.style.setProperty('--p', (.08 + rail.scrollLeft / Math.max(1, rail.scrollWidth - rail.clientWidth) * .92).toFixed(3)), { passive: true });
    // drag with the mouse where the rail scrolls natively
    let down = null, moved = false;
    rail.addEventListener('pointerdown', (e) => { if (e.pointerType !== 'mouse' || work.classList.contains('is-pinned')) return; down = { x: e.clientX, s: rail.scrollLeft }; moved = false; });
    addEventListener('pointermove', (e) => { if (!down) return; const dx = e.clientX - down.x; if (Math.abs(dx) > 4) { moved = true; rail.classList.add('is-drag'); } rail.scrollLeft = down.s - dx; });
    addEventListener('pointerup', () => { down = null; rail.classList.remove('is-drag'); });
    rail.addEventListener('click', (e) => { if (moved) { e.preventDefault(); moved = false; } }, true);
  }

  /* ---------------------------------------------------- process: one step at a time, the number rolls */
  const proc = $('.proc');
  if (proc) {
    const tabs = $$('.proc__tabs li', proc), steps = $$('.proc__step', proc), rolls = $$('.roll > span', proc);
    let cur = -1;
    const show = (i) => {
      if (i === cur) return; cur = i;
      tabs.forEach((t, k) => t.classList.toggle('is-on', k === i));
      steps.forEach((s, k) => s.classList.toggle('is-on', k === i));
      rolls[0].style.setProperty('--v', 0); rolls[1].style.setProperty('--v', i + 1);
    };
    show(0);
    onScroll.push(() => {
      const r = proc.getBoundingClientRect();
      const p = clamp(-r.top / Math.max(1, r.height - innerHeight));
      show(Math.min(steps.length - 1, Math.floor(p * steps.length * .999)));
    });
  }

  /* ---------------------------------------------------- calculator */
  const calc = $('.calc');
  let estimate = null;
  if (calc) {
    const T = JSON.parse(calc.dataset.t);
    const price = $('.calc__price', calc), care = $('.calc__care', calc);
    const pages = calc.elements.pages, pagesOut = calc.elements.pagesOut, pagesSet = pages.closest('fieldset');
    const fill = (r) => r.style.setProperty('--p', `${(r.value - r.min) / (r.max - r.min) * 100}%`);
    // the owner's ranges: landing 900–1 400 €, website 2 400–4 600 €, larger projects above that,
    // admin panel +600 €, care 150–300 €/month
    const render = () => {
      const type = calc.elements.type.value, n = +pages.value, cms = calc.elements.cms.checked, mo = +calc.elements.care.value;
      let lo, hi = 0;
      pagesSet.hidden = type !== 'site';
      if (type === 'landing') { lo = 900; hi = 1400; }
      else if (type === 'site') { const k = clamp((n - 3) / 9); lo = 2400 + k * 1400; hi = 3000 + k * 1600; }
      else lo = 4600;
      if (cms) { lo += 600; if (hi) hi += 600; }
      pagesOut.textContent = n >= 12 ? '12+' : n;
      price.textContent = hi ? `${fmt(lo)} – ${fmt(hi)} €` : `${lang === 'de' ? 'ab' : 'from'} ${fmt(lo)} €`;
      care.textContent = mo ? T.care.replace('{n}', mo) : T.noCare;
      fill(pages);
      estimate = { type, budget: hi ? Math.round((lo + hi) / 2 / 100) * 100 : Math.max(lo, 6900) };
    };
    calc.addEventListener('input', render); render();
  }

  /* ---------------------------------------------------- floating "Start a project" */
  const float = $('.float'), hero = $('.hx'), contact = $('#contact'), foot = $('.foot');
  if (float) onScroll.push(() => {
    const past = hero ? hero.getBoundingClientRect().bottom < innerHeight * .6 : scrollY > innerHeight;
    const near = [contact, foot].some((s) => s && s.getBoundingClientRect().top < innerHeight * .9);
    float.classList.toggle('is-on', past && !near && !root.classList.contains('is-sheet') && !root.classList.contains('is-menu'));
  });

  /* ---------------------------------------------------- the six-step enquiry */
  const sheet = $('#start');
  if (sheet) {
    const form = $('form', sheet);
    const qs = $$('.q[data-step]', sheet).filter((q) => /^\d+$/.test(q.dataset.step));
    const n = qs.length;
    const back = $('[data-back]', sheet), next = $('[data-next]', sheet), send = $('[data-send]', sheet);
    const count = $('.sheet__count b', sheet), bar = $('.sheet__bar', sheet), nav = $('.sheet__nav', sheet);
    const fits = JSON.parse(sheet.dataset.fits), WA = JSON.parse(sheet.dataset.wa), num = sheet.dataset.num;
    const budget = form.elements.budget, budgetOut = form.elements.budgetOut, fit = $('.budget__fit', sheet);
    const err = $('.field__err', sheet);
    let at = 0, opener = null;

    const vals = (name) => [...form.querySelectorAll(`[name="${name}"]`)].filter((i) => i.checked).map((i) => i.value);
    const waText = () => {
      const L = WA.l, lines = [WA.intro];
      const add = (k, v) => { if (v && v.length) lines.push(`${L[k]}: ${Array.isArray(v) ? v.join(', ') : v}`); };
      add('need', vals('need')); add('goal', vals('goal')); add('start', vals('start'));
      add('budget', `${fmt(+budget.value)} €${+budget.value >= 7000 ? ' +' : ''}`);
      const way = $(`.way input[value="${vals('way')[0]}"] ~ b`, sheet); add('way', way && way.textContent);
      add('name', form.elements.name.value.trim()); add('phone', form.elements.phone.value.trim()); add('email', form.elements.email.value.trim());
      return `https://wa.me/${num}?text=${encodeURIComponent(lines.join('\n'))}`;
    };
    const valid = (i) => {
      const q = qs[i]; if (!q) return true;
      const name = q.querySelector('input') && q.querySelector('input').name;
      if (['need', 'goal', 'start', 'way'].includes(name)) return vals(name).length > 0;
      return true;
    };
    const go = (i) => {
      at = clamp(i, 0, n - 1);
      qs.forEach((q, k) => q.classList.toggle('is-on', k === at));
      $$('.q--done, .q--err', sheet).forEach((q) => { q.hidden = true; q.classList.remove('is-on'); });
      nav.hidden = false;
      count.textContent = at + 1;
      bar.style.setProperty('--p', ((at + 1) / n).toFixed(3));
      back.hidden = at === 0;
      next.hidden = at === n - 1; send.hidden = at !== n - 1;
      next.disabled = !valid(at);
      const way = vals('way')[0];
      $('.opt-note', sheet).hidden = way === 'call';
      const f = qs[at].querySelector('input:not([type="hidden"])');
      if (f && at === n - 1) setTimeout(() => form.elements.name.focus({ preventScroll: true }), 80);
    };
    const end = (ok) => {
      qs.forEach((q) => q.classList.remove('is-on'));
      const q = $(ok ? '.q--done' : '.q--err', sheet); q.hidden = false; q.classList.add('is-on');
      $$('[data-wa-link]', q).forEach((a) => { a.href = waText(); });
      nav.hidden = true; bar.style.setProperty('--p', 1);
    };
    const showBudget = () => {
      const v = +budget.value; budgetOut.textContent = `${fmt(v)} €${v >= 7000 ? ' +' : ''}`;
      fit.textContent = (fits.find(([max]) => v <= max) || fits[fits.length - 1])[1];
      budget.style.setProperty('--p', `${(v - budget.min) / (budget.max - budget.min) * 100}%`);
    };
    form.addEventListener('input', (e) => {
      if (e.target === budget) showBudget();
      next.disabled = !valid(at);
      if (e.target.closest('[data-auto]') && e.target.checked) setTimeout(() => { if (valid(at) && at < n - 1) go(at + 1); }, 260);
      if (e.target.matches('.field input')) { e.target.removeAttribute('aria-invalid'); err.textContent = ''; }
    });
    next.addEventListener('click', () => { if (valid(at)) go(at + 1); });
    back.addEventListener('click', () => go(at - 1));

    const open = (from) => {
      opener = from || document.activeElement;
      form.reset(); err.textContent = '';
      $$('[aria-invalid]', form).forEach((i) => i.removeAttribute('aria-invalid'));
      const preset = { landing: [2, 1200], site: [0, 3400], premium: [1, 6900], big: [1, 6900] };
      const key = from && (from.dataset.need || (from.hasAttribute('data-from-calc') && estimate && estimate.type));
      if (key && preset[key]) {
        const box = form.querySelectorAll('[name="need"]')[preset[key][0]]; if (box) box.checked = true;
        budget.value = from.hasAttribute('data-from-calc') && estimate ? estimate.budget : preset[key][1];
      } else budget.value = 2400;
      showBudget(); go(0);
      root.classList.add('is-sheet');
      if (sheet.showModal) sheet.showModal(); else sheet.setAttribute('open', '');
    };
    const close = () => { if (sheet.close) sheet.close(); else sheet.removeAttribute('open'); };
    sheet.addEventListener('close', () => { root.classList.remove('is-sheet'); if (opener && opener.focus) opener.focus({ preventScroll: true }); run(); });
    $$('[data-close]', sheet).forEach((b) => b.addEventListener('click', close));
    sheet.addEventListener('click', (e) => { if (e.target === sheet) close(); });
    $$('[data-start]').forEach((a) => a.addEventListener('click', (e) => { e.preventDefault(); setMenu(false); open(a); }));
    if (location.hash === '#start') open();

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const way = vals('way')[0], F = form.elements;
      const need = (input, ok) => { if (ok) return true; input.setAttribute('aria-invalid', 'true'); err.textContent = input.dataset.need; input.focus(); return false; };
      if (!need(F.name, F.name.value.trim().length > 1)) return;
      if (!need(F.phone, way !== 'call' || F.phone.value.replace(/\D/g, '').length >= 6)) return;
      if (!need(F.email, (way === 'call' && !F.email.value.trim()) || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(F.email.value.trim()))) return;
      const body = new URLSearchParams();
      ['form-name', 'lang', 'company', 'name', 'phone', 'email'].forEach((k) => body.append(k, F[k].value.trim()));
      ['need', 'goal', 'start', 'way'].forEach((k) => body.append(k, vals(k).join(', ')));
      body.append('budget', `${budget.value}${+budget.value >= 7000 ? '+' : ''} €`);
      const label = $('span', send), was = label.textContent;
      send.disabled = true; label.textContent = send.dataset.sending;
      try {
        const res = await fetch(form.getAttribute('action') || '/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: body.toString() });
        end(res.ok);
      } catch (x) { end(false); }
      send.disabled = false; label.textContent = was;
    });
  }

  run();
})();
