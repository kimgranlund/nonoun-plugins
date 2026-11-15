#!/usr/bin/env node
// The skill's own check: does the feedback module do what SKILL.md says?
//
//   node scripts/check.mjs <project-with-playwright> [chromium,webkit]
//
// The project path only supplies Playwright (or playwright-core) and its browsers. Each check runs twice per engine:
// against assets/feedback.js and feedback.css as they are, where it must pass, and against a copy with one behaviour
// removed by a text edit, where it must fail (the negative control). An edit whose pattern no longer matches is an
// error, so a control can never silently remove nothing. Input is real clicks; the JSON is read from the module's own
// preview. The last check runs scripts/inline.mjs twice on a copy of the fixture; it has no control.
import { createRequire } from 'node:module'
import { execFileSync } from 'node:child_process'
import { mkdtempSync, readFileSync, writeFileSync, rmSync } from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const args = process.argv.slice(2)
if (!args[0]) { console.log('usage: node scripts/check.mjs <project-with-playwright> [chromium,webkit]'); process.exit(2) }
const req = createRequire(path.join(path.resolve(args[0]), 'package.json'))
let pw; try { pw = req('playwright') } catch (e) { pw = req('playwright-core') }
const engines = (args[1] || 'chromium,webkit').split(',')
const CSS = readFileSync(path.join(here, '../assets/feedback.css'), 'utf8')
const JS = readFileSync(path.join(here, '../assets/feedback.js'), 'utf8')
const SRC = readFileSync(path.join(here, 'check.page.html'), 'utf8')
const tmp = mkdtempSync(path.join(os.tmpdir(), 'explore-check-'))

const edit = (text, from, to) => { if (!text.includes(from)) throw new Error(`negative control: the module no longer holds ${JSON.stringify(from)}`); return text.replace(from, to) }
let n = 0
const build = ({ page = (s) => s, js = (s) => s, css = (s) => s } = {}) => {
  const f = path.join(tmp, `p${n++}.html`)
  writeFileSync(f, page(SRC).replace('/*@feedback.css*/', () => css(CSS)).replace('/*@feedback.js*/', () => js(JS)))
  return 'file://' + f
}
const eq = (a, b) => JSON.stringify(a) === JSON.stringify(b)
const json = async (p) => JSON.parse(await p.locator('.fb-json textarea').inputValue())
const verdict = (p, id, v) => p.locator(`section[data-variant="${id}"] input[name="fb-${id}-verdict"][value="${v}"]`).click()
const offered = (p, id) => p.evaluate((i) => [...document.querySelectorAll(`input[name="fb-${i}-works"]`)].map((x) => x.value), id)
const shown = (p, sel) => p.evaluate((s) => document.querySelector(s).getClientRects().length > 0, sel)
const by = (j) => Object.fromEntries(j.variants.map((v) => [v.id, v]))
const OWN = (s) => s.replace('data-round="2"', 'data-round="2" data-verdicts="keep:Keep,revert:Go back"')

