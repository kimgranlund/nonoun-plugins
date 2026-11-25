// Generated from ui-geometry/scripts/derive.mjs by scripts/build.mjs; run npm run build, do not edit.
// UI geometry calculator. Self-contained: a preset holds every constant, the equations are generic.
//   node derive.mjs --n 16 --density loose --kappa 0.5 [--kappa-card 1] [--card 4] [--width 1280 --columns 12]
//                   [--preset ladder (default) | standard | ./my-preset.json] [--json]
//   node derive.mjs --elevation popup|raised|floating|modal|all|<s> [--layers 5] [--scheme light|dark] [--n 14]
//   node derive.mjs --viewport 1024 [--dpr 2]   (n from the fluid scale; lengths off the device grid are listed)
//   node derive.mjs --tier controls|collections|containers|layout   (one tier, with the shared unit)
//   node derive.mjs --containers [--card 4 --popover 3 --dialog 6 --nest 0.5]   (padding, gap, radius for every container; popover and dialog default to ¾d and 1½d)
//   node derive.mjs --field 58 --gutter 2 --width 1440 [--dpr 2] [--max-columns 12]   (a grid for several column counts, in units u)
//   node derive.mjs --lines [--preset affine]   (adds each length's line a·n + b)
//   node derive.mjs --whole [--preset affine] [--from 10 --to 24]   (where each length is whole px with nothing snapped; exit 1 on a fractional row the preset does not name)
//   node derive.mjs --emit css|json [--preset affine]   (custom properties, each a line in the font size, with an exact em fallback)
// Prints every length of a scope as a multiple of the unit q and in px. Every length is a line in n; --lines prints it.


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

