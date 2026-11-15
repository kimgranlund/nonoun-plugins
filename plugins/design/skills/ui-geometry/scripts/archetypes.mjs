// Archetypes: profiles over the dials and page ratios (references/archetypes.json).
//   node derive.mjs --archetype fashion      the archetype's dials, then its bands beside the derived values
// An archetype is not a preset. A preset or a page is scored by its distance outside the archetype's bands.
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { PRESETS, derive } from './derive.mjs'
import { positionReport } from './dimensions.mjs'

const FILE = join(dirname(fileURLToPath(import.meta.url)), '..', 'references', 'archetypes.json')
export const loadArchetypes = () => JSON.parse(readFileSync(FILE, 'utf8'))

/** One archetype, or an error that lists the names. */
export function archetype(name, A = loadArchetypes()) {
  const a = A.archetypes[name]
  if (!a) throw new Error(`archetype "${name}" is not in references/archetypes.json. Known: ${Object.keys(A.archetypes).join(', ')}`)
  return a
}

/** A preset and dials for an archetype: its constants over the base preset, then n, density and κ. */
export function applyArchetype(name, { preset = PRESETS.standard, A = loadArchetypes() } = {}) {
  const d = archetype(name, A).dials
  const P = { ...preset, ...(d.constants ?? {}), dials: { ...(preset.dials ?? {}), density: d.density, kappa: { ...d.kappa } } }
  return { preset: P, n: d.n, density: d.density, kappa: { ...d.kappa }, icon: d.icon ?? 'md', ...(d.text ? { text: { ...d.text } } : {}) }
}

/** The size and line of running text: the role a `text` dial names, on a line of `line` × its size; without the dial, n. */
export function runningText({ preset = PRESETS.standard, n = 14, text } = {}) {
  if (!text) return { role: null, size: n, line: null }
  const t = preset.type[text.role]; if (!t) throw new Error(`text.role "${text.role}" is not a type role. Known: ${Object.keys(preset.type).join(', ')}`)
  const size = n + t[0] * (preset.unit.a * n + preset.unit.b); return { role: text.role, size, line: (text.line ?? 1.5) * size }
}

/** The observables a preset fixes, as a page would show them. Everything else in a profile is page composition.
 *  With a `text` dial, body is the running text's size and the icon, label and type contrast are measured against it; h/F stays against the control's own label, n. */
export function observe({ preset = PRESETS.standard, n = 14, density = 'default', kappa = {}, icon = 'md', text } = {}) {
  const rows = derive({ preset, n, density, kappa }), px = (id) => rows.find((r) => r.id === id)?.px
  const u = preset.unit.a * n + preset.unit.b, h = px('controls.control.h'), r = px('controls.curvature.r'), body = runningText({ preset, n, text }).size
  const roles = Object.entries(preset.type).map(([role, [m]]) => ({ role, size: n + m * u, contrast: (n + m * u) / body })).sort((a, b) => a.contrast - b.contrast)
  return {
    values: { body, loft: h / n, kappa2: Math.min(r, h / 2) / (h / 2), iconToBody: px(`controls.icon.a.${icon}`) / body, labelToBody: (n + preset.type['title-sm'][0] * u) / body, measure: preset.measure.ideal },
    roles,
  }
}

/** Distance of one value outside a band, in units of the observable's spread, capped at 3. */
export const outside = (v, [lo, , hi], scale) => Math.min(3, (v < lo ? lo - v : v > hi ? v - hi : 0) / scale)

/** Every archetype ranked for a set of observed values: the mean distance outside its bands, nearest first. */
export function rank(values, A = loadArchetypes()) {
  return Object.entries(A.archetypes).map(([name, a]) => {
    let sum = 0, count = 0; const out = []
    for (const [f, v] of Object.entries(values)) {
      if (v == null || !a.bands[f] || !(f in A.scale)) continue
      const d = outside(v, a.bands[f], A.scale[f]); sum += d; count++
      if (d > 0) out.push(f)
    }
    return { name, family: a.family, distance: count ? sum / count : Infinity, outside: out, count }
  // Nearest first; at equal distance the archetype with more bands for these values has more behind it.
  }).sort((x, y) => x.distance - y.distance || y.count - x.count)
}

/** The largest type role whose size over F is inside the archetype's contrast band. */
export function typeCap(roles, a) {
  const hi = a.bands.contrast?.[2] ?? Infinity
  return roles.filter((r) => r.contrast <= hi + 1e-9).pop()
}

const f2 = (x) => String(Math.round(x * 100) / 100)

/** An archetype's label dial resolved against the type roles: the role's size in px and the space tracking adds after each letter. Null when it has none. */
export function labelTracking(a, roles, n = a.dials?.n) {
  const d = a.dials?.label; if (!d) return null
  const role = roles.find((r) => r.role === (d.role ?? 'label')); if (!role) return null
  const size = role.size ?? role.contrast * n; return { case: d.case ?? 'none', tracking: d.tracking ?? 0, role: role.role, size, perLetter: (d.tracking ?? 0) * size }
}

