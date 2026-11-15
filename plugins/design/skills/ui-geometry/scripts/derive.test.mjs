// node --test derive.test.mjs
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { PRESETS, derive, system, validatePreset, multiGrid, multiGridFaults } from './derive.mjs'

const P = PRESETS.standard
const { q, I, mc, h, radius, cardRadius, nested } = system(P)
const densities = Object.keys(P.inset)
const close = (a, b) => assert.ok(Math.abs(a - b) < 1e-9, `${a} ≠ ${b}`)

test('standard: q is 4px at 14, 5px at 16; h is 28/32/36 at 14', () => {
  close(q(14), 4); close(q(16), 5)
  assert.deepEqual(densities.map((d) => h(d) * q(14)), [28, 32, 36])
})

test('identities hold at every density', () => {
  for (const d of densities) {
    close(h(d), P.slot + 2 * I(d))
    close(mc(d) + P.gutter, I(d))
    close(h(d) - 2 * mc(d), P.slot + 2 * P.gutter)
    close(P.icons.full, P.slot)
  }
})

test('curvature passes through square, soft and pill', () => {
  for (const d of densities) {
    close(radius(0, d), 0)
    close(radius(P.softAnchor, d), P.soft)
    close(radius(1, d), h(d) / 2)
  }
})

test('curvature is continuous, monotonic and never above h/2', () => {
  for (const d of densities) {
    let prev = -1
    for (let k = 0; k <= 1.0001; k += 0.01) {
      const r = radius(k, d)
      assert.ok(r >= prev - 1e-12 && r <= h(d) / 2 + 1e-12)
      if (prev >= 0) assert.ok(r - prev < 0.2, 'jump')
      prev = r
    }
  }
})

test('a card at inset 1 is concentric with a control: R − d = r while r ≤ soft', () => {
  for (const d of densities) for (const c of P.cardDepths.slice(1)) for (const k of [0.1, 0.3, P.softAnchor]) close(cardRadius(c, k, d) - c, radius(k, d))
})

test('a card at curvature 0 is square at every depth, and its nested cards with it', () => {
  for (const d of densities) for (const c of P.cardDepths) close(cardRadius(c, 0, d), 0)
  close(nested(4, cardRadius(4, 0, 'default'), 0.5)[1], 0)
})

test("cardRadius 'control' gives every card, nested card and panel the control's corner; the default is unchanged; another value is refused", () => {
  const cur = (o) => Object.fromEntries(derive(o).filter((r) => r.tier === 'containers' && r.group === 'curvature').map((r) => [r.id, r.px]))
  for (const density of densities) for (const kc of [0.25, 0.5, 1]) {
    const kappa = { control: kc, frame: kc, card: 0.5, panel: kc }, r = derive({ density, kappa }).find((x) => x.id === 'controls.curvature.r').px
    const flat = cur({ preset: { ...P, cardRadius: 'control' }, density, kappa })
    for (const [id, px] of Object.entries(flat)) close(px, /nest-f-0-in/.test(id) ? 0 : r)
    assert.deepEqual(cur({ preset: { ...P, cardRadius: 'concentric' }, density, kappa }), cur({ density, kappa }))
  }
  // Negative control: under the default a padded card is larger than the control's corner, so the assertion above can fail.
  assert.ok(cur({})['containers.curvature.r-card-4'] > derive().find((x) => x.id === 'controls.curvature.r').px)
  assert.throws(() => validatePreset({ cardRadius: 'round' }), /cardRadius is 'concentric' or 'control'/); assert.doesNotThrow(() => validatePreset({ cardRadius: 'control' }))
})

test('deeper cards stay soft under pill; depth 0 takes the control corner', () => {
  close(cardRadius(4, 1, 'default'), 4 + P.soft)
  close(cardRadius(0, 1, 'loose'), h('loose') / 2)
})

test('nesting keeps the parent curve and the depth sums to d', () => {
  const R = cardRadius(4, P.softAnchor, 'default')
  for (const f of [0.25, 0.5, 0.75, 1]) { const [dd, rr] = nested(4, R, f); close(dd + f * 4, 4); close(rr, R - f * 4) }
  assert.deepEqual(nested(4, R, 0), [4, 0])
})

test('chains never go negative at square', () => {
  for (const r of derive({ kappa: { control: 0, frame: 0, card: 0, panel: 0 } }).filter((x) => x.group === 'curvature')) assert.ok(r.q >= 0)
})

test('grid columns fill the width exactly', () => {
  const rows = derive({ n: 14, width: 1280, columns: 12 })
  const w = rows.find((r) => r.symbol.startsWith('w ')).q
  const M = rows.find((r) => r.symbol === 'M').q, G = rows.find((r) => r.symbol === 'G').q
  close(12 * w + 11 * G + 2 * M, 1280 / q(14))
})

