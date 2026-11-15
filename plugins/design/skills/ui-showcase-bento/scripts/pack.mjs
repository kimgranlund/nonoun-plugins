#!/usr/bin/env node
// Pack a bento: node pack.mjs <spec|source> [more…] [--content id] [--mins needs.json] [--json]
// Prints the areas, track sizes and each group's rectangle, or exits 1 naming what does not fit.
import { readFileSync } from 'node:fs'
import { loadSpec, merge, pack, setWork } from './lib.mjs'

export function cli(argv) {
  const refs = [], o = {}
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]
    if (a.startsWith('--')) { const k = a.slice(2); o[k] = ['json', 'final', 'standalone'].includes(k) ? true : argv[++i] } else refs.push(a)
  }
  if (!refs.length) throw new Error('usage: pack.mjs <spec|source> [more…] [--content id] [--mins needs.json] [--areas file.json] [--work dir] [--json]')
  if (o.work) setWork(o.work)
  const spec = merge(refs.map(loadSpec), { content: o.content })
  if (o.mins) applyMins(spec, JSON.parse(readFileSync(o.mins, 'utf8')))
  if (o.areas) spec.areas = JSON.parse(readFileSync(o.areas, 'utf8'))
  return { spec, o }
}

// needs: { group: [w, h] } as uiBentoCheck() reports it; each group's min only grows.
export function applyMins(spec, needs) {
  for (const g of spec.groups) if (needs[g.id]) g.min = (g.min ?? [0, 0]).map((v, i) => Math.max(v, needs[g.id][i]))
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    const { spec, o } = cli(process.argv.slice(2))
    const p = pack(spec)
    if (o.json) console.log(JSON.stringify(p, null, 2))
    else {
      console.log(`${spec.id}: ${spec.canvas.width} × ${spec.canvas.height}, margin ${spec.chrome.margin}, gutter ${spec.chrome.gutter}`)
      console.log('areas\n  ' + p.areas.join('\n  '))
      console.log(`columns ${p.columns.join(' ')}\nrows    ${p.rows.join(' ')}`)
      for (const [id, r] of Object.entries(p.rects)) console.log(`  ${id.padEnd(16)} ${r.w} × ${r.h} at ${r.x}, ${r.y}`)
    }
  } catch (e) { console.error(e.message); process.exit(e.code === 'NOFIT' ? 1 : 2) }
}
