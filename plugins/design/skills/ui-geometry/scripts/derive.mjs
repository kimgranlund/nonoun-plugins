#!/usr/bin/env node
// UI geometry calculator. Self-contained: a preset holds every constant, the equations are generic.
//   node derive.mjs --n 16 --density loose --kappa 0.5 [--kappa-card 1] [--card 4] [--width 1280 --columns 12]
//                   [--preset standard | --preset ./my-preset.json] [--json]
//   node derive.mjs --elevation popup|raised|floating|modal|all|<s> [--layers 5] [--scheme light|dark] [--n 14]
//   node derive.mjs --viewport 1024 [--dpr 2]   (n from the fluid scale; lengths off the device grid are listed)
//   node derive.mjs --tier controls|collections|containers|layout   (one tier, with the shared unit)
//   node derive.mjs --containers [--card 4 --popover 3 --dialog 6 --nest 0.5]   (padding, gap, radius for every container; popover and dialog default to ¾d and 1½d)
//   node derive.mjs --field 58 --gutter 2 --width 1440 [--dpr 2] [--max-columns 12]   (a grid for several column counts, in units u)
// Prints every length of a scope as a multiple of the unit q and in px.

import { readFileSync, realpathSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

/** A preset is the whole parameter set. Every length in it is in q. */
export const PRESETS = {
  standard: {
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
    levels: { composite: 0.5, group: 1, collection: 2, panel: 2, page: 4 },  // region band 2I, page margin M = 4I. page may also be { narrow, base, wide }: a margin that steps with the page's width
    marginSteps: [600, 1000],                     // px, not q: the page widths at which a stepped page margin changes from narrow to base and from base to wide
    rhythm: 'formula',                            // 'formula': a role's line is its own s_t + k_t·q; 'line': the body line is a vertical module, and lines, gaps, control boxes and rows are multiples of half of it
    cardRadius: 'concentric',                     // 'concentric': a padded card's corner is d + min(r(κ_card), soft); 'control': every card, nested card and panel takes r(κ_control)
    // The flow of a page, in F (the body size), not q: the gaps between a kicker, a heading, paragraphs, actions and a note, and a page section's padding above and below.
    flow: { kicker: 1, heading: 1.25, paragraph: 1.25, actions: 2.5, note: 1, section: 3.25 },
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
      budget: { light: 0.19, dark: 0.45 },  // B_α: the alphas sum to this, whatever the level
      levels: { raised: 0.5, popup: 1, floating: 1.5, modal: 2 },  // s
    },
    focus: { width: 0.5, offset: 0.5 },             // ring w and offset o, in q
    targets: { pointer: 24, touch: 44 },            // minimum hit target T_hit, in px (an accessibility floor, not a multiple of q)
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
export function system(P = PRESETS.standard) {
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
  /** R = d + min(r(κ), soft); 0 at κ 0, where a square child gives the card no arc to be concentric with. */
  const cardRadius = (d, kappa, dn) => (d === 0 || clamp01(kappa) === 0 ? radius(kappa, dn) : d + capped(kappa, dn))
  const nested = (d, R, f) => [(1 - f) * d, f === 0 ? 0 : inward(R, f * d)]
  /** Frame padding d_c: fixed when the preset gives a number, else m_c, the same inset as a segmented control's host. */
  const dc = (dn) => (typeof P.frameDepth === 'number' ? P.frameDepth : P.frameDepth === 'g_c' ? P.gutter : mc(dn))
  /** An item in a menu, listbox or segmented control: h − 2d_c ('fit', so one item padded d_c is exactly h), S + 2m_c, h_o = S + 2g_c, or a full control h. */
  const frameRow = (dn) => (P.frameRow === 'h' ? h(dn) : P.frameRow === 'h_o' ? P.slot + 2 * P.gutter : P.frameRow === 'm_c' ? P.slot + 2 * mc(dn) : h(dn) - 2 * dc(dn))
  /** A segmented host is h tall, so it pads what its items leave: (h − item)/2, which is d_c for 'fit' items. */
  const hostPad = (dn) => (h(dn) - frameRow(dn)) / 2
  const levelInset = (l, dn) => (l === 'page' ? pageLevel(P) : P.levels[l]) * I(dn)
  const levelGutter = (l, dn) => Math.min(P.levelGutterCap, levelInset(l, dn))
  return { P, q, I, mc, dc, frameRow, hostPad, h, radius, capped, inward, cardRadius, nested, levelInset, levelGutter }
}

/** Fluid scale: n(W) = clamp(min(n1, n2), n1 + (W − w1)·(n2 − n1)/(w2 − w1), max(n1, n2)). */
export function fluidN(W, preset = PRESETS.standard) {
  const f = { ...PRESETS.standard.fluid, ...preset.fluid }
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
export function elevation({ preset = PRESETS.standard, level = 'popup', layers, scheme = 'light', round = false } = {}) {
  const E = { ...PRESETS.standard.elevation, ...preset.elevation }
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

/** The line grid of a preset whose rhythm is 'line': the module L (the body line, or the running text's line under a `text` dial, to an even px that divides by 4), the half-line, and the three roundings. Px. */
export function lineGrid({ bodyLine }) {
  const e = Math.round(bodyLine / 2) * 2, L = e % 4 ? e + 2 : e, half = L / 2
  return { L, half, up: (v) => Math.ceil(v / half - 1e-6) * half, near: (v) => Math.max(half, Math.round(v / half) * half), heading: (size) => Math.round(size * 1.15) }
}

export function derive({ preset = PRESETS.standard, n = 14, density = 'default', kappa = {}, width, columns, cardDepth = 4, tier: only, text } = {}) {
  const P = crisp(preset, n), X = system(P)
  const ks = P.softAnchor
  const k = { control: ks, frame: ks, card: ks, panel: ks, ...P.dials?.kappa, ...kappa }
  const u = X.q(n), rows = []
  const uT = (t) => (t === 'unit' ? u : tierUnit(P, t, n))
  let T = 'unit'
  /** A value of tier `src`, expressed in the current tier's q (identity when both share a unit). */
  const from = (src, v) => (v * uT(src)) / uT(T)
  // id: a stable key per row (tier.group.symbol, slugged), unique in every run; `alias` keeps a symbol's earlier spelling.
  const add = (group, symbol, expr, inQ, count = false, alias) => rows.push({ id: rowId(T, group, symbol), tier: T, group, symbol, ...(alias ? { alias } : {}), expr, q: inQ, px: count ? NaN : inQ * uT(T) })
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
  // rhythm 'line': one vertical module. Text lines, gaps, control boxes and rows are multiples of the half-line; a heading keeps its own line and its block is padded to the grid.
  if ((P.rhythm ?? 'formula') === 'line') {
    const size = (id) => n + P.type[id][0] * u, tr = text ? P.type[text.role] : null
    if (text && !tr) throw new Error(`text.role "${text.role}" is not a type role`)
    const bodyLine = text ? (text.line ?? 1.5) * size(text.role) : size('body-md') + P.type['body-md'][1] * u, g = lineGrid({ bodyLine }), hpx = (S + 2 * i) * uT('controls')
    add('rhythm', 'L', text ? `the ${text.role} line, to an even px that divides by 4` : 'the body-md line, to an even px that divides by 4', g.L / u)
    add('rhythm', 'half-line', 'L/2', g.half / u)
    for (const id of Object.keys(P.type)) { const z = size(id), module = id === (text?.role ?? 'body-md'), head = /^(display|heading)/.test(id) && !module, upv = g.up(z * 1.15), small = !module && !head && upv > 1.8 * z
      add('rhythm', `${id} line on the grid`, module ? 'L' : head ? '1.15 · size, to a px; the block is padded below to the next half-line' : small ? 'small text under a large module: 1.5 · size, to a px; the block is padded below to the next half-line' : 'the next half-line at or above 1.15 · size', (module ? g.L : head ? g.heading(z) : small ? Math.round(z * 1.5) : upv) / u) }
    add('rhythm', 'gap floor', 'a gap is rounded to the half-line and is never under one', g.half / u)
    add('rhythm', 'control box', 'the next half-line at or above h; the control is centred in it', g.up(hpx) / u)
    add('rhythm', 'row on the grid', 'the control box', g.up(hpx) / u)
    add('rhythm', 'inside a field group', 'none beyond the control boxes: (control box − h)/2 above and below each control', (g.up(hpx) - hpx) / 2 / u)
    add('rhythm', 'around a field group', 'L', g.L / u)
  }
  const b = ({ ...PRESETS.standard.border, ...P.border }).width / u
  add('border', 'b', `${b * u}px`, b)
  const fm = { ...PRESETS.standard.font, ...P.font }, Fq = n / u
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
  add('control', 'B', 'h + 2 (title bar)', X.h(density) + 2)
  add('control', 'T', '2I (text edge)', 2 * i)
  add('control', 'D', 'I/2 (composite edge)', i / 2)
  for (const [t, a] of Object.entries(P.icons)) {
    add('icon', `a.${t}`, `${a}`, a)
    add('icon', `a.${t} offset`, 'I + (S − a)/2', i + (S - a) / 2)
  }
  add('icon', 'label after icon', '2I + S', 2 * i + S)
  add('icon', 'padding at a text edge', 'T = 2I', 2 * i)
  add('icon', 'padding at an icon edge', 'I', i)
  add('icon', 'icon box ↔ label', 'I (flex gap; no wrapper, no collapsing margins)', i)
  add('icon', 'icon-only', 'h × h', X.h(density))
  const st = { ...PRESETS.standard.iconStroke, ...P.iconStroke }
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
  add('border', 'heavy rule', 'I', i)   // where a system has a second, heavy rule (a bar beside a note, under a header band), it is the inset wide; every other rule is b

  const F = { ...PRESETS.standard.focus, ...P.focus }
  add('focus', 'ring width w', `${F.width}`, F.width)
  add('focus', 'ring offset o', `${F.offset}`, F.offset)
  add('focus', 'ring outer radius', 'r + o + w', r + F.offset + F.width)
  add('focus', 'ring centre radius', 'r + o + w/2', r + F.offset + F.width / 2)
  add('focus', 'clearance needed', 'o + w (each side; ≤ the gap to a neighbour)', F.offset + F.width)
  add('focus', 'inset ring radius (hosted option)', 'r_o − w/2, drawn inside', Math.max(0, X.inward(r, X.mc(density)) - F.width / 2))

  const Tg = { ...PRESETS.standard.targets, ...P.targets }
  for (const [mode, Tpx] of Object.entries(Tg)) {
    const Tq = Tpx / uT(T)
    add('target', `T_hit ${mode}`, `${Tpx}px`, Tq, false, `T ${mode}`)
    add('target', `expansion of h (${mode})`, 'max(0, (T_hit − h)/2) each side', Math.max(0, (Tq - X.h(density)) / 2))
    add('target', `expansion of h_o (${mode})`, 'max(0, (T_hit − h_o)/2) each side', Math.max(0, (Tq - (S + 2 * gc)) / 2))
    add('target', `minimum I for h to meet T_hit (${mode})`, '(T_hit − S)/2', (Tq - S) / 2, false, `minimum I for h to meet T (${mode})`)
  }
  for (const [name, sz] of Object.entries(P.avatars ?? PRESETS.standard.avatars)) {
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
  const rowExpr = P.frameRow === 'h' ? 'h' : P.frameRow === 'h_o' ? 'h_o = S + 2g_c' : P.frameRow === 'm_c' ? 'S + 2m_c' : 'h − 2d_c'
  add('rows', 'control in a table cell', `item ${rowExpr}, inset (h − item)/2`, from('controls', X.frameRow(density)))
  add('rows', 'edge cell of a flush table or list', 'the parent depth (d in a card, M on a page)', d)
  add('rows', 'segment, tab', 'the item height, inside an h-tall host', from('controls', X.frameRow(density)))
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
  // cardRadius 'control': a card takes the control's corner whatever its padding, so one radius serves controls, tables and cards. A control inside is then not concentric with the corner.
  const flatR = (P.cardRadius ?? 'concentric') === 'control', rCtl = from('controls', X.radius(k.control, density))
  const cardR = (c) => (flatR ? rCtl : c === 0 || rc === 0 ? from('controls', X.radius(k.card, density)) : c + rc)
  for (const c of P.cardDepths) add('curvature', `R card-${c}  κ=${flatR ? k.control : k.card}`, flatR ? 'r(κ_control)' : c === 0 ? 'r(κ)' : rc === 0 ? '0 at κ 0' : 'd + min(r(κ), soft)', cardR(c))
  const R = cardR(d)
  for (const f of P.nest) {
    const [dd, rr] = X.nested(d, R, f)
    add('curvature', `nest f=${f} in card-${d}`, flatR ? 'r(κ_control), 0 when flush' : 'R − f·d', flatR ? (f === 0 ? 0 : rCtl) : rr)
    add('frame', `nest f=${f} depth`, '(1 − f)·d', dd)
  }
  // A panel of controls is a card at depth 2I.
  add('curvature', `R panel (card at 2I)  κ=${flatR ? k.control : k.card}`, flatR ? 'r(κ_control)' : '2I + min(r(κ_card), soft)', flatR ? rCtl : from('controls', 2 * i) + rc)
  for (const [l, v] of Object.entries(P.levels)) add('frame', `${l} inset`, `${typeof v === 'number' ? v : pageLevel(P)}·I`, from('controls', X.levelInset(l, density)))
  // Card depth follows density: d_δ = d + depthStep·(I_δ − I_default). The gaps below use it.
  { const de = d + ({ ...PRESETS.standard.spacing, ...P.spacing }.depthStep) * (i - X.I('default'))
  if (Math.abs(de - d) > 1e-9) add('frame', `card-${d} at ${density}`, 'd + depthStep·(I − I_default)', de) }
  // Inside a container the gap is half its depth; a header (an unpainted title row) is spaced as any child, the full
  // depth below as above, so its text has d + I on both sides; only a painted, flush title band gives back the row's
  // inset I (optical). The gap before an action row is the full depth. Every gap snaps to ½q.
  // Three label levels, three gaps: groups in a card sit d apart, blocks inside a group d/2, a group caption I above its
  // content, a field label g_c above its control.
  add('gap', `groups in card-${d}`, 'd', d)
  add('gap', `blocks in a group, card-${d}`, 'd/2', d / 2)
  add('gap', 'group caption → content', 'I', i)
  add('gap', `header → content card-${d}`, 'd', d)
  add('gap', `band → content card-${d}`, 'max(0, d/2 − I)', Math.max(0, d / 2 - i))
  add('gap', `separate rows card-${d}`, 'd/4, snapped to ½q', Math.round(d / 2) / 2)
  add('gap', `before actions card-${d}`, 'd', d)
  // Fields sit 2I apart, as table columns do; label and help text sit g_c from the control.
  add('gap', 'between form fields', '2I (as table columns)', 2 * i)
  add('gap', 'label → control, control → help', 'g_c', from('controls', gc))
  // A field with its label, help and the actions that submit it alone is one group: g_c inside, the gap between groups around it (never under 3 g_c).
  add('gap', 'around a field group', 'max(d, 3g_c): the gap between groups', Math.max(d, 3 * from('controls', gc)))
  add('border', `card-${d} inner padding`, 'd − b', d - b * u / uT(T))
  add('border', `card-${d} inner radius`, 'R − b', Math.max(0, R - b * u / uT(T)))
  for (const w of ['dialog', 'panel', 'rail']) if (P.widths[w] !== undefined) add('width', w, `${P.widths[w]}`, P.widths[w])
  if (P.widths.panel !== undefined) add('width', 'collapse', '2 × panel: two panels side by side', 2 * P.widths.panel)
  const base = 40
  for (const [name, [aw, ah]] of Object.entries(P.aspects ?? PRESETS.standard.aspects)) add('media', `${name} ${aw}:${ah} height at w = ${base}`, `w · ${ah}/${aw}`, (base * ah) / aw)

  // Tier 4, layout: pages, grids, regions. Reads the minimum card width.
  T = 'layout'
  // The page follows the container rule: the gutter between columns and cards is half the margin, snapped to ½q.
  // A stepped margin takes its level from the page width; the gutter stays half the base margin, so columns do not jump at a step.
  const lp = pageLevel(P, width), stepped = typeof P.levels.page !== 'number', M = lp * from('controls', i), G = Math.round(pageLevel(P) * from('controls', i)) / 2
  add('grid', 'M', stepped ? `${lp}I (${width == null ? 'base' : `at ${width}px`}; ${P.levels.page.narrow}I under ${(P.marginSteps ?? PRESETS.standard.marginSteps)[0]}px, ${P.levels.page.wide}I from ${(P.marginSteps ?? PRESETS.standard.marginSteps)[1]}px)` : `${lp}I`, M)
  add('grid', 'G', 'M/2, snapped to ½q', G)
  add('gap', 'card', 'G', G)
  // The flow of a page is spaced in body sizes, whole px when crisp: it does not move with density.
  { const fl = { ...PRESETS.standard.flow, ...P.flow }, uL = uT(T), fq = (m) => (P.crisp === false ? Math.round(m * n / uL * 2) / 2 : roundEven(m * n) / uL)
    for (const [name, key] of [['kicker to heading', 'kicker'], ['heading to text', 'heading'], ['paragraphs', 'paragraph'], ['text to actions', 'actions'], ['action to note', 'note']]) add('flow', name, `${fl[key]}·F`, fq(fl[key]))
    add('flow', 'section padding', `${fl.section}·F above and below`, fq(fl.section)) }
  add('width', 'viewport margin', `${P.viewportMargin}`, P.viewportMargin)
  if (P.widths.measure !== undefined) add('width', 'measure', `${P.widths.measure}`, P.widths.measure)
  if (width && columns) {
    const W = width / uT(T)
    add('grid', `w  W=${width}px N=${columns}`, '(W − 2M − (N−1)G)/N', (W - 2 * M - (columns - 1) * G) / columns)
    add('grid', 'N_max', `⌊(W − 2M + G)/(${P.columnMin} + G)⌋`, Math.floor((W - 2 * M + G) / (P.columnMin + G)), true)
  }
  for (let kc = 1; kc <= 6; kc++) add('breakpoint', `${kc} column${kc > 1 ? 's' : ''}`, `k·w_min + (k − 1)G + 2M, w_min ${P.columnMin}`, kc * P.columnMin + (kc - 1) * G + 2 * M)
  const Ms = { ...PRESETS.standard.measure, ...P.measure }
  for (const [kname, c] of Object.entries(Ms)) add('measure', `${kname} (${c} ch)`, 'c · charWidth · F', (c * fm.charWidth * n) / uT(T))

  return only ? rows.filter((x) => x.tier === only || (only !== 'unit' && x.tier === 'unit' && x.group === 'scale')) : rows
}

/**
 * The container spacing ladder: padding, gap, radius and height for every container, inside out.
 * Each cell is a list of { e: expression, q }. Every gap is half its container's padding, the full padding before
 * actions, g_c, 0, or the item inset; a page section's are the flow gaps, multiples of F. Card depth follows density; insets, gutter and gaps land on whole px (crisp).
 */
export function containers({ preset = PRESETS.standard, n = 14, density = 'default', kappa = {}, cardDepth = 4, popoverDepth, dialogDepth, nest } = {}) {
  const P = crisp(preset, n), X = system(P), u = X.q(n)
  const sp = { ...PRESETS.standard.spacing, ...P.spacing }
  const half = (x) => Math.round(x * 2) / 2, f = nest ?? sp.nest
  // Lengths that are not built from I or g_c (depths, gaps) snap to whole px when crisp, else to ½q.
  const snap = (x) => (P.crisp === false ? half(x) : roundEven(x * u) / u)
  const ks = P.softAnchor, k = { control: ks, frame: ks, card: ks, panel: ks, ...P.dials?.kappa, ...kappa }
  const I = X.I(density), gc = P.gutter, mc = X.mc(density), S = P.slot, h = X.h(density), ho = S + 2 * gc, a = P.icons.md
  // Card depth moves with density, one q per step in the standard preset: d_δ = d + depthStep·(I_δ − I_default).
  const d = snap(cardDepth + sp.depthStep * (I - X.I('default')))
  const dp = popoverDepth ?? snap(sp.popoverRatio * d), dd = dialogDepth ?? snap(sp.dialogRatio * d)
  const r = X.radius(k.control, density), ro = X.inward(r, mc)
  const dcq = X.dc(density), rf = Math.min(X.radius(k.frame, density), P.soft), rrow = X.inward(rf, dcq)
  const rk = Math.min(X.radius(k.card, density), P.soft), R = (x) => (x === 0 || rk === 0 ? X.radius(k.card, density) : x + rk)
  const lvl = (l) => Math.min(P.levelGutterCap, l * I), L = P.levels
  const off = I + (S - a) / 2, nd = snap((1 - f) * d), nR = f === 0 ? 0 : X.inward(R(d), d - nd)
  const c = (e, q) => ({ e, q })
  const fl = { ...PRESETS.standard.flow, ...P.flow }, flow = (m) => snap(m * n / u)   // a multiple of F, in q
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
    row('controls', 'Control row', 'form actions, toolbar of separate buttons, the two halves of a split button', [c('0', 0)], [c('min(cap, I)', lvl(1))], [c('r each', r)], [c('h', h)]),
    row('controls', 'Joined controls', 'button group: one shape, shared edges, the ring drawn inside', [c('0', 0)], [c('0, shared edge', 0)], [c('r outside, 0 inside', r)], [c('h', h)]),
    // Segments and menu rows share the item height (h − 2d_c by default); the h-tall host pads what is left, (h − item)/2 = d_c.
    row('collections', 'Segmented control, tab list', 'a host of joined controls', [c('(h − item)/2 = d_c', X.hostPad(density))], [c('0', 0)], [c('host r', r), c('segment r − d_c', X.inward(r, X.hostPad(density)))], [c('host h', h), c('segment h − 2d_c', X.frameRow(density))]),
    row('collections', 'Listbox, menu, select popup', 'a frame of rows', [c(typeof P.frameDepth === 'number' ? 'd_c' : `d_c = ${P.frameDepth}`, dcq), c('rows inline: T − d_c (text at T)', 2 * I - dcq)], [c('rows 0', 0), c('separator g_c each side', gc), c('popup offset from its trigger d_c', dcq)], [c('r_f = min(r, soft)', rf), c('rows r_f − d_c', rrow)], [c(P.frameRow === 'h' ? 'rows h' : P.frameRow === 'h_o' ? 'rows h_o = S + 2g_c' : P.frameRow === 'm_c' ? 'rows S + 2m_c' : 'rows h − 2d_c', X.frameRow(density))]),
    // Lists and tables take the control radius r on their outline (rows clip to it) and use the control's insets: they share the content edge with buttons and inputs, and
    // their edge cells pad T = 2I, so cell text lines up with a button label above or below. Hairlines sit inside the row.
    row('collections', 'List, flush', 'rows with hairlines in an r-rounded outline; multi-line rows pad I above and below', [c('0, on the content edge', 0), c('text at T = 2I, as a button label', 2 * I)], [c('0, hairline inside the row', 0)], [c('outline r, as a button; rows clip', r)], [c('rows h', h)]),
    // A table row is a host: a control in a cell takes the item height and sits (h − item)/2 = d_c from the row edges.
    row('collections', 'Table', 'r-rounded outline; header and data rows; may run its own density', [c('0, on the content edge', 0), c('cells I each side', I), c('edge cells T = 2I, as a button label', 2 * I)], [c('columns 2I', 2 * I), c('rows 0, hairline inside the row', 0)], [c('outline r, as a button; rows clip', r)], [c('rows and header h', h), c(`control in a cell: item ${P.frameRow === 'h' ? 'h' : P.frameRow === 'h_o' ? 'h_o' : P.frameRow === 'm_c' ? 'S + 2m_c' : 'h − 2d_c'}`, X.frameRow(density)), c('its inset (h − item)/2 = d_c', X.hostPad(density))]),
    // An inset list (navigation, selectable list): an r-rounded outline, rows h tall (a button's height) in a d_c inset with a
    // concentric selection (r − d_c), and text at T = 2I from the list edge, where a button's label sits.
    row('collections', 'List, inset', 'navigation, selectable list: text at a button label inset', [c('d_c', dcq), c('items inline: T − d_c (text at T)', 2 * I - dcq)], [c('0, selection is a fill', 0)], [c('outline r', r), c('selection r − d_c', X.inward(r, dcq))], [c('rows h, as a button', h)]),
    // Fields sit 2I apart, the same gap as table columns (the control system's T); proximity groups each label with its control.
    // A field's control sits on the content edge like any control; its label and help text are inset T, over the value text.
    row('collections', 'Form', 'stacked fields: label, control, help text', [c('control on the content edge', 0), c('label and help at T, over the value', 2 * I)], [c('between fields: 2I, as table columns', 2 * I), c('label → control g_c', gc), c('control → help g_c', gc)], [], [c('fields h', h)]),
    // Containers and layout share one rule: gap = depth / 2; under a header the full depth; under a painted band the gap gives back I; before actions it is the full depth.
    row('containers', 'Popover, tooltip', 'small floating card, d_p = ¾d', [c('d_p', dp)], [c('d_p / 2', snap(dp / 2))], [c('d_p + min(r, soft)', R(dp))], []),
    row('containers', 'Card', `header row h, its text on the content edge d (with captions, loose text and shapes); d = ${cardDepth}q at default, ${sp.depthStep}·ΔI per density step (depthStep); a panel of controls is a card at d = 2I`, [c('d', d)], [c('blocks in a group d / 2', snap(d / 2)), c('band → content max(0, d/2 − I)', snap(Math.max(0, d / 2 - I))), c('header → content d', d), c('rows d / 4', snap(d / 4)), c('before actions d', d), c('groups d', d), c('group caption → content I', I)], [c('R = d + min(r, soft)', R(d))], [c('title row h', h)]),
    row('containers', 'Nested card, well', `a card inside a card, f = ${f}`, [c('(1 − f)·d', nd)], [c('(1 − f)·d / 2', snap(nd / 2))], [c('R − f·d', nR)], []),
    row('containers', 'Dialog, sheet', 'modal card, d_d = 1½d', [c('d_d', dd)], [c('band → body max(0, d_d/2 − I)', snap(Math.max(0, dd / 2 - I))), c('header → body d_d', dd), c('body blocks d_d / 2', snap(dd / 2)), c('before actions d_d', dd)], [c('d_d + min(r, soft)', R(dd))], [c('title row h', h)]),
    row('layout', 'Region', 'sidebar, toolbar band', [c(`${L.panel}·I`, L.panel * I)], [c(`${L.panel}·I / 2`, snap(L.panel * I / 2))], [c('0', 0)], []),
    // A page section shares the page's edge: it pads only above and below, so content never sits 2M in.
    row('layout', 'Page section', 'headings, text and actions in the flow of a page, spaced in F; shares the page edge', [c(`${fl.section}·F block`, flow(fl.section)), c('0 inline', 0)], [c(`flow: kicker → heading ${fl.kicker}·F`, flow(fl.kicker)), c(`flow: heading → text ${fl.heading}·F`, flow(fl.heading)), c(`flow: paragraphs ${fl.paragraph}·F`, flow(fl.paragraph)), c(`flow: text → actions ${fl.actions}·F`, flow(fl.actions)), c(`flow: action → note ${fl.note}·F`, flow(fl.note))], [c('0', 0)], []),
    row('layout', 'Page', 'grid of columns', [c(`M = ${pageLevel(P)}·I`, pageLevel(P) * I)], [c('G = M / 2', snap(pageLevel(P) * I / 2))], [c('0', 0)], []),
  ]
}

/**
 * A floating surface's width: its content, capped by its maximum, never narrower than the control that opens and fills it
 * (`anchor`, 0 when there is none), and in any case no wider than the viewport less a margin each side (all in one unit).
 */
export const floatingWidth = ({ content, max, W, margin, anchor = 0 }) => Math.max(0, Math.min(Math.max(anchor, Math.min(content, max)), W - 2 * margin))

/** A floating surface's height: its content, capped by the viewport's height less a margin each side. Taller content scrolls inside. */
export const floatingHeight = ({ content, H, margin }) => Math.max(0, Math.min(content, H - 2 * margin))

/**
 * A grid for several column counts (equations.md › 8): a field of U units, a gutter and a margin of g units each, so the
 * page is U + 2g units and u = W / (U + 2g), snapped to the device grid (section 12). n columns fill the field in whole
 * units when n divides U + g; each is (U − (n − 1)·g) / n units. Lists every such n up to maxColumns with a column of at
 * least one unit.
 */
export function multiGrid({ field: U, gutter: g, width: W, dpr = 1, maxColumns = 12 }) {
  if (![U, g, W].every((x) => Number.isInteger(x) && x > 0)) throw new Error('--field, --gutter and --width must be whole numbers above 0')
  const exact = W / (U + 2 * g), u = snap(exact, dpr), counts = []
  for (let n = 1; n <= maxColumns; n++) {
    const units = (U - (n - 1) * g) / n
    if ((U + g) % n === 0 && units >= 1) counts.push({ n, units, px: units * u })
  }
  return { U, g, W, dpr, exact, u, margin: g * u, gutter: g * u, field: U * u, page: (U + 2 * g) * u, counts }
}

/**
 * The faults of a multiGrid() result: a listed count whose columns are not whole units or do not fill the field, and a
 * whole count up to the largest listed one that is missing. derive.test.mjs keeps a mutated grid as a negative control.
 */
export function multiGridFaults({ U, g, counts }) {
  const out = [], listed = new Set(counts.map((c) => c.n)), top = Math.max(0, ...listed)
  for (const { n, units } of counts) if (!Number.isInteger(units) || units < 1 || n * units + (n - 1) * g !== U) out.push(`n = ${n}: ${units} units does not fill a field of ${U} in whole units`)
  for (let n = 1; n <= top; n++) if (!listed.has(n) && (U + g) % n === 0 && (U - (n - 1) * g) / n >= 1) out.push(`n = ${n} divides U + g = ${U + g} but is not listed`)
  return out
}

/**
 * The control and collection identities, checked on derive() rows. Returns the names of those that fail, so a mutated
 * table must report them (derive.test.mjs keeps one as a negative control).
 */
export function checkIdentities(rows) {
  const v = (id) => rows.find((r) => r.id === id)?.q
  const near = (a, b) => a !== undefined && b !== undefined && Math.abs(a - b) < 1e-9
  const c = (id) => v('controls.control.' + id)
  const checks = {
    'h = S + 2I': near(c('h'), c('s') + 2 * c('i')),
    'm_c + g_c = I': near(c('m_c') + c('g_c'), c('i')),
    'h_o = S + 2g_c': near(c('h_o'), c('s') + 2 * c('g_c')),
    'T = 2I': near(c('t'), 2 * c('i')),
    'item + 2d_c = h': near(v('collections.rows.menu-row') + 2 * v('collections.frame.d_c'), v('collections.rows.row')),
    'ring outer radius = r + o + w': near(v('controls.focus.ring-outer-radius'), v('controls.curvature.r') + v('controls.focus.ring-offset-o') + v('controls.focus.ring-width-w')),
  }
  return Object.entries(checks).filter(([, ok]) => !ok).map(([k]) => k)
}

/** A row's stable id: tier.group.symbol, lower-case, with runs of other characters as one hyphen. */
export const rowId = (tier, group, symbol) => [tier, group, symbol].map((x) => String(x).toLowerCase().replace(/κ=[0-9.]+/g, '').replace(/[^a-z0-9_.+]+/g, '-').replace(/^-|-$/g, '')).join('.')

/** The page level ℓ_page at a page width: a number, or the narrow, base or wide step of { narrow, base, wide } (base when no width is given). */
export function pageLevel(P, W) {
  const p = P.levels.page; if (typeof p === 'number') return p
  const [a, b] = P.marginSteps ?? PRESETS.standard.marginSteps
  return W == null ? p.base : W < a ? p.narrow : W < b ? p.base : p.wide
}

/** Keys a preset may carry besides those of PRESETS.standard. */
export const PRESET_EXTRA_KEYS = ['name', 'units', 'crisp', 'dials', '$comment']

/** Refuse a preset key the calculator does not read, so a typo never falls back to the standard preset unnoticed. */
export function validatePreset(p, where = 'preset') {
  const known = new Set([...Object.keys(PRESETS.standard), ...PRESET_EXTRA_KEYS])
  const near = (k) => [...known].map((x) => [x, lev(k.toLowerCase(), x.toLowerCase())]).sort((a, b) => a[1] - b[1])[0]
  const bad = Object.keys(p).filter((k) => !known.has(k))
  const pg = p.levels?.page, st = p.marginSteps
  if (pg !== undefined && typeof pg !== 'number' && !(pg && ['narrow', 'base', 'wide'].every((k) => typeof pg[k] === 'number') && Object.keys(pg).length === 3)) throw new Error(`${where}: levels.page is a number, or { narrow, base, wide } with a number each`)
  if (st !== undefined && !(Array.isArray(st) && st.length === 2 && st.every((x) => typeof x === 'number') && st[0] < st[1])) throw new Error(`${where}: marginSteps is two page widths in px, the smaller first`)
  if (p.cardRadius !== undefined && !['concentric', 'control'].includes(p.cardRadius)) throw new Error(`${where}: cardRadius is 'concentric' or 'control'`)
  if (p.rhythm !== undefined && !['formula', 'line'].includes(p.rhythm)) throw new Error(`${where}: rhythm is 'formula' or 'line'`)
  if (bad.length) throw new Error(`${where}: unknown key${bad.length > 1 ? 's' : ''} ${bad.map((k) => { const [x, dist] = near(k); return `"${k}"${dist <= 3 ? ` (did you mean "${x}"?)` : ''}` }).join(', ')}. Known keys: ${[...known].join(', ')}`)
  return p
}
const lev = (a, b) => { const m = Array.from({ length: a.length + 1 }, (_, i) => [i, ...new Array(b.length).fill(0)]); for (let j = 1; j <= b.length; j++) m[0][j] = j; for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++) m[i][j] = Math.min(m[i - 1][j] + 1, m[i][j - 1] + 1, m[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)); return m[a.length][b.length] }

function loadPreset(name) {
  if (!name || name in PRESETS) return PRESETS[name ?? 'standard']
  return { ...PRESETS.standard, ...validatePreset(JSON.parse(readFileSync(name, 'utf8')), name) }
}

/** An archetype's dials, read here so parse stays synchronous; scripts/archetypes.mjs holds the rest. */
function archetypeDials(name) {
  const A = JSON.parse(readFileSync(new URL('../references/archetypes.json', import.meta.url), 'utf8')).archetypes
  if (!A[name]) throw new Error(`archetype "${name}" is not in references/archetypes.json. Known: ${Object.keys(A).join(', ')}`)
  return A[name].dials
}

function parse(argv) {
  const get = (key) => { const at = argv.indexOf(`--${key}`); return at < 0 ? undefined : argv[at + 1] }
  let preset = loadPreset(get('preset'))
  // An archetype brings its constants and dial defaults (references/archetypes.json); flags still override them.
  const arch = get('archetype') ? archetypeDials(get('archetype')) : undefined
  if (arch) preset = { ...preset, ...(arch.constants ?? {}), dials: { ...(preset.dials ?? {}), density: arch.density, kappa: { ...arch.kappa } } }
  // A preset may carry default dials (`dials`: kappa per tier, cardDepth, density); flags override them.
  const D = preset.dials ?? {}
  const base = get('kappa') === undefined ? undefined : Number(get('kappa'))
  const kappa = Object.fromEntries(['control', 'frame', 'card', 'panel'].map((t) => [t, get(`kappa-${t}`) !== undefined ? Number(get(`kappa-${t}`)) : base ?? D.kappa?.[t] ?? preset.softAnchor]))
  const viewport = get('viewport') && Number(get('viewport'))
  return {
    preset, viewport, dpr: Number(get('dpr') ?? 1),
    archetype: get('archetype'), n: get('n') !== undefined ? Number(get('n')) : viewport ? fluidN(viewport, preset) : arch?.n ?? 14, density: get('density') ?? D.density ?? 'default', kappa,
    width: get('width') && Number(get('width')), columns: get('columns') && Number(get('columns')),
    cardDepth: Number(get('card') ?? D.cardDepth ?? 4), json: argv.includes('--json'), tier: get('tier'),
    elevation: get('elevation'), layers: get('layers') && Number(get('layers')), scheme: get('scheme') ?? 'light',
    containers: argv.includes('--containers'),
    field: get('field') && Number(get('field')), gutter: get('gutter') && Number(get('gutter')), maxColumns: Number(get('max-columns') ?? 12),
    popoverDepth: get('popover') && Number(get('popover')), dialogDepth: get('dialog') && Number(get('dialog')), nest: get('nest') && Number(get('nest')),
  }
}

function printElevation(o) {
  const E = { ...PRESETS.standard.elevation, ...o.preset.elevation }
  const names = o.elevation === 'all' ? Object.keys(E.levels) : [isNaN(Number(o.elevation)) ? o.elevation : Number(o.elevation)]
  const u = system(o.preset).q(o.n)
  const all = names.map((level) => elevation({ preset: o.preset, level, layers: o.layers, scheme: o.scheme }))
  if (o.json) return console.log(JSON.stringify(all, null, 2))
  for (const e of all) {
    console.log(`## elevation ${e.level} (s = ${e.s}, ${e.layers.length} layers, ${e.scheme})\n\n| k | x | y | blur | spread | alpha | y px | blur px |\n|---|---|---|---|---|---|---|---|`)
    for (const l of e.layers) console.log(`| ${l.k} | ${fmt(l.x)}q | ${fmt(l.y)}q | ${fmt(l.blur)}q | ${fmt(l.spread)}q | ${fmt(l.alpha * 100)}% | ${fmt(l.y * u)} | ${fmt(l.blur * u)} |`)
    console.log(`\ncomposite alpha at contact: ${fmt(e.composite * 100)}%\n`)
  }
}

function printMultiGrid(o) {
  const m = multiGrid({ field: o.field, gutter: o.gutter, width: o.width, dpr: o.dpr, maxColumns: o.maxColumns })
  if (o.json) return console.log(JSON.stringify(m, null, 2))
  console.log(`## grid for several column counts: U = ${m.U}, g = ${m.g}, W = ${m.W}px\n`)
  console.log(`page U + 2g = ${m.U + 2 * m.g} units  u = W / ${m.U + 2 * m.g} = ${fmt(m.exact)}px, snapped at ${m.dpr}x: ${fmt(m.u)}px`)
  console.log(`margin = gutter = g·u = ${fmt(m.margin)}px  field U·u = ${fmt(m.field)}px  page ${fmt(m.page)}px${m.page !== m.W ? ` (${fmt(m.W - m.page)}px of W left over)` : ''}\n`)
  console.log(`| n | column (units) | column (px) | span check |\n|---|---|---|---|`)
  for (const c of m.counts) console.log(`| ${c.n} | ${c.units} | ${fmt(c.px)} | ${c.n}·${c.units} + ${c.n - 1}·${m.g} = ${c.n * c.units + (c.n - 1) * m.g} |`)
  const faults = multiGridFaults(m)
  console.log(`\nn divides U + g = ${m.U + m.g}, up to ${o.maxColumns} columns.${faults.length ? ` Faults: ${faults.join('; ')}` : ''}`)
}

function printContainers(o) {
  const u = system(o.preset).q(o.n), all = containers(o)
  if (o.json) return console.log(JSON.stringify(all.map((r) => ({ ...r, px: u })), null, 2))
  const cell = (xs) => (xs.length ? xs.map((x) => `${x.e} = ${fmt(x.q)}q = ${fmt(x.q * u)}px`).join('<br>') : '—')
  console.log(`n = ${fmt(o.n)}px  q = ${fmt(u)}px  density ${o.density}  card d ${o.cardDepth}q  κ ${JSON.stringify(o.kappa)}\n`)
  for (const t of TIERS) {
    console.log(`## ${t}\n\n| container | padding | gap | radius | height |\n|---|---|---|---|---|`)
    for (const r of all.filter((x) => x.tier === t)) console.log(`| ${r.container} (${r.members}) | ${cell(r.pad)} | ${cell(r.gap)} | ${cell(r.radius)} | ${cell(r.height)} |`)
    console.log('')
  }
}

const fmt = (x) => (Number.isNaN(x) ? '—' : String(Math.round(x * 1000) / 1000))

const isMain = () => { try { return realpathSync(process.argv[1]) === fileURLToPath(import.meta.url) } catch { return false } }

// Async so the archetype report can import archetypes.mjs, which imports this module, after this module has loaded.
if (isMain()) (async () => {
  const o = parse(process.argv.slice(2))
  if (!(o.density in o.preset.inset)) throw new Error(`density must be one of ${Object.keys(o.preset.inset).join(', ')}`)
  if (o.n < o.preset.unit.nMin) console.error(`warning: n = ${o.n} is under the preset's ${o.preset.unit.nMin}px minimum`)
  if (o.field || o.gutter) return printMultiGrid(o)
  const rows = derive(o)
  if (o.containers) printContainers(o)
  else if (o.elevation) printElevation(o)
  else if (o.json) console.log(JSON.stringify(rows, null, 2))
  else {
    console.log(`n = ${fmt(o.n)}px${o.viewport ? ` (fluid at W = ${o.viewport}px)` : ''}  q = ${fmt(system(o.preset).q(o.n))}px  density ${o.density}  κ ${JSON.stringify(o.kappa)}  dpr ${o.dpr}\n`)
    const off = rows.filter((r) => !Number.isNaN(r.px) && !onGrid(r.px, o.dpr) && !['type', 'text', 'measure', 'icon stroke'].includes(r.group))
    if (off.length) console.log(`off the ${o.dpr}x device grid (snap to ${1 / o.dpr}px), ${off.length} lengths: ${off.slice(0, 12).map((r) => `${r.symbol} ${fmt(r.px)}→${fmt(snap(r.px, o.dpr))}`).join('; ')}${off.length > 12 ? `; and ${off.length - 12} more (--json for all)` : ''}\n`)
    if (o.archetype) console.log((await import('./archetypes.mjs')).archetypeReport(o.archetype, o))
    for (const t of ['unit', ...TIERS]) {
      const inTier = rows.filter((x) => x.tier === t)
      if (!inTier.length) continue
      console.log(`# ${t}${TIER_READS[t]?.length ? `  (reads from below: ${TIER_READS[t].join(', ')})` : ''}\n`)
      for (const g of [...new Set(inTier.map((r) => r.group))]) {
        console.log(`## ${t} › ${g}\n\n| symbol | expression | q | px |\n|---|---|---|---|`)
        for (const r of inTier.filter((x) => x.group === g)) console.log(`| ${r.symbol} | ${r.expr} | ${fmt(r.q)} | ${fmt(r.px)} |`)
        console.log('')
      }
    }
  }
})().catch((e) => { console.error(e.message); process.exit(1) })