test('every listed count fills the field in whole units', () => {
  const m = multiGrid({ field: 58, gutter: 2, width: 1440 })
  assert.deepEqual(m.counts.map((c) => c.n), [1, 2, 3, 4, 5, 6, 10, 12])
  assert.deepEqual(m.counts.map((c) => c.units), [58, 28, 18, 13, 10, 8, 4, 3])
  assert.deepEqual(multiGridFaults(m), [])
  for (const c of m.counts) close(c.n * c.px + (c.n - 1) * m.gutter, m.field)
  assert.equal(multiGrid({ field: 58, gutter: 2, width: 1456 }).u, 23, 'at 1x, whole px'); assert.equal(m.u, 23); assert.equal(m.margin, m.gutter); assert.equal(m.margin, 46)
  assert.equal(multiGrid({ field: 58, gutter: 2, width: 1456, dpr: 2 }).u, 23.5, 'u snaps to the device grid')
  assert.deepEqual(multiGrid({ field: 57, gutter: 2, width: 1440 }).counts.map((c) => c.n), [1], 'negative control: U + g = 59 is prime')
  assert.equal(multiGridFaults({ ...m, counts: [...m.counts, { n: 7, units: 52 / 7, px: 0 }] }).length, 1, 'negative control: 7 columns fall between units')
  assert.equal(multiGridFaults({ ...m, counts: m.counts.filter((c) => c.n !== 5) }).length, 1, 'negative control: a whole count left out')
})

test('marks, tracks and widths derive from the preset (standard at 14px)', () => {
  const px = (s) => derive().find((r) => r.symbol === s).px
  assert.equal(px('checkbox box'), 16)
  assert.equal(px('radio dot'), 8)
  assert.equal(px('switch thumb'), 12)
  assert.equal(px('progress / slider track'), 4)
  assert.equal(px('meter track'), 8)
  assert.equal(px('row'), 32)
  assert.equal(px('tree indent'), 20)
  assert.equal(px('dialog'), 480)
  assert.equal(px('popover'), 320)
  assert.ok(px('switch thumb') < px('switch track'))
})

test('a custom preset changes the system and keeps the identities', () => {
  const custom = { ...P, unit: { a: 0.25, b: 0, nMin: 8 }, slot: 6, inset: { compact: 1, default: 2, loose: 3 }, soft: 4, softAnchor: 0.5 }
  const X = system(custom)
  close(X.q(16), 4)
  close(X.h('default'), 10)
  close(X.radius(0.5, 'default'), 4)
  close(X.radius(1, 'default'), 5)
  assert.notDeepEqual(derive({ preset: custom }), derive())
})

import { elevation } from './derive.mjs'

test('elevation: standard popup is ¼, ½, 1, 2 q, each blurred twice its offset; far blur = 4q', () => {
  const e = elevation({ level: 'popup' })
  assert.deepEqual(e.layers.map((l) => l.y), [0.25, 0.5, 1, 2])
  for (const l of e.layers) close(l.blur, 2 * l.y)
  close(e.layers.at(-1).blur, 4)
})

test('elevation: standard alphas round to 7, 5, 4, 3% in light and sum to the budget', () => {
  const e = elevation({ level: 'popup' })
  assert.deepEqual(elevation({ level: 'popup', round: true }).layers.map((l) => Math.round(l.alpha * 100)), [7, 5, 4, 3])
  close(e.layers.reduce((a, l) => a + l.alpha, 0), 0.19)
  close(elevation({ level: 'popup', scheme: 'dark' }).layers.reduce((a, l) => a + l.alpha, 0), 0.45)
})

test('elevation: a level scales the lengths, never the alpha', () => {
  const pop = elevation({ level: 'popup' }), modal = elevation({ level: 'modal' })
  modal.layers.forEach((l, k) => { close(l.y, 2 * pop.layers[k].y); close(l.alpha, pop.layers[k].alpha) })
  close(modal.composite, pop.composite)
  assert.deepEqual(elevation({ level: 'raised' }).layers.map((l) => l.y), [0.125, 0.25, 0.5, 1])
})

test('elevation: five layers add a halo at 4q, keep the budget, and fade monotonically', () => {
  const e = elevation({ level: 'popup', layers: 5 })
  assert.deepEqual(e.layers.map((l) => l.y), [0.25, 0.5, 1, 2, 4])
  close(e.layers.reduce((a, l) => a + l.alpha, 0), 0.19)
  for (let k = 1; k < 5; k++) assert.ok(e.layers[k].alpha < e.layers[k - 1].alpha)
  assert.ok(e.composite < 0.19 && e.composite > 0.17)
})

test('elevation: a continuous level and a light angle', () => {
  const custom = { ...P, elevation: { ...P.elevation, angle: 45, spread: 0.25 } }
  const e = elevation({ preset: custom, level: 1.25 })
  for (const l of e.layers) { close(l.x, l.y); close(l.spread, -0.25 * l.y) }
  close(e.layers[2].y, 1.25)
})

