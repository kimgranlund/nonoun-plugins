#!/usr/bin/env node
// Fit: find the nearest UI-geometry system behind a project's measured lengths, tier by tier.
//   node fit.mjs lengths.json [--preset standard|file.json] [--json] [--md report.md]
//                [--preset-out fitted.json] [--html compare.html] [--target fitted|preset]
// lengths.json: { "source": "…", "n": 16, "lengths": [ { "id": "button.height", "role": "height", "px": 40, "tier"?: "controls", "n"?: 16 } ] }
// Prints a report: the unit, each tier's constants in notation, identity checks, and every length against
// two targets: the project's own system made consistent ("fitted") and the reference preset at the project's n.

import { readFileSync, writeFileSync, realpathSync } from 'node:fs'
import { rank } from './archetypes.mjs'
import { fileURLToPath } from 'node:url'
import { PRESETS, TIERS, system, tierUnit, crisp, pageLevel } from './derive.mjs'

/** Roles a length can play. Each belongs to one tier and is compared with one symbol. */
export const ROLES = {
  height: { tier: 'controls', symbol: 'h', says: 'control height', compare: 'h = S + 2I' },
  'label-inset': { tier: 'controls', symbol: 'T = 2I', says: 'inline padding to the label (border included)', compare: 'T = 2I' },
  inset: { tier: 'controls', symbol: 'I', says: 'block padding of a control', compare: 'I', collect: false },
  icon: { tier: 'controls', symbol: 'a', says: 'icon size in a control', compare: 'the nearest icon size' },
  radius: { tier: 'controls', symbol: 'r', says: 'control corner radius', compare: 'r(κ_control)' },
  'control-gap': { tier: 'controls', symbol: 'gap', says: 'gap between sibling controls', compare: 'the nearest of 0, g_c, m_c, min(cap, I)' },
  mark: { tier: 'controls', symbol: 'mark', says: 'checkbox, radio, switch, badge size', compare: 'itself, snapped to q/2' },
  row: { tier: 'collections', symbol: 'row', says: 'row or item height in a list, menu, table', compare: 'h at the nearest density' },
  'row-radius': { tier: 'collections', symbol: 'r_row', says: 'item radius inside a frame', compare: 'r_frame − d_c, or r when the frame has no radius' },
  'frame-depth': { tier: 'collections', symbol: 'd_c', says: 'padding of a listbox, menu or segmented host (border included)', compare: 'd_c' },
  'frame-radius': { tier: 'collections', symbol: 'r_frame', says: 'radius of that frame', compare: 'r_frame = min(r(κ_frame), soft)' },
  'row-gap': { tier: 'collections', symbol: 'row gap', says: 'gap between rows or segments', compare: 'the nearest of 0, g_c, the level gutter' },
  'cell-inset': { tier: 'collections', symbol: 'I', says: 'inline padding of a cell or item', compare: 'I (table cells)', collect: false },
  'item-inset': { tier: 'collections', symbol: 'T − d_c', says: 'inline padding of a menu or listbox row (text then sits at T)', compare: 'T − d_c (menu and listbox rows, text at T)' },
  'cell-control': { tier: 'collections', symbol: 'item = h − 2d_c', says: 'height of an input, select or button inside a table cell', compare: 'the item height h − 2d_c', collect: false },
  'host-height': { tier: 'collections', symbol: 'h', says: 'height of a segmented control or tab list (a host of joined controls)', compare: 'h' },
  'host-depth': { tier: 'collections', symbol: '(h − item)/2 = d_c', says: 'padding of that host (border included)', compare: '(h − item)/2 = d_c' },
  'host-radius': { tier: 'collections', symbol: 'r', says: 'radius of that host', compare: 'r' },
  segment: { tier: 'collections', symbol: 'item = h − 2d_c', says: 'height of a segment or tab inside the host', compare: 'the item height h − 2d_c' },
  'segment-radius': { tier: 'collections', symbol: 'r − d_c', says: 'radius of that segment', compare: 'r − d_c' },
  'card-depth': { tier: 'containers', symbol: 'd', says: 'card, dialog or panel padding (border included)', compare: 'd' },
  'card-radius': { tier: 'containers', symbol: 'R', says: 'card corner radius', compare: 'd + min(r(κ_card), soft); 0 at κ_card 0' },
  'card-gap': { tier: 'containers', symbol: 'gap in card', says: 'gap between a card’s children', compare: 'the nearest of d/4, d/2 − I, d/2, d' },
  gutter: { tier: 'layout', symbol: 'G = M/2', says: 'gap between cards or grid columns', compare: 'G = M/2' },
  margin: { tier: 'layout', symbol: 'M', says: 'page margin', compare: 'M = ℓ_page·I' },
  // Read from tokens or measured by hand: the collector does not record these (collect: false).
  'hosted-control': { tier: 'controls', symbol: 'item = h − 2d_c', says: 'a button inside an input (clear, stepper, addon)', compare: 'the item height h − 2d_c', collect: false },
  'inline-control': { tier: 'controls', symbol: 'h_o = S + 2g_c', says: 'height of a chip or tag', compare: 'h_o = S + 2g_c', collect: false },
  'focus-ring': { tier: 'controls', symbol: 'w', says: 'focus ring width', compare: 'w', collect: false },
  'popup-offset': { tier: 'collections', symbol: 'd_c', says: 'gap between a popup and its trigger', compare: 'd_c', collect: false },
  'field-gap': { tier: 'collections', symbol: '2I', says: 'gap between stacked form fields', compare: '2I, as table columns', collect: false },
  'label-gap': { tier: 'collections', symbol: 'g_c', says: 'field label → control, control → help text', compare: 'g_c', collect: false },
  'popover-depth': { tier: 'containers', symbol: 'd_p = ¾d', says: 'popover padding (border included)', compare: 'd_p = popoverRatio·d, snapped to q/2', collect: false },
  'dialog-depth': { tier: 'containers', symbol: 'd_d = 1½d', says: 'dialog padding (border included)', compare: 'd_d = dialogRatio·d, snapped to q/2', collect: false },
  'title-gap': { tier: 'containers', symbol: 'd/2 − I', says: 'gap under a card\'s painted, flush title band (a header takes d)', compare: 'max(0, d/2 − I)', collect: false },
  'section-pad': { tier: 'layout', symbol: '3¼F', says: 'page section padding above and below', compare: 'flow.section·F = 3¼F', collect: false },
}

