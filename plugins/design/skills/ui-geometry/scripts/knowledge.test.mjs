// The skill's knowledge layer: ids, presets, labels, roles, terms, generated blocks and named checks.
// Every check has a negative control: a mutated input that must fail.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, readdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { PRESETS, derive, containers, validatePreset, floatingWidth, floatingHeight, TIERS } from './derive.mjs'
import { ROLES, fit } from './fit.mjs'
import { checkTerms, checkProse, loadTerms, loadDocs, emitted } from './terms.mjs'
import { sync } from './docs.mjs'

const HERE = dirname(fileURLToPath(import.meta.url)), ROOT = join(HERE, '..')
const read = (p) => readFileSync(join(ROOT, p), 'utf8')
const dupes = (xs) => xs.filter((x, i) => xs.indexOf(x) !== i)

test('every derive row has a unique id at every density, and a duplicate is caught', () => {
  for (const density of Object.keys(PRESETS.standard.inset)) assert.deepEqual(dupes(derive({ density }).map((r) => r.id)), [], density)
  const rows = derive()
  assert.deepEqual(dupes([...rows, rows[5]].map((r) => r.id)), [rows[5].id], 'negative control')
})

test('renamed symbols keep their earlier spelling as an alias', () => {
  const rows = derive()
  assert.equal(rows.find((r) => r.alias === 'T pointer')?.symbol, 'T_hit pointer')
  assert.equal(rows.find((r) => r.alias === 'minimum I for h to meet T (touch)')?.px, 12)
})

test('presets: known keys pass, a typo is refused with a suggestion, and the fitter writes valid presets', () => {
  assert.doesNotThrow(() => validatePreset({ name: 'x', unit: { a: 0.5, b: -3 }, frameDepth: 1, dials: {} }))
  assert.throws(() => validatePreset({ framDepth: 1 }), /unknown key "framDepth" \(did you mean "frameDepth"\?\)/)
  const lengths = [{ id: 'b.height', component: 'b', role: 'height', px: 32 }, { id: 'b.label-inset', component: 'b', role: 'label-inset', px: 12 }, { id: 'b.radius', component: 'b', role: 'radius', px: 12 }]
  assert.doesNotThrow(() => validatePreset(fit({ n: 14, lengths }).preset))
})

test('printed expressions match their values: item rows read h − 2d_c, menu text T − d_c', () => {
  const rows = derive()
  assert.match(rows.find((r) => r.id === 'collections.rows.control-in-a-table-cell').expr, /^item h − 2d_c/)
  const L = containers(), at = (name, part) => L.find((r) => r.container.startsWith(name))[part]
  assert.ok(at('Listbox', 'pad').some((x) => x.e.startsWith('rows inline: T − d_c') && x.q === 2.25))
  assert.ok(at('List, inset', 'pad').some((x) => x.e.startsWith('items inline: T − d_c') && x.q === 2.25))
  assert.ok(at('Table', 'height').some((x) => x.e === 'control in a cell: item h − 2d_c' && x.q === 6.5))
  for (const r of L) for (const part of ['pad', 'gap', 'radius', 'height']) for (const x of r[part]) assert.doesNotMatch(x.e, /text at T = 2I$|item S \+ 2m_c$/, `${r.container}: ${x.e}`)
})

test('floating width: content, capped by its maximum and by the viewport less a margin each side', () => {
  assert.equal(floatingWidth({ content: 50, max: 80, W: 320, margin: 4 }), 50)
  assert.equal(floatingWidth({ content: 100, max: 80, W: 320, margin: 4 }), 80)
  assert.equal(floatingWidth({ content: 100, max: 80, W: 60, margin: 4 }), 52, 'negative control: a narrow viewport caps it')
  assert.equal(floatingWidth({ content: 30, max: 80, W: 320, margin: 4, anchor: 48 }), 48, 'a popup is at least as wide as the control that opens it')
  assert.equal(floatingWidth({ content: 30, max: 80, W: 320, margin: 4 }), 30, 'negative control: with no anchor the content sets it')
  assert.equal(floatingWidth({ content: 30, max: 80, W: 40, margin: 4, anchor: 48 }), 32, 'the viewport still caps an anchored popup')
  assert.equal(floatingHeight({ content: 900, H: 600, margin: 16 }), 568, 'a frame is no taller than the viewport less its margins')
  assert.equal(floatingHeight({ content: 300, H: 600, margin: 16 }), 300, 'negative control: short content keeps its height')
  assert.equal(derive().find((r) => r.id === 'containers.width.collapse').q, 2 * PRESETS.standard.widths.panel)
})

