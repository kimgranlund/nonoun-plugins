// Spec loading, merging and packing for ui-showcase-bento. No dependencies.
import { readFileSync, existsSync } from 'node:fs'
import { dirname, resolve, join } from 'node:path'
import { fileURLToPath } from 'node:url'

export const SKILL = resolve(dirname(fileURLToPath(import.meta.url)), '..')
export const SKILLS = resolve(SKILL, '..')
let WORK = process.cwd()
export const setWork = (dir) => { WORK = resolve(dir) }

export const DEFAULTS = {
  canvas: { width: 1280, height: 960 },
  chrome: { margin: 16, gutter: 12, pad: 16, radius: 12, titleGap: 8, specimenGap: 16, captionGap: 6, header: 0,
    font: 'system-ui, -apple-system, "Segoe UI", sans-serif', title: 13, caption: 11,
    texture: 'grid', grid: 8, gridMajor: 4,
    gridStrength: [14, 32], gridStrengthDark: [8, 20], darkThemes: ['dark', 'dim'] },
}

// The closed sets of the source contract, declared once. validateSource() refuses anything outside them, so a typo
// ("colours", "grids", a misspelt group) fails loudly instead of doing nothing. references/contract.md documents them.
export const SETS = {
  specKeys: ['id', 'title', 'brief', 'owns', 'groups', 'areas', 'mins', 'canvas', 'chrome', 'axes', 'tokens', 'acceptance', 'note'],
  owns: ['lengths', 'colors', 'paint'],          // paint is informational: no chrome field belongs to it
  canvasKeys: ['width', 'height'],
  chromeKeys: [...Object.keys(DEFAULTS.chrome), 'colors', 'derived', 'colorsNote'],
  colorKeys: ['bg', 'tile', 'fg', 'muted', 'line', 'slot'],
  textures: ['grid', 'none'],
  axisKeys: ['name', 'label', 'attr', 'values', 'invariant', 'target', 'aliases', 'captions'],
  targets: ['root', 'canvas'],
  tokenKeys: ['css', 'commands'],
  groupKeys: ['id', 'label', 'layout', 'min', 'specimens'],
  groupLayouts: ['column'],
  specimenKeys: ['id', 'label', 'depiction', 'grow', 'briefRow'],
}

const outside = (obj, allowed, where) => {
  const bad = Object.keys(obj ?? {}).filter((k) => !allowed.includes(k))
  if (bad.length) throw new Error(`${where}: unknown key${bad.length > 1 ? 's' : ''} ${bad.join(', ')} (allowed: ${allowed.join(', ')})`)
}
export function validateSource(s) {
  const at = `source ${s.id ?? '?'}`
  if (!s.id) throw new Error('every source needs an id')
  outside(Object.fromEntries(Object.entries(s).filter(([k]) => !['dir', 'catalogue'].includes(k))), SETS.specKeys, at)
  for (const o of s.owns ?? []) if (!SETS.owns.includes(o)) throw new Error(`${at}: owns "${o}" is not one of ${SETS.owns.join(', ')}`)
  outside(s.canvas, SETS.canvasKeys, `${at} canvas`)
  outside(s.chrome, SETS.chromeKeys, `${at} chrome`)
  outside(s.chrome?.colors, SETS.colorKeys, `${at} chrome.colors`)
  if (s.chrome?.texture && !SETS.textures.includes(s.chrome.texture)) throw new Error(`${at}: texture "${s.chrome.texture}" is not one of ${SETS.textures.join(', ')}`)
  outside(s.tokens, SETS.tokenKeys, `${at} tokens`)
  for (const a of s.axes ?? []) {
    outside(a, SETS.axisKeys, `${at} axis ${a.name}`)
    if (a.target && !SETS.targets.includes(a.target)) throw new Error(`${at} axis ${a.name}: target "${a.target}" is not one of ${SETS.targets.join(', ')}`)
    for (const v of Object.values(a.aliases ?? {})) if (!a.values?.includes(v)) throw new Error(`${at} axis ${a.name}: alias points to "${v}", not one of its values`)
    for (const k of Object.keys(a.captions ?? {})) if (!a.values?.includes(k)) throw new Error(`${at} axis ${a.name}: caption for "${k}", not one of its values`)
  }
  for (const g of Array.isArray(s.groups) ? s.groups : []) {
    outside(g, SETS.groupKeys, `${at} group ${g.id}`)
    if (g.layout && !SETS.groupLayouts.includes(g.layout)) throw new Error(`${at} group ${g.id}: layout "${g.layout}" is not one of ${SETS.groupLayouts.join(', ')}`)
    for (const sp of g.specimens ?? []) outside(sp, SETS.specimenKeys, `${at} specimen ${sp.id}`)
  }
  return true
}

