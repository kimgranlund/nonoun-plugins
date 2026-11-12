// node --test fit.test.mjs
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { PRESETS, TIERS, derive, system, crisp } from './derive.mjs'
import { fit, fitUnit, kappaFor, targetPx, compareHtml, report } from './fit.mjs'

const P = PRESETS.massimo, X = system(P)
const close = (a, b, e = 1e-6) => assert.ok(Math.abs(a - b) < e, `${a} ≠ ${b}`)

/** A project built exactly on massimo at n, density dn, card depth d (all κ at the soft anchor). */
function massimoProject(n, dn = 'default', d = 5) {
  const X = system(crisp(P, n)), q = X.q(n), I = X.I(dn) * q, h = X.h(dn) * q, r = X.radius(0.75, dn) * q, rf = Math.min(r, P.soft * q)
  return { source: `massimo ${n} ${dn}`, n, lengths: [
    { id: 'button.height', role: 'height', px: h }, { id: 'button.label-inset', role: 'label-inset', px: 2 * I },
    { id: 'button.radius', role: 'radius', px: r }, { id: 'button.icon', role: 'icon', px: P.icons.md * q },
    { id: 'toolbar.control-gap', role: 'control-gap', px: X.levelGutter('group', dn) * q },
    { id: 'menu.frame-depth', role: 'frame-depth', px: X.dc(dn) * q }, { id: 'menu.frame-radius', role: 'frame-radius', px: rf },
    { id: 'menu.row', role: 'row', px: X.frameRow(dn) * q }, { id: 'menu.row-radius', role: 'row-radius', px: rf - X.dc(dn) * q }, { id: 'menu.item-inset', role: 'item-inset', px: 2 * I - X.dc(dn) * q },
    { id: 'card.card-depth', role: 'card-depth', px: d * q }, { id: 'card.card-radius', role: 'card-radius', px: (d + P.soft) * q }, { id: 'card.card-gap', role: 'card-gap', px: (d / 2) * q },
    { id: 'page.gutter', role: 'gutter', px: (Math.round(P.levels.page * X.I(dn)) / 2) * q }, { id: 'page.margin', role: 'margin', px: P.levels.page * I },
  ] }
}

test('massimo at 14 fits itself: q 4, I 1.5q, every length at both targets, every identity holds', () => {
  const R = fit(massimoProject(14))
  close(R.q, 4); close(R.tiers.controls.I, 6); close(R.tiers.controls.S, 20); close(R.kappa.control, 0.75)
  for (const t of TIERS) { assert.equal(R.conformance[t].fitted, 1, t); assert.equal(R.conformance[t].preset, 1, t) }
  assert.ok(R.checks.every((c) => c.ok), JSON.stringify(R.checks.filter((c) => !c.ok)))
  assert.equal(R.refDensity, 'default')
})

// At odd q (16px gives q = 5) the crisp preset puts S, I and g_c on whole px, off exact q multiples, so a self-fit is tested at 18px.
test('massimo at 18 loose fits itself: q 6, I 2q', () => {
  const R = fit(massimoProject(18, 'loose', 4))
  close(R.q, 6); close(R.tiers.controls.I, 12); assert.equal(R.refDensity, 'loose')
  for (const t of TIERS) assert.equal(R.conformance[t].preset, 1, t)
})

test('an outlier is flagged and pulled to the fitted value', () => {
  const p = massimoProject(14)
  p.lengths.push({ id: 'input.radius', role: 'radius', px: 7 })
  const R = fit(p), l = R.lengths.find((x) => x.id === 'input.radius')
  close(l.fitted, 12); close(l.dFitted, 5)
  assert.ok(R.conformance.controls.fitted < 1)
  assert.match(report(R), /input\.radius: 7px/)
})

test('a tailwind-like project: q 4, I 2q, S 6q; the card that is less round than its padding is caught', () => {
  const R = fit({ n: 16, lengths: [
    { id: 'button.height', role: 'height', px: 40 }, { id: 'button.label-inset', role: 'label-inset', px: 16 }, { id: 'button.radius', role: 'radius', px: 6 },
    { id: 'button.icon', role: 'icon', px: 16 }, { id: 'menu.frame-depth', role: 'frame-depth', px: 4 }, { id: 'menu.frame-radius', role: 'frame-radius', px: 8 },
    { id: 'menu.row', role: 'row', px: 36 }, { id: 'menu.row-radius', role: 'row-radius', px: 4 },
    { id: 'card.card-depth', role: 'card-depth', px: 24 }, { id: 'card.card-radius', role: 'card-radius', px: 12 },
    { id: 'page.gutter', role: 'gutter', px: 24 }, { id: 'page.margin', role: 'margin', px: 32 },
  ] })
  close(R.q, 4); close(R.tiers.controls.I, 8); close(R.tiers.controls.S, 24)
  assert.equal(R.preset.slot, 6); assert.equal(R.preset.inset.default, 2)
  assert.ok(R.checks.find((c) => c.name.startsWith('concentric rows')).ok)
  assert.equal(R.checks.find((c) => c.name.startsWith('concentric card')).ok, false)
  // Its 36px menu rows are S + 2m_c (24 + 2·6): the menu-row formula, so the check passes.
  assert.equal(R.checks.find((c) => c.name.startsWith('row 36px')).ok, true)
  assert.equal(R.preset.frameRow, 'm_c')
  // The fitted preset reproduces h exactly through derive.
  const h = derive({ preset: R.preset, n: 16 }).find((x) => x.symbol === 'h')
  close(h.px, 40)
})

