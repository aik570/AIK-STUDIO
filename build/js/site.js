/* AIK Studio — site behaviour (foundation step: header state, mobile menu). */
(() => {
  const header = document.querySelector('.site-header');
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.getElementById('site-nav');

  // Header: transparent over the hero, Graphite glass once the page scrolls.
  const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 8);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // Mobile menu
  const setOpen = (open) => {
    header.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
  };
  toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
  nav.addEventListener('click', (e) => { if (e.target.closest('a')) setOpen(false); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && header.classList.contains('is-open')) { setOpen(false); toggle.focus(); }
  });
  window.matchMedia('(min-width: 961px)').addEventListener('change', (e) => { if (e.matches) setOpen(false); });

  // Header links whose section is not built yet: announced as unavailable and
  // inert, instead of jumping nowhere. They come alive once the section exists.
  header.querySelectorAll('a[href^="#"]').forEach((a) => {
    const id = a.getAttribute('href').slice(1);
    if (!id || document.getElementById(id)) return;
    a.setAttribute('aria-disabled', 'true');
    a.dataset.pending = '';
    a.addEventListener('click', (e) => e.preventDefault());
  });

  // Fitted display words (data-fit): sized to run exactly the width of their
  // column (data-fit="0.9" = 90% of it). The size is published as --fs on
  // the parent, which layouts use for overlaps.
  const fit = () => document.querySelectorAll('[data-fit]').forEach((el) => {
    const word = el.firstElementChild;
    el.style.fontSize = '';
    const w = word.getBoundingClientRect().width;
    if (w <= 0) return;
    const target = el.getBoundingClientRect().width * (parseFloat(el.dataset.fit) || 1);
    const px = (parseFloat(getComputedStyle(el).fontSize) * target / w).toFixed(2) + 'px';
    el.style.fontSize = px;
    el.parentElement.style.setProperty('--fs', px);
  });
  // Headings marked data-fit-max keep their designed size unless their
  // longest line (often a long German word) would run past the column; then
  // they shrink just enough to fit.
  const fitMax = () => document.querySelectorAll('[data-fit-max]').forEach((el) => {
    el.style.fontSize = '';
    const over = el.scrollWidth / el.clientWidth;
    if (over > 1.002) el.style.fontSize = (parseFloat(getComputedStyle(el).fontSize) / over * 0.99).toFixed(2) + 'px';
  });
  const fitAll = () => { fit(); fitMax(); };
  fitAll();
  if (document.fonts) document.fonts.ready.then(fitAll);
  addEventListener('resize', fitAll);

  // Over the light sections the header's translucent glass and scrim turn
  // into a grey band; there it becomes a solid dark bar instead.
  const light = document.querySelectorAll('.section--light, .section--light-alt');
  if (light.length && 'IntersectionObserver' in window) {
    const under = new Set();
    const watchStrip = () => new IntersectionObserver((entries) => {
      entries.forEach((e) => (e.isIntersecting ? under.add(e.target) : under.delete(e.target)));
      header.classList.toggle('is-over-light', under.size > 0);
    }, { rootMargin: `0px 0px -${Math.max(0, innerHeight - header.offsetHeight)}px 0px` });
    let strip = watchStrip();
    light.forEach((s) => strip.observe(s));
    addEventListener('resize', () => { strip.disconnect(); under.clear(); strip = watchStrip(); light.forEach((s) => strip.observe(s)); });
  }

  // Contact: the address lives in one place, data-contact-email on #contact.
  // Until it is set, no address and no mail button are shown, only the placeholder.
  const contact = document.getElementById('contact');
  const email = contact && contact.dataset.contactEmail;
  if (email) {
    const mail = contact.querySelector('.contact__mail');
    mail.href = 'mailto:' + email;
    mail.querySelector('.contact__addr').textContent = email;
    mail.closest('.contact__action').hidden = false;
    contact.querySelector('.contact__pending').hidden = true;
  }

})();