// {skills} is the folder that holds the installed skills, {bento} this skill, {spec} the spec's own folder. A command may
// name a placeholder more than once, so every occurrence is replaced.
export function expand(p, specDir) {
  return p.replaceAll('{skills}', SKILLS).replaceAll('{bento}', SKILL).replaceAll('{spec}', specDir).replaceAll('{work}', WORK).replace(/^~(?=\/)/, process.env.HOME)
}

// A spec is a file path, a bare source name (sources/<name>.json) or an object.
export function loadSpec(ref) {
  if (typeof ref === 'object') return normalise(ref, process.cwd())
  let file = ref
  for (const dir of ['sources', 'layouts']) if (!existsSync(file) && existsSync(join(SKILL, dir, ref + '.json'))) file = join(SKILL, dir, ref + '.json')
  if (!existsSync(file)) throw new Error(`spec not found: ${ref} (a path, or one of sources/*.json or layouts/*.json by name)`)
  return normalise(JSON.parse(readFileSync(file, 'utf8')), dirname(resolve(file)))
}

function normalise(spec, dir) {
  const s = structuredClone(spec)
  s.dir = dir
  if (s.groups && !Array.isArray(s.groups)) {
    const name = s.groups.catalogue
    const cat = JSON.parse(readFileSync(join(SKILL, 'catalogues', name + '.json'), 'utf8'))
    s.groups = cat.groups
    s.areas ??= cat.areas
    s.catalogue = name
  }
  if (s.tokens?.css) s.tokens.css = s.tokens.css.map((p) => expand(p, dir))
  if (s.tokens?.commands) s.tokens.commands = s.tokens.commands.map((p) => expand(p, dir))
  if (s.brief) s.brief = expand(s.brief, dir)
  validateSource(s)
  return s
}

// Sources layer in order. The content source (the first with groups, or the one named) gives groups and areas.
// Later sources override canvas and chrome field by field. The canvas always layers; where a source owns a concern,
// owns "lengths" → only that source's chrome lengths apply; owns "colors" → only its chrome colours apply.
// Axes (by name), tokens and acceptance accumulate.
export function merge(specs, { content } = {}) {
  const c = content ? specs.find((s) => s.id === content) : specs.find((s) => s.groups)
  if (!c) throw new Error(content ? `no source with id ${content}` : 'no content source: one spec must have groups')
  const out = {
    id: specs.map((s) => s.id).join('+'), title: specs.map((s) => s.title).filter(Boolean).at(-1) ?? 'Showcase',
    sources: specs.map((s) => ({ id: s.id, brief: s.brief })), content: c.id,
    canvas: { ...DEFAULTS.canvas }, chrome: { ...DEFAULTS.chrome, colors: {} },
    groups: structuredClone(c.groups), areas: c.areas, axes: [], tokens: { css: [], commands: [] }, acceptance: [],
  }
  const owner = (k) => specs.findLast((s) => s.owns?.includes(k))
  const lengthsFrom = owner('lengths'), colorsFrom = owner('colors')
  for (const s of specs) {
    const { colors, derived, colorsNote, ...rest } = s.chrome ?? {}
    Object.assign(out.canvas, s.canvas ?? {})   // the canvas is a sheet parameter, not a system length: any later source may set it
    if (!lengthsFrom || s === lengthsFrom) Object.assign(out.chrome, rest)
    for (const k of ['texture', 'gridStrength', 'gridStrengthDark', 'darkThemes']) if (s.chrome?.[k]) out.chrome[k] = s.chrome[k]   // sheet choices, not lengths
    if (!colorsFrom || s === colorsFrom) Object.assign(out.chrome.colors, colors ?? {})
    for (const a of s.axes ?? []) {
      const i = out.axes.findIndex((x) => x.name === a.name)
      if (i >= 0) out.axes[i] = { ...out.axes[i], ...a }; else out.axes.push({ invariant: true, ...a })
    }
    out.tokens.css.push(...(s.tokens?.css ?? []))
    out.tokens.commands.push(...(s.tokens?.commands ?? []))
    out.acceptance.push(...(s.acceptance ?? []).map((t) => ({ source: s.id, text: t })))
  }
  // The page always has a theme switch; a source that defines its own theme axis replaces this one.
  if (!out.axes.some((a) => a.name === 'theme')) out.axes.unshift({ name: 'theme', attr: 'data-theme', values: ['light', 'dark'], invariant: true })
  // Grid paper gets its own switch in the bar; it repaints only, so boxes must not move.
  if (out.chrome.texture === 'grid' && !out.axes.some((a) => a.name === 'grid')) out.axes.push({ name: 'grid', label: 'grid', attr: 'data-bento-grid', values: ['on', 'off'], invariant: true })
  // A layout source (areas and/or mins, no groups) rearranges the content: the last one's areas win, mins only grow.
  const gids = new Set(out.groups.map((g) => g.id))
  for (const s of specs) {
    if (s.groups) continue
    const stray = Object.keys(s.mins ?? {}).filter((id) => !gids.has(id))
    if (stray.length) throw new Error(`layout ${s.id}: mins name ${stray.join(', ')}, not groups of ${c.id}`)
    if (s.areas) out.areas = s.areas
    for (const g of out.groups) if (s.mins?.[g.id]) g.min = (g.min ?? [0, 0]).map((v, i) => Math.max(v, s.mins[g.id][i]))
  }
  if (c.title) out.title = c.title
  if (specs.at(-1).title) out.title = specs.at(-1).title
  validate(out)
  return out
}