test('the unit search prefers the prior among equally good divisors and reports them', () => {
  const u = fitUnit([4, 8, 12, 16, 24, 32, 40], { prior: 5 })
  close(u.q, 4); assert.ok(u.candidates.some((c) => c.q === 2))
  close(fitUnit([6, 12, 20, 32], { prior: 4 }).q, 4)
})

test('kappaFor inverts r(κ) at every density', () => {
  for (const dn of Object.keys(P.inset)) for (const k of [0, 0.2, 0.5, 0.75, 0.9, 1]) {
    const q = X.q(14), r = X.radius(k, dn) * q
    close(kappaFor(r, X.h(dn) * q, P.soft * q, P.softAnchor), k, 1e-9)
  }
})

test('a tier on another grid gets its own unit; the others keep the shared one', () => {
  const p = massimoProject(14)
  p.lengths = p.lengths.filter((l) => !l.id.startsWith('card.')).concat([
    { id: 'card.card-depth', role: 'card-depth', px: 25 }, { id: 'card.card-radius', role: 'card-radius', px: 35 }, { id: 'card.card-gap', role: 'card-gap', px: 15 },
  ])
  const R = fit(p)
  close(R.q, 4); assert.ok(R.units.containers); close(R.units.containers.a * 14 + R.units.containers.b, 5)
  assert.equal(R.units.controls, undefined)
  const d = targetPx({ role: 'card-depth', tier: 'containers', px: 25 }, { P: R.preset, n: 14, density: 'default', kappa: R.kappa, d: 5 })
  close(d, 25)
})

test('derive tags every row with a tier and filters by one', () => {
  const rows = derive({ n: 14 })
  assert.ok(rows.every((r) => ['unit', ...TIERS].includes(r.tier)))
  for (const t of TIERS) {
    const only = derive({ n: 14, tier: t })
    assert.ok(only.some((r) => r.tier === t)); assert.ok(only.every((r) => r.tier === t || r.group === 'scale'))
  }
  assert.equal(rows.find((r) => r.symbol === 'h').tier, 'controls')
  assert.equal(rows.find((r) => r.symbol === 'r_row').tier, 'collections')
  assert.equal(rows.find((r) => r.symbol.startsWith('R card-4')).tier, 'containers')
  assert.equal(rows.find((r) => r.symbol === 'G').tier, 'layout')
})

test('a preset unit per tier changes only that tier’s px', () => {
  const Q = { ...P, units: { containers: { a: 0.5, b: -2 } } }
  const a = derive({ n: 14 }), b = derive({ preset: Q, n: 14 })
  const px = (rows, sym) => rows.find((r) => r.symbol === sym).px
  close(px(a, 'h'), px(b, 'h')); close(px(b, 'd_c'), px(a, 'd_c'))
  close(px(b, 'blocks in a group, card-4'), 10); close(px(a, 'blocks in a group, card-4'), 8)
})

test('the compare page draws each component three times', () => {
  const html = compareHtml(fit(massimoProject(14)))
  assert.equal((html.match(/<figure>/g) || []).length, 3 * 5)
  assert.match(html, /<title>Geometry fit<\/title>/)
  assert.match(html, /prefers-color-scheme:dark/)
})

test('two scopes recover the unit line q = a·n + b', () => {
  const tag = (p, n) => p.lengths.map((l) => ({ ...l, id: `${n}.${l.id}`, n }))
  const R = fit({ n: 14, lengths: [...tag(massimoProject(14), 14), ...tag(massimoProject(18), 18)] })
  close(R.unit.a, 0.5); close(R.unit.b, -3); close(R.q, 4)
  for (const t of TIERS) assert.equal(R.conformance[t].preset, 1, t)
})

test('a padding that did not absorb its border is read without it and named', () => {
  const p = massimoProject(14)
  for (const l of p.lengths) if (l.role === 'card-depth') { l.px += 1; l.border = 1 }
  const R = fit(p)
  close(R.tiers.containers.d, 20)
  assert.ok(R.notes.some((n) => /does not absorb the border/.test(n)))
  assert.ok(R.lengths.find((l) => l.role === 'card-depth').borderOnly)
})

test('control sizes that keep the slot are read as densities', () => {
  const R = fit({ n: 14, lengths: [
    { id: 'toggle.height', role: 'height', px: 36 }, { id: 'toggle.label-inset', role: 'label-inset', px: 17, border: 1 }, { id: 'toggle.radius', role: 'radius', px: 8 },
    { id: 'button-sm.height', role: 'height', px: 32 }, { id: 'button-sm.label-inset', role: 'label-inset', px: 12, border: 0 },
    { id: 'list.row', role: 'row', px: 32 }, { id: 'tabs.host-depth', role: 'host-depth', px: 3, border: 0 },
  ] })
  close(R.tiers.controls.S, 20); close(R.tiers.controls.I, 8)
  assert.equal(R.preset.inset.default, 2); assert.equal(R.preset.inset.compact, 1.5)
  const sm = R.lengths.find((l) => l.id === 'button-sm.height')
  assert.equal(sm.density, 'compact'); close(sm.dFitted, 0)
  close(R.lengths.find((l) => l.id === 'list.row').dFitted, 0)
  // A padding that records no border is never read as one.
  assert.ok(!R.notes.some((x) => x.includes('host depth')))
  assert.equal(R.lengths.find((l) => l.id === 'tabs.host-depth').borderOnly, false)
})