/** Markdown: an archetype's bands beside what a preset and its dials derive. */
export function archetypeReport(name, o, A = loadArchetypes()) {
  const a = archetype(name, A), { values, roles } = observe({ icon: a.dials.icon, text: a.dials.text, ...o }), cap = typeCap(roles, a), out = []
  out.push(`## archetype ${name}  (${a.status}; ${a.pages} pages; recognised ${a.recognised.first} first, ${a.recognised.inTwo} within two)\n`)
  out.push(`hero: ${a.stance.hero} · space: ${a.stance.space} · the body ${a.stance.body}\n`)
  out.push('| observable | derived from | 25th · median · 75th | derived | |\n|---|---|---|---|---|')
  for (const [f, v] of Object.entries(values)) {
    const b = a.bands[f]; if (!b) continue
    out.push(`| ${f} | ${A.observables[f].derived} | ${b.map(f2).join(' · ')} | ${f2(v)} | ${outside(v, b, A.scale[f]) === 0 ? 'inside' : v < b[0] ? 'below' : 'above'} |`)
  }
  if (a.bands.contrast && cap) out.push(`| contrast | ${A.observables.contrast.derived} | ${a.bands.contrast.map(f2).join(' · ')} | up to ${cap.role} (${f2(cap.contrast)}) | cap |`)
  const page = Object.keys(a.bands).filter((f) => !(f in values) && f !== 'contrast')
  out.push(`\nIcon size in use: ${a.dials.icon ?? 'md'}. Signature: ${a.signature.join(', ') || 'none'}.`)
  const rt = runningText({ preset: o?.preset, n: o?.n ?? a.dials.n, text: o?.text ?? a.dials.text }); if (rt.role) out.push(`Running text: the ${rt.role} role, ${f2(rt.size)}px on a ${f2(rt.line)}px line (${f2(rt.line / rt.size)} × its size), not the role's heading line. Body, icon ÷ body, label ÷ body and type contrast above are against it; h/F is against the control's label, ${f2(o?.n ?? a.dials.n)}px.`)
  const lt = labelTracking(a, roles, o?.n ?? a.dials.n); if (lt) out.push(`Labels: ${lt.case === 'upper' ? 'capitals' : 'as written'}, tracking ${lt.tracking} of the ${lt.role} size (${f2(lt.size)}px): ${f2(lt.perLetter)}px after each letter, and ${f2(lt.perLetter)}px taken back at the label's end.`)
  out.push(`Page composition, not derived: ${page.map((f) => `${f} ${a.bands[f].map(f2).join(' · ')}`).join('; ')}.`)
  const r = rank(values, A)
  out.push(`\nNearest archetypes for the derived values alone: ${r.slice(0, 3).map((x) => `${x.name} ${f2(x.distance)}`).join(', ')}.\n`)
  return out.join('\n')
}

/** Markdown: every archetype ranked for a set of observed values, and where the values leave the nearest one's bands. */
/** The runner-up, when the nearest archetype names it as one it cannot be told from and it lies within 0.05. */
export function nearTwin(ranked, A = loadArchetypes()) {
  const top = ranked[0], near = A.archetypes[top.name].near ?? []
  const second = ranked[1]   // only the runner-up: an archetype of another family that lies closer than the twin is the better second reading
  return second && near.includes(second.name) && second.distance - top.distance <= 0.05 ? second : null
}

export function scoreReport(values, A = loadArchetypes(), { source, position = true } = {}) {
  const r = rank(values, A), given = Object.keys(values).filter((k) => values[k] != null && k in A.scale), out = []
  out.push(`# Archetype score${source ? `: ${source}` : ''}\n`)
  out.push(`${given.length} of ${Object.keys(A.scale).length} observables given. Distance is the mean distance outside an archetype's bands; 0 is inside every band.\n`)
  out.push('| archetype | family | distance | bands used | outside |\n|---|---|---|---|---|')
  for (const x of r) out.push(`| ${x.name} | ${x.family ?? '—'} | ${f2(x.distance)} | ${x.count} | ${x.outside.length} |`)
  const top = r[0], a = A.archetypes[top.name]
  const far = top.outside.map((f) => ({ f, v: values[f], b: a.bands[f], d: outside(values[f], a.bands[f], A.scale[f]) })).sort((x, y) => y.d - x.d)
  const twin = nearTwin(r, A)
  out.push(`\n## Nearest: ${top.name}${twin ? ` (${top.family}; ${twin.name} within ${f2(twin.distance - top.distance)})` : ''}\n`)
  if (twin) out.push(`The measured pages do not separate ${top.name} from ${twin.name}: read this as the ${top.family} family.\n`)
  if (!far.length) out.push('Every given observable is inside its band.')
  else { out.push('| observable | value | 25th · median · 75th | distance |\n|---|---|---|---|'); for (const x of far) out.push(`| ${x.f} | ${f2(x.v)} | ${x.b.map(f2).join(' · ')} | ${f2(x.d)} |`) }
  const sig = a.signature.filter((f) => values[f] != null)
  if (sig.length) out.push(`\nIts signature observables here: ${sig.map((f) => `${f} ${f2(values[f])} (${outside(values[f], a.bands[f], A.scale[f]) === 0 ? 'inside' : 'outside'})`).join(', ')}.`)
  if (position) out.push('\n' + positionReport(values).trimEnd())
  return out.join('\n') + '\n'
}

// node archetypes.mjs <observed.json>: score a file of observables ({ observables: {...} } or a plain object).
// Guarded so the module also loads in a browser bundle, where there is no process.
if (typeof process !== 'undefined' && process.argv?.[1] && fileURLToPath(import.meta.url) === process.argv[1] && process.argv[2]) {
  const data = JSON.parse(readFileSync(process.argv[2], 'utf8'))
  console.log(scoreReport(data.observables ?? data, loadArchetypes(), { source: data.source ?? process.argv[2] }))
}
