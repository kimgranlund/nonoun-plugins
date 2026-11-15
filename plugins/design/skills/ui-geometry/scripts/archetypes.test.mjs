// node --test archetypes.test.mjs
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { PRESETS, derive, checkIdentities } from './derive.mjs'
import { loadArchetypes, archetype, applyArchetype, observe, rank, outside, typeCap, archetypeReport } from './archetypes.mjs'

const A = loadArchetypes(), names = Object.keys(A.archetypes)
const DERIVE = fileURLToPath(new URL('./derive.mjs', import.meta.url))

test('archetypes.json is well formed: bands are ordered, every observable is described and scaled, signatures name bands', () => {
  assert.ok(names.length >= 8)
  for (const [name, a] of Object.entries(A.archetypes)) {
    for (const [f, b] of Object.entries(a.bands)) {
      assert.ok(b.length === 3 && b[0] <= b[1] && b[1] <= b[2], `${name}.${f} is not [25th ≤ median ≤ 75th]`)
      assert.ok(A.observables[f]?.is, `${name}.${f} has no description`)
      assert.ok(A.scale[f] > 0, `${name}.${f} has no scale`)
    }
    for (const s of a.signature) assert.ok(a.bands[s], `${name}: signature ${s} has no band`)
    assert.ok(a.recognised.first <= a.recognised.inTwo && a.recognised.inTwo <= a.pages, name)
    for (const k of ['hero', 'space', 'body']) assert.ok(a.stance[k], `${name}: no stance.${k}`)
  }
  assert.throws(() => archetype('baroque', A), /Known: instrument/)
})

test("every archetype's dials hold the identities, land the control on whole px and put h/F inside its band unless declared outside it", () => {
  for (const name of names) {
    const o = applyArchetype(name), rows = derive(o), px = (id) => rows.find((r) => r.id === id).px
    assert.deepEqual(checkIdentities(rows), [], name)
    // Instrument's unit is a half px (n 13, chosen from a drawn specimen, G-029); its control still lands on whole px. Every other unit is whole.
    if (name === 'instrument') assert.equal(px('unit.scale.q'), 3.5)
    for (const id of [...(name === 'instrument' ? [] : ['unit.scale.q']), 'controls.control.h', 'controls.control.s', 'controls.control.i', 'controls.control.t']) assert.ok(Math.abs(px(id) - Math.round(px(id))) < 1e-9, `${name}: ${id} = ${px(id)}px`)
    const { values } = observe(o), a = A.archetypes[name]
    for (const f of ['body', 'loft'].filter((x) => a.bands[x] && !a.dials.outsideBand?.[x])) assert.ok(outside(values[f], [a.bands[f][0] - 0.05, 0, a.bands[f][2] + 0.05], 1) === 0, `${name}: ${f} ${values[f]} is outside ${a.bands[f]}`)
    assert.ok(typeCap(observe(o).roles, a), `${name}: no type role fits its contrast band`)
  }
  // Negative control: fashion's dials on the standard insets fall short of its band, which is why it carries its own.
  const d = A.archetypes.fashion.dials, short = observe({ preset: PRESETS.standard, n: d.n, density: 'loose', kappa: d.kappa }).values.loft
  assert.ok(short < A.archetypes.fashion.bands.loft[0], `standard loose gives ${short}`)
  assert.ok(d.constants?.inset, 'fashion carries its own inset')
  // A dial outside its band is declared with a reason, and really is outside: terminal's h/F, set from a drawn specimen.
  assert.deepEqual(names.filter((x) => A.archetypes[x].dials.outsideBand).sort(), ['civic', 'editorial', 'marketing', 'terminal', 'toy'])
  assert.ok(observe(applyArchetype('civic')).values.body < A.archetypes.civic.bands.body[0] && A.archetypes.civic.dials.outsideBand.body.length > 20)
  assert.ok(observe(applyArchetype('marketing')).values.body > A.archetypes.marketing.bands.body[2])
  assert.ok(observe(applyArchetype('editorial')).values.body > A.archetypes.editorial.bands.body[2] && A.archetypes.editorial.dials.outsideBand.body.length > 20)
  assert.ok(observe(applyArchetype('toy')).values.body > A.archetypes.toy.bands.body[2] && A.archetypes.toy.dials.outsideBand.body.length > 20)
  assert.ok(observe(applyArchetype('terminal')).values.loft > A.archetypes.terminal.bands.loft[2] && A.archetypes.terminal.dials.outsideBand.loft.length > 20)
})