export function validate(spec) {
  const ids = new Set(), sids = new Set()
  for (const g of spec.groups) {
    if (!g.id || !g.label) throw new Error('every group needs id and label')
    if (ids.has(g.id)) throw new Error(`duplicate group ${g.id}`)
    ids.add(g.id)
    for (const sp of g.specimens ?? []) {
      if (!sp.id || !sp.label) throw new Error(`group ${g.id}: every specimen needs id and label`)
      if (sids.has(sp.id)) throw new Error(`duplicate specimen ${sp.id}`)
      sids.add(sp.id)
    }
  }
  return true
}

// Areas: rows of space-separated group ids, as CSS grid-template-areas ("." for an empty cell).
export function autoAreas(groups, { width, height }) {
  const n = groups.length
  const cols = Math.max(1, Math.ceil(Math.sqrt((n * width) / height)))
  const rows = Math.ceil(n / cols)
  const grid = []
  for (let r = 0; r < rows; r++) {
    const row = []
    const inRow = groups.slice(r * cols, (r + 1) * cols)
    for (let c = 0; c < cols; c++) row.push((inRow[Math.min(c, inRow.length - 1)] ?? groups.at(-1)).id)
    grid.push(row.join(' '))
  }
  return grid
}

export function parseAreas(areas, groups) {
  const grid = areas.map((r) => r.trim().split(/\s+/))
  const C = grid[0].length
  if (grid.some((r) => r.length !== C)) throw new Error('areas: every row needs the same number of cells')
  const span = {}
  grid.forEach((row, y) => row.forEach((id, x) => {
    if (id === '.') return
    const s = (span[id] ??= { x0: x, x1: x, y0: y, y1: y })
    s.x0 = Math.min(s.x0, x); s.x1 = Math.max(s.x1, x); s.y0 = Math.min(s.y0, y); s.y1 = Math.max(s.y1, y)
  }))
  for (const [id, s] of Object.entries(span))
    for (let y = s.y0; y <= s.y1; y++) for (let x = s.x0; x <= s.x1; x++)
      if (grid[y][x] !== id) throw new Error(`areas: ${id} is not a rectangle`)
  for (const g of groups) if (!span[g.id]) throw new Error(`areas: group ${g.id} has no cell`)
  for (const id of Object.keys(span)) if (!groups.some((g) => g.id === id)) throw new Error(`areas: ${id} is not a group`)
  return { grid, C, R: grid.length, span }
}

// Raise the narrowest tracks of a span first (water-filling), so a span's deficit lands where there is room
// instead of widening tracks that another group already sized.
function fill(t, a, b, need) {
  const seg = t.slice(a, b + 1), sum = seg.reduce((x, y) => x + y, 0)
  let lo = Math.min(...seg), hi = Math.max(...seg) + need
  for (let it = 0; it < 60; it++) { const L = (lo + hi) / 2; seg.reduce((x, v) => x + Math.max(v, L), 0) - sum > need ? (hi = L) : (lo = L) }
  for (let i = a; i <= b; i++) t[i] = Math.max(t[i], hi)
}