import { fluidN, snap, onGrid, capOffset } from './derive.mjs'
const val = (rows, sym) => rows.find((r) => r.symbol === sym || r.alias === sym)

test('focus ring: its outer corner is concentric, r + o + w', () => {
  const rows = derive()
  close(val(rows, 'ring outer radius').q, 3 + 0.5 + 0.5)
  close(val(rows, 'ring outer radius').px, 16)
  assert.ok(val(rows, 'clearance needed').q <= mc('default') + 1e-9 + 0.5 * 2, 'ring fits the grouped gap')
})

test('hit targets: 32px controls meet 24px pointer targets; touch needs 6px each side', () => {
  const rows = derive()
  close(val(rows, 'expansion of h (pointer)').px, 0)
  close(val(rows, 'expansion of h (touch)').px, 6)
  close(val(rows, 'expansion of h_o (touch)').px, 10)
  close(val(rows, 'minimum I for h to meet T (touch)').px, 12)
})

test('borders eat padding and radius', () => {
  const rows = derive({ cardDepth: 4 })
  close(val(rows, 'card-4 inner padding').px, 15)
  close(val(rows, 'card-4 inner radius').px, 23)  // R = d + min(r(κ_card = ½), soft) = 16 + 8
  close(val(rows, 'control inner radius').px, 11)
})

test('pixel snapping: whole q at even n, half px at 2x', () => {
  assert.ok(onGrid(q(14) * 1.5) && onGrid(q(16) * 0.5, 2) && !onGrid(q(15) * 1, 1))
  close(snap(4.615, 1), 5); close(snap(2.3, 2), 2.5)
})

test('text: Inter-like metrics centre the cap height in the line box', () => {
  assert.ok(Math.abs(capOffset(P.font)) < 0.005)
  close(val(derive(), 'label line box in S').q, 0.5)
})

test('fluid scale: clamps at both ends and rounds to whole q', () => {
  close(fluidN(320), 14); close(fluidN(2000), 16)
  close(fluidN(1024), 16); close(fluidN(600), 14)
  for (const W of [360, 700, 900, 1100, 1440]) assert.ok(Number.isInteger(q(fluidN(W))))
  close(fluidN(900, { ...P, fluid: { ...P.fluid, step: 0 } }), 15)
})

test('measure, media, avatars and icon stroke', () => {
  const rows = derive()
  close(val(rows, 'ideal (66 ch)').px, 66 * 0.5 * 14)
  close(val(rows, 'video 16:9 height at w = 40').q, 22.5)
  close(val(rows, 'avatar lg radius').q, 3)                     // an h-sized avatar takes the control radius
  close(val(derive({ kappa: { control: 1 } }), 'avatar xxl radius').q, 10)  // pill: half its size
  const strokes = rows.filter((r) => r.group === 'icon stroke').map((r) => r.px)
  close(strokes[1], 1.5)
  for (let k = 1; k < strokes.length; k++) assert.ok(strokes[k] > strokes[k - 1])
})

test('breakpoints: k columns fit exactly at their breakpoint', () => {
  const rows = derive(), bp = val(rows, '3 columns').q
  close(bp, 3 * 40 + 2 * 3 + 2 * 6)  // M = 4I = 6q, G = M/2 = 3q
})

test('crisp tiers: n ≡ 2 mod 4 makes half-q lengths whole; n ≡ 6 mod 8 makes quarter-q lengths whole too', () => {
  const groups = ['control', 'icon', 'curvature', 'gap']
  const offAt = (n, keep) => derive({ n }).filter((r) => groups.includes(r.group) && keep(r.q) && !onGrid(r.px)).map((r) => r.symbol)
  const isHalf = (x) => Math.abs(x * 2 - Math.round(x * 2)) < 1e-9
  for (const n of [14, 18, 22, 26]) assert.deepEqual(offAt(n, isHalf), [], `half-q at n = ${n}`)
  for (const n of [14, 22, 30]) assert.deepEqual(offAt(n, () => true), [], `all at n = ${n}`)
  const crisp = { ...P, fluid: { w1: 360, n1: 14, w2: 1920, n2: 22, step: 8, align: 6 } }
  assert.deepEqual([360, 1000, 1300, 1920].map((W) => fluidN(W, crisp)), [14, 14, 22, 22])
})

