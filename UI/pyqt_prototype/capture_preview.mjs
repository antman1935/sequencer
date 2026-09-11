import { chromium } from 'playwright';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const previewDir = dirname(fileURLToPath(import.meta.url));
const previewPath = resolve(previewDir, 'preview.html');
const screenshotPath = resolve(previewDir, 'preview.png');

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1180, height: 760 }, deviceScaleFactor: 1 });
await page.goto(`file://${previewPath}`);
await page.screenshot({ path: screenshotPath, fullPage: false });
await browser.close();
console.log(screenshotPath);
