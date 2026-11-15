#!/usr/bin/env node
// Keeps references/terms.json closed both ways against what the skill emits:
//   every emitted name (spec keys and closed sets, data attributes, --b-* variables, axis ids, CLI flags, page API)
//   is listed in some concept's names or aliases, and every listed name is emitted.
//   node scripts/terms.mjs   prints the drift and exits 1, or "terms: N names, closed both ways"
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { SKILL, SETS, loadSpec, merge, pack } from './lib.mjs'
import { render } from './scaffold.mjs'

export const loadTerms = () => JSON.parse(readFileSync(join(SKILL, 'references/terms.json'), 'utf8'))

export function emitted() {
  const out = new Set()
  for (const [k, v] of Object.entries(SETS)) { out.add(k); v.forEach((x) => out.add(x)) }
  const pages = [['ui-geometry'], ['ui-geometry', 'ui-colors', 'ui-materials']].map((refs) => {
    const specs = refs.map(loadSpec)
    for (const s of specs) if (s.id === 'ui-colors') s.tokens.css = []   // generated per run; its names belong to ui-colors
    const spec = merge(specs)
    spec.axes.forEach((a) => out.add(a.name))
    return render(spec, pack(spec))
  })
  for (const html of pages) {
    for (const m of html.matchAll(/(?<!["\w-])data-[a-z][a-z-]*/g)) out.add(m[0])   // attributes, not attribute values
    for (const m of html.matchAll(/--b-[a-z][a-z-]*/g)) out.add(m[0])
    for (const m of html.matchAll(/window\.(uiBento\w+)/g)) out.add(m[1])
    for (const m of html.matchAll(/id="(bento-[a-z-]+)"/g)) out.add(m[1])
  }
  for (const f of ['pack.mjs', 'scaffold.mjs']) {
    const src = readFileSync(join(SKILL, 'scripts', f), 'utf8')
    for (const line of src.split('\n').filter((l) => /^\/\/|usage:/.test(l)))
      for (const m of line.matchAll(/(?<![\w-])(--[a-z][a-z]+)\b(?!-)/g)) out.add(m[1])
  }
  return out
}

export function termsReport(terms = loadTerms(), names = emitted()) {
  const listed = new Set(), accepted = new Set()
  for (const c of terms.concepts) {
    for (const n of c.names ?? []) listed.add(n), accepted.add(n)
    for (const a of c.aliases ?? []) accepted.add(a)
    for (const k of ['id', 'term', 'definition']) if (!c[k]) throw new Error(`terms: concept ${c.id ?? '?'} has no ${k}`)
  }
  const ids = new Set(terms.concepts.map((c) => c.id))
  const problems = []
  for (const n of [...names].sort()) if (!accepted.has(n)) problems.push(`emitted but not in terms.json: ${n}`)
  for (const n of [...listed].sort()) if (!names.has(n)) problems.push(`in terms.json but never emitted: ${n}`)
  for (const c of terms.concepts) for (const r of c.related ?? []) if (!ids.has(r)) problems.push(`${c.id}: related "${r}" is not a concept`)
  return { problems, count: listed.size }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const { problems, count } = termsReport()
  for (const p of problems) console.log(p)
  console.log(problems.length ? `terms: ${problems.length} problems` : `terms: ${count} names, closed both ways`)
  process.exit(problems.length ? 1 : 0)
}