test('container ladder: standard defaults at 14 and its identities at every density', async () => {
  const { containers } = await import('./derive.mjs')
  const px = (rows, name, col, i = 0) => rows.find((r) => r.container === name)[col][i].q * 4
  const A = containers({ n: 14 })
  assert.deepEqual([px(A, 'Button, input, select', 'pad', 1), px(A, 'Segmented control, tab list', 'pad'), px(A, 'Listbox, menu, select popup', 'radius', 1),
    px(A, 'Card', 'radius'), px(A, 'Dialog, sheet', 'radius'), px(A, 'Page', 'pad'), px(A, 'Page', 'gap')], [12, 3, 9, 24, 32, 24, 12])
  for (const density of Object.keys(P.inset)) for (const kv of [0, 0.4, 0.75, 1]) {
    const rows = containers({ n: 14, density, kappa: { control: kv, frame: kv, card: kv }, cardDepth: 5 })
    const g = (name, col, i = 0) => rows.find((r) => r.container === name)[col][i].q
    close(g('Segmented control, tab list', 'radius', 1), Math.max(0, g('Segmented control, tab list', 'radius') - g('Segmented control, tab list', 'pad')))
    close(g('Segmented control, tab list', 'height', 1), g('Segmented control, tab list', 'height') - 2 * g('Segmented control, tab list', 'pad'))
    close(g('Listbox, menu, select popup', 'radius', 1), Math.max(0, g('Listbox, menu, select popup', 'radius') - g('Listbox, menu, select popup', 'pad')))
    close(g('Nested card, well', 'pad') * 2, g('Card', 'pad'))
    { const rk = Math.min(radius(kv, density), P.soft); close(g('Card', 'radius'), rk === 0 ? 0 : g('Card', 'pad') + rk) }   // square at κ 0
    assert.equal(rows.length, 20)
  }
})

test('standard cards default to κ ½: R − d = 2q, while controls keep κ_s', () => {
  const at = (rows, sym) => rows.find((r) => r.symbol.startsWith(sym))
  const rows = derive({ n: 14, cardDepth: 4 })
  close(at(rows, 'R card-4 ').q - 4, 2); close(at(rows, 'r  κ').q, 3)
  const own = derive({ n: 14, cardDepth: 4, kappa: { card: 0.75 } })
  close(at(own, 'R card-4 ').q, 7)
})

test('gap rule: inside every container the gap is half its padding, before actions the full padding, all on whole px', async () => {
  const { containers } = await import('./derive.mjs')
  for (const density of Object.keys(P.inset)) for (const d of [2, 3, 4, 5, 6, 8]) {
    const rows = containers({ n: 14, density, cardDepth: d })
    for (const r of rows.filter((x) => x.tier === 'containers' || x.tier === 'layout')) {
      const p = r.pad[0].q
      for (const g of r.gap) {
        assert.ok(Math.abs(g.q * 4 - Math.round(g.q * 4)) < 1e-9, `${r.container} ${g.e} = ${g.q * 4}px is off the pixel grid`)
        if (/before actions|header →/.test(g.e)) close(g.q, p)
        else if (/band →/.test(g.e)) assert.ok(g.q <= Math.round(p) / 2 + 1e-9)
        else if (!/rows d \/ 4|groups d|caption|^flow:/.test(g.e)) assert.ok(Math.abs(g.q - p / 2) <= 0.25 + 1e-9, `${r.container} ${g.e}: ${g.q} vs ${p}/2`)
      }
    }
    const pop = rows.find((x) => x.container.startsWith('Popover')).pad[0].q, dlg = rows.find((x) => x.container.startsWith('Dialog')).pad[0].q
    const card = rows.find((x) => x.container === 'Card').pad[0].q
    close(pop * 4, Math.round(0.75 * card * 4)); close(dlg * 4, Math.round(1.5 * card * 4))
  }
})

test('menu rows fit the frame: h − 2d_c with d_c = ¾q, so one row plus its padding is exactly h, at every density', async () => {
  const { containers } = await import('./derive.mjs')
  const px = (dn) => containers({ n: 14, density: dn }).find((r) => r.container.startsWith('Listbox')).height[0].q * 4
  assert.deepEqual(Object.keys(P.inset).map(px), [22, 26, 30])
  for (const density of Object.keys(P.inset)) for (const kv of [0, 0.4, 0.75, 1]) {
    const rows = containers({ n: 14, density, kappa: { control: kv, frame: kv } })
    const menu = rows.find((r) => r.container.startsWith('Listbox')), btn = rows.find((r) => r.container.startsWith('Button'))
    close(menu.height[0].q + 2 * menu.pad[0].q, btn.height[0].q)
    close(menu.pad[0].q, 0.75)
    close(menu.radius[1].q, Math.max(0, menu.radius[0].q - 0.75))
  }
})

test('segments and menu rows share the item height h − 2d_c; both hosts pad d_c = ¾q and stay concentric', async () => {
  const { containers } = await import('./derive.mjs')
  for (const density of Object.keys(P.inset)) for (const kv of [0, 0.4, 0.75, 1]) {
    const rows = containers({ n: 14, density, kappa: { control: kv, frame: kv } })
    const seg = rows.find((r) => r.container.startsWith('Segmented')), menu = rows.find((r) => r.container.startsWith('Listbox'))
    close(seg.height[1].q, menu.height[0].q); close(seg.pad[0].q, 0.75); close(seg.height[1].q + 2 * seg.pad[0].q, seg.height[0].q)
    close(seg.radius[1].q, Math.max(0, seg.radius[0].q - seg.pad[0].q))
  }
})