/** Roles collect.js records, read from its put() calls. */
const collected = () => new Set([...read('scripts/collect.js').matchAll(/put\(s\.id, '([a-z-]+)'/g)].map((m) => m[1]))
const roleClosure = (roles, got) => [
  ...[...got].filter((r) => !(r in roles)).map((r) => `collect.js records "${r}", which ROLES does not declare`),
  ...Object.entries(roles).filter(([k, r]) => r.collect !== false && !got.has(k)).map(([k]) => `ROLES declares "${k}" as collected, but collect.js never records it`),
]

test('roles are declared once in ROLES and match collect.js both ways', () => {
  assert.deepEqual(roleClosure(ROLES, collected()), [])
  assert.equal(roleClosure({ ...ROLES, ghost: { tier: 'controls' } }, collected()).length, 1, 'negative control: a declared role nobody collects')
  for (const k of ['host-depth', 'segment', 'cell-control', 'segment-radius']) assert.match(ROLES[k].symbol + ROLES[k].compare, /d_c/, k)
})

test('terms.json is in step with what the scripts emit, and each kind of drift is caught', () => {
  const T = loadTerms(), E = emitted()
  assert.deepEqual(checkTerms(T, E), [])
  const mut = (f) => { const t = structuredClone(T); f(t); return checkTerms(t, E) }
  assert.ok(mut((t) => t.concepts[1].names.push('symbol:h')).some((x) => /belongs to both/.test(x)), 'one name, two concepts')
  assert.ok(mut((t) => t.concepts[0].names.push('symbol:zz')).some((x) => /not emitted/.test(x)), 'a name nothing emits')
  assert.ok(mut((t) => { t.concepts = t.concepts.filter((c) => c.id !== 'slot') }).some((x) => /symbol "S"/.test(x)), 'a printed symbol with no concept')
})

test('no doc uses a phrase terms.json bans outright, and a planted one is caught', () => {
  const T = loadTerms()
  assert.deepEqual(checkProse(T, loadDocs()), [])
  assert.equal(checkProse(T, [['x.md', 'The budget B is redistributed over five layers.']]).length, 1, 'negative control: the bare letter')
  assert.equal(checkProse(T, [['x.md', '| card depths | frame ladder | 0…9 |']]).length, 1, 'negative control: the retired phrase')
  assert.deepEqual(checkProse(T, [['x.md', 'The budget B_α is redistributed.']]), [], 'the subscripted symbol passes')
})

/** Symbols a tier's Owns cell uses that another tier owns and its Reads cell does not name. rows: [tier, owns, reads]. */
const SYMBOL = /(?<![A-Za-z_])([A-Za-zκ](?:_[a-z]+)?)(?![A-Za-z_])/g
const unread = (rows, terms) => {
  const tierOf = new Map(terms.concepts.flatMap((c) => (c.names ?? []).filter((n) => n.startsWith('symbol:')).map((n) => [n.slice(7), c.layer])))
  return rows.flatMap(([tier, owns, reads]) => {
    const named = new Set([...reads.matchAll(SYMBOL)].map((m) => m[1]))
    return [...new Set([...owns.matchAll(SYMBOL)].map((m) => m[1]))]
      .filter((s) => TIERS.includes(tierOf.get(s)) && tierOf.get(s) !== tier && !named.has(s))
      .map((s) => `${tier} uses ${s} (${tierOf.get(s)}) but does not list it under Reads`)
  })
}

test("a tier's Reads column names every symbol it takes from another tier, and a missing one is caught", () => {
  const T = loadTerms()
  const skill = [...read('SKILL.md').matchAll(/^\| \d (\w+) \| [^|]* \| ([^|]*) \| ([^|]*) \|/gm)].map((m) => [m[1], m[2], m[3]])
  const eq = [...read('references/equations.md').split('## 18.')[1].split('##')[0].matchAll(/^\| (controls|collections|containers|layout) \| ([^|]*) \| ([^|]*) \|/gm)].map((m) => [m[1], m[2], m[3]])
  assert.equal(skill.length, TIERS.length); assert.equal(eq.length, TIERS.length)
  assert.deepEqual(unread(skill, T), []); assert.deepEqual(unread(eq, T), [])
  assert.deepEqual(unread([['layout', 'M = 4I, G = M/2', 'minimum card width']], T), ['layout uses I (controls) but does not list it under Reads'], 'negative control')
})

/** Why a host would refuse a description: too long, or not a plain YAML scalar (it is written unquoted). */
const descriptionProblems = (d) => [
  d.length > 1024 ? `${d.length} characters (limit 1,024)` : null,
  Buffer.byteLength(d) > 1024 ? `${Buffer.byteLength(d)} bytes (limit 1,024)` : null,
  /: | #/.test(d) ? 'holds ": " or " #", which ends a plain YAML scalar' : null,
  /^[[{&*!|>'"%@`]|^[-?] /.test(d) ? 'starts with a YAML indicator' : null,
].filter(Boolean)

test('SKILL.md fits its hosts: the description is a plain YAML scalar of at most 1,024 characters, the file under 18,000', () => {
  const md = read('SKILL.md'), desc = md.match(/^description: (.*)$/m)[1]
  assert.deepEqual(descriptionProblems(desc), [])
  assert.ok(md.length < 18000, `SKILL.md is ${md.length} characters`)
  assert.equal(descriptionProblems('x'.repeat(1025)).length, 2, 'negative control: too long, in characters and in bytes')
  assert.equal(descriptionProblems('in four tiers (controls, layout): insets, slots').length, 1, 'negative control: a colon and a space')
})

test('generated tables in references/ match their sources, and drift is caught', () => {
  assert.deepEqual(sync({ check: true }), [])
  ROLES.zz = { tier: 'controls', symbol: 'z', says: 'z', compare: 'z' }
  try { assert.equal(sync({ check: true }).length, 1, 'negative control: a role missing from fit.md') } finally { delete ROLES.zz }
})

/** Quoted test names after "Checked:" in SKILL.md and equations.md that no test starts with. */
const unnamed = (docs, names) => docs.flatMap((d) => [...d.matchAll(/Checked[^"\n]*?((?:"[^"]+"(?:,? (?:and )?)?)+)/g)].flatMap((m) => [...m[1].matchAll(/"([^"]+)"/g)].map((x) => x[1])))
  .filter((q) => !names.some((n) => n.startsWith(q)))

test('every check SKILL.md and equations.md name exists as a test', () => {
  const names = readdirSync(HERE).filter((f) => f.endsWith('.test.mjs')).flatMap((f) => [...readFileSync(join(HERE, f), 'utf8').matchAll(/^test\((['"])(.+?)\1/gm)].map((m) => m[2]))
  const docs = [read('SKILL.md'), read('references/equations.md')]
  assert.deepEqual(unnamed(docs, names), [])
  assert.deepEqual(unnamed(['Checked: "a test nobody wrote".'], names), ['a test nobody wrote'], 'negative control')
})

test('the tiers are copied into SKILL.md and equations.md as TIERS declares them', () => {
  const skill = [...read('SKILL.md').matchAll(/^\| \d (\w+) \|/gm)].map((m) => m[1])
  const eq = [...read('references/equations.md').split('## 18.')[1].split('##')[0].matchAll(/^\| (controls|collections|containers|layout) \|/gm)].map((m) => m[1])
  assert.deepEqual(skill, TIERS); assert.deepEqual(eq, TIERS)
  assert.notDeepEqual([...TIERS].reverse(), TIERS, 'negative control: order matters')
})

// Host-project names, stored reversed so this file does not contain them.
const HOST_NAMES = ['omissam', 'nosiam'].map((w) => [...w].reverse().join(''))
const hostNames = (files) => files.flatMap(([path, text]) => HOST_NAMES.filter((w) => text.toLowerCase().includes(w)).map((w) => `${path}: names a host project`))
const walk = (dir, rel = '') => readdirSync(join(dir, rel), { withFileTypes: true }).flatMap((e) =>
  e.name.startsWith('.') ? [] : e.isDirectory() ? walk(dir, join(rel, e.name)) : [[join(rel, e.name), readFileSync(join(dir, rel, e.name), 'utf8')]])

test('no file names a host project, and a planted name is caught', () => {
  assert.deepEqual(hostNames(walk(ROOT)), [])
  assert.equal(hostNames([['references/x.md', `Built for ${HOST_NAMES[0].toUpperCase()} UI.`]]).length, 1)
})