const median = (a) => { if (!a.length) return undefined; const s = [...a].sort((x, y) => x - y); const m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2 }
/** The most frequent value; a tie goes to the one listed first, so list the primary component first. */
const mode = (a) => {
  if (!a.length) return undefined
  const c = new Map(); for (const v of a) c.set(v, (c.get(v) ?? 0) + 1)
  const top = Math.max(...c.values()); return a.find((v) => c.get(v) === top)
}
const r2 = (x) => Math.round(x * 100) / 100
export const snapHalf = (x) => Math.round(x * 2) / 2
const nearest = (v, list) => list.reduce((b, x) => (Math.abs(x - v) < Math.abs(b - v) ? x : b), list[0])

/**
 * Unit search. A length is on the grid of q when it is a multiple of q/2 within tol px.
 * Every divisor of the true unit also catches its lengths (and a 2px unit catches any whole px), so the score
 * trades the hit rate against distance from the prior (the preset's q at the project's n):
 *   score(q) = hit(q) − λ·|ln(q / prior)|,  λ = 0.25
 * A stray length or two (a 1px border, a one-off) costs a few points of hit rate, not the unit.
 * The runners-up (hit rate within `slack` of the best) are reported.
 */
export function fitUnit(values, { prior = 5, tol = 0.26, lo = 2, hi = 10, step = 0.25, slack = 0.15, lambda = 0.25, div = 2 } = {}) {
  // A value may be { px, alt }: a padding with its border, which also counts as on the grid without it.
  const vs = values.map((v) => (typeof v === 'number' ? { px: v } : v)).filter((v) => v.px > 0)
  if (!vs.length) return { q: prior, hit: 0, whole: 0, candidates: [], assumed: true }
  const cands = []
  for (let q = lo; q <= hi + 1e-9; q += step) {
    let hit = 0, whole = 0
    for (const { px, alt } of vs) {
      const at = (v) => { const m = Math.round(v / (q / div)); return Math.abs(v - m * (q / div)) <= tol ? m * (2 / div) : null }
      const m = at(px) ?? (alt === undefined ? null : at(alt))
      if (m !== null) { hit++; if (m % 2 === 0) whole++ }
    }
    cands.push({ q: r2(q), hit: hit / vs.length, whole: whole / vs.length })
  }
  const best = Math.max(...cands.map((c) => c.hit))
  const score = (c) => c.hit - lambda * Math.abs(Math.log(c.q / prior))
  const ranked = [...cands].sort((a, b) => score(b) - score(a) || b.whole - a.whole)
  const near = ranked.filter((c) => c.hit >= best - slack)
  return { ...ranked[0], best, candidates: [ranked[0], ...near.filter((c) => c !== ranked[0])].slice(0, 4) }
}

/** κ from a radius: the inverse of r(κ) (in px, with soft and h in px). */
export function kappaFor(r, h, soft, ks = 0.75) {
  const half = h / 2, s = Math.min(soft, half)
  if (r >= half - 1e-9) return 1
  if (r <= s) return s > 0 ? (ks * r) / s : 1
  return ks + ((1 - ks) * (r - s)) / (half - s)
}

