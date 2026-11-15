// Generated blocks in the references: node docs.mjs (rewrite) | node docs.mjs --check (exit 1 on drift).
// Each block sits between <!-- generated:<name> --> and <!-- /generated:<name> -->; edit the source, never the block.
//   roles   references/fit.md        from ROLES in fit.mjs
//   ladder  references/equations.md  from containers() at n = 14, default density, card depth 4, standard
//   archetypes  references/equations.md  from references/archetypes.json and what each archetype's dials derive
import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { containers, system, PRESETS, TIERS } from './derive.mjs'
import { ROLES } from './fit.mjs'
import { loadArchetypes, applyArchetype, observe } from './archetypes.mjs'

const REF = join(dirname(fileURLToPath(import.meta.url)), '..', 'references')
const num = (x) => String(Math.round(x * 1000) / 1000)

export function rolesTable() {
  const rows = Object.entries(ROLES).map(([k, r]) => `| ${k} | ${r.tier} | ${r.compare}${r.collect === false ? ' (not collected)' : ''} |`)
  return ['| Role | Tier | Compared with |', '|---|---|---|', ...rows].join('\n')
}

export function ladderTable() {
  const u = system(PRESETS.standard).q(14)
  const cell = (xs) => (xs.length ? xs.map((x) => `${x.e} (${num(x.q * u)})`).join('; ') : '—')
  const rows = []
  for (const t of TIERS) for (const r of containers({ n: 14, cardDepth: 4 }).filter((x) => x.tier === t))
    rows.push(`| ${t} | ${r.container} | ${cell(r.pad)} | ${cell(r.gap)} | ${cell(r.radius)} | ${cell(r.height)} |`)
  return ['| Tier | Container | Padding (px) | Gap (px) | Radius (px) | Height (px) |', '|---|---|---|---|---|---|', ...rows].join('\n')
}

export function archetypesTable() {
  const A = loadArchetypes(), rows = []
  for (const [name, a] of Object.entries(A.archetypes)) {
    const o = applyArchetype(name), { values } = observe(o), d = a.dials, band = (f) => (a.bands[f] ? `${num(a.bands[f][0])} to ${num(a.bands[f][2])}` : '—')
    rows.push(`| ${name} | ${a.family}${a.near?.length ? `, near ${a.near.join(', ')}` : ''} | ${a.stance.hero} | ${d.n} | ${d.density}${d.constants?.inset ? ' (own inset)' : ''}${typeof d.constants?.levels?.page === 'object' ? ' (stepped margin)' : ''} | ${num(d.kappa.control)} / ${num(d.kappa.card)} | ${num(Math.round(values.loft * 100) / 100)} | ${band('loft')} | ${d.typeCap} | ${a.signature.join(', ')} | ${a.recognised.first} / ${a.recognised.inTwo} of ${a.pages} |`)
  }
  return ['| Archetype | Family | Hero | n | Density | κ control / card | h/F derived | h/F band | Type cap | Signature | Recognised first / in two |', '|---|---|---|---|---|---|---|---|---|---|---|', ...rows].join('\n')
}

export const BLOCKS = { roles: ['fit.md', rolesTable], ladder: ['equations.md', ladderTable], archetypes: ['equations.md', archetypesTable] }

export function sync({ check = false } = {}) {
  const drift = []
  for (const [name, [file, make]] of Object.entries(BLOCKS)) {
    const path = join(REF, file), text = readFileSync(path, 'utf8')
    const open = `<!-- generated:${name} -->`, close = `<!-- /generated:${name} -->`
    const a = text.indexOf(open), b = text.indexOf(close)
    if (a < 0 || b < a) { drift.push(`${file}: no ${open} … ${close} block`); continue }
    const want = `${open}\n${make()}\n${close}`
    if (text.slice(a, b + close.length) !== want) {
      if (check) drift.push(`${file}: the ${name} block differs from its source; run node scripts/docs.mjs`)
      else writeFileSync(path, text.slice(0, a) + want + text.slice(b + close.length))
    }
  }
  return drift
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const drift = sync({ check: process.argv.includes('--check') })
  for (const d of drift) console.error(d)
  console.log(drift.length ? `docs: ${drift.length} drift` : 'docs: in step')
  process.exit(drift.length ? 1 : 0)
}
