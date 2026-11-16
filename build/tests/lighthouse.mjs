// Lighthouse (performance, accessibility, best practices, SEO) for both
// routes on the mobile preset. Needs the site served on :8765 (npm run serve)
// and a Chromium: CHROME_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
import lighthouse from 'lighthouse';
import * as chromeLauncher from 'chrome-launcher';

const routes = ['http://localhost:8765/', 'http://localhost:8765/de/'];
const chrome = await chromeLauncher.launch({ chromeFlags: ['--headless=new', '--no-sandbox'] });
try {
  for (const url of routes) {
    const { lhr } = await lighthouse(url, { port: chrome.port, output: 'json', logLevel: 'error' });
    const s = Object.fromEntries(Object.entries(lhr.categories).map(([k, v]) => [k, Math.round(v.score * 100)]));
    const lcp = lhr.audits['largest-contentful-paint'].displayValue, cls = lhr.audits['cumulative-layout-shift'].displayValue;
    console.log(url, JSON.stringify(s), 'LCP', lcp, 'CLS', cls);
    for (const a of Object.values(lhr.audits)) if (a.score !== null && a.score < 0.9 && a.scoreDisplayMode === 'binary') console.log('  ✗', a.id, '—', a.title);
  }
} finally { await chrome.kill(); }