test('tables host cell controls at item height; tables and lists take the button radius and its label inset; inset list selections are concentric', async () => {
  const { containers } = await import('./derive.mjs')
  for (const density of Object.keys(P.inset)) for (const d of [3, 4, 6]) {
    const rows = containers({ n: 14, density, cardDepth: d })
    const g = (name) => rows.find((r) => r.container === name)
    const t = g('Table'), flush = g('List, flush'), inset = g('List, inset'), menu = g('Listbox, menu, select popup'), btn = g('Button, input, select')
    close(t.height[1].q + 2 * t.height[2].q, t.height[0].q)
    close(t.height[0].q, h(density)); close(flush.height[0].q, h(density))
    // Edge text sits at T = 2I, where a button's label sits, so a table above a button lines up.
    close(t.pad[2].q, btn.pad[1].q); close(flush.pad[1].q, btn.pad[1].q)
    close(t.radius[0].q, btn.radius[0].q); close(flush.radius[0].q, btn.radius[0].q)
    close(inset.height[0].q, btn.height[0].q); close(inset.pad[0].q, menu.pad[0].q); close(inset.radius[0].q, btn.radius[0].q); close(inset.radius[1].q, Math.max(0, btn.radius[0].q - inset.pad[0].q))
    close(inset.pad[0].q + inset.pad[1].q, btn.pad[1].q)
  }
})

test('form fields sit 2I apart, the same as table columns; labels and help text sit g_c from the control', async () => {
  const { containers } = await import('./derive.mjs')
  for (const density of Object.keys(P.inset)) {
    const rows = containers({ n: 14, density })
    const form = rows.find((r) => r.container === 'Form'), table = rows.find((r) => r.container === 'Table')
    close(form.gap[0].q, table.gap[0].q)
    close(form.gap[1].q, P.gutter); close(form.gap[2].q, P.gutter)
    assert.ok(form.gap[0].q >= 2 * form.gap[1].q, 'fields at least twice as far apart as label and control')
  }
  assert.equal(containers({ n: 14 }).find((r) => r.container === 'Form').gap[0].q * 4, 12)
})

test('card depth follows density, one q per step; the band gap holds at 2px; a header has d below as above', async () => {
  const { containers } = await import('./derive.mjs')
  const card = (density) => containers({ n: 14, density }).find((r) => r.container === 'Card')
  const gap = (density, re) => card(density).gap.find((g) => re.test(g.e)).q * 4
  assert.deepEqual(['compact', 'default', 'loose'].map((x) => card(x).pad[0].q * 4), [12, 16, 20])
  assert.deepEqual(['compact', 'default', 'loose'].map((x) => gap(x, /^band →/)), [2, 2, 2])
  assert.deepEqual(['compact', 'default', 'loose'].map((x) => gap(x, /^header →/)), [12, 16, 20])
})

test('crisp: at 16px every padding, gap and height is a whole px, and h = 40', async () => {
  const { containers } = await import('./derive.mjs')
  for (const density of Object.keys(P.inset)) {
    const rows = containers({ n: 16, density })
    for (const r of rows) for (const col of ['pad', 'gap', 'height']) for (const x of r[col]) assert.ok(Math.abs(x.q * 5 - Math.round(x.q * 5)) < 1e-9, `${density} ${r.container} ${x.e} = ${x.q * 5}px`)
  }
  close(containers({ n: 16 }).find((r) => r.container.startsWith('Button')).height[0].q * 5, 40)
})

test('the flow of a page is spaced in body sizes: the same at every density, text to actions twice the paragraph gap, sections 6½F apart', async () => {
  const { containers, derive: dv } = await import('./derive.mjs')
  for (const n of [14, 16, 18, 20]) {
    const at = (density) => containers({ n, density }).find((r) => r.container === 'Page section')
    const sec = at('default'), g = (re) => sec.gap.find((x) => re.test(x.e)).q, px = (v) => v * system(P).q(n)
    for (const d of densities) assert.deepEqual(at(d).gap.map((x) => x.q), sec.gap.map((x) => x.q), `n ${n} ${d}: flow gaps move with density`)
    close(px(g(/paragraphs/)), Math.round(1.25 * n) - (Math.abs((1.25 * n) % 1 - 0.5) < 1e-9 && Math.round(1.25 * n) % 2 ? 1 : 0))   // whole px, ties to even
    close(px(g(/kicker/)), n); close(px(g(/action → note/)), n)
    assert.ok(Math.abs(px(g(/text → actions/)) - 2 * px(g(/paragraphs/))) <= 1, 'text to actions is twice the paragraph gap, to the pixel')
    assert.ok(Math.abs(2 * px(sec.pad[0].q) - 6.5 * n) <= 1)
    assert.ok(g(/text → actions/) < sec.pad[0].q, 'no flow gap exceeds the section padding')
    const rows = dv({ n }), row = (id) => rows.find((r) => r.id === 'layout.flow.' + id)
    close(row('paragraphs').px, px(g(/paragraphs/))); close(row('section-padding').px, px(sec.pad[0].q))
  }
  // Negative control: the card keeps the gap rule; its gaps do move with density.
  assert.notDeepEqual(containers({ n: 14, density: 'compact' }).find((r) => r.container === 'Card').pad[0].q, containers({ n: 14, density: 'loose' }).find((r) => r.container === 'Card').pad[0].q)
})

