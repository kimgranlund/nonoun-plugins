// Generated from ui-geometry/scripts/derive.mjs by scripts/build.mjs; run npm run build, do not edit.
// UI geometry calculator. Self-contained: a preset holds every constant, the equations are generic.
//   node derive.mjs --n 16 --density loose --kappa 0.5 [--kappa-card 1] [--card 4] [--width 1280 --columns 12]
//                   [--preset massimo | --preset ./my-preset.json] [--json]
//   node derive.mjs --elevation popup|raised|floating|modal|all|<s> [--layers 5] [--scheme light|dark] [--n 14]
//   node derive.mjs --viewport 1024 [--dpr 2]   (n from the fluid scale; lengths off the device grid are listed)
//   node derive.mjs --tier controls|collections|containers|layout   (one tier, with the shared unit)
//   node derive.mjs --containers [--card 4 --popover 3 --dialog 6 --nest 0.5]   (padding, gap, radius for every container; popover and dialog default to ¾d and 1½d)
// Prints every length of a scope as a multiple of the unit q and in px.


/** A preset is the whole parameter set. Every length in it is in q. */
export const PRESETS = {
  massimo: {
    unit: { a: 0.5, b: -3, nMin: 12 },          // q = a·n + b px
    inset: { compact: 1, default: 1.5, loose: 2 }, // I by density
    gutter: 0.5,                                  // g_c, fixed
    slot: 5,                                      // S
    softAnchor: 0.75,                             // κ at which r = soft
    soft: 3,                                      // r at the soft anchor
    frameDepth: 0.75,                             // d_c, the padding of menus, listboxes and segmented hosts: a number in q, 'g_c' or 'm_c'
    frameRow: 'fit',                              // their items: 'fit' (h − 2d_c, so one item plus its padding is h), 'm_c' (S + 2m_c), 'h_o' (S + 2g_c) or 'h'
    cardDepths: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    nest: [0, 0.25, 0.5, 0.75, 1],
    levels: { composite: 0.5, group: 1, collection: 2, panel: 2, region: 4, page: 4 },  // region band 2I, page section 4I, page margin M = 4I
    levelGutterCap: 2,
    columnMin: 40,
    icons: { sm: 'F', md: 4, lg: 4.5, full: 5 },   // sm is tethered to the text size F = n; md and lg sit on the q ladder; full = S
    marks: { checkRadius: 1, switchWidth: 7, badgeDot: 2 },  // box = icon md; switch height = icon md
    tracks: { track: 1, meter: 2, sliderMin: 10 },
    widths: { tooltip: 60, popover: 80, dialog: 120, rail: 56, panel: 72, measure: 160 },
    viewportMargin: 4,
    elevation: {
      ey: 1,            // e.y: the key offset, in q, at level scale 1
      ratio: 2,         // ρ: each layer's offset is ρ times the one before
      anchor: 2,        // k_a: the layer whose offset is e.y·s
      blur: 2,          // β: blur = β · offset
      spread: 0,        // σ: spread = −σ · offset (tightens the penumbra under the surface)
      angle: 0,         // θ in degrees from vertical: x = y · tan θ
      layers: 4,        // L
      decay: 0.75,      // λ: each layer's alpha is λ times the one before
      budget: { light: 0.19, dark: 0.45 },  // B: the alphas sum to this, whatever the level
      levels: { raised: 0.5, popup: 1, floating: 1.5, modal: 2 },  // s
    },
    focus: { width: 0.5, offset: 0.5 },             // ring w and offset o, in q
    targets: { pointer: 24, touch: 44 },            // minimum hit target T, in px (an accessibility floor, not a multiple of q)
    border: { width: 1 },                            // b, in device-independent px
    font: { ascent: 0.96875, descent: 0.2421875, cap: 0.727, charWidth: 0.5 },  // em fractions (Inter-like)
    fluid: { w1: 360, n1: 14, w2: 1440, n2: 16, step: 2 },  // n(W): linear, clamped, rounded to step (2 keeps q whole; 0 = continuous)
    measure: { min: 45, ideal: 66, max: 75 },        // characters per line
    aspects: { square: [1, 1], photo: [4, 3], classic: [3, 2], video: [16, 9], cinema: [21, 9] },
    avatars: { xs: 4, sm: 5, md: 6, lg: 8, xl: 10, xxl: 20 },  // a.md, S, h_o, h, 2S, 4S
    iconStroke: { ratio: 0.09375, min: 1 },          // stroke = max(min px, ratio · a): 1.5px at 16px
    spacing: { popoverRatio: 0.75, dialogRatio: 1.5, nest: 0.5, depthStep: 2 },  // depthStep: card depth moves 2·ΔI per density step (3q / 4q / 5q)  // popover and dialog depths as ratios of the card depth d (snapped to ½q), nest is f
    dials: { kappa: { card: 0.5 } },                  // default κ per tier where it differs from κ_s: cards ½, so R = d + 2q
    type: {
      'display-lg': [12.5, 1], 'display-md': [8.5, 1], 'display-sm': [5.5, 1],
      'heading-lg': [4, 1.5], 'heading-md': [2.5, 1.5], 'heading-sm': [1.5, 1.5],
      'title-lg': [0.75, 1], 'title-md': [0.25, 1], 'title-sm': [0, 1],
      'body-lg': [0.5, 1.5], 'body-md': [0, 1.5], 'body-sm': [-0.25, 1.5],
      label: [-0.5, 1], 'kicker-lg': [0, 0.5], 'kicker-md': [-0.5, 0.5], 'kicker-sm': [-1, 0.5], code: [-0.25, 1.5],
    },
  },
}

