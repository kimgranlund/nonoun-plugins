// Position: where a measured page sits on the dimensions pages actually vary along (references/dimensions.json).
//   node dimensions.mjs <observed.json>     the page's score on each dimension, beside the archetypes on either side of it
// An archetype is the nearest named region; position is the fuller answer for a page or a kit that sits between names.
// The dimensions are principal components of 66 observables over the measured pages; six can be named, three cannot.
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const FILE = () => join(dirname(fileURLToPath(import.meta.url)), '..', 'references', 'dimensions.json')
export const loadDimensions = () => JSON.parse(readFileSync(FILE(), 'utf8'))

/** The standard normal quantile (Acklam's approximation, error under 1.2e-9). */
export function normalQuantile(p) {
  const a = [-39.6968302866538, 220.946098424521, -275.928510446969, 138.357751867269, -30.6647980661472, 2.50662827745924], b = [-54.4760987982241, 161.585836858041, -155.698979859887, 66.8013118877197, -13.2806815528857]
  const c = [-0.00778489400243029, -0.322396458041136, -2.40075827716184, -2.54973253934373, 4.37466414146497, 2.93816398269878], d = [0.00778469570904146, 0.32246712907004, 2.445134137143, 3.75440866190742], lo = 0.02425
  if (p < lo) { const q = Math.sqrt(-2 * Math.log(p)); return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1) }
  if (p > 1 - lo) return -normalQuantile(1 - p)
  const q = p - 0.5, r = q * q
  return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
}

/** A value's share of the measured pages at or below it, from the observable's quantile table (ties take the middle of their run). */
export function percentile(v, table) {
  const n = table.length - 1; if (v < table[0]) return 0; if (v > table[n]) return 1
  let lo = 0; while (lo < n && table[lo + 1] < v) lo++
  let hi = lo; while (hi < n && table[hi + 1] <= v) hi++
  if (table[lo] === v || hi > lo + 1 || table[hi] === v) { const first = table[lo] === v ? lo : lo + 1; return (first + hi) / 2 / n }   // on a tabulated value: the middle of the run
  return (lo + (v - table[lo]) / (table[lo + 1] - table[lo])) / n
}

/**
 * A page's position: one score per dimension, in standard deviations of the measured pages (0 is the middle page).
 * Each observable is turned into a normal score by its rank among the measured pages, then weighted. An observable not given counts as the middle.
 * Throws when fewer than D.need observables are given: a preset alone fixes six, which is not a position.
 */
export function position(observables, D = loadDimensions()) {
  const given = D.observables.filter((k) => typeof observables[k] === 'number' && !Number.isNaN(observables[k]))
  if (given.length < D.need) throw new Error(`cannot place: ${given.length} of ${D.observables.length} observables given, and a position needs ${D.need}. Measure the page with observe.mjs; a preset alone fixes six.`)
  const eps = 0.5 / D.pages, z = D.observables.map((k) => (given.includes(k) ? normalQuantile(Math.min(1 - eps, Math.max(eps, percentile(observables[k], D.quantiles[k])))) : 0))
  return { used: given.length, scores: D.components.map((c) => ({ id: c.id, name: c.name, score: c.weights.reduce((s, w, i) => s + w * z[i], 0) })) }
}

const f2 = (v) => (Math.round(v * 100) / 100).toFixed(2)

/** Markdown: the named dimensions, the page's score on each, and the archetypes whose mean lies on either side. */
export function positionReport(observables, D = loadDimensions()) {
  let p; try { p = position(observables, D) } catch (e) { return `## Position\n\nNot given: ${e.message.replace(/^cannot place: /, '')}\n` }
  const out = ['## Position\n', `Score on each named dimension, in standard deviations of the ${D.pages} measured pages (0 is the middle page); ${p.used} of ${D.observables.length} observables used. The archetypes named are those whose mean lies on either side.\n`, '| dimension | score | low end | high end | between |', '|---|---|---|---|---|']
  D.components.forEach((c, i) => { if (!c.name) return; const s = p.scores[i].score, means = Object.entries(D.archetypes).map(([n, a]) => [n, a.mean[i]]).sort((x, y) => x[1] - y[1])
    const below = means.filter(([, m]) => m <= s).pop(), above = means.find(([, m]) => m > s), fmt = (x) => `${x[0]} (${f2(x[1])})`
    out.push(`| ${c.name} | ${f2(s)} | ${c.low} | ${c.high} | ${below && above ? `${fmt(below)} and ${fmt(above)}` : below ? `above every archetype; highest is ${fmt(below)}` : `below every archetype; lowest is ${fmt(above)}`} |`) })
  return out.join('\n') + '\n'
}

if (typeof process !== 'undefined' && process.argv?.[1] && fileURLToPath(import.meta.url) === process.argv[1] && process.argv[2]) {
  const data = JSON.parse(readFileSync(process.argv[2], 'utf8'))
  console.log(positionReport(data.observables ?? data))
}