test('a page section shares the page edge: no inline padding', async () => {
  const { containers } = await import('./derive.mjs')
  const sec = containers({ n: 14 }).find((r) => r.container === 'Page section')
  close(sec.pad[1].q, 0)
})

test('menu and listbox text sits at T, where the select trigger shows its value', async () => {
  const { containers } = await import('./derive.mjs')
  for (const density of Object.keys(P.inset)) {
    const rows = containers({ n: 14, density })
    const menu = rows.find((r) => r.container.startsWith('Listbox')), btn = rows.find((r) => r.container.startsWith('Button'))
    close(menu.pad[0].q + menu.pad[1].q, btn.pad[1].q)
  }
})

test('controls pad by edge: text 2I, icon I; an icon box S places the glyph at I + (S − a)/2 and the label at 2I + S', async () => {
  const { containers } = await import('./derive.mjs')
  for (const density of Object.keys(P.inset)) {
    const btn = containers({ n: 14, density }).find((r) => r.container.startsWith('Button'))
    const [, text, icon] = btn.pad.map((x) => x.q), gap = btn.gap[0].q, margin = btn.gap[1].q, S = btn.height[1].q
    close(text, 2 * I(density)); close(icon, I(density)); close(gap, I(density))
    close(icon + margin, I(density) + (P.slot - P.icons.md) / 2)
    close(icon + S + gap, 2 * I(density) + P.slot)
    close(icon + S + icon, h(density))
  }
})

test('icon buttons centre every icon size with a whole-px margin', async () => {
  const { containers } = await import('./derive.mjs')
  for (const n of [14, 16, 18]) {
    const q = system(P).q(n), ib = containers({ n }).find((r) => r.container === 'Icon button')
    for (const m of ib.gap) assert.ok(Math.abs(m.q * q - Math.round(m.q * q)) < 1e-9, `${n}px ${m.e} = ${m.q * q}`)
  }
  assert.deepEqual(containers({ n: 14 }).find((r) => r.container === 'Icon button').gap.map((m) => m.q * 4), [2, 3, 1, 0])
})

test('one left edge: an unframed choice mark starts on the content edge; text inside shapes and field labels sit at T', async () => {
  const { containers } = await import('./derive.mjs')
  for (const density of Object.keys(P.inset)) {
    const rows = containers({ n: 14, density })
    const ch = rows.find((r) => r.container === 'Choice row'), btn = rows.find((r) => r.container.startsWith('Button')), form = rows.find((r) => r.container === 'Form')
    close(ch.pad[0].q, 0); close(ch.pad[1].q, 0)
    close(ch.gap[0].q, I(density) + (P.slot - P.icons.md) / 2)
    close(form.pad[1].q, btn.pad[1].q)
  }
})

test('a field label sits at T over the value; the control box stays on the content edge', async () => {
  const { containers } = await import('./derive.mjs')
  for (const density of Object.keys(P.inset)) {
    const rows = containers({ n: 14, density })
    const form = rows.find((r) => r.container === 'Form'), btn = rows.find((r) => r.container.startsWith('Button'))
    close(form.pad[0].q, 0); close(form.pad[1].q, btn.pad[1].q)
  }
})

test('three label levels, three gaps: groups d apart, blocks d/2, a group caption I, a field label g_c', async () => {
  const { containers } = await import('./derive.mjs')
  for (const density of Object.keys(P.inset)) {
    const rows = containers({ n: 14, density })
    const card = rows.find((r) => r.container === 'Card'), form = rows.find((r) => r.container === 'Form')
    const g = (e) => card.gap.find((x) => x.e.startsWith(e)).q
    close(g('groups d'), card.pad[0].q); close(g('blocks in a group'), card.pad[0].q / 2); close(g('group caption'), I(density))
    assert.ok(g('groups d') > g('blocks in a group') && g('blocks in a group') > form.gap[1].q && g('group caption') > form.gap[1].q)
  }
})