/** Fit a measured project. Returns the unit, each tier's constants, a fitted preset, identity checks and targets. */
export function fit(data, { preset = PRESETS.standard, tol = 0.26 } = {}) {
  const P = preset, X = system(P)
  const lengths = data.lengths.map((l) => ({ ...l, tier: l.tier ?? ROLES[l.role]?.tier ?? 'controls', px: Number(l.px) }))
  const ns = [...new Set(lengths.map((l) => l.n ?? data.n).filter(Boolean))]
  const n = data.n ?? ns[0] ?? 16
  const prior = X.q(n)
  const notes = []
  if (data.n === undefined && !ns.length) notes.push('No n given: assumed 16px.')

  // Paddings that record a border may sit on the grid with or without it.
  const PADS0 = ['label-inset', 'frame-depth', 'card-depth', 'host-depth'], b0 = (P.border ?? PRESETS.standard.border).width
  const unitVal = (l) => (PADS0.includes(l.role) && l.border > 0 ? { px: l.px, alt: l.px - l.border } : l.px)
  // 1. The unit. Several scopes (lengths tagged with different n) fit q = a·n + b; one scope keeps the preset's slope.
  let unit, q
  if (ns.length >= 2) {
    const pts = ns.map((nn) => { const at = lengths.filter((l) => (l.n ?? data.n) === nn), c = at.filter((l) => l.tier === 'controls'); return [nn, fitUnit((c.length >= 3 ? c : at).map(unitVal), { prior: X.q(nn), tol }).q] })
    const mx = pts.reduce((s, p) => s + p[0], 0) / pts.length, my = pts.reduce((s, p) => s + p[1], 0) / pts.length
    const a = pts.reduce((s, p) => s + (p[0] - mx) * (p[1] - my), 0) / pts.reduce((s, p) => s + (p[0] - mx) ** 2, 0)
    unit = { a: r2(a), b: r2(my - a * mx), scopes: pts }
    q = unit.a * n + unit.b
  } else {
    // Controls own q: the shared unit is fitted on them (when there are enough), so one deviant tier cannot drag it to a divisor.
    const base = lengths.filter((l) => l.tier === 'controls')
    const u = fitUnit((base.length >= 3 ? base : lengths).map(unitVal), { prior, tol })
    q = u.q
    unit = { a: P.unit.a, b: r2(q - P.unit.a * n), hit: u.hit, whole: u.whole, candidates: u.candidates, slopeAssumed: true }
  }

  // 2. A tier may run on its own unit: only when the shared q misses most of its lengths and its own q catches them.
  //    A padding that lands on the shared grid once its border is taken off counts as on it.
  const bpx = (P.border ?? PRESETS.standard.border).width
  const onG = (px, qq) => Math.abs(px - Math.round(px / (qq / 2)) * (qq / 2)) <= tol
  const PADS = ['label-inset', 'frame-depth', 'card-depth', 'host-depth']
  /** The border to take off a padding: the measured one when the length says, else the preset's (assumed). */
  const bOf = (l) => (l.border > 0 ? l.border : 0)
  const units = {}, tierFit = {}
  for (const t of TIERS) {
    const ls = lengths.filter((l) => l.tier === t), vs = ls.map((l) => l.px)
    // Frame and host paddings, item insets and item radii may sit on ¼q (a ¾q frame padding is part of the system),
    // so on the shared grid they count when they land on a quarter of q.
    const QUARTER = ['frame-depth', 'host-depth', 'item-inset', 'row-radius', 'segment-radius']
    const onQ = (px) => Math.abs(px - Math.round(px / (q / 4)) * (q / 4)) <= tol
    const shared = fitUnit(ls.map((l) => (QUARTER.includes(l.role) && onQ(l.px) ? Math.round(l.px / (q / 2)) * (q / 2) : PADS.includes(l.role) && l.border > 0 && !onG(l.px, q) && onG(l.px - bOf(l), q) ? l.px - bOf(l) : l.px)), { prior: q, tol, lo: q, hi: q })
    const own = fitUnit(vs, { prior: q, tol })
    tierFit[t] = { count: vs.length, sharedHit: shared.hit, ownQ: own.q, ownHit: own.hit }
    if (vs.length >= 3 && shared.hit < 0.75 && own.hit >= shared.hit + 0.25 && Math.abs(own.q - q) > 1e-9) {
      units[t] = { a: P.unit.a, b: r2(own.q - P.unit.a * n) }
      notes.push(`${t} runs on its own unit q = ${own.q}px (shared q catches ${Math.round(shared.hit * 100)}%, its own ${Math.round(own.hit * 100)}%).`)
    }
  }
  const qT = (t) => (units[t] ? units[t].a * n + units[t].b : q)
  const of = (role) => lengths.filter((l) => l.role === role).map((l) => l.px)
  const qC = qT('controls'), q2 = qT('collections'), q3 = qT('containers'), q4 = qT('layout')
  const soft = P.soft * qC
  // A padding that is on the grid only without its border did not absorb the border (the system's depth includes it).
  const unborderL = (l, qq, what) => {
    if (!l) return undefined
    const b = bOf(l)
    // Only a recorded border is taken off; an unrecorded one is never guessed (¼q paddings sit off the ½q grid by design).
    if (!(l.border > 0) || onG(l.px, qq) || !onG(l.px - b, qq)) return l.px
    notes.push(`${what} ${l.px}px is read as ${l.px - b}px + the ${b}px border${l.border === undefined ? ' (border assumed: the length did not record one)' : ''}: the padding does not absorb the border.`)
    return l.px - b
  }
  /** The length behind a role's most frequent value. */
  const pickL = (role) => { const v = mode(of(role)); return v === undefined ? undefined : lengths.find((l) => l.role === role && l.px === v) }
  const compOf = (l) => l.component ?? l.id.split('.')[0]

  // 3. Tier 1, controls.
  //    Control sizes are densities when the slot holds still: S = h − 2I is the same at each size and only I changes.
  //    The first listed control sets the default density.
  const sizes = []
  //    Sizes are read in the main scope; lengths from other scopes keep the default density.
  const main = lengths.filter((l) => (l.n ?? n) === n)
  for (const c of [...new Set(main.filter((l) => l.tier === 'controls').map(compOf))]) {
    const ls = main.filter((l) => compOf(l) === c)
    const hl = ls.find((l) => l.role === 'height'), tl = ls.find((l) => l.role === 'label-inset'), il = ls.find((l) => l.role === 'inset')
    if (!hl || (!tl && !il)) continue
    const Ic = tl ? unborderL(tl, qC, `The ${c} label inset`) / 2 : il.px
    sizes.push({ c, h: hl.px, I: Ic, S: hl.px - 2 * Ic })
  }
  const S0 = mode(sizes.map((x) => r2(x.S)))
  let h = sizes.length ? sizes[0].h : mode(of('height')) ?? X.h('default') * qC
  let I = sizes.length ? sizes[0].I : mode(of('inset'))
  if (I === undefined) { I = X.I('default') * qC; notes.push('No label-inset or inset measured: I assumed from the preset.') }
  const S = h - 2 * I
  const keep = sizes.filter((x) => Math.abs(x.S - S) <= tol)
  const Is = [...new Set(keep.map((x) => r2(x.I)))].sort((a, b) => a - b)
  const lower = Is.filter((x) => x < I - tol).pop(), higher = Is.find((x) => x > I + tol)
  const densityOfI = (Ic) => (Math.abs(Ic - I) <= tol ? 'default' : lower !== undefined && Math.abs(Ic - lower) <= tol ? 'compact' : higher !== undefined && Math.abs(Ic - higher) <= tol ? 'loose' : undefined)
  const compDensity = Object.fromEntries(sizes.filter((x) => Math.abs(x.S - S) <= tol).map((x) => [x.c, densityOfI(x.I)]))
  const refOfI = (Ic) => Object.entries(P.inset).reduce((b, [k, v]) => (Math.abs(v * X.q(n) - Ic) < Math.abs(P.inset[b] * X.q(n) - Ic) ? k : b), 'default')
  const compRef = Object.fromEntries(sizes.map((x) => [x.c, refOfI(x.I)]))
  for (const x of sizes) if (Math.abs(x.S - S) > tol) notes.push(`${x.c} (h ${x.h}px, I ${r2(x.I)}px) does not keep the slot: S = ${r2(x.S)}px, not ${r2(S)}px.`)
  if (S0 !== undefined && Math.abs(S0 - S) > tol) notes.push(`Most control sizes keep S = ${S0}px, but the first listed has S = ${r2(S)}px: list the default control first.`)
  const r = mode(of('radius'))
  const icons = [...new Set(of('icon'))].sort((a, b) => a - b)
  const controls = { h, I, S, r, icons, sizes: sizes.map((x) => ({ ...x, density: compDensity[x.c] })), kappa: r === undefined ? P.softAnchor : kappaFor(r, h, soft, P.softAnchor), gaps: [...new Set(of('control-gap'))] }

  // 4. Tier 2, collections.
  const dc = unborderL(pickL('frame-depth'), q2, 'The frame depth'), rf = mode(of('frame-radius')), rr = mode(of('row-radius')), row = mode(of('row'))
  const host = { hh: mode(of('host-height')), hd: unborderL(pickL('host-depth'), q2, 'The host depth'), hr: mode(of('host-radius')), seg: mode(of('segment')), segR: mode(of('segment-radius')) }
  const collections = { row, dc, rf, rr, host, kappa: rf === undefined ? controls.kappa : kappaFor(rf, h, soft, P.softAnchor), gaps: [...new Set(of('row-gap'))] }

  // 5. Tier 3, containers.
  const d = unborderL(pickL('card-depth'), q3, 'The card depth'), R = mode(of('card-radius'))
  const inner = d !== undefined && R !== undefined ? R - d : undefined
  const containers = { d, R, inner, kappa: inner === undefined ? controls.kappa : kappaFor(Math.max(0, inner), h, soft, P.softAnchor), gaps: [...new Set(of('card-gap'))] }

  // 6. Tier 4, layout.
  const G = mode(of('gutter')), M = mode(of('margin'))
  const layout = { G, M }

  // 7. The fitted preset: the project's constants in q, snapped to half-q.
  const Iq = snapHalf(I / qC)
  const Pf = JSON.parse(JSON.stringify(P))
  Pf.unit = { a: unit.a, b: unit.b, nMin: P.unit.nMin }
  if (Object.keys(units).length) Pf.units = units
  // h snaps first and the slot takes the rest, so h = S + 2I holds exactly in the fitted system.
  Pf.inset = { compact: lower !== undefined ? snapHalf(lower / qC) : Math.max(0.5, Iq - 0.5), default: Iq, loose: higher !== undefined ? snapHalf(higher / qC) : Iq + 0.5 }
  Pf.slot = snapHalf(h / qC) - 2 * Iq
  const iq = icons.map((a) => snapHalf(a / qC))
  if (iq.length === 1) Pf.icons = { sm: iq[0] - 0.5, md: iq[0], lg: iq[0] + 0.5, full: Pf.slot }
  else if (iq.length) Pf.icons = { sm: iq[0], md: iq[Math.min(1, iq.length - 1)], lg: iq[Math.min(2, iq.length - 1)], full: Pf.slot }
  // A frame that pads like the segmented host (m_c at its density) keeps the shared rule; any other padding is fixed.
  if (dc !== undefined) Pf.frameDepth = Math.abs(dc - (I - P.gutter * qC)) <= tol ? 'm_c' : Math.round((dc / q2) * 4) / 4
  const gcp = P.gutter * qC
  if (row !== undefined) Pf.frameRow = dc !== undefined && Math.abs(row - (h - 2 * dc)) <= tol ? 'fit' : Math.abs(row - (S + 2 * (I - gcp))) <= tol ? 'm_c' : Math.abs(row - (S + 2 * gcp)) <= tol ? 'h_o' : 'h'
  if (M !== undefined) Pf.levels = { ...P.levels, page: snapHalf(M / (Iq * qC)) || pageLevel(P) }
  const dq = d === undefined ? 4 : snapHalf(d / q3)
  Pf.cardDepths = [...new Set([...P.cardDepths, dq])].sort((a, b) => a - b)
  const kappa = { control: controls.kappa, frame: collections.kappa, card: containers.kappa, panel: containers.kappa }
  Pf.dials = { kappa: Object.fromEntries(Object.entries(kappa).map(([t, v]) => [t, r2(v)])), cardDepth: dq, density: 'default' }

  // 8. Targets: the fitted system, and the reference preset at the project's n (nearest density and card depth).
  const refDensity = refOfI(I)
  const targets = {
    fitted: { P: Pf, n, density: 'default', kappa, d: dq },
    preset: { P, n, density: refDensity, kappa, d: nearest(d === undefined ? 4 : d / X.q(n), P.cardDepths) },
  }
  const rounded = new Set(lengths.filter((l) => l.role === 'frame-radius' && l.px > 0).map(compOf))
  const rowsOut = lengths.map((l0) => {
    const l = l0.role === 'row-radius' && !rounded.has(compOf(l0)) ? { ...l0, squareFrame: true } : l0
    // A length from another scope is compared at its own n.
    const nn = l.n ?? n, U = units[l.tier] ?? unit, qt = U.a * nn + U.b
    const m = Math.round(l.px / (qt / 2)), onGrid = Math.abs(l.px - m * (qt / 2)) <= tol
    // A control is compared at its own size's density.
    const c = compOf(l), inMain = (l.n ?? n) === n
    const dF = (inMain && compDensity[c]) || 'default', dP = (inMain && compRef[c]) || refDensity
    const fitted = targetPx(l, { ...targets.fitted, n: nn, density: dF }), ref = targetPx(l, { ...targets.preset, n: nn, density: dP })
    const borderOnly = !onGrid && PADS.includes(l.role) && l.border > 0 && onG(l.px - bOf(l), qt)
    return { ...l, density: compDensity[c], inQ: r2(l.px / qt), onGrid, borderOnly, fitted: r2(fitted), dFitted: r2(fitted - l.px), preset: r2(ref), dPreset: r2(ref - l.px) }
  })

  // 9. Identities.
  const checks = []
  const chk = (tier, name, ok, detail) => checks.push({ tier, name, ok, detail })
  if (h !== undefined) chk('controls', 'h = S + 2I gives a slot at least the icon', icons.every((a) => a <= S + tol), `S = h − 2I = ${r2(S)}px; icons ${icons.join(', ') || '—'}px`)
  if (h !== undefined) chk('controls', `h meets the pointer target (${P.targets?.pointer ?? 24}px)`, h >= (P.targets?.pointer ?? 24), `h = ${h}px`)
  if (rf !== undefined && rr !== undefined && dc !== undefined) chk('collections', 'concentric rows: r_row = r_frame − d_c', Math.abs(rr - Math.max(0, rf - dc)) <= tol, `${rr} vs ${rf} − ${dc} = ${Math.max(0, rf - dc)}px`)
  if (sizes.length > 1) chk('controls', 'every control size keeps the slot: S = h − 2I', sizes.every((x) => Math.abs(x.S - S) <= tol), sizes.map((x) => `${x.c} ${x.h} = ${r2(x.S)} + 2·${r2(x.I)}`).join('; '))
  if (host.hh !== undefined && host.hd !== undefined && host.seg !== undefined) chk('collections', 'segments fill the host: item = h_host − 2·host padding', Math.abs(host.seg - (host.hh - 2 * host.hd)) <= 1, `${host.seg} vs ${host.hh} − 2·${host.hd} = ${host.hh - 2 * host.hd}px`)
  if (host.hr !== undefined && host.hd !== undefined && host.segR !== undefined) chk('collections', 'concentric segments: r_seg = r_host − host padding', Math.abs(host.segR - Math.max(0, host.hr - host.hd)) <= tol, `${host.segR} vs ${host.hr} − ${host.hd} = ${Math.max(0, host.hr - host.hd)}px`)
  for (const v of [...new Set(of('row'))]) chk('collections', `row ${v}px is a control height (h at some density, an item h − 2d_c or S + 2m_c, or h_o)`, sizes.some((x) => Math.abs(x.h - v) <= tol) || Math.abs(v - h) <= tol || Math.abs(v - (S + 2 * P.gutter * qC)) <= tol || Math.abs(v - (S + 2 * (I - P.gutter * qC))) <= tol || (dc !== undefined && Math.abs(v - (h - 2 * dc)) <= tol), `control heights ${[...new Set([h, ...sizes.map((x) => x.h)])].join(', ')}px`)
  if (inner !== undefined) chk('containers', 'concentric card: R − d = min(r, soft)', r !== undefined && Math.abs(inner - Math.min(r, soft)) <= tol, `R − d = ${r2(inner)}px, min(r, soft) = ${r === undefined ? '—' : r2(Math.min(r, soft))}px`)
  if (inner !== undefined && inner < 0) chk('containers', 'no negative inner radius', false, `R ${R} < d ${d}`)
  for (const g of containers.gaps) if (d !== undefined) chk('containers', `card gap ${g}px on the d ladder (d/4, d/2 − I, d/2, d)`, [d / 4, d / 2 - I, d / 2, d].some((x) => Math.abs(x - g) <= tol), `d = ${d}px`)
  if (G !== undefined && M !== undefined) chk('layout', 'G = M/2 (the gutter is half the margin)', Math.abs(G - M / 2) <= q4 / 2 + tol, `G ${G}px, M/2 ${r2(M / 2)}px`)
  if (G !== undefined && M !== undefined) chk('layout', 'M is a whole multiple of I', Math.abs(M / I - Math.round(M / I)) < 0.01, `M = ${M}px = ${r2(M / I)}·I`)

  // 10. Conformance per tier: the share of lengths already at the target.
  const conformance = Object.fromEntries(TIERS.map((t) => {
    const ls = rowsOut.filter((x) => x.tier === t)
    const at = (k) => (ls.length ? ls.filter((x) => Math.abs(x[k]) <= tol).length / ls.length : null)
    return [t, { count: ls.length, onGrid: ls.length ? ls.filter((x) => x.onGrid).length / ls.length : null, fitted: at('dFitted'), preset: at('dPreset') }]
  }))

  return { source: data.source, n, q, unit, units, tierFit, notes, tiers: { controls, collections, containers, layout }, kappa, preset: Pf, refDensity, targets: { fitted: { density: 'default', d: dq }, preset: { density: refDensity, d: targets.preset.d } }, checks, conformance, lengths: rowsOut }
}

