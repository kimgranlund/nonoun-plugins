// node --test scripts/
import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, writeFileSync, mkdirSync, readFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { loadSpec, merge, pack, parseAreas, expand } from './lib.mjs'
import { applyMins } from './pack.mjs'
import { render } from './scaffold.mjs'

const one = (...refs) => merge(refs.map(loadSpec))
const close = (spec, p) => {
  const { width: W, height: H } = spec.canvas, { margin: M, gutter: G } = spec.chrome
  assert.equal(p.columns.reduce((a, b) => a + b, 0) + (p.columns.length - 1) * G + 2 * M, W)
  assert.equal(p.rows.reduce((a, b) => a + b, 0) + (p.rows.length - 1) * G + 2 * M, H)
}

test('each source stands alone: its groups and specimens (geometry 10 and 28, the others 8 and 24), tracks close on the canvas', () => {
  for (const [id, groups, specimens] of [['ui-geometry', 10, 28], ['ui-colors', 8, 24], ['ui-materials', 8, 24]]) {
    const s = one(id)
    assert.equal(s.groups.length, groups, id)
    assert.equal(s.groups.flatMap((g) => g.specimens).length, specimens, id)
    const p = pack(s); close(s, p)
    for (const r of Object.values(p.rects)) assert.ok(Number.isInteger(r.w) && Number.isInteger(r.h) && r.w > 0 && r.h > 0)
  }
})

test('geometry owns lengths and colours owns colours, in any order', () => {
  for (const order of [['ui-geometry', 'ui-colors', 'ui-materials'], ['ui-colors', 'ui-materials', 'ui-geometry']]) {
    const s = merge(order.map(loadSpec), { content: 'ui-geometry' })
    assert.equal(s.chrome.margin, 36); assert.equal(s.chrome.pad, 20)
    assert.equal(s.chrome.colors.bg, 'var(--colors-bg)'); assert.equal(s.chrome.colors.tile, 'var(--colors-bg-subtle)')
    assert.deepEqual(s.axes.map((a) => a.name).sort(), ['anatomy', 'grid', 'material', 'theme'])
    assert.equal(s.axes.find((a) => a.name === 'theme').attr, 'class')
    assert.equal(s.groups[0].id, 'actions')
  }
})

test('the first source with groups is the content unless one is named', () => {
  assert.equal(one('ui-colors', 'ui-geometry').content, 'ui-colors')
  assert.equal(merge(['ui-colors', 'ui-geometry'].map(loadSpec), { content: 'ui-geometry' }).groups[0].id, 'actions')
  assert.throws(() => merge([{ id: 'x' }].map(loadSpec)), /no content source/)
})

test('a page theme axis exists by default', () => {
  const s = one('ui-geometry')
  assert.deepEqual(s.axes[0], { name: 'theme', attr: 'data-theme', values: ['light', 'dark'], invariant: true })
})

test('minimums grow their tracks, the rest is shared evenly', () => {
  const s = one('ui-geometry')
  applyMins(s, { actions: [500, 600] })
  const p = pack(s); close(s, p)
  assert.ok(p.rects.actions.w >= 500 && p.rects.actions.h >= 600)
  assert.equal(new Set(p.columns.slice(1)).size, 1)
})

test('a spanning minimum spreads over its tracks', () => {
  const s = one('ui-colors')
  applyMins(s, { scales: [0, 900] })
  const p = pack(s); close(s, p)
  assert.ok(p.rects.scales.h >= 900)
})

test('negative control: minimums that do not fit fail and never shrink', () => {
  const s = one('ui-geometry')
  applyMins(s, { actions: [700, 0], choices: [700, 0] })
  assert.throws(() => pack(s), (e) => e.code === 'NOFIT' && /width: the minimums need \d+px more/.test(e.message) && /never scaled down/.test(e.message))
  const t = one('ui-geometry'); applyMins(t, { actions: [0, 1600] })
  assert.throws(() => pack(t), /height/)
})

test('areas must be rectangles and name every group', () => {
  const g = [{ id: 'a' }, { id: 'b' }]
  assert.throws(() => parseAreas(['a b', 'b a'], g), /not a rectangle/)
  assert.throws(() => parseAreas(['a a'], g), /b has no cell/)
  assert.throws(() => parseAreas(['a b c'], g), /c is not a group/)
  assert.throws(() => parseAreas(['a b', 'a'], g), /same number/)
  assert.equal(parseAreas(['a b', 'a .'], g).R, 2)
})