// The ladder preset (the default answer since 2026-11-18): the standard preset on the unit q = ¾n − 6.75, so h = 8q =
// 6n − 54: 30px controls at n 14 (24 at 13, 36 at 15, 48 at 17, 60 at 19), from a measured product kit's size
// ladder. Every other constant is the standard preset's; 'standard' keeps h = 32 at 14 (alias 'standard-32').
PRESETS.ladder = { ...PRESETS.standard, name: 'ladder', unit: { a: 0.75, b: -6.75, nMin: 12 } }
PRESETS['standard-32'] = PRESETS.standard
// The affine preset: an exact system. Every constant is a line in n with its own slope and offset, so no one unit q
// holds them (S = 2n − 8 and I = n − 9 share no factor); the unit is one px and nothing is rounded. The lines listed in
// `source` are a measured kit's own (a light-DOM component kit whose every length is a line in its scope's font size);
// the rest are the nearest expression of the standard preset's rows in the same lines and are not that kit's.
// Density is not a dial here: a denser or looser region is a scope with another n, so the three insets are one line.
const ln = (a, b, more) => ({ a, b, ...more })
PRESETS.affine = {
  ...PRESETS.standard, name: 'affine', exact: true, crisp: false,
  unit: { a: 0, b: 1, nMin: 10 },
  slot: ln(2, -8),
  inset: { compact: ln(1, -9), default: ln(1, -9), loose: ln(1, -9) },
  gutter: 0,
  soft: ln(1, -6),
  frameDepth: 'm_c', frameRow: 'fit',
  cardRadius: 'level',
  cardDepths: [0, { name: 'inset', ...ln(1, -9) }, { name: 'text-edge', ...ln(2, -18) }, { name: 'slot', ...ln(2, -8) }, { name: 'control', ...ln(4, -26) }],
  levels: { composite: 0.5, group: 1, collection: 2, panel: ln(2, -8), page: ln(4, -26) },
  levelGutterCap: ln(2, -18),
  columnMin: ln(8, 48),
  flow: { kicker: 1, heading: 1, paragraph: 1, actions: 2, note: 1, section: 3 },
  icons: { sm: 'F', md: ln(1.5, -4), lg: ln(2, -8), full: ln(2, -8) },
  marks: { checkRadius: ln(0.375, -1), switchWidth: ln(3, -12), badgeDot: ln(1, -9) },
  tracks: { track: ln(0.5, -4, { min: 1 }), meter: ln(1, -8, { min: 2 }), sliderMin: ln(8, -42) },
  widths: { tooltip: ln(16, 16), popover: ln(24, -16), dialog: ln(32, 32), rail: ln(8, -42), panel: ln(16, 16), measure: ln(44, 0) },
  viewportMargin: ln(2, -8),
  focus: { width: 2, offset: 0 },
  avatars: { xs: ln(1.5, -4), sm: ln(2, -8), md: ln(3, -17), lg: ln(4, -26), xl: ln(4, -16), xxl: ln(8, -32) },
  spacing: { ...PRESETS.standard.spacing, fieldGap: ln(1, -9), popover: ln(1, -9), dialog: ln(4, -26) },
  grid: { gutter: ln(2, -18), inset: ln(1, -9), columns: 12 },
  dials: { cardDepth: ln(2, -8) },
  type: {
    'display-lg': [ln(4, -18), ln(1, -6)], 'display-md': [ln(4, -26), ln(1, -8)], 'display-sm': [ln(4, -34), ln(1, -10)],
    'heading-lg': [ln(2, -4), ln(1, -6)], 'heading-md': [ln(2, -8), ln(1, -8)], 'heading-sm': [ln(2, -10), ln(1, -8)],
    'title-lg': [ln(1, 4), ln(1, -6)], 'title-md': [ln(1, 2), ln(1, -8)], 'title-sm': [ln(1, 0), ln(1, -10)],
    'body-lg': [ln(1, 2), ln(1, -6)], 'body-md': [ln(1, 0), ln(1, -8)], 'body-sm': [ln(1, -2, { min: 9 }), ln(1, -10)],
    label: [ln(1, -2, { min: 9 }), ln(1, -8)], 'kicker-lg': [ln(1, 0), ln(1, -8)], 'kicker-md': [ln(1, -2, { min: 9 }), ln(1, -8)], 'kicker-sm': [ln(1, -4, { min: 9 }), ln(1, -8)], code: [ln(1, -2, { min: 9 }), ln(1, -8)],
  },
  // Why each input is what it is. A constant with no reason here is derived from these or inherited from standard.
  reasons: {
    slot: 'S = 2n − 8: the slot grows two px per px of text, and the offset makes the control inset zero at 10px text',
    inset: 'I = n − 9: S − n − 1, so h = S + 2I = 4n − 26; one line for every density, since a denser region is a scope with a smaller n',
    gutter: '0: a hosted control is the slot itself (h_o = S), and its corner is r − I',
    soft: 'r = n − 6 at the soft anchor: one px of radius per px of text, capped at a pill',
    cardRadius: "'level': a radius steps one inset per level out (r − I, r, r + I, r + 2I), not with the padding",
    focus: 'a 2px ring at no offset: the ring touches the control, so it needs no room of its own beyond its width',
    grid: 'twelve columns with no gap; what sits on them pads itself by the column inset, half the 2I gutter, so nothing needs a negative margin',
  },
  // The rows that are not whole px at every n, each accepted by name: the medium icon and mark (a blend, 1.5n − 4) with its halves and quarters, and half and quarter depths.
  fractional: ['controls.control.d', 'controls.icon.a.md-offset', 'controls.mark.choice-label', 'controls.mark.checkbox-radius', 'controls.mark.radio-dot', 'containers.frame.composite-inset', 'controls.icon.a.sm-offset', 'controls.icon.a.md', 'controls.mark.checkbox-box', 'controls.mark.radio-box', 'controls.mark.switch-thumb', 'controls.track.progress-slider-track', 'controls.track.slider-thumb', 'containers.frame.nest-f-0.25-depth', 'containers.frame.nest-f-0.75-depth', 'containers.gap.separate-rows-card-d'],
  // The rows a measured kit states as its own lines (row id → line). scripts/derive.test.mjs holds the calculator to them.
  source: {
    'controls.control.s': [2, -8], 'controls.control.i': [1, -9], 'controls.control.h': [4, -26], 'controls.control.h_o': [2, -8], 'controls.control.t': [2, -18],
    'controls.icon.a.sm': [1, 0], 'controls.icon.a.md': [1.5, -4], 'controls.icon.a.lg': [2, -8],
    'controls.curvature.r': [1, -6], 'controls.curvature.r_s': [0, 3],
    'controls.mark.switch-track': [3, -12], 'controls.mark.checkbox-radius': [0.375, -1],
    'containers.curvature.r-card-slot': [2, -15], 'containers.curvature.r-dialog': [3, -24],
    'containers.frame.dialog-inset': [4, -26], 'containers.frame.page-inset': [4, -26], 'containers.frame.panel-inset': [2, -8],
    'containers.gap.label-control-control-help': [1, -9],
    'containers.width.rail': [8, -42], 'containers.width.panel': [16, 16], 'layout.width.measure': [44, 0],
    'layout.grid.g': [2, -18], 'layout.grid.column-inset': [1, -9],
    'unit.type.label': [1, -2], 'unit.type.body-md': [1, 0], 'unit.type.title-md': [1, 2], 'unit.type.heading-sm': [2, -10], 'unit.type.heading-md': [2, -8], 'unit.type.display-md': [4, -26],
    'unit.type.body-md-line': [2, -8],
  },
}

