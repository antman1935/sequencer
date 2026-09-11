import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdir, readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const environmentPython = resolve(root, process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');
const python = process.env.SEQUENCER_PYTHON || (existsSync(environmentPython) ? environmentPython : 'python');
const server = spawn(python, ['UI/pyqt_prototype/web_server.py', '--port', '0'], {cwd: root, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe']});
let logs = '', browser;
server.stderr.on('data', (chunk) => { logs += chunk; });
const artifacts = resolve(root, '.venv/ui-test-artifacts');
await mkdir(artifacts, {recursive: true});

try {
  const url = await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`Server startup timed out: ${logs}`)), 15000);
    let output = '';
    server.stdout.on('data', (chunk) => {
      output += chunk;
      const match = output.match(/Sequencer: (http:\/\/127\.0\.0\.1:\d+\/)/);
      if (match) { clearTimeout(timer); resolve(match[1]); }
    });
    server.once('error', reject);
    server.once('exit', (code) => { clearTimeout(timer); reject(new Error(`Server exited (${code}): ${logs}`)); });
  });
  browser = await chromium.launch({headless: true, ...(process.env.SEQUENCER_BROWSER_CHANNEL ? {channel: process.env.SEQUENCER_BROWSER_CHANNEL} : {})});
  const page = await browser.newPage({viewport: {width: 1180, height: 760}});
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto(url);
  await page.waitForFunction(() => document.querySelector('#status').textContent === 'Ready');
  const run = async (status = 'Complete') => {
    await page.getByRole('button', {name: 'Run query', exact: true}).click();
    await page.waitForFunction(() => ['Complete', 'Failed'].includes(document.querySelector('#status').textContent));
    assert.equal(await page.locator('#status').textContent(), status, await page.locator('#error').textContent());
  };
  for (const [name, count] of Object.entries({catalan: 14, fubini: 75, parking_func: 125, stirling: 105, type_b: 116})) {
    await page.getByLabel('Object', {exact: true}).selectOption(name);
    await page.locator('#parameters [data-parameter="n"]').fill('4');
    await run();
    assert.match(await page.locator('#panel-0').textContent(), new RegExp(`= ${count}\\s*$`));
  }
  await page.getByLabel('Object', {exact: true}).selectOption('fubini');
  await page.locator('#parameters [data-parameter="n"]').fill('3');
  await page.getByLabel('API', {exact: true}).selectOption('range');
  await run('Failed');
  assert.match(await page.locator('#error').textContent(), /at least one range dimension/);
  await page.getByLabel('Parameter: n', {exact: true}).check();
  await page.getByLabel('Computed: Runs', {exact: true}).check();
  await page.getByRole('button', {name: '+ Add OR restriction group', exact: true}).click();
  await page.getByLabel('Restriction', {exact: true}).selectOption('zigzag');
  await page.locator('.restriction-row [data-parameter="is"]').selectOption('true');
  await run();
  assert.deepEqual(await page.locator('tbody tr').allTextContents(), ['n=110', 'n=211', 'n=306']);
  await page.getByRole('tab', {name: 'Text', exact: true}).click();
  assert.match(await page.locator('#panel-0').textContent(), /Range Query on FubiniRankings/);
  await page.getByRole('tab', {name: 'Text', exact: true}).press('ArrowRight');
  assert.equal(await page.getByRole('tab', {name: 'Table', exact: true}).getAttribute('aria-selected'), 'true');
  await page.getByLabel('Show generated elements').check();
  await run();
  assert.match(await page.locator('#panel-0').textContent(), /Elements:/);
  await page.screenshot({path: resolve(artifacts, 'browser-desktop.png')});

  await page.getByLabel('Range output').selectOption('latex');
  await run();
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('link', {name: 'Download out.tex'}).click();
  const download = await downloadPromise;
  const file = resolve(artifacts, 'browser-output.tex');
  await download.saveAs(file);
  assert.match(await readFile(file, 'utf8'), /\\documentclass\{article\}/);
  assert.match(await readFile(file, 'utf8'), /\\end\{document\}/);

  await page.getByLabel('Range output').selectOption('raw');
  await run();
  assert.match(await page.locator('#panel-0').textContent(), /Raw output:/);
  await page.getByLabel('Computed: Runs', {exact: true}).uncheck();
  await page.getByLabel('Range output').selectOption('oeis');
  await run();
  assert.match(await page.locator('#panel-0').textContent(), /n\(1-3\): 1 2 6/);
  await page.getByRole('button', {name: 'Remove restriction group', exact: true}).click();
  await page.getByLabel('Range output').selectOption('ascii');
  await page.getByLabel('Computed: Runs', {exact: true}).check();
  await page.getByLabel('Parameter: k', {exact: true}).check();
  await page.locator('#parameters [data-parameter="k"]').fill('3');
  await run();
  assert.ok(await page.getByRole('tab').count() > 2);

  // AND in a group, OR between groups, removal, and explicit false.
  await page.getByLabel('API', {exact: true}).selectOption('point');
  await page.getByRole('button', {name: '+ Add OR restriction group', exact: true}).click();
  await page.getByLabel('Restriction', {exact: true}).selectOption('zigzag');
  await page.locator('.restriction-row [data-parameter="is"]').selectOption('true');
  await page.getByRole('button', {name: '+ Add restriction', exact: true}).click();
  await page.getByLabel('Restriction', {exact: true}).nth(1).selectOption('zigzag');
  await page.locator('.restriction-row [data-parameter="is"]').nth(1).selectOption('false');
  await run();
  assert.match(await page.locator('#panel-0').textContent(), /= 0\s*$/);
  await page.getByRole('button', {name: 'Remove restriction', exact: true}).nth(1).click();
  await page.getByRole('button', {name: '+ Add OR restriction group', exact: true}).click();
  await page.getByLabel('Restriction', {exact: true}).nth(1).selectOption('zigzag');
  await page.locator('.restriction-row [data-parameter="is"]').nth(1).selectOption('false');
  await run();
  assert.match(await page.locator('#panel-0').textContent(), /= 13\s*$/);
  await page.getByLabel('Statistic', {exact: true}).selectOption('runs');
  await run();
  assert.doesNotMatch(await page.locator('#panel-0').textContent(), /= 13\s*$/);

  // A narrow viewport must not horizontally clip the form or result card.
  await page.setViewportSize({width: 390, height: 844});
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  await page.screenshot({path: resolve(artifacts, 'browser-mobile.png'), fullPage: true});
  await page.setViewportSize({width: 1180, height: 760});
  await page.evaluate(() => { document.documentElement.style.fontSize = '32px'; });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  await page.screenshot({path: resolve(artifacts, 'browser-large-text.png'), fullPage: true});
  assert.deepEqual(errors, []);
  console.log('Browser integration passed: all object families, range formats, restrictions, exports, keyboard tabs, mobile, and enlarged text.');
  console.log(`Screenshots: ${artifacts}`);
} finally {
  await browser?.close();
  if (process.platform === 'win32') spawnSync('taskkill', ['/PID', String(server.pid), '/T', '/F'], {windowsHide: true, stdio: 'ignore'});
  else server.kill();
}