test('render: every group and specimen, filled slots, missing tokens named', () => {
  const dir = mkdtempSync(join(tmpdir(), 'bento-'))
  mkdirSync(join(dir, 'sp'))
  writeFileSync(join(dir, 'sp', 'button.html'), '<span data-part="button">Save</span>')
  const s = one('ui-geometry', 'ui-materials')
  const html = render(s, pack(s), { specimens: join(dir, 'sp') })
  for (const g of s.groups) { assert.ok(html.includes(`data-group="${g.id}"`)); for (const sp of g.specimens) assert.ok(html.includes(`data-specimen="${sp.id}"`)) }
  assert.equal(html.match(/data-slot data-placeholder/g).length, 27)
  assert.ok(html.includes('data-part="button">Save'))
  assert.ok(html.includes('id="bento-spec"') && html.includes('window.uiBentoCheck'))
  assert.ok(/^<title>Material showcase<\/title>/.test(html))
  const c = loadSpec('ui-colors'); c.tokens.css = [join(dir, 'nope.css')]
  assert.throws(() => render(merge([c]), pack(merge([c]))), /nope\.css is missing\. Produce it first: \[ -f \S+colors-request\.json \] \|\| echo '\{\}' > [^{}]+ ; node [^{}]+$/)
})

test('duplicate ids are refused', () => {
  assert.throws(() => merge([{ id: 'x', groups: [{ id: 'a', label: 'A', specimens: [{ id: 's', label: 'S' }] }, { id: 'b', label: 'B', specimens: [{ id: 's', label: 'S' }] }] }].map(loadSpec)), /duplicate specimen s/)
})

test('tight spans: falls back to the exact greedy and closes on the canvas', () => {
  // ARIA 24 content on the geometry lengths (margin 36), on the 1280 × 1280 canvas its eight groups were measured for.
  const s = merge(['ui-geometry', 'ui-materials', { id: 'big', canvas: { height: 1280 } }].map(loadSpec), { content: 'ui-materials' })
  s.areas = ['d d d d d c', 's s s n n n', 'i i i i a a', 'v v v v f f'].map((r) => r.replace(/\b(\w)\b/g, (m) => ({ d: 'disclosure', c: 'choices', s: 'selection', n: 'navigation', i: 'input', a: 'actions', v: 'values', f: 'feedback' })[m]))
  applyMins(s, { choices: [241, 300], disclosure: [955, 309], input: [802, 298], actions: [394, 266], navigation: [597, 264], selection: [599, 208], feedback: [394, 284], values: [802, 194] })
  const p = pack(s); close(s, p)
  for (const [id, [w, h]] of Object.entries({ choices: [241, 300], disclosure: [955, 309], input: [802, 298], actions: [394, 266], navigation: [597, 264], selection: [599, 208] }))
    assert.ok(p.rects[id].w >= w && p.rects[id].h >= h, id)
  applyMins(s, { choices: [242, 0] })
  assert.throws(() => pack(s), /1px more/)
})

test('a layout source sets the canvas, the areas and the minimums', () => {
  const s = one('ui-geometry', 'ui-colors', 'ui-materials', 'geometry-28-1280')
  assert.equal(s.canvas.height, 1600)
  assert.equal(s.areas[0].split(' ')[0], 'disclosure')
  assert.equal(s.areas.at(-1).split(' ')[0], 'type')
  assert.deepEqual(s.groups.find((g) => g.id === 'input').min, [802, 266])
  const p = pack(s); close(s, p)
  assert.ok(p.rects.disclosure.h >= 311 && p.rects.choices.w >= 241)
  for (const g of s.groups) assert.ok(p.rects[g.id].w >= g.min[0] && p.rects[g.id].h >= g.min[1], `${g.id} has its minimum`)
  assert.equal(one('ui-geometry').groups.find((g) => g.id === 'input').min, undefined)
})

