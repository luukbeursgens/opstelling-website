// Controleert de SEO-basis van elke pagina: titels, beschrijvingen, canoniek adres,
// gestructureerde gegevens, koppen, afbeeldingen met alt-tekst en de link naar de app.
import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const PAGINAS = ['/', '/prijzen/', '/wisselschema-maken/', '/speeltijd-eerlijk-verdelen/', '/knvb-wedstrijdvormen/', '/tips-en-tops-per-speler/', '/voetbal-nl-kalender-koppelen/', '/contact/'];
const TIPS = '/tips-en-tops-per-speler/', AGENDA = '/voetbal-nl-kalender-koppelen/';
const SITE = fs.readFileSync(path.join(process.cwd(), 'build.py'), 'utf8').match(/^SITE = "([^"]+)"/m)[1];   // het adres uit build.py
const titels = new Set(), beschrijvingen = new Set();
const BEACON = 'https://static.cloudflareinsights.com/beacon.min.js';
const BUILD = fs.readFileSync(path.join(process.cwd(), 'build.py'), 'utf8');
const APP = BUILD.match(/^APP = "([^"]+)"/m)[1];   // adres van de app uit build.py
const TOKEN = (BUILD.match(/^CF_TOKEN = "([^"]*)"/m) || [])[1] || '';

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
      const bestand = path.join(process.cwd(), href.split('#')[0], 'index.html');
      expect(fs.existsSync(bestand), `interne link ${href} bestaat niet`).toBe(true);
    }
    // geen javascript nodig; alleen de bezoekersteller van Cloudflare mag er staan
    for (const sc of await page.locator('script:not([type="application/ld+json"])').all()) {
      expect(await sc.getAttribute('src'), 'onverwacht script').toBe(BEACON);
    }

    // geen stukjes programmacode die per ongeluk als tekst op de pagina staan
    const tekst = await page.locator('body').innerText();
    expect(tekst, 'programmacode zichtbaar op de pagina').not.toMatch(/\{[a-z_]+\(|\}\}/);

    // elke afbeelding bestaat echt
    for (const img of await page.locator('img').all()) {
      const src = await img.getAttribute('src');
      expect(fs.existsSync(path.join(process.cwd(), src)), `afbeelding ${src} ontbreekt`).toBe(true);
    }
  });
}

const OPENBAAR = BUILD.includes('PUBLIEK = True');

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

test('bezoekersteller van Cloudflare staat aan als er een token is', async ({ page }) => {
  for (const p of PAGINAS) {
    await page.goto(p);
    const tellers = page.locator(`script[src="${BEACON}"]`);
    if (TOKEN) {
      await expect(tellers, `teller ontbreekt op ${p}`).toHaveCount(1);
      expect(JSON.parse(await tellers.getAttribute('data-cf-beacon')).token).toBe(TOKEN);
      expect(await tellers.getAttribute('defer')).not.toBeNull();
    } else {
      await expect(tellers).toHaveCount(0);
    }
  }
});