/** The system for one preset. Every function returns q unless named px. */
export function system(P = PRESETS.massimo) {
  const q = (n) => P.unit.a * n + P.unit.b
  const I = (dn) => P.inset[dn]
  const mc = (dn) => I(dn) - P.gutter
  const h = (dn) => P.slot + 2 * I(dn)
  const clamp01 = (k) => Math.min(1, Math.max(0, k))
  /** r(κ): (κ/κ_s)·soft on [0, κ_s], then soft → h/2 on [κ_s, 1]. */
  const radius = (kappa, dn) => {
    const k = clamp01(kappa), half = h(dn) / 2, soft = Math.min(P.soft, half), ks = P.softAnchor
    return k <= ks ? (k / ks) * soft : soft + ((k - ks) / (1 - ks)) * (half - soft)
  }
  const capped = (kappa, dn) => Math.min(radius(kappa, dn), P.soft)
  const inward = (r, e) => Math.max(0, r - e)
  const cardRadius = (d, kappa, dn) => (d === 0 ? radius(kappa, dn) : d + capped(kappa, dn))
  const nested = (d, R, f) => [(1 - f) * d, f === 0 ? 0 : inward(R, f * d)]
  /** Frame padding d_c: fixed when the preset gives a number, else m_c, the same inset as a segmented control's host. */
  const dc = (dn) => (typeof P.frameDepth === 'number' ? P.frameDepth : P.frameDepth === 'g_c' ? P.gutter : mc(dn))
  /** An item in a menu, listbox or segmented control: S + 2m_c (one item padded g_c is exactly h), h_o = S + 2g_c, or a full control h. */
  const frameRow = (dn) => (P.frameRow === 'h' ? h(dn) : P.frameRow === 'h_o' ? P.slot + 2 * P.gutter : P.frameRow === 'm_c' ? P.slot + 2 * mc(dn) : h(dn) - 2 * dc(dn))
  /** A segmented host is h tall, so it pads what its items leave: (h − item)/2, which is d_c for 'fit' items. */
  const hostPad = (dn) => (h(dn) - frameRow(dn)) / 2
  const levelInset = (l, dn) => P.levels[l] * I(dn)
  const levelGutter = (l, dn) => Math.min(P.levelGutterCap, levelInset(l, dn))
  return { P, q, I, mc, dc, frameRow, hostPad, h, radius, capped, inward, cardRadius, nested, levelInset, levelGutter }
}

/** Fluid scale: n(W) = clamp(min(n1, n2), n1 + (W − w1)·(n2 − n1)/(w2 − w1), max(n1, n2)). */
export function fluidN(W, preset = PRESETS.massimo) {
  const f = { ...PRESETS.massimo.fluid, ...preset.fluid }
  let n = f.n1 + ((W - f.w1) * (f.n2 - f.n1)) / (f.w2 - f.w1)
  n = Math.min(Math.max(n, Math.min(f.n1, f.n2)), Math.max(f.n1, f.n2))
  const a = f.align ?? 0
  return f.step ? Math.round((n - a) / f.step) * f.step + a : n
}

/** Pixel snapping: a px length lands on the device grid when px·dpr is a whole number. */
export const snap = (px, dpr = 1) => Math.round(px * dpr) / dpr
export const onGrid = (px, dpr = 1) => Math.abs(px * dpr - Math.round(px * dpr)) < 1e-6

/** Optical centring: how far the cap-height centre sits below the line-box centre, in em. 0 = centred. */
export const capOffset = ({ ascent, descent, cap }) => (ascent - descent - cap) / 2

/**
 * Elevation: a stack of L layers. Layer k (0 = contact … L−1 = far halo) at level scale s:
 *   y_k = e.y · s · ρ^(k − k_a),  blur_k = β·y_k,  spread_k = −σ·y_k,  x_k = y_k·tan θ   (lengths, in q)
 *   α_k = B · (1 − λ)·λ^k / (1 − λ^L)                                                   (alpha, independent of s)
 * The level scales the lengths, never the alpha: a higher surface casts a wider halo, not a darker one.
 * Returns the layers and the composite alpha where all of them overlap, 1 − Π(1 − α_k).
 */
