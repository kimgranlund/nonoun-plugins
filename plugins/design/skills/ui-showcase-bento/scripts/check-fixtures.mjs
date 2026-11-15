#!/usr/bin/env node
// Runs the in-page checker (check.js) on one passing fixture sheet and five broken copies in headless Chromium.
// Each broken copy must fail on its own error; the passing sheet must pass with every axis combination checked.
//   node scripts/check-fixtures.mjs        prints one line per case and exits 1 on a wrong verdict, 0 with "skipped" when no Chromium is found
// Chromium: $BENTO_CHROME, else Google Chrome, Chrome Canary or Chromium in /Applications, else Playwright's cache.
import { existsSync, mkdtempSync, mkdirSync, writeFileSync, readdirSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
import { tmpdir, homedir } from 'node:os'
import { join } from 'node:path'
import { merge, pack } from './lib.mjs'
import { render } from './scaffold.mjs'

export function findChrome() {
  const fixed = [process.env.BENTO_CHROME,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser']
  for (const p of fixed) if (p && existsSync(p)) return p
  for (const cache of [join(homedir(), 'Library/Caches/ms-playwright'), join(homedir(), '.cache/ms-playwright')]) {
    if (!existsSync(cache)) continue
    for (const d of readdirSync(cache).filter((d) => d.startsWith('chromium_headless_shell-')).sort().reverse())
      for (const sub of readdirSync(join(cache, d))) {
        const p = join(cache, d, sub, 'chrome-headless-shell')
        if (existsSync(p)) return p
      }
  }
  return null
}

// A small sheet: two groups, three specimens and 40 axis combinations (more than the old default cap of 24).
const SPEC = {
  id: 'fixture', owns: ['lengths'], title: 'Fixture', canvas: { width: 640, height: 420 },
  chrome: { margin: 16, gutter: 12, pad: 16, radius: 12, texture: 'grid' },
  groups: [
    { id: 'g1', label: 'One', specimens: [{ id: 'a', label: 'A' }, { id: 'b', label: 'B' }] },
    { id: 'g2', label: 'Two', specimens: [{ id: 'c', label: 'C' }] },
  ],
  axes: [
    { name: 'material', attr: 'data-material', values: ['x', 'y', 'z', 'u', 'v'], captions: { y: 'Y caption', z: 'Z caption' } },   // x has none: the bar must not change height
    { name: 'k', attr: 'data-k', values: ['p', 'q'] },
  ],
}
const STYLE = '.box { display: inline-block; width: 80px; height: 32px; background: #ccc }\n'
const PART = (id) => `<span class="box" data-part="${id}">${id}</span>`

export const CASES = [
  { name: 'pass', expect: null },
  { name: 'scaled', expect: /^scaled: a /, style: '[data-specimen="a"] .box { transform: scale(.5) }' },
  { name: 'overflow', expect: /^overflow: g1 needs \d+px more width/, fragments: { a: '<span class="box" data-part="a" style="width: 2000px">a</span>' } },
  { name: 'padding', expect: /^clipped: g2 › c leaves the tile's content box/, style: '[data-group="g2"] { position: relative }',
    fragments: { c: PART('c') + '<span data-part="c-pad" style="position: absolute; right: 4px; bottom: 4px; width: 8px; height: 8px; background: #c00"></span>' } },
  { name: 'label', expect: /^label: specimen:b has no \[data-label\] text/, mutate: (h) => h.replace('data-label>B</figcaption>', 'data-label></figcaption>') },
  { name: 'moves', expect: /^invariance: \d+ boxes differ/, style: ':root[data-material="y"] [data-part="a"] { width: 90px }' },
]

const RESULT = `<script>document.fonts.ready.then(() => { const r = uiBentoCheck({ final: true }); const p = document.createElement('pre');
p.id = 'bento-result'; p.textContent = JSON.stringify(r); document.body.append(p) })</script>`
const unescape = (s) => s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&')

export function runFixtures(chrome = findChrome()) {
  if (!chrome) return null
  const dir = mkdtempSync(join(tmpdir(), 'bento-fixtures-'))
  const spec = merge([{ ...structuredClone(SPEC), dir }])
  const p = pack(spec)
  return CASES.map((c) => {
    const sp = join(dir, c.name); mkdirSync(sp)
    for (const id of ['a', 'b', 'c']) writeFileSync(join(sp, id + '.html'), c.fragments?.[id] ?? PART(id))
    writeFileSync(join(sp, 'style.css'), STYLE + (c.style ?? ''))
    let html = '<!doctype html>\n<html lang="en"><meta charset="utf-8">\n' + render(spec, p, { specimens: sp, style: join(sp, 'style.css') }) + RESULT
    if (c.mutate) html = c.mutate(html)
    const file = join(dir, c.name + '.html'); writeFileSync(file, html)
    const dom = execFileSync(chrome, ['--headless=new', '--disable-gpu', '--dump-dom', '--virtual-time-budget=3000', '--window-size=900,700', 'file://' + file],
      { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], timeout: 60000 })
    const m = dom.match(/<pre id="bento-result">([\s\S]*?)<\/pre>/)
    if (!m) return { name: c.name, pass: false, why: 'no result in the page' }
    const r = JSON.parse(unescape(m[1]))
    if (!c.expect) {
      const sampled = r.warnings.find((w) => w.startsWith('axes: checked'))
      return { name: c.name, pass: r.ok && !sampled, why: r.ok ? sampled ?? 'ok, every combination checked' : r.errors[0] }
    }
    const hit = r.errors.find((e) => c.expect.test(e))
    return { name: c.name, pass: !r.ok && !!hit, why: hit ?? `expected ${c.expect}, got ${r.errors[0] ?? 'no error'}` }
  })
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const res = runFixtures()
  if (!res) { console.log('skipped: no Chromium found (set BENTO_CHROME)'); process.exit(0) }
  for (const r of res) console.log(`${r.pass ? 'ok  ' : 'FAIL'} ${r.name.padEnd(9)} ${r.why}`)
  const bad = res.filter((r) => !r.pass).length
  console.log(bad ? `${bad} of ${res.length} fixture cases wrong` : `${res.length} of ${res.length} fixture cases right`)
  process.exit(bad ? 1 : 0)
}
