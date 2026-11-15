// The position score: references/dimensions.json against scripts/dimensions.mjs and references/archetypes.json.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { loadDimensions, position, positionReport, percentile, normalQuantile } from './dimensions.mjs'
import { loadArchetypes, rank, nearTwin, scoreReport } from './archetypes.mjs'

const D = loadDimensions(), A = loadArchetypes(), names = Object.keys(A.archetypes)
const medians = (name) => Object.fromEntries(Object.entries(A.archetypes[name].bands).map(([f, b]) => [f, b[1]]))

test('dimensions.json is well formed: a weight and a quantile table per observable, six named dimensions, a mean per archetype', () => {
  assert.equal(D.components.length, 9)
  assert.deepEqual(D.components.filter((c) => c.name).map((c) => c.name), ['richness', 'body size', 'colour', 'white space', 'text cover', 'lightness'])
  for (const c of D.components) { assert.equal(c.weights.length, D.observables.length); if (c.name) assert.ok(c.low && c.high && Object.keys(c.loads).length) }
  for (const k of D.observables) { const t = D.quantiles[k]; assert.equal(t.length, 41, k); assert.ok(t.every((v, i) => !i || v >= t[i - 1]), `${k}: quantiles fall`); assert.ok(k in A.scale, `${k} is not an observable of archetypes.json`) }
  assert.deepEqual(Object.keys(D.archetypes).sort(), [...names].sort())
  for (const a of names) { assert.equal(D.archetypes[a].mean.length, 9); assert.equal(D.archetypes[a].pages, A.archetypes[a].pages, `${a}: pages`) }
})

test('the rank transform: the middle of a table is 0.5, ties take the middle of their run, and values outside it clamp', () => {
  const t = Array.from({ length: 41 }, (_, i) => i)
  assert.equal(percentile(20, t), 0.5); assert.equal(percentile(-5, t), 0); assert.equal(percentile(99, t), 1); assert.ok(Math.abs(percentile(10.5, t) - 10.5 / 40) < 1e-12)
  const tied = [...Array(21).fill(0), ...Array.from({ length: 20 }, (_, i) => i + 1)]
  assert.equal(percentile(0, tied), 10 / 40)   // 21 pages at 0: the middle of positions 0 to 20
  assert.ok(Math.abs(normalQuantile(0.5)) < 1e-9); assert.ok(Math.abs(normalQuantile(0.975) - 1.959964) < 1e-5)
})

test("an archetype's medians sit near its own mean on every named dimension, and far from an archetype at the other end", () => {
  for (const name of names) {
    const p = position(medians(name)).scores, a = D.archetypes[name]
    D.components.forEach((c, i) => { if (c.name) assert.ok(Math.abs(p[i].score - a.mean[i]) <= 2 * a.sd[i] + 0.5, `${name} ${c.name}: ${p[i].score.toFixed(2)} against mean ${a.mean[i]} ± ${a.sd[i]}`) })
  }
  const s = (name, dim) => position(medians(name)).scores[D.components.findIndex((c) => c.name === dim)].score
  // Negative controls: the dimensions separate what they are named for.
  assert.ok(s('marketing', 'richness') - s('terminal', 'richness') > 1.5)
  assert.ok(s('editorial', 'body size') - s('fashion', 'body size') > 1.5)
  assert.ok(s('editorial', 'text cover') - s('toy', 'text cover') > 1)
})

test('a position needs 40 observables: a preset\'s six are refused with the reason, and the report says so instead of failing', () => {
  assert.throws(() => position({ body: 16, loft: 2.75, kappa2: 0.5, iconToBody: 1.25, labelToBody: 1, measure: 66 }), /^Error: cannot place: 5 of 66 observables given, and a position needs 40/)
  assert.match(positionReport({ body: 16 }), /## Position\n\nNot given: 1 of 66/)
  assert.equal(position(medians('civic')).used >= 40, true)
})

test('families: every archetype has one, near is mutual or points at the centre of its family, and the report names the family only for a near twin', () => {
  for (const n of names) { const a = A.archetypes[n]; assert.ok(a.family, n); for (const m of a.near) { assert.ok(names.includes(m), `${n} near ${m}`); assert.equal(A.archetypes[m].family, a.family, `${n} and ${m} share a family`) } }
  assert.deepEqual(A.archetypes.instrument.near, ['product']); assert.deepEqual(A.archetypes.product.near, ['instrument'])
  const mid = Object.fromEntries(Object.keys(A.archetypes.instrument.bands).filter((f) => A.archetypes.product.bands[f]).map((f) => [f, (A.archetypes.instrument.bands[f][1] + A.archetypes.product.bands[f][1]) / 2]))
  const r = rank(mid, A); assert.ok(['instrument', 'product'].includes(r[0].name)); assert.equal(r[0].family, 'application')
  assert.ok(nearTwin(r, A), 'halfway between instrument and product, the runner-up is its twin'); assert.match(scoreReport(mid, A), /## Nearest: (instrument|product) \(application; (instrument|product) within [\d.]+\)/)
  // A twin that is not the runner-up does not count: here instrument lies between toy and its twin marketing.
  assert.equal(nearTwin([{ name: 'toy', distance: 0.1 }, { name: 'instrument', distance: 0.1 }, { name: 'marketing', distance: 0.12 }], A), null)
  assert.equal(nearTwin([{ name: 'toy', distance: 0.1 }, { name: 'marketing', distance: 0.12 }, { name: 'instrument', distance: 0.13 }], A).name, 'marketing')
  // Negative control: fashion has no twin, so its report names fashion alone.
  const f = rank(medians('fashion'), A); assert.equal(f[0].name, 'fashion'); assert.equal(nearTwin(f, A), null); assert.match(scoreReport(medians('fashion'), A), /## Nearest: fashion\n/)
})