test('lettertypes komen van de eigen site, niet van Google', async ({ page }) => {
  const extern = [];
  page.on('request', r => { const u = new URL(r.url()); if (u.hostname !== 'localhost' && !u.hostname.endsWith('cloudflareinsights.com')) extern.push(r.url()); });
  await page.goto('/', { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  expect(extern, 'verzoeken naar andere sites').toEqual([]);
  const geladen = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/"/g, '')));
  expect(geladen).toContain('Bricolage Grotesque');
  expect(geladen).toContain('Figtree');
});

test.describe('zonder JavaScript', () => {
  test.use({ javaScriptEnabled: false, viewport: { width: 1280, height: 900 } });
  test('de vier stappen op de homepagina zijn aan te klikken', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#hoe .screens .s1')).toBeVisible();
    await expect(page.locator('#hoe .screens .s2')).toBeHidden();
    for (const n of [2, 3, 4]) {
      await page.click(`#hoe label[for=t${n}]`);
      await expect(page.locator(`#hoe .screens .s${n}`)).toBeVisible();
      await expect(page.locator(`#hoe .screens .s1`)).toBeHidden();
    }
  });
});

test('schermafbeeldingen in het telefoonframe worden niet afgesneden of vervormd', async ({ page }) => {
  for (const p of ['/', TIPS, AGENDA]) {
  await page.goto(p);
  for (const img of await page.locator('img[loading=lazy]').all()) await img.scrollIntoViewIfNeeded();
  await page.waitForLoadState('networkidle');
  const maten = await page.$$eval('.phone img, .report img, .kaartbeeld img, .plaatje img', imgs => imgs.map(i => {
    const cs = getComputedStyle(i);
    const w = i.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    const h = i.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
    return { src: i.getAttribute('src'), zichtbaar: h / w, echt: i.height && i.width ? Number(i.getAttribute('height')) / Number(i.getAttribute('width')) : 0, fit: cs.objectFit, w };
  }));
  expect(maten.length).toBeGreaterThan(1);
  for (const m of maten) {
    if (!m.w) continue;   // verborgen stap
    expect(m.fit, `${m.src} wordt bijgesneden`).not.toBe('cover');
    expect(Math.abs(m.zichtbaar - m.echt), `${m.src} is vervormd`).toBeLessThan(0.02);
  }
  }
});

test('contactformulier gaat via Netlify naar een bedankpagina', async ({ page }) => {
  await page.goto('/contact/');
  const form = page.locator('form[name=contact]');
  await expect(form).toHaveCount(1);
  expect(await form.getAttribute('data-netlify')).toBe('true');
  expect(await form.getAttribute('method')).toBe('POST');
  expect(await form.getAttribute('netlify-honeypot')).toBe('bedrijf');
  expect(await form.locator('input[name=form-name]').getAttribute('value')).toBe('contact');
  for (const veld of ['naam', 'email', 'bericht']) {
    expect(await form.locator(`[name=${veld}]`).getAttribute('required'), `${veld} verplicht`).not.toBeNull();
  }
  for (const veld of await form.locator('input:not([type=hidden]):not([name=bedrijf]), select, textarea').all()) {
    const id = await veld.getAttribute('id');
    await expect(page.locator(`label[for="${id}"]`), `label bij ${id}`).toHaveCount(1);
  }
  await expect(page.locator('a[href="mailto:info@opstellingapp.nl"]')).toHaveCount(1);
  const doel = await form.getAttribute('action');
  expect(fs.existsSync(path.join(process.cwd(), doel, 'index.html'))).toBe(true);
  await page.goto(doel);
  await expect(page.locator('h1')).toContainText('Bedankt');
  expect(await page.getAttribute('meta[name=robots]', 'content')).toBe('noindex, nofollow');
  const sm = await (await page.request.get('/sitemap.xml')).text();
  expect(sm).not.toContain('/bedankt/');
});

test('knoppen naar de app openen account aanmaken; geen privacypagina, geen O13, prijs per seizoen', async ({ page }) => {
  for (const p of PAGINAS) {
    await page.goto(p);
    const knoppen = await page.$$eval(`a[href^="${APP}"]`, as => as.map(a => a.getAttribute('href')));
    expect(knoppen.length).toBeGreaterThan(0);
    for (const k of knoppen) expect(k, `knop op ${p}`).toBe(`${APP}/?account=nieuw`);
    await expect(page.locator('a[href*="netlify.app"]'), `oud adres op ${p}`).toHaveCount(0);
    await expect(page.locator('a[href^="/privacy"]'), `link naar privacy op ${p}`).toHaveCount(0);
    expect(await page.locator('body').innerText(), `O13 op ${p}`).not.toContain('O13');
  }
  expect(fs.existsSync(path.join(process.cwd(), 'privacy'))).toBe(false);
  for (const p of ['/', '/prijzen/']) {
    await page.goto(p);
    await expect(page.locator('.plan.featured')).toContainText('€ 29,99');
    await expect(page.locator('.plan.featured')).toContainText('per seizoen');
  }
});

test('stijlbestand heeft een versienummer dat bij de inhoud past', async ({ page }) => {
  const crypto = await import('crypto');
  const verwacht = crypto.createHash('sha256').update(fs.readFileSync(path.join(process.cwd(), 'style.css'))).digest('hex').slice(0, 10);
  for (const p of PAGINAS) {
    await page.goto(p);
    expect(await page.getAttribute('link[rel=stylesheet]', 'href'), `stijl op ${p}`).toBe(`/style.css?v=${verwacht}`);
  }
});

// ---------- tips en tops en de wedstrijdagenda (sept 2026) ----------

test('menu: tips en tops en wedstrijdagenda bovenaan, KNVB-wedstrijdvormen alleen in de voettekst', async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto('/');
  const kop = await page.$$eval('header.site nav a', as => as.map(a => a.getAttribute('href')));
  expect(kop).toEqual(['/wisselschema-maken/', '/speeltijd-eerlijk-verdelen/', TIPS, AGENDA, '/prijzen/', '/contact/']);
  const voet = await page.$$eval('footer.site nav a', as => as.map(a => a.getAttribute('href')));
  for (const p of [TIPS, AGENDA, '/knvb-wedstrijdvormen/']) expect(voet, `voettekst mist ${p}`).toContain(p);
  await page.goto(TIPS);
  await expect(page.locator(`header.site nav a[href="${TIPS}"]`)).toHaveAttribute('aria-current', 'page');
});

