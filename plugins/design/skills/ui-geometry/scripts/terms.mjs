// Keeps references/terms.json in step with what the scripts emit.
//   node terms.mjs --check   exit 1 on any finding
// Rules: every name resolves to something emitted (a derive symbol, alias or id, a fit role, a preset key path, a tier,
// a CLI flag, a file); no name belongs to two concepts; every notation symbol derive prints, every fit role and every
// tier is named by exactly one concept; concept ids are unique; no doc uses a phrase a concept lists under avoidExact.
import { readFileSync, existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { derive, PRESETS, TIERS } from './derive.mjs'
import { ROLES } from './fit.mjs'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const FLAGS = ['--n', '--density', '--kappa', '--card', '--preset', '--tier', '--containers', '--elevation', '--scheme', '--nest', '--json', '--viewport', '--dpr', '--archetype', '--field', '--gutter', '--max-columns', '--lines', '--whole', '--emit', '--from', '--to']
export const NOTATION = /^([A-Za-zκ](_[a-z]+)?)(\.[a-z]+)?$/
const strip = (s) => s.replace(/\s+κ=[0-9.]+$/, '').trim()

export function emitted() {
  const rows = ['compact', 'default', 'loose'].flatMap((density) => derive({ density }))
  const keys = []
  const walk = (o, p) => { for (const [k, v] of Object.entries(o)) { const q = p ? `${p}.${k}` : k; keys.push(q); if (v && typeof v === 'object' && !Array.isArray(v)) walk(v, q) } }
  walk(PRESETS.standard, '')
  return {
    symbol: new Set(rows.map((r) => strip(r.symbol))), alias: new Set(rows.map((r) => r.alias).filter(Boolean)),
    id: new Set(rows.map((r) => r.id)), role: new Set(Object.keys(ROLES)), preset: new Set(keys), tier: new Set(TIERS), flag: new Set(FLAGS),
  }
}

export function checkTerms(terms, E = emitted()) {
  const out = [], owner = new Map(), ids = new Set()
  for (const c of terms.concepts) {
    if (ids.has(c.id)) out.push(`concept id "${c.id}" appears twice`)
    ids.add(c.id)
    for (const k of ['definition', 'intent']) if (!c[k]) out.push(`${c.id}: no ${k}`)
    for (const name of c.names ?? []) {
      const [kind, ...rest] = name.split(':'), v = rest.join(':')
      const ok = kind === 'file' ? existsSync(join(ROOT, v)) : E[kind]?.has(v)
      if (!ok) out.push(`${c.id}: "${name}" is not emitted by the scripts`)
      if (owner.has(name) && owner.get(name) !== c.id) out.push(`"${name}" belongs to both ${owner.get(name)} and ${c.id}: one name, one meaning`)
      owner.set(name, c.id)
    }
  }
  for (const s of E.symbol) if (NOTATION.test(s) && !owner.has(`symbol:${s}`)) out.push(`symbol "${s}" is printed by derive but has no concept`)
  for (const r of E.role) if (!owner.has(`role:${r}`)) out.push(`role "${r}" is in ROLES but has no concept`)
  for (const t of E.tier) if (!owner.has(`tier:${t}`)) out.push(`tier "${t}" has no concept`)
  return out
}

export const loadTerms = () => JSON.parse(readFileSync(join(ROOT, 'references', 'terms.json'), 'utf8'))

/** The docs the vocabulary governs, as [path, text] pairs. */
export const loadDocs = () => ['SKILL.md', 'references/equations.md', 'references/fit.md', 'references/showcase.md'].map((p) => [p, readFileSync(join(ROOT, p), 'utf8')])

/** Every use, in the docs, of an exact phrase a concept bans outright (`avoidExact`). Case-sensitive, whole words. */
export function checkProse(terms, docs = loadDocs()) {
  const out = []
  for (const c of terms.concepts) for (const phrase of c.avoidExact ?? []) {
    const re = new RegExp(`(?<![\\w-])${phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?![\\w-])`)
    for (const [path, text] of docs) text.split('\n').forEach((line, i) => { if (re.test(line)) out.push(`${path}:${i + 1} "${phrase}" is avoided for ${c.term}`) })
  }
  return out
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const found = [...checkTerms(loadTerms()), ...checkProse(loadTerms())]
  for (const f of found) console.error(f)
  console.log(found.length ? `terms: ${found.length} findings` : `terms: ${loadTerms().concepts.length} concepts in step`)
  process.exit(found.length ? 1 : 0)
}