test('a button inside an input is an item in a host; a popup sits d_c from its trigger', async () => {
  const { containers } = await import('./derive.mjs')
  for (const density of Object.keys(P.inset)) {
    const rows = containers({ n: 14, density })
    const hc = rows.find((r) => r.container === 'Hosted control'), seg = rows.find((r) => r.container.startsWith('Segmented')), menu = rows.find((r) => r.container.startsWith('Listbox'))
    close(hc.height[0].q, seg.height[1].q); close(hc.pad[0].q, seg.pad[0].q); close(hc.radius[0].q, seg.radius[1].q)
    close(menu.gap.find((g) => g.e.startsWith('popup offset')).q, menu.pad[0].q)
  }
})

// ---- named checks for SKILL.md › Identities, with negative controls ----
import { checkIdentities, containers as ladder } from './derive.mjs'

test('identities hold at every density under checkIdentities(), and a mutated table fails', () => {
  for (const density of densities) assert.deepEqual(checkIdentities(derive({ density })), [], density)
  const bad = derive().map((r) => (r.id === 'controls.control.h' ? { ...r, q: r.q + 0.25 } : r))
  assert.ok(checkIdentities(bad).includes('h = S + 2I'), 'negative control: a mutated h must fail')
})

/** Gaps that exceed the largest padding of a padded container (popover, card, dialog, region, page section, page). */
export const gapOverruns = (rows) => rows.filter((r) => ['containers', 'layout'].includes(r.tier) && r.pad.some((p) => p.q > 0))
  .flatMap((r) => r.gap.filter((g) => g.q > Math.max(...r.pad.map((p) => p.q)) + 1e-9).map((g) => `${r.container}: ${g.e}`))

test("no gap exceeds its container's padding, at every density and card depth", () => {
  for (const density of densities) for (const cardDepth of [2, 3, 4, 5, 6]) assert.deepEqual(gapOverruns(ladder({ density, cardDepth })), [], `${density} d ${cardDepth}`)
  const bad = ladder().map((r) => (r.container === 'Card' ? { ...r, gap: [...r.gap, { e: 'mutant', q: 99 }] } : r))
  assert.deepEqual(gapOverruns(bad), ['Card: mutant'], 'negative control: an oversized gap must be reported')
})

test('a control with no inset is its slot, and h/F is 2 to 2.57 with the standard insets', () => {
  assert.deepEqual(densities.map((d) => Math.round((h(d) * q(14) / 14) * 100) / 100), [2, 2.29, 2.57])
  const bare = { ...P, inset: { compact: 0, default: 0.5, loose: 1 }, gutter: 0 }
  const rows = derive({ preset: bare, n: 15, density: 'compact' }), px = (id) => rows.find((r) => r.id === id).px
  assert.deepEqual(checkIdentities(rows), [])
  assert.equal(px('controls.control.h'), px('controls.control.s'))
  assert.equal(px('controls.control.m_c'), 0)
  assert.equal(px('controls.control.t'), 0)
  // Negative control: the standard gutter with no inset puts the margin below zero.
  const bad = derive({ preset: { ...bare, gutter: 0.5 }, n: 15, density: 'compact' })
  assert.ok(bad.find((r) => r.id === 'controls.control.m_c').px < 0)
})

test('the heavy rule is the inset at every density and size, and the hairline does not move', async () => {
  const { derive: dv } = await import('./derive.mjs')
  for (const n of [14, 16, 18]) for (const density of densities) {
    const rows = dv({ n, density }), px = (id) => rows.find((r) => r.id === id).px
    close(px('controls.border.heavy-rule'), px('controls.control.i')); close(px('unit.border.b'), 1)
  }
  // Negative control: it is not a multiple of the hairline: it changes with density while b does not.
  const at = (density) => dv({ n: 14, density }).find((r) => r.id === 'controls.border.heavy-rule').px
  assert.notEqual(at('compact'), at('loose'))
})

test('a stepped page margin: the standard preset gives one M at every width; three levels give 2I, 4I and 8I either side of each step, with G unchanged', async () => {
  const { derive: dv, pageLevel, validatePreset, PRESETS: PR } = await import('./derive.mjs')
  const M = (o) => dv(o).find((r) => r.id === 'layout.grid.m').px, Gt = (o) => dv(o).find((r) => r.id === 'layout.grid.g').px
  for (const width of [undefined, 390, 800, 1440]) close(M({ n: 16, density: 'loose', width, columns: 4 }), M({ n: 16, density: 'loose' }))
  const P3 = { ...PR.standard, levels: { ...PR.standard.levels, page: { narrow: 2, base: 4, wide: 8 } } }, I = dv({ preset: P3, n: 16, density: 'loose' }).find((r) => r.id === 'controls.control.i').px
  for (const [width, l] of [[390, 2], [599, 2], [600, 4], [999, 4], [1000, 8], [1440, 8], [undefined, 4]]) { close(M({ preset: P3, n: 16, density: 'loose', width, columns: 4 }), l * I); close(Gt({ preset: P3, n: 16, density: 'loose', width, columns: 4 }), 2 * I); assert.equal(pageLevel(P3, width), l) }
  for (const width of [390, 1440]) assert.deepEqual(checkIdentities(dv({ preset: P3, n: 16, density: 'loose', width, columns: 4 })), [], `identities at ${width}`)
  // Negative controls: a malformed level or step is refused, with the reason.
  assert.throws(() => validatePreset({ levels: { page: { narrow: 2, wide: 8 } } }), /levels\.page is a number, or \{ narrow, base, wide \}/)
  assert.throws(() => validatePreset({ marginSteps: [1000, 600] }), /marginSteps is two page widths in px, the smaller first/)
  assert.throws(() => validatePreset({ marginSteps: [600] }), /marginSteps/)
})

