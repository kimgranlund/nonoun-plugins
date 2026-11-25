// node --test preset.test.mjs
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { mkdtempSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { PRESETS } from './derive.mjs'

const derive = (...args) => spawnSync(process.execPath, [new URL('./derive.mjs', import.meta.url).pathname, ...args], { encoding: 'utf8' })

test('an unknown --preset exits 2 and names the built-in presets', () => {
  const r = derive('--preset', 'nosuch')
  assert.equal(r.status, 2)
  assert.match(r.stderr, /unknown preset "nosuch": use one of /)
  for (const name of Object.keys(PRESETS)) assert.ok(r.stderr.includes(name), `stderr names ${name}`)
  assert.ok(r.stderr.includes('affine') && r.stderr.includes('ladder'))
  assert.doesNotMatch(r.stderr, /ENOENT/)
  assert.doesNotMatch(r.stderr, /did you mean/)
})

test('a near miss gets a did-you-mean hint', () => {
  const r = derive('--preset', 'afine')
  assert.equal(r.status, 2)
  assert.match(r.stderr, /did you mean "affine"\?/)
})

test('a built-in name and a valid preset path still load', () => {
  assert.equal(derive('--preset', 'affine').status, 0)
  const file = join(mkdtempSync(join(tmpdir(), 'preset-')), 'p.json')
  writeFileSync(file, JSON.stringify({ name: 'mine' }))
  const r = derive('--preset', file)
  assert.equal(r.status, 0, r.stderr)
})