export function elevation({ preset = PRESETS.massimo, level = 'popup', layers, scheme = 'light', round = false } = {}) {
  const E = { ...PRESETS.massimo.elevation, ...preset.elevation }
  const s = typeof level === 'number' ? level : E.levels[level]
  if (!(s > 0)) throw new Error(`unknown elevation level ${level}`)
  const L = layers ?? E.layers, B = E.budget[scheme], lam = E.decay
  const tan = Math.tan((E.angle * Math.PI) / 180)
  const norm = lam === 1 ? 1 / L : (1 - lam) / (1 - lam ** L)
  const out = []
  for (let k = 0; k < L; k++) {
    const y = E.ey * s * E.ratio ** (k - E.anchor)
    let alpha = B * norm * lam ** k
    if (round) alpha = Math.round(alpha * 100) / 100
    out.push({ k, x: y * tan, y, blur: E.blur * y, spread: -E.spread * y, alpha })
  }
  const composite = 1 - out.reduce((p, l) => p * (1 - l.alpha), 1)
  return { level, s, scheme, layers: out, composite }
}

/**
 * The four tiers. Each owns its constants and reads only the values named in TIER_READS from the tier below.
 * `unit` is not a tier: F, q, the type scale and text metrics are shared inputs.
 */
export const TIERS = ['controls', 'collections', 'containers', 'layout']
export const TIER_READS = {
  controls: [],
  collections: ['h', 'r(κ) via κ_frame'],
  containers: ['r(κ) via κ_card', 'the content edge'],
  layout: ['minimum card width'],
}

/** q for a tier: a preset may give a tier its own unit in `units`; otherwise every tier uses `unit`. */
export function tierUnit(P, tier, n) {
  const U = (P.units && P.units[tier]) || P.unit
  return U.a * n + U.b
}

/** Round half to even, so 2.5 → 2 and 7.5 → 8. */
const roundEven = (x) => { const r = Math.round(x); return Math.abs((x % 1) - 0.5) < 1e-9 ? 2 * Math.round(x / 2) : r }

/**
 * A crisp preset at n: the insets I and the gutter g_c snap to whole px (round half to even) and the slot S to even px,
 * so every length built from them lands on the pixel grid even where q is odd (at 16px: S = 24, I = 8, g_c = 2, h = 40).
 * Set `crisp: false` to keep exact q.
 */
export function crisp(P0, n) {
  const u = P0.unit.a * n + P0.unit.b
  if (!(u > 0)) return P0
  // Tethered values resolve at n: an icon size of 'F' is the text size, n px.
  const P = { ...P0, icons: Object.fromEntries(Object.entries(P0.icons).map(([k, v]) => [k, v === 'F' ? n / u : v])) }
  if (P.crisp === false) return P
  const snapQ = (x) => roundEven(x * u) / u
  // The slot snaps to an even px count, so an icon centres on whole px and h = S + 2I stays even (40 at 16px, not 41).
  const slot = (2 * roundEven((P.slot * u) / 2)) / u
  // Icon sizes snap to even px, so each glyph centres in the slot with a whole-px margin (S − a)/2.
  const even = (x) => (2 * roundEven((x * u) / 2)) / u
  const fd = typeof P.frameDepth === 'number' ? snapQ(P.frameDepth) : P.frameDepth
  return { ...P, frameDepth: fd, slot, icons: Object.fromEntries(Object.entries(P.icons).map(([k, v]) => [k, k === 'full' ? slot : P0.icons[k] === 'F' ? v : even(v)])), inset: Object.fromEntries(Object.entries(P.inset).map(([k, v]) => [k, snapQ(v)])), gutter: snapQ(P.gutter) }
}

