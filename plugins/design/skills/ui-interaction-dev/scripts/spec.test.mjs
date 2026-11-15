// node --test scripts/   The spec's rules, each with a negative control: a mutated spec that must fail.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, readdirSync, statSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { load, validate, render, BANNED } from './spec.mjs'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const spec = load()
const clone = () => structuredClone(spec)
const first = (s, status) => s.rules.find((r) => r.status === status)

test('the committed spec is valid and spec.md is in step', () => {
  assert.deepEqual(validate(spec, BANNED), [])
  assert.equal(readFileSync(join(ROOT, 'references', 'spec.md'), 'utf8'), render(spec), 'run node scripts/spec.mjs')
})

test('a duplicate id, an undeclared area and an id outside its area are caught', () => {
  const s = clone(); s.rules.push({ ...s.rules[0] })
  assert.match(validate(s).join('\n'), /duplicate id/)
  const a = clone(); a.rules[0].area = 'nowhere'
  assert.match(validate(a).join('\n'), /not declared/)
  const b = clone(); b.rules[0].id = 'hover.misfiled'
  assert.match(validate(b).join('\n'), /must start with its area/)
})

test('a rule states one RFC 2119 obligation, and gives a why', () => {
  const s = clone(); s.rules[0].rule = 'Drags should probably wait a bit.'
  assert.match(validate(s).join('\n'), /MUST, SHOULD or MAY/)
  const w = clone(); delete w.rules[0].why
  assert.match(validate(w).join('\n'), /needs a why/)
})

test('a validated rule carries a dated record with where, finding and check', () => {
  const s = clone(); first(s, 'validated').validated = []
  assert.match(validate(s).join('\n'), /carries a validation record/)
  const d = clone(); first(d, 'validated').validated[0].on = 'last week'
  assert.match(validate(d).join('\n'), /YYYY-MM-DD/)
  const c = clone(); delete first(c, 'validated').validated[0].check
  assert.match(validate(c).join('\n'), /needs "check"/)
  const p = clone(); first(p, 'sourced').validated = [{ on: '2026-01-01', where: 'x', finding: 'y', check: 'z' }]
  assert.match(validate(p).join('\n'), /its status is validated/)
})

test('a sourced rule cites an https source; a contested one cites the two that disagree', () => {
  const s = clone(); first(s, 'sourced').sources = []
  assert.match(validate(s).join('\n'), /cites a source/)
  const h = clone(); first(h, 'sourced').sources = ['http://example.com']
  assert.match(validate(h).join('\n'), /https URL/)
  const c = clone(); first(c, 'contested').sources = [first(c, 'contested').sources[0]]
  assert.match(validate(c).join('\n'), /sources that disagree/)
})

test('no record names a host project, anywhere in the skill', () => {
  const s = clone(); first(s, 'validated').validated[0].where = `the ${BANNED[0]} showcase`
  assert.match(validate(s, BANNED).join('\n'), /names a host project/)
  const walk = (d) => readdirSync(d).flatMap((f) => { const p = join(d, f); if (f === '.git' || f === 'node_modules') return []; return statSync(p).isDirectory() ? walk(p) : [p] })
  const hits = walk(ROOT).filter((p) => !p.endsWith('spec.mjs')).filter((p) => BANNED.some((w) => readFileSync(p, 'utf8').toLowerCase().includes(w)))
  assert.deepEqual(hits, [])
})

test('spec.md drift is caught', () => {
  const s = clone(); s.rules[0].rule += ' MUST also do more.'
  assert.notEqual(render(s), readFileSync(join(ROOT, 'references', 'spec.md'), 'utf8'))
})

test('SKILL.md routes to every reference and script that exists', () => {
  const skill = readFileSync(join(ROOT, 'SKILL.md'), 'utf8')
  for (const f of [...readdirSync(join(ROOT, 'references')).map((f) => `references/${f}`), 'scripts/spec.mjs'])
    assert.ok(skill.includes(f), `SKILL.md does not name ${f}`)
  const desc = skill.match(/^description: (.+)$/m)?.[1] ?? ''
  assert.ok(desc.length > 200 && desc.length <= 1024, `description is ${desc.length} characters (200 to 1024)`)
  assert.match(desc, /NOT for/)
})
