/* Runs before first paint (loaded without defer, in <head>). Kept as a file, not inline,
   so the Content-Security-Policy can forbid inline scripts. */
document.documentElement.classList.add('is-loading');
/* The cinematic opening is opt-in. Reduced motion or no script: the Hero renders as a finished still. */
if (!matchMedia('(prefers-reduced-motion: reduce)').matches) document.documentElement.classList.add('cine-on');
