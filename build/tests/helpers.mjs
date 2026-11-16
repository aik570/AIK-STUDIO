// Shared expectations for the AIK Studio pages.
export const ROUTES = [
  { path: '/', lang: 'en' },
  { path: '/de/', lang: 'de' },
];
export const VIEWPORTS = [
  { name: 'desktop-1440', width: 1440, height: 900 },
  { name: 'laptop-1024', width: 1024, height: 768 },
  { name: 'tablet-768', width: 768, height: 1024 },
  { name: 'phone-390', width: 390, height: 844, mobile: true },
  { name: 'phone-375', width: 375, height: 812, mobile: true },
];

// Files that only exist once generated or supplied; see playwright.config.mjs.
//   AIK_MEDIA_OPTIONAL=1     no generated film and no logo files (bare checkout)
//   AIK_MEDIA_OPTIONAL=logo  film present, only the original logo files missing
const MODE = process.env.AIK_MEDIA_OPTIONAL;
const LOGO = [/\/media\/intro\//, /\/media\/logo\/aik-lockup\.png/];
const OPTIONAL_MEDIA = MODE === '1' ? [/\/media\/flight\//, ...LOGO] : MODE === 'logo' ? LOGO : [];
const OPTIONAL_LOG = MODE === '1' ? [/\[AIK intro\]/, /Failed to load resource/]
  : MODE === 'logo' ? [/\[AIK intro\] The logo video could not be played/, /Failed to load resource/] : [];
const optional = OPTIONAL_MEDIA.length > 0;
export const isOptionalMedia = (url) => OPTIONAL_MEDIA.some((re) => re.test(url));

// Collects console errors, page errors and failed requests for one page.
export function watch(page) {
  const problems = [];
  page.on('pageerror', (e) => problems.push(`pageerror: ${e.message}`));
  page.on('console', (m) => {
    if (m.type() !== 'error') return;
    if (optional && OPTIONAL_LOG.some((r) => r.test(m.text()))) return;
    problems.push(`console: ${m.text()}`);
  });
  page.on('response', (r) => {
    if (r.status() < 400) return;
    if (optional && OPTIONAL_MEDIA.some((re) => re.test(r.url()))) return;
    problems.push(`http ${r.status()}: ${r.url()}`);
  });
  page.on('requestfailed', (r) => {
    if (optional && OPTIONAL_MEDIA.some((re) => re.test(r.url()))) return;
    problems.push(`failed: ${r.url()} ${r.failure()?.errorText}`);
  });
  return problems;
}

// Scrolls through the whole page so lazy images and reveals run.
export async function scrollThrough(page) {
  await page.evaluate(async () => {
    const step = innerHeight * 0.8;
    for (let y = 0; y < document.documentElement.scrollHeight; y += step) {
      scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 120));
    }
  });
  await page.waitForTimeout(1500);
}
