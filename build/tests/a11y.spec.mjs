// Automated accessibility (axe-core, WCAG 2.1 A/AA rules). A pass here is not
// a compliance claim: keyboard, screen-reader and contrast-over-image checks
// still need a person.
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { ROUTES } from './helpers.mjs';

for (const route of ROUTES) {
  for (const vp of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
    test(`axe ${route.path} @ ${vp.width}`, async ({ browser }) => {
      const ctx = await browser.newContext({ viewport: vp, reducedMotion: 'reduce' });
      const page = await ctx.newPage();
      await page.goto(route.path);
      const r = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
      const serious = r.violations.filter((v) => ['serious', 'critical'].includes(v.impact));
      expect(serious.map((v) => `${v.id}: ${v.nodes.length} × ${v.nodes[0].target}`)).toEqual([]);
      await ctx.close();
    });
  }
}