/** The preset an answer uses when none is named. */
export const DEFAULT_PRESET = 'ladder'

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
 * A line in n: { a, b } is the length a·n + b px, with an optional floor `min` and cap `max` in px. It is the primitive
 * of the system: a multiple k of the unit q = a_q·n + b_q is the line k·a_q·n + k·b_q, and an exact preset (`exact:
 * true`, unit 0·n + 1, so q is one px) gives its constants as lines directly, each with its own slope and offset.
 */
export const isLine = (v) => v !== null && typeof v === 'object' && !Array.isArray(v) && typeof v.a === 'number' && typeof v.b === 'number'
/** A line's value at n, in px. */
export const lineAt = (v, n) => { let x = v.a * n + v.b; if (v.min !== undefined) x = Math.max(x, v.min); if (v.max !== undefined) x = Math.min(x, v.max); return x }

/** The preset keys whose values, or whose members' values, may be lines. `levels` and `type` are resolved apart. */
const LINE_KEYS = ['slot', 'gutter', 'soft', 'frameDepth', 'viewportMargin', 'columnMin', 'levelGutterCap']
const LINE_GROUPS = ['inset', 'icons', 'marks', 'tracks', 'widths', 'focus', 'avatars', 'grid', 'spacing']

/**
 * A preset with every line constant resolved at n to the number of q the equations take: line(n) / q(n). A level given
 * as a line is that length, so it resolves to the multiple of I it comes to at this n and density; a type role given as
 * [size line, leading line] resolves to its [m_t, k_t]. A preset with no line comes back unchanged.
 */
export function resolveLines(P0, n, density = 'default') {
  const u = P0.unit.a * n + P0.unit.b
  const any = (o) => o && typeof o === 'object' && Object.values(o).some((v) => isLine(v) || (Array.isArray(v) && v.some(isLine)))
  if (!(u > 0) || !(LINE_KEYS.some((k) => isLine(P0[k])) || [...LINE_GROUPS, 'levels', 'type'].some((k) => any(P0[k])) || (Array.isArray(P0.cardDepths) && P0.cardDepths.some(isLine)))) return P0
  const q = (v) => (isLine(v) ? lineAt(v, n) / u : v)
  const group = (o) => (o && typeof o === 'object' && Object.values(o).some(isLine) ? Object.fromEntries(Object.entries(o).map(([k, v]) => [k, q(v)])) : o)
  const P = { ...P0 }
  for (const k of LINE_KEYS) if (isLine(P[k])) P[k] = q(P[k])
  for (const k of LINE_GROUPS) if (P[k]) P[k] = group(P[k])
  if (P.levels && Object.values(P.levels).some(isLine)) { const I = P.inset[density] ?? P.inset.default; P.levels = Object.fromEntries(Object.entries(P.levels).map(([k, v]) => [k, isLine(v) ? lineAt(v, n) / u / I : v])) }
  if (P.type && Object.values(P.type).some((t) => t.some(isLine))) P.type = Object.fromEntries(Object.entries(P.type).map(([id, [m, k]]) => [id, [isLine(m) ? (lineAt(m, n) - n) / u : m, q(k)]]))
  if (Array.isArray(P.cardDepths) && P.cardDepths.some(isLine)) { P.cardDepthNames = P.cardDepths.map((c, i) => (isLine(c) ? c.name ?? `l${i}` : String(c))); P.cardDepths = P.cardDepths.map(q) }
  return P
}

/**
 * A crisp preset at n: the insets I and the gutter g_c snap to whole px (round half to even) and the slot S to even px,
 * so every length built from them lands on the pixel grid even where q is odd (at 16px: S = 24, I = 8, g_c = 2, h = 40).
 * Set `crisp: false` to keep exact q.
 */