export function derive({ preset = PRESETS.massimo, n = 14, density = 'default', kappa = {}, width, columns, cardDepth = 4, tier: only } = {}) {
  const P = crisp(preset, n), X = system(P)
  const ks = P.softAnchor
  const k = { control: ks, frame: ks, card: ks, panel: ks, ...P.dials?.kappa, ...kappa }
  const u = X.q(n), rows = []
  const uT = (t) => (t === 'unit' ? u : tierUnit(P, t, n))
  let T = 'unit'
  /** A value of tier `src`, expressed in the current tier's q (identity when both share a unit). */
  const from = (src, v) => (v * uT(src)) / uT(T)
  const add = (group, symbol, expr, inQ, count = false) => rows.push({ tier: T, group, symbol, expr, q: inQ, px: count ? NaN : inQ * uT(T) })
  const i = X.I(density), d = cardDepth, S = P.slot, gc = P.gutter, dc = X.dc(density)
  const dcExpr = typeof P.frameDepth === 'number' ? `${P.frameDepth}` : P.frameDepth === 'g_c' ? 'g_c' : 'm_c = I − g_c'

  // unit: shared inputs
  add('scale', 'F', 'n', n / u)
  add('scale', 'q', `${P.unit.a}·n ${P.unit.b < 0 ? '−' : '+'} ${Math.abs(P.unit.b)}`, 1)
  for (const t of TIERS) if (P.units && P.units[t]) add('scale', `q_${t}`, `${P.units[t].a}·n ${P.units[t].b < 0 ? '−' : '+'} ${Math.abs(P.units[t].b)} (own unit)`, uT(t) / u)
  for (const [id, [m, kk]] of Object.entries(P.type)) {
    add('type', id, `F + ${m}q`, n / u + m)
    add('type', `${id} line`, `size + ${kk}q`, n / u + m + kk)
  }
  const b = ({ ...PRESETS.massimo.border, ...P.border }).width / u
  add('border', 'b', `${b * u}px`, b)
  const fm = { ...PRESETS.massimo.font, ...P.font }, Fq = n / u
  add('text', 'cap offset', '(ascent − descent − cap)/2 · F (+ = cap centre below line centre)', capOffset(fm) * Fq)
  add('text', 'label line box in S', 'S − (F + q): half-leading room in the slot', S - (Fq + 1))
  for (const [id, [m, kk]] of Object.entries(P.type)) {
    const lh = Fq + m + kk, rem = ((lh % 1) + 1) % 1
    if (rem > 1e-6) add('text', `${id} off the q grid by`, 'line height mod q', rem)
  }

  // Tier 1, controls: buttons, inputs, menus' items, widgets, marks
  T = 'controls'
  add('control', 'I', 'by density', i)
  add('control', 'm_c', 'I − g_c', X.mc(density))
  add('control', 'g_c', `${gc}`, gc)
  add('control', 'S', `${S}`, S)
  add('control', 'h', 'S + 2I', X.h(density))
  add('control', 'h_o', 'S + 2g_c', S + 2 * gc)
  add('control', 'B', 'h + 2', X.h(density) + 2)
  add('control', 'T', '2I', 2 * i)
  add('control', 'D', 'I/2', i / 2)
  for (const [t, a] of Object.entries(P.icons)) {
    add('icon', `a.${t}`, `${a}`, a)
    add('icon', `a.${t} offset`, 'I + (S − a)/2', i + (S - a) / 2)
  }
  add('icon', 'label after icon', '2I + S', 2 * i + S)
  add('icon', 'padding at a text edge', 'T = 2I', 2 * i)
  add('icon', 'padding at an icon edge', 'I', i)
  add('icon', 'icon box ↔ label', 'I (flex gap; no wrapper, no collapsing margins)', i)
  add('icon', 'icon-only', 'h × h', X.h(density))
  const st = { ...PRESETS.massimo.iconStroke, ...P.iconStroke }
  for (const [t, a] of Object.entries(P.icons)) add('icon stroke', `a.${t}`, `max(${st.min}px, ${st.ratio}·a)`, Math.max(st.min / uT(T), st.ratio * a))

  const md = P.icons.md, mk = P.marks, tr = P.tracks
  add('mark', 'choice row', 'h; the mark is the visible edge and starts on the content edge', X.h(density))
  add('mark', 'choice label', 'a + I + (S − a)/2', md + i + (S - md) / 2)
  add('mark', 'checkbox box', 'a.md', md)
  add('mark', 'checkbox radius', `${mk.checkRadius}`, mk.checkRadius)
  add('mark', 'radio box', 'a.md, round', md)
  add('mark', 'radio dot', 'a.md / 2', md / 2)
  add('mark', 'switch track', `${mk.switchWidth} × a.md, round`, mk.switchWidth)
  add('mark', 'switch thumb', 'a.md − 2g_c', md - 2 * gc)
  add('mark', 'badge', 'S', S)
  add('mark', 'badge dot', `${mk.badgeDot}`, mk.badgeDot)
  add('mark', 'separator', 'hairline, g_c above and below', gc)
  add('mark', 'tree indent', 'S per level', S)
  add('track', 'progress / slider track', `${tr.track}`, tr.track)
  add('track', 'meter track', `${tr.meter}`, tr.meter)
  add('track', 'slider hit area', 'S', S)
  add('track', 'slider thumb', 'a.md, round', md)
  add('track', 'slider minimum length', `${tr.sliderMin}`, tr.sliderMin)

  const r = X.radius(k.control, density)
  add('curvature', `r  κ=${k.control}`, 'r(κ)', r)
  add('curvature', 'r_o', 'r − m_c', X.inward(r, X.mc(density)))
  add('curvature', 'r_s', 'r − I', X.inward(r, i))
  add('border', 'control inner radius', 'r − b', Math.max(0, r - b * u / uT(T)))

  const F = { ...PRESETS.massimo.focus, ...P.focus }
  add('focus', 'ring width w', `${F.width}`, F.width)
  add('focus', 'ring offset o', `${F.offset}`, F.offset)
  add('focus', 'ring outer radius', 'r + o + w', r + F.offset + F.width)
  add('focus', 'ring centre radius', 'r + o + w/2', r + F.offset + F.width / 2)
  add('focus', 'clearance needed', 'o + w (each side; ≤ the gap to a neighbour)', F.offset + F.width)
  add('focus', 'inset ring radius (hosted option)', 'r_o − w/2, drawn inside', Math.max(0, X.inward(r, X.mc(density)) - F.width / 2))

  const Tg = { ...PRESETS.massimo.targets, ...P.targets }
  for (const [mode, Tpx] of Object.entries(Tg)) {
    const Tq = Tpx / uT(T)
    add('target', `T ${mode}`, `${Tpx}px`, Tq)
    add('target', `expansion of h (${mode})`, 'max(0, (T − h)/2) each side', Math.max(0, (Tq - X.h(density)) / 2))
    add('target', `expansion of h_o (${mode})`, 'max(0, (T − h_o)/2) each side', Math.max(0, (Tq - (S + 2 * gc)) / 2))
    add('target', `minimum I for h to meet T (${mode})`, '(T − S)/2', (Tq - S) / 2)
  }
  for (const [name, sz] of Object.entries(P.avatars ?? PRESETS.massimo.avatars)) {
    add('media', `avatar ${name}`, `${sz}`, sz)
    add('media', `avatar ${name} radius`, `r(κ_control) at size ${sz}: min(r(κ)·size/h, size/2)`, Math.min(r * (sz / X.h(density)), sz / 2))
  }
  add('media', 'avatar in slot radius', 'r − I (concentric with the control)', X.inward(r, i))
  add('gap', 'joined', '0', 0)
  add('gap', 'seam', 'g_c each side', gc)
  add('gap', 'hosted', 'm_c', X.mc(density))
  add('gap', 'grouped', `min(${P.levelGutterCap}, I)`, X.levelGutter('group', density))

  // Tier 2, collections: listboxes, menus, segmented controls, lists, tables, toolbars. Reads h and r(κ) from controls.
  T = 'collections'
  const hC = from('controls', X.h(density))
  add('rows', 'row', 'h (read from controls)', hC)
  add('rows', 'cell inline padding', 'I', from('controls', i))
  add('rows', 'cell label', '≥ S, one line', from('controls', S))
  add('rows', 'control in a table cell', 'item S + 2m_c, inset (h − item)/2', from('controls', X.frameRow(density)))
  add('rows', 'edge cell of a flush table or list', 'the parent depth (d in a card, M on a page)', d)
  add('rows', 'segment, tab', 'the item height, inside an h-tall host', from('controls', X.frameRow(density)))
  const rowExpr = P.frameRow === 'h' ? 'h' : P.frameRow === 'h_o' ? 'h_o = S + 2g_c' : P.frameRow === 'm_c' ? 'S + 2m_c' : 'h − 2d_c'
  add('rows', 'menu row', `${rowExpr} (one row + 2d_c = h)`, from('controls', X.frameRow(density)))
  add('frame', 'd_c', dcExpr, from('controls', dc))
  add('gap', 'popup offset from its trigger', 'd_c (the gap matches the padding inside the popup)', from('controls', dc))
  add('frame', 'host pad', '(h − item)/2', from('controls', X.hostPad(density)))
  const rf = Math.min(from('controls', X.radius(k.frame, density)), P.soft)
  add('curvature', `r_frame  κ=${k.frame}`, 'min(r(κ), soft)', rf)
  add('curvature', 'r_row', 'r_frame − d_c', X.inward(rf, from('controls', dc)))
  for (const w of ['tooltip', 'popover']) if (P.widths[w] !== undefined) add('width', w, `${P.widths[w]}`, P.widths[w])

  // Tier 3, containers: cards, dialogs, panels, sheets. Reads r(κ_card) from controls and the content edge.
  T = 'containers'
  const rc = Math.min(from('controls', X.radius(k.card, density)), P.soft)
  const cardR = (c) => (c === 0 ? from('controls', X.radius(k.card, density)) : c + rc)
  for (const c of P.cardDepths) add('curvature', `R card-${c}  κ=${k.card}`, c === 0 ? 'r(κ)' : 'd + min(r(κ), soft)', cardR(c))
  const R = cardR(d)
  for (const f of P.nest) {
    const [dd, rr] = X.nested(d, R, f)
    add('curvature', `nest f=${f} in card-${d}`, 'R − f·d', rr)
    add('frame', `nest f=${f} depth`, '(1 − f)·d', dd)
  }
  // A panel of controls is a card at depth 2I.
  add('curvature', `R panel (card at 2I)  κ=${k.card}`, '2I + min(r(κ_card), soft)', from('controls', 2 * i) + rc)
  for (const [l, v] of Object.entries(P.levels)) add('frame', `${l} inset`, `${v}·I`, from('controls', X.levelInset(l, density)))
  // Card depth follows density: d_δ = d + depthStep·(I_δ − I_default). The gaps below use it.
  { const de = d + ({ ...PRESETS.massimo.spacing, ...P.spacing }.depthStep) * (i - X.I('default'))
  if (Math.abs(de - d) > 1e-9) add('frame', `card-${d} at ${density}`, 'd + depthStep·(I − I_default)', de) }
  // Inside a container the gap is half its depth; the gap under a title row gives back the row's inset I (optical);
  // the gap before an action row is the full depth. Every gap snaps to ½q.
  // Three label levels, three gaps: groups in a card sit d apart, blocks inside a group d/2, a group caption I above its
  // content, a field label g_c above its control.
  add('gap', `groups in card-${d}`, 'd', d)
  add('gap', `blocks in a group, card-${d}`, 'd/2', d / 2)
  add('gap', 'group caption → content', 'I', i)
  add('gap', `title → content card-${d}`, 'max(0, d/2 − I)', Math.max(0, d / 2 - i))
  add('gap', `separate rows card-${d}`, 'd/4, snapped to ½q', Math.round(d / 2) / 2)
  add('gap', `before actions card-${d}`, 'd', d)
  // Fields sit 2I apart, as table columns do; label and help text sit g_c from the control.
  add('gap', 'between form fields', '2I (as table columns)', 2 * i)
  add('gap', 'label → control, control → help', 'g_c', from('controls', gc))
  add('border', `card-${d} inner padding`, 'd − b', d - b * u / uT(T))
  add('border', `card-${d} inner radius`, 'R − b', Math.max(0, R - b * u / uT(T)))
  for (const w of ['dialog', 'panel', 'rail']) if (P.widths[w] !== undefined) add('width', w, `${P.widths[w]}`, P.widths[w])
  const base = 40
  for (const [name, [aw, ah]] of Object.entries(P.aspects ?? PRESETS.massimo.aspects)) add('media', `${name} ${aw}:${ah} height at w = ${base}`, `w · ${ah}/${aw}`, (base * ah) / aw)

  // Tier 4, layout: pages, grids, regions. Reads the minimum card width.
  T = 'layout'
  // The page follows the container rule: the gutter between columns and cards is half the margin, snapped to ½q.
  const M = P.levels.page * from('controls', i), G = Math.round(M) / 2
  add('grid', 'M', `${P.levels.page}I`, M)
  add('grid', 'G', 'M/2, snapped to ½q', G)
  add('gap', 'card', 'G', G)
  add('width', 'viewport margin', `${P.viewportMargin}`, P.viewportMargin)
  if (P.widths.measure !== undefined) add('width', 'measure', `${P.widths.measure}`, P.widths.measure)
  if (width && columns) {
    const W = width / uT(T)
    add('grid', `w  W=${width}px N=${columns}`, '(W − 2M − (N−1)G)/N', (W - 2 * M - (columns - 1) * G) / columns)
    add('grid', 'N_max', `⌊(W − 2M + G)/(${P.columnMin} + G)⌋`, Math.floor((W - 2 * M + G) / (P.columnMin + G)), true)
  }
  for (let kc = 1; kc <= 6; kc++) add('breakpoint', `${kc} column${kc > 1 ? 's' : ''}`, `k·w_min + (k − 1)G + 2M, w_min ${P.columnMin}`, kc * P.columnMin + (kc - 1) * G + 2 * M)
  const Ms = { ...PRESETS.massimo.measure, ...P.measure }
  for (const [kname, c] of Object.entries(Ms)) add('measure', `${kname} (${c} ch)`, 'c · charWidth · F', (c * fm.charWidth * n) / uT(T))

  return only ? rows.filter((x) => x.tier === only || (only !== 'unit' && x.tier === 'unit' && x.group === 'scale')) : rows
}

