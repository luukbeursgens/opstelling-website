// Controleert de SEO-basis van elke pagina: titels, beschrijvingen, canoniek adres,
// gestructureerde gegevens, koppen, afbeeldingen met alt-tekst en de link naar de app.
import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const PAGINAS = ['/', '/prijzen/', '/wisselschema-maken/', '/speeltijd-eerlijk-verdelen/', '/knvb-wedstrijdvormen/', '/privacy/'];
const SITE = 'https://opstelling.nl';
const titels = new Set(), beschrijvingen = new Set();

for (const p of PAGINAS) {
  test(`SEO-basis op ${p}`, async ({ page }) => {
    const res = await page.goto(p);
    expect(res.status()).toBe(200);

    const titel = await page.title();
    expect(titel.length, 'titel te kort of te lang').toBeGreaterThan(20);
    expect(titel.length).toBeLessThan(65);
    expect(titels.has(titel), 'dubbele titel').toBe(false); titels.add(titel);

    const desc = await page.getAttribute('meta[name=description]', 'content');
    expect(desc.length).toBeGreaterThan(70);
    expect(desc.length).toBeLessThan(165);
    expect(beschrijvingen.has(desc), 'dubbele beschrijving').toBe(false); beschrijvingen.add(desc);

    expect(await page.getAttribute('link[rel=canonical]', 'href')).toBe(SITE + p);
    expect(await page.getAttribute('html', 'lang')).toBe('nl');
    await expect(page.locator('h1')).toHaveCount(1);
    expect((await page.locator('h1').textContent()).trim().length).toBeGreaterThan(10);

    // gestructureerde gegevens zijn geldig en horen bij deze pagina
    const ld = JSON.parse(await page.locator('script[type="application/ld+json"]').first().textContent());
    const types = ld['@graph'].map(x => x['@type']);
    expect(types).toContain('WebPage');
    expect(ld['@graph'].find(x => x['@type'] === 'WebPage').url).toBe(SITE + p);

    // sociale kaart
    expect(await page.getAttribute('meta[property="og:title"]', 'content')).toBe(titel);
    expect(await page.getAttribute('meta[property="og:image"]', 'content')).toBe(SITE + '/img/og.png');

    // elke afbeelding heeft alt-tekst en afmetingen (voorkomt verspringen)
    for (const img of await page.locator('img').all()) {
      expect(await img.getAttribute('alt'), 'afbeelding zonder alt').not.toBeNull();
      expect(await img.getAttribute('width'), 'afbeelding zonder breedte').not.toBeNull();
    }

    // duidelijke oproep naar de app
    const cta = page.locator('a[href*="opstellingapp"]');
    expect(await cta.count()).toBeGreaterThan(0);

    // interne links werken
    for (const a of await page.locator('main a[href^="/"]').all()) {
      const href = await a.getAttribute('href');
      const bestand = path.join('/home/claude/site', href, 'index.html');
      expect(fs.existsSync(bestand), `interne link ${href} bestaat niet`).toBe(true);
    }
    // geen javascript nodig
    expect(await page.locator('script:not([type="application/ld+json"])').count()).toBe(0);
  });
}

const OPENBAAR = fs.readFileSync(path.join(process.cwd(), 'build.py'), 'utf8').includes('PUBLIEK = True');

test('sitemap en robots kloppen bij de huidige stand', async ({ page }) => {
  const sm = await (await page.request.get('/sitemap.xml')).text();
  for (const p of PAGINAS) expect(sm).toContain(`<loc>${SITE}${p}</loc>`);
  const rb = await (await page.request.get('/robots.txt')).text();
  if (OPENBAAR) {
    expect(rb).toContain('Sitemap: ' + SITE + '/sitemap.xml');
    expect(rb).not.toContain('Disallow: /');
  } else {
    // nog niet openbaar: zoekmachines moeten geweerd worden
    expect(rb).toContain('Disallow: /');
    await page.goto('/');
    expect(await page.getAttribute('meta[name=robots]', 'content')).toBe('noindex, nofollow');
  }
});

test('pagina is licht en laadt snel', async ({ page }) => {
  let bytes = 0;
  page.on('response', async r => { try { bytes += (await r.body()).length; } catch { /* */ } });
  await page.goto('/', { waitUntil: 'load' });
  expect(bytes, 'homepagina groter dan 500 kB').toBeLessThan(500 * 1024);
});
