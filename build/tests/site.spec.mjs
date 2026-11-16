// Routes, layout, links and content integrity at every agreed viewport.
import { test, expect } from '@playwright/test';
import { ROUTES, VIEWPORTS, watch, scrollThrough, isOptionalMedia } from './helpers.mjs';

for (const vp of VIEWPORTS) {
  for (const route of ROUTES) {
    test.describe(`${route.path} @ ${vp.name}`, () => {
      test.use({ viewport: { width: vp.width, height: vp.height }, isMobile: !!vp.mobile, hasTouch: !!vp.mobile });

      test('loads cleanly, nothing overflows, every image and font arrives', async ({ page }) => {
        const problems = watch(page);
        const res = await page.goto(route.path, { waitUntil: 'load' });
        expect(res.status()).toBe(200);
        await expect(page.locator('html')).toHaveAttribute('lang', route.lang);
        await scrollThrough(page);

        const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
        expect(overflow, 'horizontal overflow in px').toBeLessThanOrEqual(0);

        const clipped = await page.evaluate(() => [...document.querySelectorAll('main h1, main h2, main h3, main p, main dd, main li:not(.project)')]
          .filter((e) => !e.closest('.cine, [aria-hidden="true"]') && e.clientWidth > 0 && e.scrollWidth > e.clientWidth + 2)
          .map((e) => `${e.tagName}: ${e.textContent.trim().slice(0, 40)}`));
        expect(clipped, 'text running past its own box').toEqual([]);

        const broken = await page.evaluate(() => [...document.querySelectorAll('main img')]
          .filter((i) => !i.closest('.cine') && i.complete && i.naturalWidth === 0).map((i) => i.currentSrc || i.src));
        expect(broken.filter((u) => !isOptionalMedia(u)), 'broken content images').toEqual([]);

        const fonts = await page.evaluate(async () => { await document.fonts.ready;
          return [...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family.replace(/"/g, '')); });
        expect(fonts).toEqual(expect.arrayContaining(['Space Grotesk', 'Inter']));

        expect(problems, problems.join('\n')).toEqual([]);
      });

      test('every in-page link has a target; language links resolve', async ({ page, request }) => {
        await page.goto(route.path);
        const missing = await page.evaluate(() => [...document.querySelectorAll('a[href^="#"]')]
          .map((a) => a.getAttribute('href').slice(1)).filter((id) => id && !document.getElementById(id)));
        expect(missing, 'anchors without a target').toEqual([]);
        expect(await page.locator('[aria-disabled="true"]').count(), 'nav links still pending').toBe(0);
        for (const href of await page.locator('.lang a, link[rel=alternate]').evaluateAll((as) => as.map((a) => a.href))) {
          expect((await request.get(href)).status(), href).toBe(200);
        }
      });
    });
  }
}

test.describe('behaviour', () => {
  test('skip intro reaches the Hero, the nav appears, Let’s Talk lands on Contact', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto('/');
    const skip = page.locator('.cine__skip');
    // The button appears once the opening has started (none without the film).
    if (await skip.waitFor({ state: 'visible', timeout: 8_000 }).then(() => true, () => false)) await skip.click();
    await expect(page.locator('.site-header')).not.toHaveClass(/is-cine-hidden/, { timeout: 15_000 });
    await page.locator('.site-header .btn').click();
    await expect(page).toHaveURL(/#contact$/);
    await expect(page.locator('#contact')).toBeInViewport();
  });

  test('mobile menu opens, closes with Escape and returns focus', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/#work');
    const toggle = page.locator('.menu-toggle');
    await toggle.click();
    await expect(toggle).toHaveAttribute('aria-expanded', 'true');
    await page.keyboard.press('Escape');
    await expect(toggle).toHaveAttribute('aria-expanded', 'false');
    await expect(toggle).toBeFocused();
  });

  test('reduced motion: no opening, nothing hidden', async ({ browser }) => {
    const ctx = await browser.newContext({ reducedMotion: 'reduce', viewport: { width: 390, height: 844 } });
    const page = await ctx.newPage();
    await page.goto('/de/');
    await expect(page.locator('html')).not.toHaveClass(/cine-on/);
    await scrollThrough(page);
    const hidden = await page.evaluate(() => [...document.querySelectorAll('main *')]
      .filter((e) => e.closest('#work, #services, #approach, #about, #contact') && getComputedStyle(e).opacity === '0').length);
    expect(hidden).toBe(0);
    await ctx.close();
  });

  for (const [path, width, height] of [['/', 1440, 900], ['/de/', 390, 844]]) {
    test(`with motion, every reveal settles once scrolled into view (${path} @ ${width})`, async ({ page }) => {
      await page.setViewportSize({ width, height });
      await page.goto(path);
      const skip = page.locator('.cine__skip');
      if (await skip.waitFor({ state: 'visible', timeout: 8_000 }).then(() => true, () => false)) await skip.click();
      await expect(page.locator('html')).toHaveClass(/reveal-on/);
      await scrollThrough(page);
      await page.waitForTimeout(2200);                  // longest transition + stagger
      const left = await page.evaluate(() => ({
        pending: [...document.querySelectorAll('main [data-reveal]:not(.is-in)')].map((e) => e.className || e.tagName),
        hidden: [...document.querySelectorAll('main *')]
          .filter((e) => e.closest('#work, #services, #approach, #about, #contact') && getComputedStyle(e).opacity === '0')
          .map((e) => e.className || e.tagName),
      }));
      expect(left).toEqual({ pending: [], hidden: [] });
    });
  }

  test('without JavaScript every section is readable', async ({ browser }) => {
    const ctx = await browser.newContext({ javaScriptEnabled: false });
    const page = await ctx.newPage();
    await page.goto('/');
    for (const id of ['work', 'services', 'approach', 'about', 'contact']) await expect(page.locator('#' + id)).toBeVisible();
    await ctx.close();
  });
});
