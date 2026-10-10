// Maakt img/og.png (de deelkaart) uit tests/deelkaart.html. Draai: npm run deelkaart
import { chromium } from '@playwright/test';
import path from 'path';
import { pathToFileURL } from 'url';

const bron = pathToFileURL(path.join(process.cwd(), 'tests', 'deelkaart.html')).href;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
await page.goto(bron);
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: path.join(process.cwd(), 'img', 'og.png') });
await browser.close();
console.log('Deelkaart gemaakt: img/og.png');