/** The px a length would have in a target system. */
export function targetPx(l, { P: P0, n, density: dn, kappa: k, d }) {
  // Targets use the crisp preset at n, as derive does: I, g_c and S on whole px.
  const P = crisp(P0, n), X = system(P)
  const u = (t) => tierUnit(P, t, n), uC = u('controls'), u2 = u('collections'), u3 = u('containers'), u4 = u('layout')
  const I = X.I(dn), gc = P.gutter
  const rf = Math.min(X.radius(k.frame, dn) * uC, P.soft * u2)
  const dcPx = X.dc(dn) * (typeof P.frameDepth === 'number' ? u2 : uC)
  const snapIn = (t) => snapHalf(l.px / u(t)) * u(t)
  switch (l.role) {
    case 'height': return X.h(dn) * uC
    case 'label-inset': return 2 * I * uC
    case 'inset': return I * uC
    case 'icon': return nearest(l.px / uC, Object.values(P.icons)) * uC
    case 'radius': return X.radius(k.control, dn) * uC
    case 'control-gap': return nearest(l.px / uC, [0, gc, X.mc(dn), X.levelGutter('group', dn)]) * uC
    // A row takes the height of the nearest density: a list may run compact inside a default page.
    case 'row': return nearest(l.px / uC, [...Object.keys(P.inset).map((x) => X.h(x)), X.frameRow(dn)]) * uC
    // Rows in a frame with no radius (a square region) have nothing to be concentric with: they take r.
    case 'row-radius': return l.squareFrame ? X.radius(k.control, dn) * uC : Math.max(0, rf - dcPx)
    case 'frame-depth': return dcPx
    case 'frame-radius': return rf
    case 'row-gap': return nearest(l.px / uC, [0, gc, X.levelGutter('collection', dn)]) * uC
    case 'cell-inset': return I * uC
    case 'item-inset': return (2 * I - X.dc(dn)) * uC
    case 'host-height': return X.h(dn) * uC
    case 'host-depth': return X.hostPad(dn) * uC
    case 'host-radius': return X.radius(k.control, dn) * uC
    case 'segment': case 'cell-control': return X.frameRow(dn) * uC
    case 'segment-radius': return X.inward(X.radius(k.control, dn), X.hostPad(dn)) * uC
    case 'card-depth': return d * u3
    case 'card-radius': return d === 0 ? X.radius(k.card, dn) * uC : d * u3 + Math.min(X.radius(k.card, dn) * uC, P.soft * u3)
    case 'card-gap': return nearest(l.px / u3, [Math.round(d / 2) / 2, Math.max(0, snapHalf(d / 2 - I * uC / u3)), snapHalf(d / 2), d]) * u3
    case 'gutter': return snapHalf((pageLevel(P) * I * uC) / u4 / 2) * u4
    case 'margin': return pageLevel(P) * I * uC
    case 'hosted-control': return X.frameRow(dn) * uC
    case 'inline-control': return (P.slot + 2 * gc) * uC
    case 'focus-ring': return P.focus.width * uC
    case 'popup-offset': return dcPx
    case 'field-gap': return 2 * I * uC
    case 'label-gap': return gc * uC
    case 'popover-depth': return snapHalf((P.spacing?.popoverRatio ?? 0.75) * d) * u3
    case 'dialog-depth': return snapHalf((P.spacing?.dialogRatio ?? 1.5) * d) * u3
    case 'title-gap': return Math.max(0, snapHalf(d / 2 - I * uC / u3)) * u3
    case 'section-pad': return Math.round((P.flow?.section ?? 3.25) * n)
    default: return snapIn(l.tier)
  }
}

