#!/usr/bin/env node
// The skill's own check. No dependency: node scripts/check.mjs
//
// Each check reads SKILL.md (and every other text file of the skill for the last one) and returns the faults it finds.
// Each has a negative control: a copy of the text with one fault planted, on which the check must fail. A control that
// passes is itself a failure, so a check can never go quiet.
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs'
import { dirname, join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const walk = (dir) => readdirSync(dir).flatMap((n) => { const p = join(dir, n); return n === '.git' || n === 'node_modules' ? [] : statSync(p).isDirectory() ? walk(p) : [p] })
const load = () => ({
  skill: readFileSync(join(ROOT, 'SKILL.md'), 'utf8'),
  files: walk(ROOT).filter((p) => /\.(md|mjs|js|json|css|html)$/.test(p)).map((p) => [relative(ROOT, p), readFileSync(p, 'utf8')]),
})
const slug = (h) => h.toLowerCase().replace(/[^a-z0-9 -]/g, '').trim().replace(/ +/g, '-')
const MINUS = '−', INF = '∞', NBSP = ' '
// The eight rules, by the bold lead-in that opens each: T-002 to T-008, and Boundaries from T-001.
const RULES = ['**Figures.**', '**Signs.**', '**Units.**', '**Floors.**', '**Widths that hold.**', '**Time.**', '**Labels.**', '## Boundaries']

const CHECKS = {
  // Front matter a strict host can read: a name equal to the folder's, a plain one-line description within the limit.
  frontMatter(c) {
    const f = [], m = /^---\n([\s\S]*?)\n---\n/.exec(c.skill)
    if (!m) return ['SKILL.md has no front matter']
    const name = (/^name: (.*)$/m.exec(m[1]) || [])[1], desc = (/^description: (.*)$/m.exec(m[1]) || [])[1]
    if (name !== 'ui-content') f.push(`name is ${JSON.stringify(name)}, not "ui-content"`)
    if (!desc) return [...f, 'SKILL.md has no description']
    if (desc.length > 1024) f.push(`description is ${desc.length} characters (limit 1024)`)
    if (/: | #/.test(desc)) f.push('description holds ": " or " #", which ends a plain YAML scalar')
    return f
  },
  // The description says what the skill is not for, by naming each sibling that owns the neighbouring ground.
  notCases(c) {
    const desc = (/^description: (.*)$/m.exec(c.skill) || [])[1] || ''
    if (!/\bNOT for\b/.test(desc)) return ['description has no "NOT for" part']
    return ['ui-geometry', 'ui-colors', 'ui-materials', 'ui-interaction-dev'].filter((s) => !desc.includes(s)).map((s) => `description does not name ${s} as a NOT-case`)
  },
  // Every link resolves: an anchor to a heading of SKILL.md, a relative path to a file of the skill.
  links(c) {
    const heads = new Set([...c.skill.matchAll(/^#{1,6} (.+)$/gm)].map((m) => slug(m[1])))
    return [...c.skill.matchAll(/\]\(([^)]+)\)/g)].map((m) => m[1]).filter((to) => !/^https?:/.test(to))
      .filter((to) => (to.startsWith('#') ? !heads.has(to.slice(1)) : !existsSync(join(ROOT, to.split('#')[0]))))
      .map((to) => `SKILL.md: link ${to} does not resolve`)
  },
  // Each rule is still there, under its lead-in.
  rules: (c) => RULES.filter((r) => !c.skill.includes(r)).map((r) => `SKILL.md no longer holds the rule that opens ${r}`),
  // The skill prints what it tells others to print: a true minus before the infinity sign and before a digit of an
  // example value, never a hyphen-minus; and it names the characters by code point.
  glyphs(c) {
    const f = []
    if (!c.skill.includes(MINUS + INF)) f.push('the floor is not written as U+2212 U+221E anywhere')
    if (c.skill.includes('-' + INF)) f.push('a floor is written with a hyphen-minus before the infinity sign')
    for (const m of c.skill.matchAll(/[(\s]-\d[\d:.]*/g)) f.push(`an example value is written with a hyphen-minus: ${m[0].trim()}`)
    for (const cp of ['U+2212', 'U+221E', 'U+00A0']) if (!c.skill.includes(cp)) f.push(`SKILL.md no longer names ${cp}`)
    if (c.skill.includes(NBSP)) f.push('SKILL.md holds a literal no-break space, which an editor cannot see; name it as U+00A0')
    return f
  },
  // No file names a host project: the skill serves every system.
  hostNames: (c) => {
    const names = ['omissam', 'nosiam', 'msinredom latnemurtsni'].map((w) => [...w].reverse().join(''))
    return c.files.flatMap(([path, text]) => names.filter((w) => text.toLowerCase().includes(w)).map(() => `${path}: names a host project`))
  },
}

const swap = (from, to) => (c) => { if (!c.skill.includes(from)) throw new Error(`control: SKILL.md no longer holds ${JSON.stringify(from)}`); c.skill = c.skill.replace(from, to); return c }
const CONTROLS = {
  frontMatter: [swap('name: ui-content', 'name: ui-text'), swap('description: Print values', 'description: Note: print values')],
  notCases: swap('ui-interaction-dev)', 'the interaction skill)'),
  links: swap('](#boundaries)', '](#borders)'),
  rules: swap('**Floors.**', '**Bottoms.**'),
  glyphs: [swap(MINUS + INF, '-' + INF), swap(`(${MINUS}0:42)`, '(-0:42)'), swap('U+00A0', 'a no-break space')],
  hostNames: (c) => { c.files = [...c.files, ['notes.md', 'Built for ' + [...'omissam'].reverse().join('') + '.']]; return c },
}

const base = load()
let failed = 0, missed = 0, passed = 0, bit = 0
for (const [name, check] of Object.entries(CHECKS)) {
  const out = check(base)
  if (out.length) { failed++; console.log(`FAIL ${name}`); for (const x of out) console.log(`     ${x}`) } else { passed++; console.log(`ok   ${name}`) }
}
for (const [name, mutates] of Object.entries(CONTROLS)) for (const [n, mutate] of [].concat(mutates).entries()) {
  const out = CHECKS[name](mutate({ skill: base.skill, files: [...base.files] })), label = n ? `${name} (${n + 1})` : name
  if (out.length) { bit++; console.log(`ok   control ${label} fails as it must (${out[0].slice(0, 80)})`) } else { missed++; console.log(`FAIL control ${label}: the mutated copy passed`) }
}
console.log(`ui-content check ${failed || missed ? 'FAILED' : 'passed'}: ${passed} checks passed, ${failed} failed; ${bit} controls bit, ${missed} did not`)
process.exit(failed || missed ? 1 : 0)
