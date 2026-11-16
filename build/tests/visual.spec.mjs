// @visual — sequential screenshots of the whole homepage, per route and
// viewport, into tests/output/. Not a pixel-diff suite: these are for review.
import { test } from '@playwright/test';
import { ROUTES, VIEWPORTS } from './helpers.mjs';

for (const route of ROUTES) {
  for (const vp of VIEWPORTS) {
    test(`@visual ${route.lang} ${vp.name}`, async ({ browser }) => {
      const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height }, isMobile: !!vp.mobile, hasTouch: !!vp.mobile, deviceScaleFactor: vp.mobile ? 2 : 1 });
      const page = await ctx.newPage();
      await page.goto(route.path);
      const skip = page.locator('.cine__skip');
      if (await skip.waitFor({ state: 'visible', timeout: 8_000 }).then(() => true, () => false)) await skip.click();
      await page.waitForTimeout(2500);
      const base = `tests/output/${route.lang}-${vp.name}`;
      await page.screenshot({ path: `${base}-00-hero.jpg`, type: 'jpeg', quality: 72 });
      const stops = await page.evaluate(() => [...document.querySelectorAll('#work, .project, #services, #approach, #about, #contact, .footer')]
        .map((e) => Math.round(e.getBoundingClientRect().top + scrollY - (innerWidth < 761 ? 64 : 80))));
      let i = 1;
      for (const y of stops) {
        await page.evaluate(async (t) => { const s = scrollY; for (let k = 1; k <= 20; k++) { scrollTo(0, s + (t - s) * k / 20); await new Promise((r) => setTimeout(r, 25)); } }, y);
        await page.waitForTimeout(1600);
        await page.screenshot({ path: `${base}-${String(i++).padStart(2, '0')}.jpg`, type: 'jpeg', quality: 72 });
      }
      await ctx.close();
    });
  }
}