const pct = (x) => (x === null || x === undefined ? '—' : `${Math.round(x * 100)}%`)
const f = (x) => (x === undefined || x === null || Number.isNaN(x) ? '—' : String(r2(x)))
const sign = (x) => (Math.abs(x) < 0.005 ? '0' : x > 0 ? `+${r2(x)}` : String(r2(x)))

/** The report as Markdown. */
export function report(R, presetName = 'standard') {
  const { tiers: T, q } = R, Pf = R.preset, qI = (v, qq = q) => (v === undefined ? '—' : `${f(v / qq)}q`)
  const out = []
  out.push(`# Geometry fit${R.source ? `: ${R.source}` : ''}\n`)
  out.push(`n = ${R.n}px · q = ${f(q)}px${R.unit.slopeAssumed ? ` (one scope: slope a = ${R.unit.a} assumed, so q = ${R.unit.a}·n ${R.unit.b < 0 ? '−' : '+'} ${Math.abs(R.unit.b)})` : ` = ${R.unit.a}·n ${R.unit.b < 0 ? '−' : '+'} ${Math.abs(R.unit.b)} from ${R.unit.scopes.length} scopes`}`)
  if (R.unit.candidates) out.push(`Units that fit as well: ${R.unit.candidates.map((c) => `${c.q}px (${pct(c.hit)} on grid, ${pct(c.whole)} whole)`).join(' · ')}`)
  for (const nt of R.notes) out.push(`- ${nt}`)
  out.push('\n## Tiers\n\n| tier | lengths | on the q/2 grid | at fitted target | at ' + presetName + ' target |\n|---|---|---|---|---|')
  for (const t of TIERS) { const c = R.conformance[t]; out.push(`| ${t} | ${c.count} | ${pct(c.onGrid)} | ${pct(c.fitted)} | ${pct(c.preset)} |`) }
  out.push(`\n${presetName} target: density ${R.refDensity}, card depth ${R.targets.preset.d}q, κ as fitted.`)

  out.push('\n## Notation\n')
  out.push(`**Controls** (own: q, I, S, h, κ_control, icons)\n`)
  out.push(`- I = ${f(T.controls.I)}px = ${qI(T.controls.I)} · S = ${f(T.controls.S)}px = ${qI(T.controls.S)} · h = S + 2I = ${f(T.controls.h)}px = ${qI(T.controls.h)}`)
  out.push(`- r = ${f(T.controls.r)}px = ${qI(T.controls.r)} → κ_control = ${f(T.controls.kappa)}`)
  out.push(`- icons: ${T.controls.icons.map((a) => `${a}px = ${qI(a)}`).join(', ') || '—'}`)
  if (T.controls.sizes.length > 1) out.push(`- sizes: ${T.controls.sizes.map((x) => `${x.c} h ${f(x.h)} = S ${f(x.S)} + 2·${f(x.I)} (${x.density ?? 'off the slot'})`).join(' · ')}`)
  if (T.controls.gaps.length) out.push(`- gaps: ${T.controls.gaps.map((g) => `${g}px = ${qI(g)} = ${f(g / T.controls.I)}·I`).join(', ')}`)
  const q2 = R.units.collections ? R.units.collections.a * R.n + R.units.collections.b : q
  out.push(`\n**Collections** (own: d_c, κ_frame; reads h, r)\n`)
  out.push(`- row = ${f(T.collections.row)}px = ${qI(T.collections.row, q2)} · d_c = ${f(T.collections.dc)}px = ${qI(T.collections.dc, q2)}`)
  out.push(`- r_frame = ${f(T.collections.rf)}px → κ_frame = ${f(T.collections.kappa)} · r_row = ${f(T.collections.rr)}px (concentric: r_frame − d_c = ${f(T.collections.rf === undefined || T.collections.dc === undefined ? undefined : Math.max(0, T.collections.rf - T.collections.dc))}px)`)
  const H = T.collections.host
  if (H.hh !== undefined) out.push(`- host: h ${f(H.hh)}px, padding ${f(H.hd)}px, r ${f(H.hr)}px · segment ${f(H.seg)}px, r ${f(H.segR)}px`)
  const q3 = R.units.containers ? R.units.containers.a * R.n + R.units.containers.b : q
  out.push(`\n**Containers** (own: d, κ_card; reads r)\n`)
  out.push(`- d = ${f(T.containers.d)}px = ${qI(T.containers.d, q3)} · R = ${f(T.containers.R)}px = ${qI(T.containers.R, q3)} · R − d = ${f(T.containers.inner)}px → κ_card = ${f(T.containers.kappa)}`)
  if (T.containers.gaps.length && T.containers.d) out.push(`- gaps: ${T.containers.gaps.map((g) => `${g}px = ${f(g / T.containers.d)}·d`).join(', ')}`)
  const q4 = R.units.layout ? R.units.layout.a * R.n + R.units.layout.b : q
  out.push(`\n**Layout** (own: G, M; reads the minimum card width)\n`)
  out.push(`- G = ${f(T.layout.G)}px = ${qI(T.layout.G, q4)} · M = ${f(T.layout.M)}px = ${qI(T.layout.M, q4)} = ${f(T.layout.M === undefined ? undefined : T.layout.M / T.controls.I)}·I`)
  out.push(`\nFitted preset: unit ${Pf.unit.a}·n ${Pf.unit.b < 0 ? '−' : '+'} ${Math.abs(Pf.unit.b)}, inset ${JSON.stringify(Pf.inset)}, slot ${Pf.slot}, icons ${JSON.stringify(Pf.icons)}, d_c ${Pf.frameDepth}, page ${Pf.levels.page}·I.`)

  // Archetypes, from the three figures a fit has: n, control height and control radius. Page composition decides the rest.
  const hh = T.controls.h, rr = T.controls.r
  if (hh) {
    const ranked = rank({ body: R.n, loft: hh / R.n, kappa2: rr === undefined ? undefined : Math.min(rr, hh / 2) / (hh / 2) })
    out.push(`\n## Archetype\n\nh/F = ${f(hh / R.n)}. Nearest by n, h/F and control curvature: ${ranked.slice(0, 3).map((x) => `${x.name} (${f(x.distance)})`).join(', ')}. A distance of 0 is inside every band; text and image coverage, which a fit does not measure, decide between near ones (references/archetypes.json).`)
  }
  out.push('\n## Identities\n')
  for (const c of R.checks) out.push(`- ${c.ok ? '✓' : '✗'} ${c.tier}: ${c.name}. ${c.detail}`)

  out.push(`\n## Lengths\n\n| id | tier | role | px | q | grid | fitted | Δ | ${presetName} | Δ |\n|---|---|---|---|---|---|---|---|---|---|`)
  for (const t of TIERS) for (const l of R.lengths.filter((x) => x.tier === t)) out.push(`| ${l.id} | ${l.tier} | ${l.role} | ${f(l.px)} | ${f(l.inQ)} | ${l.onGrid ? '✓' : '✗'} | ${f(l.fitted)} | ${sign(l.dFitted)} | ${f(l.preset)} | ${sign(l.dPreset)} |`)
  const out2 = R.lengths.filter((l) => !l.onGrid || Math.abs(l.dFitted) > 0.26)
  if (out2.length) { out.push('\n## Outliers\n'); for (const l of out2) out.push(`- ${l.id}: ${f(l.px)}px${l.onGrid ? '' : l.borderOnly ? ' is on the grid only without its border' : ' is off the q/2 grid'}${Math.abs(l.dFitted) > 0.26 ? `; the fitted system puts it at ${f(l.fitted)}px` : ''}`) }
  return out.join('\n') + '\n'
}