// Track sizes that meet every group's minimum (the spans' sum plus inner gutters), then share what is left
// by water-filling, so tracks stay as equal as the minimums allow. Never scales anything down: a deficit throws.
function tracks(n, avail, gutter, needs) {
  const total = avail - (n - 1) * gutter
  // First try: grow each span's narrowest tracks (even, good-looking tracks).
  let t = new Array(n).fill(0)
  const order = [...needs].sort((a, b) => (a.b - a.a) - (b.b - b.a))
  for (let it = 0; it < 100; it++) {
    let moved = false
    for (const { a, b, min } of order) {
      const have = t.slice(a, b + 1).reduce((s, v) => s + v, 0) + (b - a) * gutter
      if (min - have > 1e-6) { fill(t, a, b, min - have); moved = true }
    }
    if (!moved) break
  }
  // If that overshoots, use the exact greedy for interval covering: spans by right end, each deficit on its
  // rightmost track. It gives the least total any arrangement can have, so a deficit after it is real.
  if (t.reduce((s, v) => s + v, 0) - total > 0.5) {
    t = new Array(n).fill(0)
    for (const { a, b, min } of [...needs].sort((x, y) => x.b - y.b || y.a - x.a)) {
      const have = t.slice(a, b + 1).reduce((s, v) => s + v, 0) + (b - a) * gutter
      if (min - have > 1e-6) t[b] += min - have
    }
  }
  for (let i = 0; i < n; i++) t[i] = Math.ceil(t[i] - 1e-6)
  const used = t.reduce((s, v) => s + v, 0)
  if (used - total > 0.5) return { deficit: used - total, t }
  let lo = 0, hi = total
  for (let it = 0; it < 60; it++) { const L = (lo + hi) / 2; t.reduce((s, v) => s + Math.max(v, L), 0) > total ? (hi = L) : (lo = L) }
  const f = t.map((v) => Math.max(v, lo))
  // whole px, largest remainder, so the tracks close exactly on the canvas
  const fl = f.map(Math.floor)
  let rest = Math.round(total - fl.reduce((s, v) => s + v, 0))
  f.map((v, i) => [v - Math.floor(v), i]).sort((a, b) => b[0] - a[0] || a[1] - b[1]).forEach(([, i]) => { if (rest > 0) { fl[i]++; rest-- } })
  return { t: fl, deficit: 0 }
}

export function pack(spec) {
  const { width: W, height: H } = spec.canvas
  const ch = spec.chrome
  const areas = spec.areas ?? autoAreas(spec.groups, spec.canvas)
  const { C, R, span } = parseAreas(areas, spec.groups)
  const availW = W - 2 * ch.margin, availH = H - 2 * ch.margin - ch.header - (ch.header ? ch.gutter : 0)
  const min = Object.fromEntries(spec.groups.map((g) => [g.id, g.min ?? [0, 0]]))
  const cols = tracks(C, availW, ch.gutter, Object.entries(span).map(([id, s]) => ({ a: s.x0, b: s.x1, min: min[id][0] })))
  const rows = tracks(R, availH, ch.gutter, Object.entries(span).map(([id, s]) => ({ a: s.y0, b: s.y1, min: min[id][1] })))
  const problems = []
  if (cols.deficit) problems.push(`width: the minimums need ${Math.ceil(cols.deficit)}px more than the canvas has`)
  if (rows.deficit) problems.push(`height: the minimums need ${Math.ceil(rows.deficit)}px more than the canvas has`)
  if (problems.length) {
    const e = new Error('does not fit, and specimens are never scaled down: ' + problems.join('; ') +
      '. Rearrange the areas, cut words, or change a parameter (canvas, density, card depth).')
    e.code = 'NOFIT'; throw e
  }
  const pos = (t, i) => t.slice(0, i).reduce((s, v) => s + v, 0) + i * ch.gutter
  const top = ch.margin + (ch.header ? ch.header + ch.gutter : 0)
  const rects = Object.fromEntries(Object.entries(span).map(([id, s]) => [id, {
    x: ch.margin + pos(cols.t, s.x0), y: top + pos(rows.t, s.y0),
    w: pos(cols.t, s.x1 + 1) - pos(cols.t, s.x0) - ch.gutter, h: pos(rows.t, s.y1 + 1) - pos(rows.t, s.y0) - ch.gutter,
  }]))
  return { areas, columns: cols.t, rows: rows.t, rects }
}