test('homepagina: blok over het hele seizoen met echte schermen en links naar beide pagina\'s', async ({ page }) => {
  await page.goto('/');
  const blok = page.locator('#seizoen');
  await expect(blok.locator('h2').first()).toHaveText('Het hele seizoen in één app');
  await expect(blok.locator(`a[href="${AGENDA}"]`)).toHaveCount(1);
  await expect(blok.locator(`a[href="${TIPS}"]`)).toHaveCount(1);
  const beelden = await blok.locator('img').evaluateAll(i => i.map(x => x.getAttribute('src')));
  expect(beelden).toEqual(['/img/site-agenda-wedstrijden.webp', '/img/site-ouders-plaatje.webp', '/img/site-speler-tips-tops.webp']);
  await expect(blok).toContainText('wie de shirts wast');
  await expect(page.locator('label[for=t4] b')).toHaveText('Bijhouden en verbeteren');
  await expect(page.locator('.checks')).toContainText('Voetbal.nl');
  await expect(page.locator('.incl')).toContainText('Tips en tops per speler');
});

test('nieuwe pagina\'s: kruimelpad, veelgestelde vragen en functies in de gegevens voor zoekmachines', async ({ page }) => {
  for (const [p, naam] of [[TIPS, 'Tips en tops'], [AGENDA, 'Wedstrijdagenda']]) {
    await page.goto(p);
    await expect(page.locator('nav.kruimel a[href="/"]')).toHaveCount(1);
    await expect(page.locator('nav.kruimel')).toContainText(naam);
    const graph = JSON.parse(await page.locator('script[type="application/ld+json"]').first().textContent())['@graph'];
    const kruimel = graph.find(x => x['@type'] === 'BreadcrumbList');
    expect(kruimel.itemListElement.map(x => x.name)).toEqual(['Home', naam]);
    expect(kruimel.itemListElement[1].item).toBe(SITE + p);
    const faq = graph.find(x => x['@type'] === 'FAQPage');
    expect(faq.mainEntity.length).toBeGreaterThanOrEqual(4);
    // wat op de pagina staat, staat ook in de gegevens (en andersom)
    await expect(page.locator('.faq summary')).toHaveText(faq.mainEntity.map(q => q.name));
  }
  await page.goto('/');
  const app = JSON.parse(await page.locator('script[type="application/ld+json"]').first().textContent())['@graph'].find(x => x['@type'] === 'SoftwareApplication');
  expect(app.featureList.join(' ')).toContain('Tips en tops');
  expect(app.featureList.join(' ')).toContain('Voetbal.nl');
});

test('agendapagina: drie stappen en een eigen blok over het plaatje voor de ouders', async ({ page }) => {
  await page.goto(AGENDA);
  await expect(page.locator('ol.stappen li')).toHaveCount(3);
  const blok = page.locator('.ouderblok');
  await expect(blok.locator('h2')).toHaveText('Verzameltijd, wassen en fruit in één plaatje');
  await expect(blok.locator('.ouderpunten > div')).toHaveCount(4);
  await expect(blok.locator('img[src="/img/site-ouders-plaatje.webp"]')).toHaveCount(1);
  await expect(page.locator('main')).toContainText('niet verbonden aan Voetbal.nl');
});

