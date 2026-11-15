// Measures a page with scripts/observe.js and scores it against references/archetypes.json.
//   node observe.mjs <url or file.html> [--out observed.json] [--json] [--wait 1500] [--single]
// Three loads: 1440 × 900 preferring light (all DOM observables, plus pixels from a screenshot), the same preferring
// dark (followsScheme), and 390 × 844 (bodyRatio). --single does the first only.
// Needs Playwright, which the skill does not ship: it is loaded from the folder the command runs in, then from this
// folder. Exit 0 measured, 1 the page failed to load or measure, 2 could not run (prints "cannot observe: <reason>").
import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join, resolve, sep } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { rank, loadArchetypes, scoreReport } from './archetypes.mjs'
import { position } from './dimensions.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
const argv = process.argv.slice(2), flag = (k) => { const i = argv.indexOf(`--${k}`); return i < 0 ? undefined : argv[i + 1] }
const target = argv.find((a, i) => !a.startsWith('--') && !['--out', '--wait'].includes(argv[i - 1]))
const cannot = (why) => { console.error(`cannot observe: ${why}`); process.exit(2) }
if (!target) cannot('give a URL or an HTML file')
const url = /^[a-z]+:\/\//i.test(target) ? target : existsSync(target) ? pathToFileURL(resolve(target)).href : cannot(`${target} is neither a URL nor a file`)
let chromium
for (const folder of [process.cwd(), HERE]) { try { ({ chromium } = createRequire(folder + sep)('playwright')); break } catch (e) { if (e.code !== 'MODULE_NOT_FOUND') cannot(`playwright failed to load from ${folder}: ${e.message}`) } }
if (!chromium) cannot(`playwright does not resolve from ${process.cwd()} or ${HERE}; run this from a project that has it installed, or evaluate scripts/observe.js in the page yourself`)

const src = readFileSync(join(HERE, 'observe.js'), 'utf8'), wait = Number(flag('wait') ?? 1500)
let browser
try { browser = await chromium.launch() } catch (e) { cannot(`the browser did not start: ${String(e.message).split('\n')[0]}`) }
const load = async (opts) => {
  const ctx = await browser.newContext(opts), page = await ctx.newPage()
  await page.goto(url, { waitUntil: 'load', timeout: 45000 }); await page.waitForTimeout(wait); await page.evaluate(src)
  return { ctx, page }
}
let out
try {
  const { ctx, page } = await load({ viewport: { width: 1440, height: 900 }, colorScheme: 'light' })
  out = await page.evaluate('uiGeometryObserve()')
  const o = out.observables, png = await page.screenshot({ type: 'png' }), jpeg = await page.screenshot({ type: 'jpeg', quality: 80 })
  const blank = await ctx.newPage(); await blank.goto('about:blank'); await blank.evaluate(src)
  const px = await blank.evaluate(`uiGeometryObserve.pixelStats(${JSON.stringify(png.toString('base64'))})`)
  Object.assign(o, { bgShare: px.bgShare, edgeDensity: px.edgeDensity, colourCount: px.colourCount, colourfulness: px.colourfulness, mirrorLR: px.mirrorLR, balanceLR: px.balanceLR, jpegKb: Math.round(jpeg.length / 102.4) / 10, followsScheme: null, bodyRatio: null })
  const light = await page.evaluate('uiGeometryObserve.quick()'); await ctx.close()
  if (!argv.includes('--single')) {
    const dark = await load({ viewport: { width: 1440, height: 900 }, colorScheme: 'dark' }); const dq = await dark.page.evaluate('uiGeometryObserve.quick()'); await dark.ctx.close()
    o.followsScheme = light.pageTone != null && dq.pageTone != null ? +(light.pageTone - dq.pageTone >= 40) : null
    const phone = await load({ viewport: { width: 390, height: 844 }, colorScheme: 'light', isMobile: true, hasTouch: true }); const pq = await phone.page.evaluate('uiGeometryObserve.quick()'); await phone.ctx.close()
    o.bodyRatio = light.body && pq.body ? Math.round((pq.body / light.body) * 100) / 100 : null
  }
  out.notMeasured = Object.keys(o).filter((k) => o[k] == null)
  out.source = url
} catch (e) { console.error(`could not measure ${url}: ${String(e.message).split('\n')[0]}`); await browser.close(); process.exit(1) }
await browser.close()

const A = loadArchetypes()
try { out.position = position(out.observables).scores.map((s) => ({ ...s, score: Math.round(s.score * 100) / 100 })) } catch (e) { out.position = null; out.positionNote = e.message }
out.ranking = rank(out.observables, A).map((r) => ({ name: r.name, family: r.family, distance: Math.round(r.distance * 1000) / 1000, observables: r.count, outside: r.outside }))
if (flag('out')) writeFileSync(flag('out'), JSON.stringify(out, null, 1))
console.log(argv.includes('--json') ? JSON.stringify(out, null, 1) : scoreReport(out.observables, A, { source: url }))
