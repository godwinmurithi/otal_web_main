// QA: every page loads, no JS errors, no horizontal overflow, no broken internal links/images; screenshots.
import { chromium } from '/root/shots/node_modules/playwright-core/index.mjs';
import fs from 'fs';
const ORIGIN = process.env.ORIGIN || 'https://orionterrametrics.com';
const BASE = '/company/';
const SHOTS = process.env.SHOTS || '/tmp/corp-shots';
fs.mkdirSync(SHOTS, { recursive: true });
const pages = JSON.parse(fs.readFileSync(new URL('../dist/search-index.json', import.meta.url))).map(p => p.u);
const browser = await chromium.launch({ executablePath: '/root/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell' });
const problems = []; const seen = new Set(); const links = new Set();
for (const [vw, vh, tag] of [[1440, 900, 'd'], [390, 844, 'm']]) {
  const ctx = await browser.newContext({ viewport: { width: vw, height: vh } });
  for (const p of pages) {
    const pg = await ctx.newPage(); const errs = [];
    pg.on('pageerror', e => errs.push(e.message));
    pg.on('response', r => { if (r.status() >= 400 && r.url().startsWith(ORIGIN + BASE)) errs.push(r.status() + ' ' + r.url()); });
    await pg.goto(ORIGIN + BASE + p, { waitUntil: 'networkidle' });
    await pg.evaluate(() => document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager'));
    await pg.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } scrollTo(0, 0); });
    await pg.waitForLoadState('networkidle');
    const ov = await pg.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    if (ov > 1) problems.push(`${tag} ${p || 'index'}: horizontal overflow ${ov}px`);
    errs.forEach(e => problems.push(`${tag} ${p || 'index'}: ${e}`));
    if (tag === 'd') (await pg.$$eval('a[href]', as => as.map(a => a.href))).forEach(h => links.add(h));
    if (['', 'proposal.html', 'surveying.html', 'health.html', 'portfolio.html', 'projects/athi-water-works-registry.html', 'technology.html', 'careers.html', 'contact.html', 'about.html'].includes(p)) {
      await pg.screenshot({ path: `${SHOTS}/${tag}-${(p || 'index').replace(/\W+/g, '_')}.png`, fullPage: true });
    }
    await pg.close();
  }
  await ctx.close();
}
// internal link check
for (const h of links) {
  const url = h.split('#')[0].split('?')[0];
  if (!url.startsWith(ORIGIN + BASE) || seen.has(url)) continue; seen.add(url);
  const r = await fetch(url); if (r.status >= 400) problems.push('broken link ' + r.status + ' ' + url);
}
await browser.close();
console.log(`pages ${pages.length} x2 viewports, internal links ${seen.size}, problems ${problems.length}`);
problems.forEach(p => console.log(' - ' + p));
