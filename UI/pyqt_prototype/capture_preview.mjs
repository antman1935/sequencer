import { chromium } from 'playwright';
import { resolve } from 'node:path';

const previewPath = resolve('UI/pyqt_prototype/preview.html');
const screenshotPath = resolve('UI/pyqt_prototype/preview.png');

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1180, height: 760 }, deviceScaleFactor: 1 });
await page.goto(`file://${previewPath}`);
await page.screenshot({ path: screenshotPath, fullPage: false });
await browser.close();
console.log(screenshotPath);