test("rhythm 'line' puts text lines, gaps, control boxes and rows on half of the body line; a heading keeps its own line; the default prints nothing", async () => {
  const { lineGrid } = await import('./derive.mjs'), { applyArchetype } = await import('./archetypes.mjs')
  // The default preset has no rhythm rows, and its other rows are unchanged by the setting's existence (negative control).
  assert.equal(derive({}).filter((r) => r.group === 'rhythm').length, 0)
  const plain = derive({ n: 16 }), lined = derive({ preset: { ...P, rhythm: 'line' }, n: 16 })
  assert.deepEqual(lined.filter((r) => r.group !== 'rhythm').map((r) => [r.id, r.px]), plain.map((r) => [r.id, r.px]))
  // The module: an even px that divides by 4. 20 at n 14, 24 at n 16 (23.5 by the formula), 36 for running text of 35.25.
  assert.deepEqual([20, 23.5, 35.25, 18, 21].map((b) => lineGrid({ bodyLine: b }).L), [20, 24, 36, 20, 24])
  for (const name of ['product', 'civic', 'editorial', 'calm', 'marketing']) {
    const rows = derive(applyArchetype(name)).filter((r) => r.group === 'rhythm'), px = (sym) => rows.find((r) => r.symbol === sym).px, L = px('L'), half = px('half-line')
    assert.equal(half, L / 2); assert.equal(L % 4, 0, `${name}: L ${L}`)
    for (const r of rows.filter((x) => / line on the grid$/.test(x.symbol))) {
      const padded = /padded/.test(r.expr); assert.ok(Number.isInteger(r.px), `${name}: ${r.symbol} ${r.px}`)
      if (!padded) assert.ok(Math.abs(r.px / half - Math.round(r.px / half)) < 1e-9, `${name}: ${r.symbol} ${r.px} is not a half-line multiple`)
    }
    for (const sym of ['gap floor', 'control box', 'row on the grid', 'around a field group']) assert.ok(Math.abs(px(sym) / half - Math.round(px(sym) / half)) < 1e-9, `${name}: ${sym}`)
    assert.ok(px('control box') >= derive(applyArchetype(name)).find((r) => r.id === 'controls.control.h').px)
  }
  // What was drawn: product rows of 40 in place of 32, civic boxes of 48 for 40; civic's heading 41px (36 × 1.15) where the formula gives 43.5; editorial's module is its running text.
  const v = (name, sym) => derive(applyArchetype(name)).find((r) => r.group === 'rhythm' && r.symbol === sym).px
  assert.equal(v('product', 'row on the grid'), 40); assert.equal(v('civic', 'control box'), 48); assert.equal(v('civic', 'heading-lg line on the grid'), 41); assert.equal(v('civic', 'around a field group'), 24)
  // The floor of 1.15 (1.3 was tried and dropped): product's 17px title stays on the 20px body line; civic's 19.75px title takes 24px. Toy was kept off the grid.
  assert.equal(v('product', 'title-lg line on the grid'), 20); assert.equal(v('product', 'body-sm line on the grid'), 20); assert.equal(v('civic', 'title-lg line on the grid'), 24); assert.equal(v('calm', 'L'), 28); assert.equal(v('marketing', 'control box'), 56)
  assert.equal(derive(applyArchetype('toy')).filter((r) => r.group === 'rhythm').length, 0)
  assert.equal(v('editorial', 'L'), 36); assert.equal(v('editorial', 'heading-sm line on the grid'), 36); assert.equal(v('editorial', 'body-md line on the grid'), 24)
  assert.throws(() => validatePreset({ rhythm: 'baseline' }), /rhythm is 'formula' or 'line'/)
})

test('a field with its help and its own actions is one group: g_c inside, the gap between groups around it, never under three times the inside', () => {
  for (const density of densities) for (const n of [13, 14, 16, 18]) { const rows = derive({ n, density }), px = (sym) => rows.find((r) => r.symbol === sym).px
    assert.ok(px('around a field group') >= 3 * px('label → control, control → help') - 1e-9, `n ${n} ${density}`); assert.equal(px('around a field group'), Math.max(px('groups in card-4'), 3 * px('label → control, control → help'))) }
})