test("an archetype's own medians score 0 against it, its dials rank it nearest among the derived values, and distance grows outside a band", () => {
  for (const name of names) {
    const med = Object.fromEntries(Object.entries(A.archetypes[name].bands).map(([f, b]) => [f, b[1]]))
    assert.equal(rank(med, A).find((r) => r.name === name).distance, 0, name)
  }
  const first = (name) => rank(observe(applyArchetype(name)).values, A)[0]
  // Toy's dials (n 18, loose, the full icon, G-033) rank it first; at n 16 with the md icon they sat inside marketing's bands and ranked marketing first.
  // Marketing is left out: its dials were set from a drawn specimen (n 18, pills) and rank calm first; it declares body outside its band.
  for (const name of ['fashion', 'calm', 'civic', 'editorial', 'toy']) assert.equal(first(name).name, name)
  assert.equal(rank(observe({ n: 16, density: 'loose', kappa: A.archetypes.toy.dials.kappa, icon: 'md' }).values, A)[0].name, 'marketing')
  assert.deepEqual(rank(observe(applyArchetype('marketing')).values, A).slice(0, 2).map((r) => r.name), ['calm', 'marketing'])
  // Equal distance: the archetype with more bands for the values comes first.
  assert.deepEqual(rank({ body: 14 }, { scale: { body: 1, loft: 1 }, archetypes: { thin: { bands: { body: [13, 14, 15] } }, full: { bands: { body: [13, 14, 15], loft: [2, 2, 2] } } } }).map((r) => r.name), ['thin', 'full'])
  assert.deepEqual(rank({ body: 14, loft: 2 }, { scale: { body: 1, loft: 1 }, archetypes: { thin: { bands: { body: [13, 14, 15] } }, full: { bands: { body: [13, 14, 15], loft: [2, 2, 2] } } } }).map((r) => r.name), ['full', 'thin'])
  assert.equal(outside(5, [1, 2, 3], 2), 1); assert.equal(outside(2, [1, 2, 3], 2), 0); assert.equal(outside(99, [1, 2, 3], 2), 3)
  // Negative control: the standard preset as shipped is not nearest fashion, calm or terminal.
  const shipped = rank(observe({ n: 14 }).values, A)
  // The three nearest are within 0.02 of each other: its control curvature of ¾ is inside marketing's band and above product's and instrument's.
  assert.ok(['product', 'instrument', 'marketing'].includes(shipped[0].name), `standard is nearest ${shipped[0].name}`)
  assert.ok(shipped.findIndex((r) => r.name === 'fashion') > 1)
})