test('the two tested layouts: each fits its own content, shares the ARIA 24 minimums, and refuses the other content', () => {
  const lay = (id) => JSON.parse(read(`layouts/${id}.json`))
  const a = lay('aria-24-1280'), g = lay('geometry-28-1280')
  for (const [id, min] of Object.entries(a.mins)) assert.deepEqual(g.mins[id], min, `${id}: one measurement, two layouts`)
  assert.deepEqual(Object.keys(g.mins).filter((id) => !a.mins[id]), ['type', 'space'])
  // The canvas is no taller than the rows need plus one row of slack, and never shorter: room comes from height, not from scale.
  const rows = (l) => l.areas.map((r) => Math.max(...[...new Set(r.split(' '))].map((id) => l.mins[id][1])))
  const need = (l) => rows(l).reduce((x, y) => x + y, 0) + (l.areas.length - 1) * 12 + 2 * 36
  assert.equal(need(a), 1161 + 72); assert.equal(need(g), 1509 + 72)
  assert.ok(g.canvas.height >= need(g) && a.canvas.height >= need(a))
  const s = merge(['ui-geometry', 'ui-materials', 'aria-24-1280'].map(loadSpec), { content: 'ui-materials' })
  assert.equal(s.canvas.height, 1280); close(s, pack(s))
  assert.throws(() => pack(one('ui-geometry', 'aria-24-1280')), /group type has no cell/, 'negative control: the ARIA 24 layout has no cell for Type')
  assert.throws(() => one('ui-materials', 'geometry-28-1280'), /mins name type, space, not groups of ui-materials/)
})

test('tiles are grid paper by default, ruled from the content edge; texture none turns it off', () => {
  const s = one('ui-geometry')
  const html = render(s, pack(s))
  assert.match(html, /background-size: 32px 32px, 32px 32px, 8px 8px, 8px 8px/)
  assert.match(html, /background-position: 20px 20px/)
  const t = one('ui-geometry', { id: 'plain', chrome: { texture: 'none' } })
  assert.doesNotMatch(render(t, pack(t)), /Grid paper/)
})