/** A standalone before/after page: one specimen per component, drawn with measured px and with each target. */
export function compareHtml(R, presetName = 'standard') {
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c])
  const comps = new Map()
  for (const l of R.lengths) {
    const c = l.component ?? l.id.split('.')[0]
    if (!comps.has(c)) comps.set(c, { name: c, tier: l.tier, roles: {} })
    comps.get(c).roles[l.role] = l
  }
  const v = (c, role, key) => c.roles[role]?.[key]
  const ctl = (key) => {
    const base = [...comps.values()].find((c) => c.roles.height)
    return { h: base ? v(base, 'height', key) : 32, r: base ? v(base, 'radius', key) ?? 6 : 6, p: base ? v(base, 'label-inset', key) ?? 12 : 12 }
  }
  const specimen = (c, key) => {
    const g = (role, fb) => v(c, role, key) ?? fb
    if (c.roles.height || c.roles['label-inset'] || c.roles['control-gap']) {
      const base = ctl(key)
      const h = g('height', base.h), p = g('label-inset', base.p), r = g('radius', base.r), a = g('icon', 0), gap = g('control-gap', 8)
      const one = (label, icon) => `<span class="ctl" style="height:${h}px;padding:0 ${p}px;border-radius:${Math.min(r, h / 2)}px;gap:${Math.max(4, (h - (a || 16)) / 4)}px">${icon && a ? `<i style="width:${a}px;height:${a}px"></i>` : ''}${label}</span>`
      return `<div class="row" style="gap:${gap}px">${one('Save', true)}${one('Cancel', false)}</div>`
    }
    if (c.roles['host-height'] || c.roles.segment) {
      const hh = g('host-height', ctl(key).h), hd = g('host-depth', 3), hr = g('host-radius', ctl(key).r), seg = g('segment', hh - 2 * hd), sr = g('segment-radius', Math.max(0, hr - hd))
      return `<div class="host" style="height:${hh}px;padding:${hd}px;border-radius:${hr}px">${['Overview', 'Details', 'Notes'].map((t, k) => `<span class="seg${k === 0 ? ' on' : ''}" style="height:${seg}px;border-radius:${sr}px">${t}</span>`).join('')}</div>`
    }
    if (c.roles['frame-depth'] || c.roles.row) {
      const d = g('frame-depth', 4), rf = g('frame-radius', 0), row = g('row', ctl(key).h), rr = g('row-radius', Math.max(0, rf - d)), gap = g('row-gap', 0), ci = g('cell-inset', 8)
      return `<div class="frame" style="padding:${d}px;border-radius:${rf}px;gap:${gap}px">${['Inbox', 'Drafts', 'Archive'].map((t, k) => `<span class="item${k === 1 ? ' on' : ''}" style="height:${row}px;border-radius:${rr}px;padding:0 ${ci}px">${t}</span>`).join('')}</div>`
    }
    if (c.roles['card-depth'] || c.roles['card-radius']) {
      const d = g('card-depth', 16), R = g('card-radius', 12), gap = g('card-gap', d / 2), { h } = ctl(key)
      return `<div class="card" style="padding:${d}px;border-radius:${R}px;gap:${gap}px"><b style="height:${h}px">Card title</b><span class="bar"></span><span class="bar short"></span></div>`
    }
    if (c.roles.gutter || c.roles.margin) {
      const G = g('gutter', 16), M = g('margin', 24)
      return `<div class="page" style="padding:0 ${M}px;gap:${G}px"><span></span><span></span><span></span></div>`
    }
    const vals = Object.values(c.roles)
    return `<div class="row">${vals.map((l) => `<span class="sq" style="width:${l[key]}px;height:${l[key]}px" title="${esc(l.id)}"></span>`).join('')}</div>`
  }
  const deltas = (c, key, dk) => Object.values(c.roles).filter((l) => Math.abs(l[dk]) > 0.26).map((l) => `${esc(l.role)} ${f(l.px)}→${f(l[key])}`).join(' · ') || 'no change'
  const sections = TIERS.map((t) => {
    const cs = [...comps.values()].filter((c) => c.tier === t)
    if (!cs.length) return ''
    const c0 = R.conformance[t]
    return `<section><h2>${t}<small>${pct(c0.onGrid)} on grid · ${pct(c0.fitted)} at fitted · ${pct(c0.preset)} at ${esc(presetName)}</small></h2>${cs.map((c) => `
<div class="cmp"><h3>${esc(c.name)}</h3>
<figure><figcaption>Before (measured)</figcaption>${specimen(c, 'px')}</figure>
<figure><figcaption>Fitted system<em>${deltas(c, 'fitted', 'dFitted')}</em></figcaption>${specimen(c, 'fitted')}</figure>
<figure><figcaption>${esc(presetName)} at n ${R.n}<em>${deltas(c, 'preset', 'dPreset')}</em></figcaption>${specimen(c, 'preset')}</figure></div>`).join('')}</section>`
  }).join('')
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>Geometry fit</title><meta name="claude:viewport-fit-sides" content="cover">
<style>
:root{--bg:#F4F4F2;--panel:#FFFFFF;--ink:#1A1A1E;--mute:#62626B;--line:#DCDCE0;--fill:#ECECEF;--accent:#2B54D4;--onaccent:#FFFFFF;--delta:#B45309}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141416;--panel:#1E1E22;--ink:#EDEDF0;--mute:#A0A0AA;--line:#34343A;--fill:#2A2A30;--accent:#7C9BFF;--onaccent:#0E1430;--delta:#F59E0B;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#141416;--panel:#1E1E22;--ink:#EDEDF0;--mute:#A0A0AA;--line:#34343A;--fill:#2A2A30;--accent:#7C9BFF;--onaccent:#0E1430;--delta:#F59E0B;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;padding-block:24px;padding-left:max(16px, env(safe-area-inset-left, 0px));padding-right:max(16px, env(safe-area-inset-right, 0px));background:var(--bg);color:var(--ink);font:14px/20px Inter,system-ui,sans-serif}
header,section{max-width:1200px;margin:0 auto 16px}.findings{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:4px 24px;margin:12px 0 0;padding:0;list-style:none;font-size:13px}.findings li{display:flex;gap:8px}.findings b{font-weight:600;min-width:1em}.ok{color:var(--mute)}.bad b{color:var(--delta)}h1{font-size:20px;margin:0 0 4px}header p{margin:0;color:var(--mute)}
section{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:16px}h2{margin:0 0 8px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;display:flex;gap:12px;align-items:baseline}h2 small{letter-spacing:0;text-transform:none;font-weight:400;color:var(--mute)}
.cmp{display:grid;grid-template-columns:120px repeat(3,minmax(0,1fr));gap:12px;align-items:start;padding:12px 0;border-top:1px solid var(--line)}h3{margin:0;font-size:13px}
@media (max-width:760px){.cmp{grid-template-columns:1fr}}
figure{margin:0;display:flex;flex-direction:column;gap:8px;min-width:0}figcaption{font-size:12px;color:var(--mute);display:flex;flex-direction:column}figcaption em{font-style:normal;color:var(--delta)}
.row{display:flex;flex-wrap:wrap;align-items:center}.ctl{display:inline-flex;align-items:center;background:var(--accent);color:var(--onaccent);font-weight:600}.ctl+.ctl{background:var(--fill);color:var(--ink)}.ctl i{display:inline-block;border-radius:2px;background:currentColor;opacity:.6}
.host{display:inline-flex;box-sizing:border-box;background:var(--fill);align-items:center}.seg{display:flex;align-items:center;padding:0 10px;font-size:13px;color:var(--mute)}.seg.on{background:var(--panel);color:var(--ink);box-shadow:0 1px 2px rgba(0,0,0,.12)}
.frame{display:flex;flex-direction:column;border:1px solid var(--line);background:var(--panel);max-width:220px}.item{display:flex;align-items:center}.item.on{background:var(--fill)}
.card{display:flex;flex-direction:column;border:1px solid var(--line);background:var(--bg);max-width:280px}.card b{display:flex;align-items:center;padding:0 12px}.bar{height:12px;border-radius:6px;background:var(--fill)}.bar.short{width:60%}
.page{display:grid;grid-template-columns:repeat(3,1fr);height:64px;background:var(--fill);border-radius:8px}.page span{background:var(--panel);border:1px dashed var(--line)}
.sq{display:inline-block;background:var(--fill);border:1px solid var(--line);margin-right:8px}
</style></head><body><header><h1>Geometry fit${R.source ? `: ${esc(R.source)}` : ''}</h1><p>n ${R.n}px · q ${f(R.q)}px · κ control ${f(R.kappa.control)}, frame ${f(R.kappa.frame)}, card ${f(R.kappa.card)}. Each specimen is drawn with the measured lengths, the project's own system made consistent, and ${esc(presetName)}.</p><ul class="findings">${R.notes.map((x) => `<li class="bad"><b>!</b><span>${esc(x)}</span></li>`).join('')}${R.checks.map((c) => `<li class="${c.ok ? 'ok' : 'bad'}"><b>${c.ok ? '✓' : '✗'}</b><span>${esc(c.tier)}: ${esc(c.name)}. ${esc(c.detail)}</span></li>`).join('')}</ul></header>${sections}</body></html>`
}