test('--archetype takes n, density and κ from the dials, a flag still overrides them, and an unknown name is refused', () => {
  const run = (...args) => execFileSync(process.execPath, [DERIVE, ...args], { encoding: 'utf8' })
  const d = A.archetypes.calm.dials
  assert.match(run('--archetype', 'calm'), new RegExp(`^n = ${d.n}px  q = \\d+px  density ${d.density}  κ \\{"control":${d.kappa.control},`))
  assert.match(run('--archetype', 'calm'), /## archetype calm/)
  assert.match(run('--archetype', 'calm', '--n', '14', '--density', 'compact'), /^n = 14px  q = 4px  density compact/)
  assert.match(archetypeReport('editorial', applyArchetype('editorial')), /\| measure \| measure\.ideal \|/)
  assert.throws(() => run('--archetype', 'baroque'), /Known: instrument/)
})

test('a label dial resolves to px: tracking adds its width after every letter and the same is taken back; no dial, no line', async () => {
  const { labelTracking, archetypeReport } = await import('./archetypes.mjs')
  const roles = observe(applyArchetype('fashion')).roles, a = { dials: { n: 14, label: { case: 'upper', tracking: 0.22, role: 'label' } } }
  const lt = labelTracking(a, roles); assert.equal(lt.role, 'label'); assert.ok(Math.abs(lt.size - 12) < 1e-9, `label is ${lt.size}px at n 14`); assert.ok(Math.abs(lt.perLetter - 2.64) < 1e-9)
  assert.equal(labelTracking({ dials: { n: 14 } }, roles), null)
  // Fashion and editorial carry the dial, each with its reason; no other report prints a Labels line (negative control).
  assert.deepEqual(names.filter((x) => A.archetypes[x].dials.label), ['editorial', 'fashion']); assert.ok(A.archetypes.fashion.dials.label.note.length > 40 && A.archetypes.editorial.dials.label.note.length > 40)
  assert.ok(A.archetypes.fashion.dials.label.tracking > A.scale.ctlTracking, 'the dial is above the largest tracking measured, which is why it carries a note')
  for (const name of names.filter((x) => !A.archetypes[x].dials.label)) assert.doesNotMatch(archetypeReport(name, applyArchetype(name), A), /\nLabels: /)
  assert.match(archetypeReport('editorial', applyArchetype('editorial'), A), /Labels: capitals, tracking 0\.08 of the label size \(13\.5px\): 1\.08px after each letter/)
  assert.match(archetypeReport('fashion', applyArchetype('fashion'), A), /Labels: capitals, tracking 0\.22 of the label size \(12px\): 2\.64px after each letter, and 2\.64px taken back/)
})

test('a text dial sets running text in a type role: body and the ratios against it move, h/F and the lengths do not; no dial, nothing changes', async () => {
  const { runningText } = await import('./archetypes.mjs')
  const base = { n: 16, density: 'default', kappa: A.archetypes.editorial.dials.kappa, icon: 'sm' }, plain = observe(base), set = observe({ ...base, text: { role: 'heading-sm', line: 1.5 } })
  // Without the dial running text is n, and every role is measured against n.
  assert.equal(plain.values.body, 16); assert.equal(plain.values.labelToBody, 1); assert.deepEqual(runningText({ n: 16 }), { role: null, size: 16, line: null })
  // With it: heading-sm at 16 is 23.5px on a 35.25px line; icon, label and type contrast are against 23.5; h/F, curvature and the measure are untouched.
  const rt = runningText({ n: 16, text: { role: 'heading-sm', line: 1.5 } }); assert.equal(rt.size, 23.5); assert.equal(rt.line, 35.25)
  assert.equal(set.values.body, 23.5); assert.ok(Math.abs(set.values.labelToBody - 16 / 23.5) < 1e-9); assert.ok(Math.abs(set.values.iconToBody - 16 / 23.5) < 1e-9)
  for (const f of ['loft', 'kappa2', 'measure']) assert.equal(set.values[f], plain.values[f], f)
  assert.ok(Math.abs(set.roles.find((r) => r.role === 'display-md').contrast - 58.5 / 23.5) < 1e-9); assert.equal(set.roles.find((r) => r.role === 'display-md').size, plain.roles.find((r) => r.role === 'display-md').size)
  assert.throws(() => runningText({ n: 16, text: { role: 'essay' } }), /not a type role/)
  // Editorial alone carries the dial. Its type cap follows from it, and without it the same dials rank marketing first (negative control).
  assert.deepEqual(names.filter((x) => A.archetypes[x].dials.text), ['editorial'])
  const e = applyArchetype('editorial'), o = observe(e); assert.equal(typeCap(o.roles, A.archetypes.editorial).role, 'display-md'); assert.equal(A.archetypes.editorial.dials.typeCap, 'display-md')
  assert.equal(rank(o.values, A)[0].name, 'editorial'); assert.equal(rank(observe({ ...e, text: undefined }).values, A)[0].name, 'marketing')
  assert.match(archetypeReport('editorial', e, A), /Running text: the heading-sm role, 23\.5px on a 35\.25px line \(1\.5 × its size\)/)
  for (const name of names.filter((x) => x !== 'editorial')) assert.doesNotMatch(archetypeReport(name, applyArchetype(name), A), /Running text: /)
})