test('grid paper is fainter in dark themes, whichever attribute the theme axis sets', () => {
  const a = one('ui-geometry'), ha = render(a, pack(a))
  assert.match(ha, /:root\[data-theme="dark"\] \{ --b-grid-minor: 8%; --b-grid-strong: 20% \}/)
  assert.match(ha, /:root \{ --b-grid-minor: 14%; --b-grid-strong: 32% \}/)
  const b = one('ui-geometry', 'ui-colors'); b.tokens.css = []
  const hb = render(b, pack(b))
  assert.match(hb, /:root\.dark, :root\.dim \{ --b-grid-minor: 8%/)
  assert.match(hb, /:root\.light \{ --b-grid-minor: 14%/)
})

test('the grid has its own switch, and texture none removes it', () => {
  const s = one('ui-geometry')
  assert.deepEqual(s.axes.find((a) => a.name === 'grid'), { name: 'grid', label: 'grid', attr: 'data-bento-grid', values: ['on', 'off'], invariant: true })
  assert.match(render(s, pack(s)), /data-bento-grid="off"\] \.b-tile \{ background-image: none \}/)
  assert.equal(one('ui-geometry', { id: 'plain', chrome: { texture: 'none' } }).axes.some((a) => a.name === 'grid'), false)
})

// ---- closed sets (contract) ----
import { readdirSync, existsSync as exists } from 'node:fs'
import { SETS, SKILL, SKILLS, validateSource } from './lib.mjs'
import { termsReport, loadTerms, emitted } from './terms.mjs'
import { runFixtures, findChrome } from './check-fixtures.mjs'
const read = (p) => readFileSync(join(SKILL, p), 'utf8')

test('negative controls: values and keys outside the closed sets fail loudly', () => {
  const base = { id: 'x', groups: [{ id: 'g', label: 'G', specimens: [{ id: 's', label: 'S' }] }] }
  const bad = [
    [{ owns: ['colours'] }, /owns "colours" is not one of/],
    [{ chrome: { texture: 'grids' } }, /texture "grids" is not one of/],
    [{ chrome: { padding: 4 } }, /chrome: unknown key padding/],
    [{ chrome: { colors: { background: 'red' } } }, /chrome.colors: unknown key background/],
    [{ colour: 1 }, /unknown key colour/],
    [{ axes: [{ name: 'm', attr: 'data-m', values: ['a'], target: 'body' }] }, /target "body" is not one of/],
    [{ axes: [{ name: 'm', attr: 'data-m', values: ['a'], aliases: { old: 'b' } }] }, /alias points to "b"/],
    [{ axes: [{ name: 'm', attr: 'data-m', values: ['a'], captions: { b: 'B' } }] }, /caption for "b"/],
    [{ axes: [{ name: 'm', attr: 'data-m', values: ['a'], colour: 1 }] }, /axis m: unknown key colour/],
    [{ tokens: { stylesheets: [] } }, /tokens: unknown key stylesheets/],
    [{ groups: [{ id: 'g', label: 'G', layout: 'row', specimens: [] }] }, /layout "row" is not one of/],
    [{ groups: [{ id: 'g', label: 'G', specimens: [{ id: 's', label: 'S', colour: 1 }] }] }, /specimen s: unknown key colour/],
  ]
  for (const [patch, re] of bad) assert.throws(() => loadSpec({ ...base, ...patch }), re, JSON.stringify(patch))
  assert.throws(() => merge(['ui-geometry', { id: 'l', mins: { disclosre: [1, 1] } }].map(loadSpec)), /mins name disclosre, not groups of ui-geometry/)
})

test('every shipped source, layout and template loads against the closed sets', () => {
  for (const dir of ['sources', 'layouts', 'sources/templates'])
    for (const f of readdirSync(join(SKILL, dir)).filter((f) => f.endsWith('.json'))) assert.ok(loadSpec(join(SKILL, dir, f)), f)
})

test('contract.md names every closed set value declared in lib.mjs', () => {
  const doc = read('references/contract.md')
  const missing = Object.values(SETS).flat().filter((v) => !doc.includes(v))
  assert.deepEqual(missing, [])
})

// ---- cross-skill agreement (the sources are a registry of the sibling skills' briefs) ----
const brief = (skill) => join(SKILLS, skill, 'references', 'showcase.md')

test('the ui-geometry source canvas is the one its brief names for this renderer, and tall enough', (t) => {
  if (!exists(brief('ui-geometry'))) return t.skip('ui-geometry is not installed')
  const text = readFileSync(brief('ui-geometry'), 'utf8')
  const named = text.match(/ui-showcase-bento uses (\d+) × (\d+)/)
  const need = text.match(/need about ([\d,]+)px of height/)
  assert.ok(named && need, 'the brief names the bento canvas and the height its regions need')
  const c = loadSpec('ui-geometry').canvas
  assert.deepEqual(c, { width: +named[1], height: +named[2] })
  assert.ok(c.height >= +need[1].replace(',', ''), `canvas ${c.height} is shorter than the ${need[1]}px the brief needs`)
})

function depictionRows(file) {
  const lines = readFileSync(file, 'utf8').split('\n')
  const i = lines.findIndex((l) => /^\| (Pattern|Specimen) \| (Required )?[Dd]epiction/.test(l))
  const rows = []
  for (const l of lines.slice(i + 2)) { if (!l.startsWith('|')) break; rows.push(l.split('|')[1].trim()) }
  return rows
}
/** Every depiction table of a brief, in order: the patterns, then any table of further specimens. */
function allDepictionRows(file) {
  const lines = readFileSync(file, 'utf8').split('\n'), rows = []
  lines.forEach((l, i) => {
    if (!/^\| (Pattern|Specimen) \| (Required )?[Dd]epiction/.test(l)) return
    for (const r of lines.slice(i + 2)) { if (!r.startsWith('|')) break; rows.push(r.split('|')[1].trim()) }
  })
  return rows
}
for (const [skill, cat, every] of [['ui-geometry', 'aria-24'], ['ui-geometry', 'geometry-28', true], ['ui-colors', 'colour-24']])
  test(`${skill}'s required depictions and the ${cat} catalogue match both ways`, (t) => {
    if (!exists(brief(skill))) return t.skip(`${skill} is not installed`)
    const rows = (every ? allDepictionRows : depictionRows)(brief(skill))
    assert.ok(rows.length >= 20, 'found the depiction table')
    const specimens = JSON.parse(read(`catalogues/${cat}.json`)).groups.flatMap((g) => g.specimens)
    const name = (s) => s.briefRow ?? s.label
    assert.deepEqual(rows.filter((r) => !specimens.some((s) => name(s) === r)), [], 'brief rows with no specimen')
    assert.deepEqual(specimens.filter((s) => !rows.includes(name(s))).map((s) => s.id), [], 'specimens with no brief row')
  })

test('geometry-28 is aria-24, group for group, plus Type and Space, and the brief names every group', (t) => {
  const groups = (cat) => JSON.parse(read(`catalogues/${cat}.json`)).groups
  const g = groups('geometry-28'), a = groups('aria-24')
  assert.deepEqual(g.slice(0, a.length), a)
  assert.deepEqual(g.slice(a.length).map((x) => [x.id, x.specimens.length]), [['type', 2], ['space', 2]])
  assert.notDeepEqual([...g.slice(0, 7), { ...g[7], label: 'Values' }], a, 'negative control: a relabelled group')
  assert.equal(loadSpec('ui-geometry').catalogue, 'geometry-28')
  if (!exists(brief('ui-geometry'))) return t.skip('ui-geometry is not installed')
  const text = readFileSync(brief('ui-geometry'), 'utf8')
  for (const x of g) assert.match(text, new RegExp(`^\\| ${x.label} \\|`, 'm'), `the brief's grouping table has ${x.label}`)
})

test("the ui-colors source's mode axis lists only modes ui-colors forces with one class", (t) => {
  const file = join(SKILLS, 'ui-colors', 'references', 'terms.json')
  if (!exists(file)) return t.skip('ui-colors is not installed')
  const forced = JSON.parse(readFileSync(file, 'utf8')).concepts.find((c) => c.id === 'mode').names.filter((n) => /^\.[a-z-]+$/.test(n)).map((n) => n.slice(1))
  const outside = (values) => values.filter((v) => !forced.includes(v))
  const axis = loadSpec('ui-colors').axes.find((a) => a.attr === 'class')
  assert.ok(forced.length >= 2, 'ui-colors names its single-class modes')
  assert.deepEqual(outside(axis.values), [])
  assert.deepEqual(outside([...axis.values, 'light-contrast']), ['light-contrast'], 'negative control: a contrast mode takes two classes')
})

/** Scripts a source's commands name under {skills} that are not installed; and whether a colours request is overwritten. */
const missingScripts = (commands) => commands.flatMap((c) => [...c.matchAll(/\{skills\}\/([\w./-]+\.(?:mjs|cjs|js))/g)].map((m) => m[1])).filter((p) => !exists(join(SKILLS, p)))

test('the materials source writes the colours request with a script that exists, and the colours source keeps it', (t) => {
  if (!exists(join(SKILLS, 'ui-materials', 'SKILL.md'))) return t.skip('ui-materials is not installed')
  const raw = (id) => JSON.parse(read(`sources/${id}.json`)).tokens.commands, mat = raw('ui-materials'), col = raw('ui-colors')
  assert.equal(mat[0], 'node {skills}/ui-materials/scripts/request.mjs > {work}/colors-request.json')
  // Every placeholder is expanded, however often a command names it.
  for (const c of [...loadSpec('ui-materials').tokens.commands, ...loadSpec('ui-colors').tokens.commands]) assert.doesNotMatch(c, /\{(skills|bento|spec|work)\}/, c)
  assert.doesNotMatch(expand('{work}/a {work}/b {skills}/c {skills}/d', '.'), /\{(skills|work)\}/)
  assert.match('{work}/a {work}/b'.replace('{work}', 'W'), /\{work\}/, 'negative control: replacing once leaves the second')
  assert.deepEqual(missingScripts([...mat, ...col]), [])
  assert.deepEqual(missingScripts(['node {skills}/ui-materials/scripts/nope.mjs > {work}/x.json']), ['ui-materials/scripts/nope.mjs'], 'negative control: a script that is not there')
  const keeps = (commands) => commands.filter((c) => c.includes('> {work}/colors-request.json')).every((c) => c.startsWith('[ -f {work}/colors-request.json ] || '))
  assert.ok(keeps(col), 'the colours source writes its default request only when none exists')
  assert.equal(keeps(["echo '{}' > {work}/colors-request.json"]), false, 'negative control: a command that overwrites the request')
})

// ---- vocabulary ----
test('terms.json is closed both ways against what the skill emits', () => {
  assert.deepEqual(termsReport().problems, [])
})

test('negative controls: a dropped term and an unemitted term are both reported', () => {
  const terms = loadTerms()
  const c = terms.concepts.find((x) => x.id === 'grid-paper')
  c.names = c.names.filter((n) => n !== 'gridStrengthDark')
  c.names.push('gridDensity')
  const { problems } = termsReport(terms, emitted())
  assert.ok(problems.includes('emitted but not in terms.json: gridStrengthDark'))
  assert.ok(problems.includes('in terms.json but never emitted: gridDensity'))
})

// ---- materials axes ----
test('anatomy has four views with on kept as an alias, and materials caption their settings', () => {
  const s = one('ui-geometry', 'ui-materials')
  const anat = s.axes.find((a) => a.name === 'anatomy')
  assert.deepEqual(anat.values, ['off', 'layer', 'relief', 'face'])
  assert.equal(anat.aliases.on, 'relief')
  const html = render(s, pack(s))
  assert.match(html, /<span class="b-cap" data-cap="material"><\/span>/)
  assert.match(html, /:root\[data-material="glass"\] \[data-cap="material"\]::after \{ content: "Glass: lit · clear · fill · colour · lens off" \}/)
  assert.match(html, /:root\[data-show-anatomy="relief"\] \[data-cap="anatomy"\]::after, :root\[data-show-anatomy="on"\] \[data-cap="anatomy"\]::after/)
  assert.match(html, /\[data-show-anatomy="on"\]\) \[data-relief="raised"\]/)
})