export function crisp(Praw, n, density = 'default') {
  const P0 = resolveLines(Praw, n, density)
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

export function derive({ preset = PRESETS.standard, n = 14, density = 'default', kappa = {}, width, columns, cardDepth, tier: only, text } = {}) {
  const P = crisp(preset, n, density), X = system(P)
  // exact: nothing is rounded anywhere, so every length stays the line its constants give. `wholeness()` is the proof.
  const exact = P.exact === true
  // The card depth: the dial in q, or, where a preset's dial is a line, that length (its rows are then named card-d).
  const rawD = cardDepth ?? (isLine(preset.dials?.cardDepth) ? preset.dials.cardDepth : 4), dName = isLine(rawD) ? 'd' : rawD
  const ks = P.softAnchor
  const k = { control: ks, frame: ks, card: ks, panel: ks, ...P.dials?.kappa, ...kappa }
  const u = X.q(n), rows = []
  const uT = (t) => (t === 'unit' ? u : tierUnit(P, t, n))
  let T = 'unit'
  /** A value of tier `src`, expressed in the current tier's q (identity when both share a unit). */
  const from = (src, v) => (v * uT(src)) / uT(T)
  // id: a stable key per row (tier.group.symbol, slugged), unique in every run; `alias` keeps a symbol's earlier spelling.
  const add = (group, symbol, expr, inQ, count = false, alias) => rows.push({ id: rowId(T, group, symbol), tier: T, group, symbol, ...(alias ? { alias } : {}), expr, q: inQ, px: count ? NaN : inQ * uT(T) })
  const i = X.I(density), d = isLine(rawD) ? lineAt(rawD, n) / tierUnit(P, 'containers', n) : rawD, S = P.slot, gc = P.gutter, dc = X.dc(density)
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
  // cardRadius 'level': a radius steps by one inset per level out, whatever the padding: a nested control r − I, a control r, a card r + I, a dialog r + 2I.
  const levelR = P.cardRadius === 'level', flatR = (P.cardRadius ?? 'concentric') === 'control' || levelR, rCtl = from('controls', X.radius(k.control, density)) + (levelR ? from('controls', i) : 0)
  const cardR = (c) => (flatR ? rCtl : c === 0 || rc === 0 ? from('controls', X.radius(k.card, density)) : c + rc)
  const flatExpr = levelR ? 'r(κ_control) + I' : 'r(κ_control)'
  P.cardDepths.forEach((c, ci) => add('curvature', `R card-${P.cardDepthNames?.[ci] ?? c}  κ=${flatR ? k.control : k.card}`, flatR ? flatExpr : c === 0 ? 'r(κ)' : rc === 0 ? '0 at κ 0' : 'd + min(r(κ), soft)', cardR(c)))
  if (levelR) add('curvature', `R dialog  κ=${k.control}`, 'r(κ_control) + 2I', rCtl + from('controls', i))
  const R = cardR(d)
  for (const f of P.nest) {
    const [dd, rr] = X.nested(d, R, f)
    add('curvature', `nest f=${f} in card-${dName}`, flatR ? `${levelR ? 'r(κ_control): one level in' : 'r(κ_control)'}, 0 when flush` : 'R − f·d', flatR ? (f === 0 ? 0 : levelR ? from('controls', X.radius(k.control, density)) : rCtl) : rr)
    add('frame', `nest f=${f} depth`, '(1 − f)·d', dd)
  }
  // A panel of controls is a card at depth 2I.
  add('curvature', `R panel (card at 2I)  κ=${flatR ? k.control : k.card}`, flatR ? flatExpr : '2I + min(r(κ_card), soft)', flatR ? rCtl : from('controls', 2 * i) + rc)
  for (const [l, v] of Object.entries(P.levels)) add('frame', `${l} inset`, `${typeof v === 'number' ? v : pageLevel(P)}·I`, from('controls', X.levelInset(l, density)))
  // Card depth follows density: d_δ = d + depthStep·(I_δ − I_default). The gaps below use it.
  { const de = d + ({ ...PRESETS.standard.spacing, ...P.spacing }.depthStep) * (i - X.I('default'))
  if (Math.abs(de - d) > 1e-9) add('frame', `card-${dName} at ${density}`, 'd + depthStep·(I − I_default)', de) }
  // The dialog's depth as a row, so a kit can read it as a token: d_d = dialogRatio · the density's card depth, snapped
  // as containers() snaps it (whole px when crisp, else ½q). The same value as the "Dialog, sheet" line of --containers.
  { const sp = { ...PRESETS.standard.spacing, ...P.spacing }, snap = (x) => (exact ? x : P.crisp === false ? Math.round(x * 2) / 2 : roundEven(x * u) / u)
    add('frame', 'dialog inset', sp.dialog !== undefined ? 'd_d, the preset\'s own line' : `d_d = ${sp.dialogRatio}·d`, sp.dialog ?? snap(sp.dialogRatio * snap(d + sp.depthStep * (i - X.I('default'))))) }
  // Inside a container the gap is half its depth; a header (an unpainted title row) is spaced as any child, the full
  // depth below as above, so its text has d + I on both sides; only a painted, flush title band gives back the row's
  // inset I (optical). The gap before an action row is the full depth. Every gap snaps to ½q.
  // Three label levels, three gaps: groups in a card sit d apart, blocks inside a group d/2, a group caption I above its
  // content, a field label g_c above its control.
  add('gap', `groups in card-${dName}`, 'd', d)
  add('gap', `blocks in a group, card-${dName}`, 'd/2', d / 2)
  add('gap', 'group caption → content', 'I', i)
  add('gap', `header → content card-${dName}`, 'd', d)
  add('gap', `band → content card-${dName}`, 'max(0, d/2 − I)', Math.max(0, d / 2 - i))
  add('gap', `separate rows card-${dName}`, exact ? 'd/4' : 'd/4, snapped to ½q', exact ? d / 4 : Math.round(d / 2) / 2)
  add('gap', `before actions card-${dName}`, 'd', d)
  // Fields sit 2I apart, as table columns do; label and help text sit g_c from the control.
  add('gap', 'between form fields', '2I (as table columns)', 2 * i)
  { const fg = ({ ...PRESETS.standard.spacing, ...P.spacing }).fieldGap
    add('gap', 'label → control, control → help', fg === undefined ? 'g_c' : 'the field gap, the preset\'s own line', fg ?? from('controls', gc)) }
  // A field with its label, help and the actions that submit it alone is one group: g_c inside, the gap between groups around it (never under 3 g_c).
  add('gap', 'around a field group', 'max(d, 3g_c): the gap between groups', Math.max(d, 3 * from('controls', gc)))
  add('border', `card-${dName} inner padding`, 'd − b', d - b * u / uT(T))
  add('border', `card-${dName} inner radius`, 'R − b', Math.max(0, R - b * u / uT(T)))
  for (const w of ['dialog', 'panel', 'rail']) if (P.widths[w] !== undefined) add('width', w, `${P.widths[w]}`, P.widths[w])
  if (P.widths.panel !== undefined) add('width', 'collapse', '2 × panel: two panels side by side', 2 * P.widths.panel)
  const base = 40
  for (const [name, [aw, ah]] of Object.entries(P.aspects ?? PRESETS.standard.aspects)) add('media', `${name} ${aw}:${ah} height at w = ${base}`, `w · ${ah}/${aw}`, (base * ah) / aw)

  // Tier 4, layout: pages, grids, regions. Reads the minimum card width.
  T = 'layout'
  // The page follows the container rule: the gutter between columns and cards is half the margin, snapped to ½q.
  // A stepped margin takes its level from the page width; the gutter stays half the base margin, so columns do not jump at a step.
  const lp = pageLevel(P, width), stepped = typeof P.levels.page !== 'number', M = lp * from('controls', i), G = P.grid?.gutter ?? (exact ? (pageLevel(P) * from('controls', i)) / 2 : Math.round(pageLevel(P) * from('controls', i)) / 2)
  add('grid', 'M', stepped ? `${lp}I (${width == null ? 'base' : `at ${width}px`}; ${P.levels.page.narrow}I under ${(P.marginSteps ?? PRESETS.standard.marginSteps)[0]}px, ${P.levels.page.wide}I from ${(P.marginSteps ?? PRESETS.standard.marginSteps)[1]}px)` : `${lp}I`, M)
  add('grid', 'G', P.grid?.gutter !== undefined ? 'the preset\'s own line' : exact ? 'M/2' : 'M/2, snapped to ½q', G)
  // A gutterless grid: the columns touch, and what is placed on them pads itself by the column inset (half the gutter).
  if (P.grid?.inset !== undefined) add('grid', 'column inset', 'G/2: what sits on a column pads itself; the columns have no gap', P.grid.inset)
  if (P.grid?.columns !== undefined) add('grid', 'columns', `${P.grid.columns}`, P.grid.columns, true)
  // Between columns: G, or nothing where the grid is gutterless and what sits on a column pads itself.
  const Gc = P.grid?.inset !== undefined ? 0 : G
  add('gap', 'card', 'G', G)
  // The flow of a page is spaced in body sizes, whole px when crisp: it does not move with density.
  { const fl = { ...PRESETS.standard.flow, ...P.flow }, uL = uT(T), fq = (m) => (exact ? (m * n) / uL : P.crisp === false ? Math.round(m * n / uL * 2) / 2 : roundEven(m * n) / uL)
    for (const [name, key] of [['kicker to heading', 'kicker'], ['heading to text', 'heading'], ['paragraphs', 'paragraph'], ['text to actions', 'actions'], ['action to note', 'note']]) add('flow', name, `${fl[key]}·F`, fq(fl[key]))
    add('flow', 'section padding', `${fl.section}·F above and below`, fq(fl.section)) }
  add('width', 'viewport margin', `${P.viewportMargin}`, P.viewportMargin)
  if (P.widths.measure !== undefined) add('width', 'measure', `${P.widths.measure}`, P.widths.measure)
  if (width && columns) {
    const W = width / uT(T)
    add('grid', `w  W=${width}px N=${columns}`, Gc ? '(W − 2M − (N−1)G)/N' : '(W − 2M)/N: the columns touch', (W - 2 * M - (columns - 1) * Gc) / columns)
    add('grid', 'N_max', Gc ? `⌊(W − 2M + G)/(${P.columnMin} + G)⌋` : `⌊(W − 2M)/${fmt(P.columnMin)}⌋`, Math.floor((W - 2 * M + Gc) / (P.columnMin + Gc)), true)
  }
  for (let kc = 1; kc <= 6; kc++) add('breakpoint', `${kc} column${kc > 1 ? 's' : ''}`, Gc ? `k·w_min + (k − 1)G + 2M, w_min ${P.columnMin}` : `k·w_min + 2M, w_min ${fmt(P.columnMin)}: the columns touch`, kc * P.columnMin + (kc - 1) * Gc + 2 * M)
  const Ms = { ...PRESETS.standard.measure, ...P.measure }
  for (const [kname, c] of Object.entries(Ms)) add('measure', `${kname} (${c} ch)`, 'c · charWidth · F', (c * fm.charWidth * n) / uT(T))

  return only ? rows.filter((x) => x.tier === only || (only !== 'unit' && x.tier === 'unit' && x.group === 'scale')) : rows
}

/**
 * The container spacing ladder: padding, gap, radius and height for every container, inside out.
 * Each cell is a list of { e: expression, q }. Every gap is half its container's padding, the full padding before
 * actions, g_c, 0, or the item inset; a page section's are the flow gaps, multiples of F. Card depth follows density; insets, gutter and gaps land on whole px (crisp).
 */
export function containers({ preset = PRESETS.standard, n = 14, density = 'default', kappa = {}, cardDepth: cardDepthArg, popoverDepth, dialogDepth, nest } = {}) {
  const P = crisp(preset, n, density), X = system(P), u = X.q(n), exact = P.exact === true
  const rawD = cardDepthArg ?? (isLine(preset.dials?.cardDepth) ? preset.dials.cardDepth : 4), cardDepth = isLine(rawD) ? lineAt(rawD, n) / u : rawD
  const sp = { ...PRESETS.standard.spacing, ...P.spacing }
  const half = (x) => Math.round(x * 2) / 2, f = nest ?? sp.nest
  // Lengths that are not built from I or g_c (depths, gaps) snap to whole px when crisp, else to ½q.
  const snap = (x) => (exact ? x : P.crisp === false ? half(x) : roundEven(x * u) / u)
  const ks = P.softAnchor, k = { control: ks, frame: ks, card: ks, panel: ks, ...P.dials?.kappa, ...kappa }
  const I = X.I(density), gc = P.gutter, mc = X.mc(density), S = P.slot, h = X.h(density), ho = S + 2 * gc, a = P.icons.md
  // Card depth moves with density, one q per step in the standard preset: d_δ = d + depthStep·(I_δ − I_default).
  const d = snap(cardDepth + sp.depthStep * (I - X.I('default')))
  const dp = popoverDepth ?? sp.popover ?? snap(sp.popoverRatio * d), dd = dialogDepth ?? sp.dialog ?? snap(sp.dialogRatio * d)
  const r = X.radius(k.control, density), ro = X.inward(r, mc)
  const dcq = X.dc(density), rf = Math.min(X.radius(k.frame, density), P.soft), rrow = X.inward(rf, dcq)
  const rk = Math.min(X.radius(k.card, density), P.soft), levelR = P.cardRadius === 'level', R = (x, lv = 1) => (levelR ? r + lv * I : x === 0 || rk === 0 ? X.radius(k.card, density) : x + rk)
  const lvl = (l) => Math.min(P.levelGutterCap, l * I), L = P.levels
  const off = I + (S - a) / 2, nd = snap((1 - f) * d), nR = f === 0 ? 0 : levelR ? r : X.inward(R(d), d - nd)
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
    row('collections', 'Form', 'stacked fields: label, control, help text', [c('control on the content edge', 0), c('label and help at T, over the value', 2 * I)], [c('between fields: 2I, as table columns', 2 * I), c(sp.fieldGap === undefined ? 'label → control g_c' : 'label → control: the field gap', sp.fieldGap ?? gc), c(sp.fieldGap === undefined ? 'control → help g_c' : 'control → help: the field gap', sp.fieldGap ?? gc)], [], [c('fields h', h)]),
    // Containers and layout share one rule: gap = depth / 2; under a header the full depth; under a painted band the gap gives back I; before actions it is the full depth.
    row('containers', 'Popover, tooltip', 'small floating card, d_p = ¾d', [c('d_p', dp)], [c('d_p / 2', snap(dp / 2))], [c(levelR ? 'r + I: one level out' : 'd_p + min(r, soft)', R(dp))], []),
    row('containers', 'Card', `header row h, its text on the content edge d (with captions, loose text and shapes); d = ${cardDepth}q at default, ${sp.depthStep}·ΔI per density step (depthStep); a panel of controls is a card at d = 2I`, [c('d', d)], [c('blocks in a group d / 2', snap(d / 2)), c('band → content max(0, d/2 − I)', snap(Math.max(0, d / 2 - I))), c('header → content d', d), c('rows d / 4', snap(d / 4)), c('before actions d', d), c('groups d', d), c('group caption → content I', I)], [c(levelR ? 'R = r + I: one level out' : 'R = d + min(r, soft)', R(d))], [c('title row h', h)]),
    row('containers', 'Nested card, well', `a card inside a card, f = ${f}`, [c('(1 − f)·d', nd)], [c('(1 − f)·d / 2', snap(nd / 2))], [c(levelR ? 'r: one level in' : 'R − f·d', nR)], []),
    row('containers', 'Dialog, sheet', 'modal card, d_d = 1½d', [c('d_d', dd)], [c('band → body max(0, d_d/2 − I)', snap(Math.max(0, dd / 2 - I))), c('header → body d_d', dd), c('body blocks d_d / 2', snap(dd / 2)), c('before actions d_d', dd)], [c(levelR ? 'r + 2I: two levels out' : 'd_d + min(r, soft)', R(dd, 2))], [c('title row h', h)]),
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

/**
 * Every row of derive() with the line it follows: { a, b } where px = a·n + b at n, n + 2 and n + 4, else null (a floor,
 * a cap, a snap or a curvature bend makes it piecewise there). Sampled, not symbolic, so it holds for any preset.
 */
export function lines(o = {}) {
  const n = o.n ?? 14, at = (k) => new Map(derive({ ...o, n: n + k }).map((r) => [r.id, r.px]))
  const p2 = at(2), p4 = at(4)
  return derive({ ...o, n }).map((r) => {
    const y0 = r.px, y2 = p2.get(r.id), y4 = p4.get(r.id)
    if ([y0, y2, y4].some((y) => y === undefined || Number.isNaN(y)) || Math.abs(y4 - y2 - (y2 - y0)) > 1e-9) return { ...r, line: null }
    const a = (y2 - y0) / 2, clean = (x) => Math.round(x * 1e9) / 1e9
    return { ...r, line: { a: clean(a), b: clean(y0 - a * n) } }
  })
}

/** A line as text: 4n − 26, 1.5n − 4, 3, n. */
export const lineText = (l) => (l === null ? 'not a line here' : l.a === 0 ? fmt(l.b) : `${l.a < 0 ? '−' : ''}${Math.abs(l.a) === 1 ? '' : fmt(Math.abs(l.a))}n${l.b === 0 ? '' : ` ${l.b < 0 ? '−' : '+'} ${fmt(Math.abs(l.b))}`}`)

/** The groups whose lengths must land on whole px. Text metrics, strokes, media ratios, targets and the measure are not held to it. */
export const WHOLE_GROUPS = ['control', 'icon', 'mark', 'track', 'curvature', 'frame', 'gap', 'rows', 'grid', 'width', 'focus', 'type', 'flow', 'breakpoint']

/**
 * Where each length is a whole number of px, with nothing snapped: derive() runs with the preset's rounding off (crisp
 * false) at every whole n from `from` to `to`. Returns, per row that is ever fractional, the n at which it is whole and a
 * verdict: 'even n', 'odd n', 'never', or the list. `halfStep` are the rows whole at every even n (a line with a half
 * slope), `fractional` the rest. A preset names the rows it accepts in its `fractional` list: `unnamed` are those it does
 * not name, a fault, and `stale` the names that are whole after all.
 */
export function wholeness({ preset = PRESETS.standard, from, to = 24, ...o } = {}) {
  const P = { ...preset, crisp: false }, lo = from ?? preset.unit.nMin ?? 12, seen = new Map()
  const whole = (px) => Math.abs(px - Math.round(px)) < 1e-9
  for (let n = lo; n <= to; n++) for (const r of derive({ ...o, preset: P, n })) {
    if (Number.isNaN(r.px) || !WHOLE_GROUPS.includes(r.group)) continue
    if (!seen.has(r.id)) seen.set(r.id, { id: r.id, symbol: r.symbol, wholeAt: [], fractionalAt: [] })
    seen.get(r.id)[whole(r.px) ? 'wholeAt' : 'fractionalAt'].push(n)
  }
  const rows = [...seen.values()].filter((r) => r.fractionalAt.length).map((r) => ({ ...r, verdict: !r.wholeAt.length ? 'never' : r.wholeAt.every((n) => n % 2 === 0) && r.fractionalAt.every((n) => n % 2) ? 'even n' : r.wholeAt.every((n) => n % 2) && r.fractionalAt.every((n) => n % 2 === 0) ? 'odd n' : `n = ${r.wholeAt.join(', ')}` }))
  // A preset names the rows it accepts as not whole at every n (`fractional`); any other is a fault.
  const named = new Set(preset.fractional ?? [])
  return { from: lo, to, checked: seen.size, halfStep: rows.filter((r) => r.verdict === 'even n'), fractional: rows.filter((r) => r.verdict !== 'even n'), unnamed: rows.filter((r) => !named.has(r.id)), stale: [...named].filter((id) => !rows.some((r) => r.id === id)) }
}

/**
 * What a kit reads: one entry per row that is a line, with its custom property, the declaration that computes it from
 * the font size of the element that uses it (1em, left unresolved in an unregistered property), and its fallback at n = 16 as an exact ratio in em (never truncated digits).
 */
export function emit(o = {}) {
  const frac = (x) => { for (let d = 1; d <= 256; d++) if (Math.abs(x * d - Math.round(x * d)) < 1e-9) return d === 1 ? `${Math.round(x)}` : `calc(${Math.round(x * d)} / ${d})`; return null }
  const out = [], names = new Set()
  for (const r of lines(o)) {
    if (!r.line || Number.isNaN(r.px) || !(r.group === 'scale' || WHOLE_GROUPS.includes(r.group))) continue
    const name = `--${r.id.replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}`
    if (names.has(name)) throw new Error(`emit: two rows would share the name ${name}`)
    names.add(name)
    const { a, b } = r.line, em = (a * 16 + b) / 16, ratio = frac(em)
    if (ratio === null) continue
    out.push({ id: r.id, name, line: r.line, text: lineText(r.line), px: r.px, css: a === 0 ? `${fmt(b)}px` : `calc(${fmt(a)} * 1em${b === 0 ? '' : ` ${b < 0 ? '-' : '+'} ${fmt(Math.abs(b))}px`})`, fallback: em === 0 ? '0em' : `${ratio}${ratio.startsWith('calc') ? '' : 'em'}`.replace(/^calc\((.+)\)$/, 'calc($1 * 1em)') })
  }
  return out
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
export const PRESET_EXTRA_KEYS = ['name', 'units', 'crisp', 'dials', '$comment', 'exact', 'grid', 'reasons', 'source', 'fractional']

/** Refuse a preset key the calculator does not read, so a typo never falls back to the standard preset unnoticed. */
export function validatePreset(p, where = 'preset') {
  const known = new Set([...Object.keys(PRESETS.standard), ...PRESET_EXTRA_KEYS])
  const near = (k) => [...known].map((x) => [x, lev(k.toLowerCase(), x.toLowerCase())]).sort((a, b) => a[1] - b[1])[0]
  const bad = Object.keys(p).filter((k) => !known.has(k))
  const pg = p.levels?.page, st = p.marginSteps
  if (pg !== undefined && typeof pg !== 'number' && !isLine(pg) && !(pg && ['narrow', 'base', 'wide'].every((k) => typeof pg[k] === 'number') && Object.keys(pg).length === 3)) throw new Error(`${where}: levels.page is a number, or { narrow, base, wide } with a number each`)
  if (st !== undefined && !(Array.isArray(st) && st.length === 2 && st.every((x) => typeof x === 'number') && st[0] < st[1])) throw new Error(`${where}: marginSteps is two page widths in px, the smaller first`)
  if (p.cardRadius !== undefined && !['concentric', 'control', 'level'].includes(p.cardRadius)) throw new Error(`${where}: cardRadius is 'concentric', 'control' or 'level'`)
  if (p.rhythm !== undefined && !['formula', 'line'].includes(p.rhythm)) throw new Error(`${where}: rhythm is 'formula' or 'line'`)
  if (bad.length) throw new Error(`${where}: unknown key${bad.length > 1 ? 's' : ''} ${bad.map((k) => { const [x, dist] = near(k); return `"${k}"${dist <= 3 ? ` (did you mean "${x}"?)` : ''}` }).join(', ')}. Known keys: ${[...known].join(', ')}`)
  return p
}
const lev = (a, b) => { const m = Array.from({ length: a.length + 1 }, (_, i) => [i, ...new Array(b.length).fill(0)]); for (let j = 1; j <= b.length; j++) m[0][j] = j; for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++) m[i][j] = Math.min(m[i - 1][j] + 1, m[i][j - 1] + 1, m[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)); return m[a.length][b.length] }