// name, what the control removes, and fn(page, errors) -> true when the behaviour is there
const CHECKS = [
  { name: 'the module runs after a page script that ends without a semicolon',
    control: { js: (s) => edit(s, '\n;(function () {', '\n(function () {') },
    fn: async (p, errors) => errors.length === 0 && await p.locator('section[data-variant="m-a"] form.fb').count() === 1 },
  { name: 'aspects: a wrapper’s list wins over the container’s',
    control: { js: (s) => edit(s, "s.closest('[data-aspects]')", 'null') },
    fn: async (p) => eq(await offered(p, 'm-a'), ['Lit', 'Narrow']) && eq(await offered(p, 't-a'), ['Fits', 'Reads']) },
  { name: 'the JSON lists each variant’s offered aspects',
    control: { js: (s) => edit(s, ', offered: aspectsOf(s)', '') },
    fn: async (p) => { const j = by(await json(p)); return eq(j['m-a'].offered, ['Lit', 'Narrow']) && eq(j['t-b'].offered, ['Fits', 'Reads']) } },
  { name: 'rounds: the page opens on the current round, and All rounds shows the earlier one',
    control: { css: (s) => edit(s, '.fb-this-round [data-fb-older] { display: none !important; }', '') },
    fn: async (p) => { const before = [await shown(p, 'section[data-variant="old-a"]'), await shown(p, '#old-table'), await shown(p, 'section[data-variant="t-a"]')]
      await p.locator('.fb-rounds input[value="all"]').click()
      return eq(before, [false, false, true]) && await shown(p, 'section[data-variant="old-a"]') && (await json(p)).variants.length === 6 } },
  { name: 'verdicts: a page’s own verdicts are offered, exported and summarised',
    page: OWN, control: { js: (s) => edit(s, "root.dataset.verdicts || ''", "''") },
    fn: async (p) => { const labels = await p.evaluate(() => [...document.querySelectorAll('section[data-variant="t-a"] input[name="fb-t-a-verdict"]')].map((i) => i.value + ':' + i.nextElementSibling.textContent))
      if (!eq(labels, ['keep:Keep', 'revert:Go back'])) return false
      await verdict(p, 't-a', 'keep'); const j = await json(p)
      return by(j)['t-a'].verdict === 'keep' && eq(j.verdicts, ['keep', 'revert']) && /Keep: Tally A\. Go back: none\./.test(await p.locator('.fb-sum').textContent()) } },
  { name: 'verdicts: a page that names none gets the default three and no verdicts key',
    fn: async (p) => { await verdict(p, 't-a', 'parts'); const j = await json(p)
      return by(j)['t-a'].verdict === 'parts' && !('verdicts' in j) && /Pursue: none\. Keep parts: Tally A\. Drop: none\./.test(await p.locator('.fb-sum').textContent()) } },
  { name: 'pick one: the first verdict moves the moment’s other variants to the last, and leaves a middle verdict',
    control: { js: (s) => edit(s, "h.dataset.pick === 'one'", 'false') },
    fn: async (p) => { await verdict(p, 'm-a', 'pursue'); let j = by(await json(p))
      const first = [j['m-a'].verdict, j['m-b'].verdict, j['m-c'].verdict]
      const radio = await p.evaluate(() => document.querySelector('input[name="fb-m-b-verdict"]:checked')?.value)
      await verdict(p, 'm-c', 'parts'); await verdict(p, 'm-b', 'pursue'); j = by(await json(p))
      return eq(first, ['pursue', 'drop', 'drop']) && radio === 'drop' && eq([j['m-a'].verdict, j['m-b'].verdict, j['m-c'].verdict], ['drop', 'pursue', 'parts']) } },
  { name: 'pick one: a moment without it is left alone',
    fn: async (p) => { await verdict(p, 't-a', 'pursue'); return by(await json(p))['t-b'].verdict === null } },
  { name: 'the draft survives a reload',
    control: { js: (s) => edit(s, 'localStorage.setItem(KEY, JSON.stringify(state))', 'void 0') },
    fn: async (p) => { await verdict(p, 't-b', 'drop'); await p.reload(); return by(await json(p))['t-b'].verdict === 'drop' } },
]

let bad = 0
const say = (ok, line) => { if (!ok) bad++; console.log(`${ok ? 'ok  ' : 'BAD '} ${line}`) }
for (const name of engines) {
  const browser = await pw[name].launch()
  for (const c of CHECKS) for (const run of c.control ? ['module', 'control'] : ['module']) {
    const url = build({ page: c.page, ...(run === 'control' ? c.control : {}) })
    const ctx = await browser.newContext(), p = await ctx.newPage(), errors = []
    p.on('pageerror', (e) => errors.push(String(e)))
    let got = false, note = ''
    try { await p.goto(url); got = await Promise.race([c.fn(p, errors), new Promise((r) => setTimeout(() => r(false), 8000))]) } catch (e) { note = ' (' + String(e.message).split('\n')[0].slice(0, 80) + ')' }
    await ctx.close()
    const want = run === 'module'
    say(got === want, `${name.padEnd(8)} ${run === 'module' ? 'holds        ' : 'control fails'}  ${c.name}${got === want ? '' : note}`)
  }
  await browser.close()
}
// The inliner: run twice, one fenced copy of each file, and the inlined JS is the asset.
{ const f = path.join(tmp, 'inline.html'); writeFileSync(f, SRC)
  const inline = path.join(here, 'inline.mjs')
  execFileSync('node', [inline, f], { stdio: 'ignore' }); execFileSync('node', [inline, f], { stdio: 'ignore' })
  const html = readFileSync(f, 'utf8')
  say((html.match(/@begin feedback\.js/g) || []).length === 1 && (html.match(/@begin feedback\.css/g) || []).length === 1 && html.includes(`/*@begin feedback.js*/\n${JS.trim()}\n/*@end feedback.js*/`),
    'inline.mjs, run twice, leaves one fenced copy of each file, equal to the asset (no control)') }
rmSync(tmp, { recursive: true, force: true })
console.log(bad ? `${bad} unexpected` : 'ui-explore-variants check passed')
process.exit(bad ? 1 : 0)