/** The anatomy legend is typed twice: words in the source's captions, colours and line styles in the overlay CSS. */
function legendProblems(captions, css) {
  const out = [], hexOf = new Map(), wordOf = new Map(), captioned = new Set()
  for (const [view, caption] of Object.entries(captions)) for (const [, word, value] of caption.matchAll(/([a-z]+) = ([a-z]+)/g)) {
    captioned.add(`${view}=${value}`)
    const rule = css.match(new RegExp(`\\[data-${view}="${value}"\\] \\{ --anat: (#[0-9a-f]+)([^}]*)\\}`))
    if (!rule) { out.push(`${view}: the caption names ${value}, which the overlay CSS does not colour`); continue }
    if (word === 'solid' || word === 'dashed') { if ((word === 'dashed') !== /outline-style: dashed/.test(rule[2])) out.push(`${view}: ${value} is captioned ${word}, the CSS draws it otherwise`); continue }
    if (hexOf.has(word) && hexOf.get(word) !== rule[1]) out.push(`"${word}" names both ${hexOf.get(word)} and ${rule[1]}`)
    if (wordOf.has(rule[1]) && wordOf.get(rule[1]) !== word) out.push(`${rule[1]} is called both ${wordOf.get(rule[1])} and ${word}`)
    hexOf.set(word, rule[1]); wordOf.set(rule[1], word)
  }
  for (const [, view, value] of css.matchAll(/\[data-(layer|relief|face)="([a-z]+)"\] \{ --anat:/g)) if (!captioned.has(`${view}=${value}`)) out.push(`${view}: the CSS colours ${value}, which no caption names`)
  return out
}

test('the anatomy legend and the overlay CSS agree: every value drawn, one word per colour', () => {
  const captions = loadSpec('ui-materials').axes.find((a) => a.name === 'anatomy').captions
  const css = read('sources/ui-materials.anatomy.css')
  assert.deepEqual(legendProblems(captions, css), [])
  assert.equal(legendProblems(captions, css.replace('[data-relief="ground"] { --anat: #8a8a8a }', '[data-relief="ground"] { --anat: #777777 }')).length, 1, 'negative control: grey drawn in two colours')
  assert.equal(legendProblems({ ...captions, face: captions.face + ' · teal = lamp' }, css).length, 1, 'negative control: a captioned value the CSS does not colour')
  assert.equal(legendProblems({ ...captions, face: captions.face.replace(' · amber = display', '') }, css).length, 1, 'negative control: a coloured value no caption names')
})

// ---- the in-page checker ----
test('checker fixtures: the clean sheet passes every combination, each broken copy fails on its own error', { timeout: 300000 }, (t) => {
  if (!findChrome()) return t.skip('no Chromium found (set BENTO_CHROME)')
  const res = runFixtures()
  assert.deepEqual(res.filter((r) => !r.pass), [])
  assert.equal(res.length, 6)
})

// ---- entry file and statements ----
test('SKILL.md: description and size budgets, every reference routed, contents anchors resolve', () => {
  const md = read('SKILL.md')
  const desc = md.match(/^description: (.*)$/m)[1]
  assert.ok(desc.length <= 1024, `description is ${desc.length} characters`)
  // An unquoted description must stay a plain YAML scalar: ": " or " #" ends it, and a strict host refuses the file.
  assert.doesNotMatch(desc, /: | #/, 'the description holds ": " or " #"')
  assert.match('Generate bento showcases: a fixed canvas', /: | #/, 'negative control: a colon and a space')
  assert.match(desc, /NOT for .*ui-kit-inspector.*component-variants/)
  assert.ok(md.length < 18000)
  for (const f of readdirSync(join(SKILL, 'references'))) assert.ok(md.includes(`references/${f}`), `${f} is routed`)
  for (const [, a] of md.matchAll(/\]\(#([a-z-]+)\)/g)) assert.match(md, new RegExp(`^## ${a}$`, 'im'), `#${a} resolves`)
  for (const [, p] of md.matchAll(/`((?:references|scripts|catalogues|layouts|sources)\/[^`*<]+)`/g)) assert.ok(exists(join(SKILL, p)), `${p} exists`)
})

test('statements: no vague words, and the mode axis is not called a theme in prose', () => {
  const docs = ['SKILL.md', 'references/contract.md', 'references/sources.md', 'references/authoring.md']
  const banned = /\b(should|probably|maybe|several|freely|when one fits|appropriate|as needed|if possible)\b/i
  for (const d of docs) read(d).split('\n').forEach((l, i) => {
    const prose = l.replace(/`[^`]*`/g, '')
    assert.doesNotMatch(prose, banned, `${d}:${i + 1}`)
    assert.doesNotMatch(prose, /\btheme\b/i, `${d}:${i + 1} says theme outside code`)
  })
})

test('paint rules stay with ui-materials: the bento docs route to it instead of restating them', () => {
  const owned = ['Flat has no direction', 'inset 0 -1px 0', '--shade-k', '--lit-k', 'Every shadow token is a valid list', 'faces are step 1']
  const leaks = (text) => owned.filter((o) => text.includes(o))
  const docs = ['SKILL.md', 'references/authoring.md', 'references/sources.md', 'references/contract.md', 'sources/ui-colors.json'].map(read).join('\n')
  assert.deepEqual(leaks(docs), [], 'these belong in ui-materials')
  assert.deepEqual(leaks('Flat raised and overlay faces are step 1, so a flat dialog separates from its tile.'), ['faces are step 1'], 'negative control')
  assert.match(read('references/authoring.md'), /belongs to ui-materials/)
})

test('trigger cases cover the description: four that load it, and a near miss for every sibling it names', () => {
  const ev = JSON.parse(read('evals/triggers.json'))
  assert.ok(ev.should_trigger.length >= 4)
  const desc = read('SKILL.md').match(/^description: (.*)$/m)[1]
  const named = [...desc.matchAll(/\((ui-[a-z-]+|component-variants|wireframe-review|brand-system-sheets)\)/g)].map((m) => m[1])
  for (const n of named) assert.ok(ev.should_not_trigger.some((c) => c.owner === n), `a near miss for ${n}`)
})

// Host-project names, stored reversed so this file does not contain them.
const HOST_NAMES = ['omissam', 'nosiam'].map((w) => [...w].reverse().join(''))
const hostNames = (files) => files.flatMap(([path, text]) => HOST_NAMES.filter((w) => text.toLowerCase().includes(w)).map(() => `${path}: names a host project`))
const walkSkill = (rel = '') => readdirSync(join(SKILL, rel), { withFileTypes: true }).flatMap((e) =>
  e.name.startsWith('.') ? [] : e.isDirectory() ? walkSkill(join(rel, e.name)) : [[join(rel, e.name), readFileSync(join(SKILL, rel, e.name), 'utf8')]])

test('no file names a host project, and a planted name is caught', () => {
  assert.deepEqual(hostNames(walkSkill()), [])
  assert.equal(hostNames([['references/x.md', `Built for ${HOST_NAMES[0].toUpperCase()} UI.`]]).length, 1)
})