test('tips-en-topspagina: alle vaardigheden uit de app staan als tekst op de pagina', async ({ page }) => {
  await page.goto(TIPS);
  const tekst = await page.locator('.kolommen').innerText();
  for (const v of ['Passen over de grond', 'Aannemen in beweging', 'Drijven', 'Knijpen', 'Rugdekking geven', 'Druk zetten rennend']) expect(tekst).toContain(v);
  await expect(page.locator('main')).toContainText('Alleen zichtbaar voor trainers');
});

test('llms.txt vat de site samen voor AI-assistenten', async ({ page }) => {
  const r = await page.request.get('/llms.txt');
  expect(r.status()).toBe(200);
  const t = await r.text();
  expect(t.startsWith('# Opstelling\n')).toBe(true);
  expect(t).toMatch(/^> .+/m);
  for (const p of PAGINAS) expect(t, `llms.txt mist ${p}`).toContain(`(${SITE}${p})`);
  expect(t).toContain('29,99 euro per team per seizoen');
  expect(t).toContain('Voetbal.nl');
  const rb = await (await page.request.get('/robots.txt')).text();
  if (OPENBAAR) expect(rb).not.toMatch(/Disallow: \/\s/);
});

test('geen horizontaal scrollen op telefoon, tablet en laptop', async ({ page }) => {
  for (const breedte of [320, 390, 768, 1024, 1440]) {
    await page.setViewportSize({ width: breedte, height: 900 });
    for (const p of PAGINAS) {
      await page.goto(p);
      const [sw, cw] = await page.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]);
      expect(sw, `${p} is breder dan het scherm op ${breedte}px`).toBeLessThanOrEqual(cw);
    }
  }
});

// ---------- prijs: 29,99 euro per team per seizoen (okt 2026) ----------

test('prijs is overal 29,99 euro per team per seizoen, ook in de gegevens voor Google en AI', async ({ page }) => {
  const oud = /kwartaal|opzegbaar|(^|[^0-9])6,99/i;
  for (const p of PAGINAS) {
    await page.goto(p);
    expect(await page.locator('body').innerText(), `oude prijs op ${p}`).not.toMatch(oud);
    expect(await page.title(), `oude prijs in titel van ${p}`).not.toMatch(oud);
    for (const sel of ['meta[name=description]', 'meta[property="og:description"]', 'meta[property="og:title"]']) {
      expect(await page.getAttribute(sel, 'content'), `oude prijs in ${sel} op ${p}`).not.toMatch(oud);
    }
    for (const ld of await page.locator('script[type="application/ld+json"]').allTextContents()) {
      expect(ld, `oude prijs in de gestructureerde gegevens van ${p}`).not.toMatch(oud);
    }
  }
  for (const p of ['/', '/prijzen/']) {
    await page.goto(p);
    const graph = JSON.parse(await page.locator('script[type="application/ld+json"]').first().textContent())['@graph'];
    const app = graph.find(x => x['@type'] === 'SoftwareApplication');
    expect(app, `app-gegevens op ${p}`).toBeTruthy();
    const prijzen = app.offers.map(o => [o.price, o.priceCurrency]);
    expect(prijzen).toEqual([['0', 'EUR'], ['29.99', 'EUR']]);
    expect(app.offers[1].description).toContain('seizoen');
  }
  await page.goto('/prijzen/');
  expect(await page.title()).toContain('29,99');
  expect(await page.getAttribute('meta[name=description]', 'content')).toContain('per seizoen');
  const llms = await (await page.request.get('/llms.txt')).text();
  expect(llms).not.toMatch(oud);
  expect(llms).toContain('vooraf');
});

test('agendapagina: beschrijving sluit aan op de zoekvraag en belooft geen "één tik" voor het ouderplaatje', async ({ page }) => {
  await page.goto(AGENDA);
  const desc = await page.getAttribute('meta[name=description]', 'content');
  expect(desc).toContain('Voetbal.nl-kalender');
  expect(desc).toContain('3 stappen');
  expect(desc).not.toContain('één tik');
  expect(await page.locator('main').textContent()).not.toContain('één tik');
  // ook op de homepagina geen "één tik" bij het plaatje voor de ouders
  await page.goto('/');
  const seizoen = await page.locator('main').textContent();
  expect(seizoen).not.toMatch(/één tik een plaatje/);
  expect(seizoen).not.toMatch(/met één tik weten wie er meegaat/);
});
