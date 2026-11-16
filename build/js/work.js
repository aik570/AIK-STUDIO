/* AIK Studio — reveals for every section below the Hero (rules in site.css,
   image variants in work.css): elements rise into place once, as they enter
   the viewport. Reduced motion or no IntersectionObserver: nothing is hidden.
   (Fitted names, data-fit, are sized by site.js.) */
(() => {
  const items = document.querySelectorAll('main [data-reveal]');
  if (!items.length || !('IntersectionObserver' in window)) return;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  // Anything already on screen (deep link, reload mid-page) stays visible.
  const vh = window.innerHeight;
  const pending = [...items].filter((el) => el.getBoundingClientRect().top > vh);
  if (!pending.length) return;

  // Children of a group rise in turn.
  document.querySelectorAll('main [data-reveal="group"]').forEach((g) => {
    [...g.children].forEach((c, i) => c.style.setProperty('--i', i));
  });

  // Hide without a transition (no fade-out), then let transitions run again.
  const root = document.documentElement;
  root.classList.add('reveal-on', 'reveal-arming');
  items.forEach((el) => { if (!pending.includes(el)) el.classList.add('is-in'); });
  requestAnimationFrame(() => requestAnimationFrame(() => root.classList.remove('reveal-arming')));

  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-in');
      io.unobserve(e.target);
    });
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.01 });
  pending.forEach((el) => io.observe(el));
})();
