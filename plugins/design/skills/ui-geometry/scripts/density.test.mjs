// node --test density.test.mjs
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const derive = fileURLToPath(new URL('./derive.mjs', import.meta.url))
const run = (...args) => spawnSync(process.execPath, [derive, ...args], { encoding: 'utf8' })
const NOTE = /has no effect under the affine preset/

test('affine: a non-default --density prints a stderr note and marks the header', () => {
  for (const d of ['loose', 'compact']) {
    const r = run('--n', '16', '--density', d)
    assert.equal(r.status, 0)
    assert.match(r.stderr, NOTE)
    assert.match(r.stderr, new RegExp(`--density ${d}`))
    assert.match(r.stdout.split('\n')[0], new RegExp(`density ${d} \\(no effect`))
  }
})

test('affine: density default prints no note and keeps the header', () => {
  const r = run('--n', '16')
  assert.doesNotMatch(r.stderr, NOTE)
  assert.match(r.stdout.split('\n')[0], /density default {2}κ/)
})

test('unit presets (ladder, standard): no note, header unmarked', () => {
  for (const p of ['ladder', 'standard']) {
    const r = run('--preset', p, '--n', '16', '--density', 'loose')
    assert.equal(r.status, 0)
    assert.doesNotMatch(r.stderr, /no effect/)
    assert.doesNotMatch(r.stdout, /no effect/)
    assert.match(r.stdout.split('\n')[0], /density loose {2}κ/)
  }
})
