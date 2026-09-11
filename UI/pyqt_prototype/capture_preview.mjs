import { chromium } from 'playwright';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const previewDir = dirname(fileURLToPath(import.meta.url));
const screenshotPath = resolve(previewDir, 'preview.png');

const browser = await chromium.launch({ headless: true, ...(process.env.SEQUENCER_BROWSER_CHANNEL ? { channel: process.env.SEQUENCER_BROWSER_CHANNEL } : {}) });
const page = await browser.newPage({ viewport: { width: 1180, height: 760 }, deviceScaleFactor: 1 });
await page.goto(process.env.SEQUENCER_URL || 'http://127.0.0.1:8765/');
await page.waitForFunction(() => document.querySelector('#status')?.textContent === 'Ready');
await page.screenshot({ path: screenshotPath, fullPage: false });
await browser.close();
console.log(screenshotPath);
