// The C20 keyboard check: a part holding focus rises, so a later sibling never paints over its ring.
//
//   node checks/focus-on-top/run.mjs <project-with-playwright> [chromium,firefox,webkit] [--negative]
//
// Each case puts two parts side by side with no gap, moves focus to the first by the keyboard (Tab), and reads
// one screen pixel 3px past the focused root's inline-end edge, at its vertical middle: on the ring (offset 2px,
// width 2px) and inside the neighbour's box. It must match the ring as read on the root's inline-start side, where
// nothing overlaps it, within 24 per channel, and that reference must differ from the neighbour's own face, so the
// sample can tell the two apart.
// --negative serves the kit with the C20 rules removed (the reset's z-index and the :focus-within z-index of
// text-field, combobox and spinbutton) and passes only when every case then sees the neighbour on top.
// Writes checks/focus-on-top/results.json.
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const args = process.argv.slice(2);
const negative = args.includes('--negative');
const positional = args.filter((a) => !a.startsWith('--'));
if (!positional[0]) { console.log('usage: node checks/focus-on-top/run.mjs <project-with-playwright> [engines] [--negative]'); process.exit(2); }
const { chromium, firefox, webkit } = createRequire(path.join(path.resolve(positional[0]), 'package.json'))('playwright');
const ENGINES = { chromium, firefox, webkit };
const engines = (positional[1] ?? 'chromium,firefox,webkit').split(',');
const TOLERANCE = 24;

/** The C20 rules, removed for the negative control. Each pattern must match, or the control removes nothing. */
const STRIP = {
  'kit/styles/reset.css': [/:where\(:is\(:focus-visible, \[data-focus-visible\]\)\) \{ z-index: 1; \}/],
  'kit/components/text-field/text-field.css': [/(:scope:where\(:focus-within\) \{\s*)z-index: 1;/],
  'kit/components/combobox/combobox.css': [/(:scope:where\(:focus-within\) \{\s*)z-index: 1;/],
  'kit/components/spinbutton/spinbutton.css': [/(:scope:where\(:focus-within\) \{\s*)z-index: 1;/],
};
const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml' };
const server = http.createServer((req, res) => {
  const rel = decodeURIComponent(new URL(req.url, 'http://x').pathname).replace(/^\/+/, '');
  const file = path.join(root, rel);
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end(); return; }
  let body = fs.readFileSync(file, 'utf8');
  if (negative && STRIP[rel]) for (const pattern of STRIP[rel]) {
    if (!pattern.test(body)) throw new Error(`negative control: ${rel} no longer holds ${pattern}`);
    body = body.replace(pattern, '$1');
  }
  res.writeHead(200, { 'content-type': TYPES[path.extname(file)] ?? 'application/octet-stream' });
  res.end(body);
});
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const url = `http://127.0.0.1:${server.address().port}/checks/focus-on-top/page.html`;

const CASES = [
  { name: 'two joined buttons: the focused button rises (reset)', focus: '#a-focus', active: '#a-focus', next: '#a-next', tabs: 1 },
  { name: 'a text field joined to a button: the field rises on :focus-within', focus: '#b-focus', active: '#b-input', next: '#b-next', tabs: 3 },
];

/** One pixel of the screen, as [r, g, b]. */
async function pixel(page, x, y) {
  const png = await page.screenshot({ clip: { x: Math.round(x), y: Math.round(y), width: 1, height: 1 }, animations: 'disabled', caret: 'hide' });
  return await page.evaluate(async (b64) => {
    const img = new Image(); img.src = `data:image/png;base64,${b64}`; await img.decode();
    const c = new OffscreenCanvas(1, 1).getContext('2d'); c.drawImage(img, 0, 0);
    return [...c.getImageData(0, 0, 1, 1).data.slice(0, 3)];
  }, png.toString('base64'));
}
const near = (a, b) => a.every((v, i) => Math.abs(v - b[i]) <= TOLERANCE);

const results = { negative, engines: [] };
let failed = 0;
for (const name of engines) {
  const browser = await ENGINES[name].launch();
  const page = await browser.newPage({ viewport: { width: 480, height: 240 }, deviceScaleFactor: 1 });
  await page.goto(url);
  await page.waitForSelector('html[data-ready]');
  const engine = { engine: `${name} ${browser.version()}`, cases: [] };
  for (const c of CASES) {
    await page.evaluate(() => { document.activeElement?.blur(); window.focus(); });
    await page.locator('body').click({ position: { x: 2, y: 2 } });
    for (let i = 0; i < c.tabs; i++) await page.keyboard.press(name === 'webkit' ? 'Alt+Tab' : 'Tab');
    // Tab until the intended part holds focus; WebKit's Tab order may skip parts.
    for (let i = 0; i < 6 && !(await page.evaluate((s) => document.activeElement === document.querySelector(s), c.active)); i++) await page.keyboard.press(name === 'webkit' ? 'Alt+Tab' : 'Tab');
    const focused = await page.evaluate((s) => document.activeElement === document.querySelector(s), c.active);
    const box = await page.locator(c.focus).boundingBox();
    const nextBox = await page.locator(c.next).boundingBox();
    const mid = box.y + box.height / 2;
    const ring = await pixel(page, box.x - 3, mid);                 // the ring where nothing overlaps it
    const sample = await pixel(page, box.x + box.width + 2, mid);   // 3px past the end edge: pixel column edge+2 covers [edge+2, edge+3)
    await page.evaluate(() => document.activeElement?.blur());
    const face = await pixel(page, box.x + box.width + 2, mid);     // the neighbour's own paint at the same point, with no ring
    const joined = Math.abs(nextBox.x - (box.x + box.width)) < 1;
    const discriminates = !near(ring, face);
    const onTop = near(sample, ring);
    const holds = focused && joined && discriminates && (negative ? !onTop : onTop);
    if (!holds) failed++;
    engine.cases.push({ name: c.name, focused, joined, ring, sample, face, discriminates, ringOnTop: onTop, holds });
    console.log(`${holds ? 'ok  ' : 'FAIL'} ${name}: ${c.name}: ring ${ring} sample ${sample} neighbour ${face}${focused ? '' : ' (focus not reached)'}${joined ? '' : ' (not joined)'}${discriminates ? '' : ' (ring and neighbour alike)'}`);
  }
  results.engines.push(engine);
  await browser.close();
}
server.close();
fs.writeFileSync(path.join(here, negative ? 'results.negative.json' : 'results.json'), JSON.stringify(results, null, 2) + '\n');
console.log(`${failed ? failed + ' case(s) failed' : 'all cases hold'}${negative ? ' (negative control: each case must see the neighbour on top)' : ''}`);
process.exit(failed ? 1 : 0);