/**
 * The container spacing ladder: padding, gap, radius and height for every container, inside out.
 * Each cell is a list of { e: expression, q }. Every gap is half its container's padding, the full padding before
 * actions, g_c, 0, or the item inset. Card depth follows density; insets, gutter and gaps land on whole px (crisp).
 */
export function containers({ preset = PRESETS.massimo, n = 14, density = 'default', kappa = {}, cardDepth = 4, popoverDepth, dialogDepth, nest } = {}) {
  const P = crisp(preset, n), X = system(P), u = X.q(n)
  const sp = { ...PRESETS.massimo.spacing, ...P.spacing }
  const half = (x) => Math.round(x * 2) / 2, f = nest ?? sp.nest
  // Lengths that are not built from I or g_c (depths, gaps) snap to whole px when crisp, else to ½q.
  const snap = (x) => (P.crisp === false ? half(x) : roundEven(x * u) / u)
  const ks = P.softAnchor, k = { control: ks, frame: ks, card: ks, panel: ks, ...P.dials?.kappa, ...kappa }
  const I = X.I(density), gc = P.gutter, mc = X.mc(density), S = P.slot, h = X.h(density), ho = S + 2 * gc, a = P.icons.md
  // Card depth moves with density, one q per step in massimo: d_δ = d + depthStep·(I_δ − I_default).
  const d = snap(cardDepth + sp.depthStep * (I - X.I('default')))
  const dp = popoverDepth ?? snap(sp.popoverRatio * d), dd = dialogDepth ?? snap(sp.dialogRatio * d)
  const r = X.radius(k.control, density), ro = X.inward(r, mc)
  const dcq = X.dc(density), rf = Math.min(X.radius(k.frame, density), P.soft), rrow = X.inward(rf, dcq)
  const rk = Math.min(X.radius(k.card, density), P.soft), R = (x) => (x === 0 ? X.radius(k.card, density) : x + rk)
  const lvl = (l) => Math.min(P.levelGutterCap, l * I), L = P.levels
  const off = I + (S - a) / 2, nd = snap((1 - f) * d), nR = f === 0 ? 0 : X.inward(R(d), d - nd)
  const c = (e, q) => ({ e, q })
  const row = (tier, container, members, pad, gap, radius, height) => ({ tier, container, members, pad, gap, radius, height })
  return [
    // No wrappers: padding follows what sits at each edge (text 2I, icon I); an icon owns an S-square box with its glyph a
    // centred, a margin of (S − a)/2; icon and label are I apart. Glyph at I + (S − a)/2, label after an icon at 2I + S.
    row('controls', 'Button, input, select', 'padding by edge: text 2I, icon I; icon box S; label is a bare text node', [c('block I', I), c('text edge T = 2I', 2 * I), c('icon edge I', I)], [c('icon box ↔ label I', I), c('glyph margin (S − a)/2', (S - a) / 2)], [c('r(κ)', r)], [c('h = S + 2I', h), c('icon box S', S)]),
    row('controls', 'Icon button', 'square control: icon edge on both sides; any icon size centres in the S box', [c('icon edge I', I)], [c('glyph margin (S − a)/2, a.md', (S - a) / 2), ...['sm', 'lg', 'full'].filter((t) => P.icons[t] !== undefined).map((t) => c(`a.${t}`, (S - P.icons[t]) / 2))], [c('r', r)], [c('h × h = I + S + I', h)]),
    // One left edge: an unframed choice row (checkbox, radio, switch) has no shape around it, so its mark is the visible edge
    // and starts on the content edge, with headings, captions and shapes. The label follows at I + (S − a)/2.
    row('controls', 'Choice row', 'checkbox, radio, switch: the mark is the visible edge and starts on the content edge', [c('to the mark: 0, on the content edge', 0), c('to a switch track: 0', 0)], [c('mark ↔ label I + (S − a)/2', I + (S - a) / 2)], [c('checkbox r_mark, radio round', P.marks.checkRadius)], [c('row h', h), c('mark a', a)]),
    row('controls', 'Inline control', 'chip, tag: standalone, shorter than a control', [c('g_c', gc), c('I', I)], [], [c('r_o = r − m_c', ro)], [c('h_o = S + 2g_c', ho)]),
    // A button inside an input (clear, reveal, a stepper, an addon) is an item in a host: it takes the item height and inset.
    row('controls', 'Hosted control', 'a button inside an input: an item in a host', [c('inset (h − item)/2 = d_c', X.hostPad(density))], [c('0, or g_c between two', 0)], [c('r − d_c', X.inward(r, X.hostPad(density)))], [c('item h − 2d_c', X.frameRow(density))]),
    row('controls', 'Control row', 'form actions, toolbar of separate buttons', [c('0', 0)], [c('min(cap, I)', lvl(1))], [c('r each', r)], [c('h', h)]),
    row('controls', 'Joined controls', 'button group, split button', [c('0', 0)], [c('0, shared edge', 0)], [c('r outside, 0 inside', r)], [c('h', h)]),
    // Segments and menu rows share the item height (S + 2m_c by default); the h-tall host pads what is left, (h − item)/2 = g_c.
    row('collections', 'Segmented control, tab list', 'a host of joined controls', [c('(h − item)/2 = d_c', X.hostPad(density))], [c('0', 0)], [c('host r', r), c('segment r − d_c', X.inward(r, X.hostPad(density)))], [c('host h', h), c('segment h − 2d_c', X.frameRow(density))]),
    row('collections', 'Listbox, menu, select popup', 'a frame of rows', [c(typeof P.frameDepth === 'number' ? 'd_c' : `d_c = ${P.frameDepth}`, dcq), c('rows: T − d_c inline, text at T = 2I', 2 * I - dcq)], [c('rows 0', 0), c('separator g_c each side', gc), c('popup offset from its trigger d_c', dcq)], [c('r_f = min(r, soft)', rf), c('rows r_f − d_c', rrow)], [c(P.frameRow === 'h' ? 'rows h' : P.frameRow === 'h_o' ? 'rows h_o = S + 2g_c' : P.frameRow === 'm_c' ? 'rows S + 2m_c' : 'rows h − 2d_c', X.frameRow(density))]),
    // Lists and tables take the control radius r on their outline (rows clip to it) and use the control's insets: they share the content edge with buttons and inputs, and
    // their edge cells pad T = 2I, so cell text lines up with a button label above or below. Hairlines sit inside the row.
    row('collections', 'List, flush', 'rows with hairlines in an r-rounded outline; multi-line rows pad I above and below', [c('0, on the content edge', 0), c('text at T = 2I, as a button label', 2 * I)], [c('0, hairline inside the row', 0)], [c('outline r, as a button; rows clip', r)], [c('rows h', h)]),
    // A table row is a host: a control in a cell takes the item height and sits (h − item)/2 = g_c from the row edges.
    row('collections', 'Table', 'r-rounded outline; header and data rows; may run its own density', [c('0, on the content edge', 0), c('cells I each side', I), c('edge cells T = 2I, as a button label', 2 * I)], [c('columns 2I', 2 * I), c('rows 0, hairline inside the row', 0)], [c('outline r, as a button; rows clip', r)], [c('rows and header h', h), c('control in a cell: item S + 2m_c', X.frameRow(density)), c('its inset (h − item)/2', X.hostPad(density))]),
    // An inset list (navigation, selectable list): an r-rounded outline, rows h tall (a button's height) in a g_c inset with a
    // concentric selection (r − g_c), and text at T = 2I from the list edge, where a button's label sits.
    row('collections', 'List, inset', 'navigation, selectable list: text at a button label inset', [c('d_c', dcq), c('items: T − d_c inline, text at T = 2I', 2 * I - dcq)], [c('0, selection is a fill', 0)], [c('outline r', r), c('selection r − d_c', X.inward(r, dcq))], [c('rows h, as a button', h)]),
    // Fields sit 2I apart, the same gap as table columns (the control system's T); proximity groups each label with its control.
    // A field's control sits on the content edge like any control; its label and help text are inset T, over the value text.
    row('collections', 'Form', 'stacked fields: label, control, help text', [c('control on the content edge', 0), c('label and help at T, over the value', 2 * I)], [c('between fields: 2I, as table columns', 2 * I), c('label → control g_c', gc), c('control → help g_c', gc)], [], [c('fields h', h)]),
    // Containers and layout share one rule: gap = depth / 2; under a title row the gap gives back I; before actions it is the full depth.
    row('containers', 'Popover, tooltip', 'small floating card, d_p = ¾d', [c('d_p', dp)], [c('d_p / 2', snap(dp / 2))], [c('d_p + min(r, soft)', R(dp))], []),
    row('containers', 'Card', `title row h, its text on the content edge d (with captions, loose text and shapes); d = ${cardDepth}q at default, one q per density step; a panel of controls is a card at d = 2I`, [c('d', d)], [c('blocks in a group d / 2', snap(d / 2)), c('title → content max(0, d/2 − I)', snap(Math.max(0, d / 2 - I))), c('rows d / 4', snap(d / 4)), c('before actions d', d), c('groups d', d), c('group caption → content I', I)], [c('R = d + min(r, soft)', R(d))], [c('title row h', h)]),
    row('containers', 'Nested card, well', `a card inside a card, f = ${f}`, [c('(1 − f)·d', nd)], [c('(1 − f)·d / 2', snap(nd / 2))], [c('R − f·d', nR)], []),
    row('containers', 'Dialog, sheet', 'modal card, d_d = 1½d', [c('d_d', dd)], [c('title → body max(0, d_d/2 − I)', snap(Math.max(0, dd / 2 - I))), c('body blocks d_d / 2', snap(dd / 2)), c('before actions d_d', dd)], [c('d_d + min(r, soft)', R(dd))], [c('title row h', h)]),
    row('layout', 'Region', 'sidebar, toolbar band', [c(`${L.panel}·I`, L.panel * I)], [c(`${L.panel}·I / 2`, snap(L.panel * I / 2))], [c('0', 0)], []),
    // A page section shares the page's edge: it pads only above and below, so content never sits 2M in.
    row('layout', 'Page section', 'a block of cards; shares the page edge', [c(`${L.region}·I block`, L.region * I), c('0 inline', 0)], [c(`${L.region}·I / 2`, snap(L.region * I / 2))], [c('0', 0)], []),
    row('layout', 'Page', 'grid of columns', [c(`M = ${L.page}·I`, L.page * I)], [c('G = M / 2', snap(L.page * I / 2))], [c('0', 0)], []),
  ]
}