const isMain = () => { try { return realpathSync(process.argv[1]) === fileURLToPath(import.meta.url) } catch { return false } }
if (isMain()) {
  const argv = process.argv.slice(2)
  const get = (k) => { const i = argv.indexOf(`--${k}`); return i < 0 ? undefined : argv[i + 1] }
  const file = argv.find((a, i) => !a.startsWith('--') && !argv[i - 1]?.startsWith('--'))
  if (!file) { console.error('usage: node fit.mjs lengths.json [--preset standard|file.json] [--json] [--md out.md] [--preset-out fitted.json] [--html compare.html]'); process.exit(2) }
  const pname = get('preset') ?? 'standard'
  const preset = pname in PRESETS ? PRESETS[pname] : { ...PRESETS.standard, ...JSON.parse(readFileSync(pname, 'utf8')) }
  const R = fit(JSON.parse(readFileSync(file, 'utf8')), { preset })
  const label = pname in PRESETS ? pname : 'reference'
  if (get('preset-out')) writeFileSync(get('preset-out'), JSON.stringify(R.preset, null, 2) + '\n')
  if (get('html')) writeFileSync(get('html'), compareHtml(R, label))
  if (get('md')) writeFileSync(get('md'), report(R, label))
  console.log(argv.includes('--json') ? JSON.stringify(R, null, 2) : report(R, label))
}
