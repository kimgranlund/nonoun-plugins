// node --test observe.test.mjs
import { test } from 'node:test'
import assert from 'node:assert/strict'
import vm from 'node:vm'
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { loadArchetypes, scoreReport, rank } from './archetypes.mjs'

const file = (name) => fileURLToPath(new URL(name, import.meta.url))
const ctx = {}; vm.createContext(ctx); vm.runInContext(readFileSync(file('./observe.js'), 'utf8'), ctx)
const O = ctx.uiGeometryObserve, A = loadArchetypes()
const near = (a, b, tol) => assert.ok(Math.abs(a - b) <= tol, `${a} is not within ${tol} of ${b}`)

test('observe.js loads without a page and names exactly the observables of archetypes.json, and a stray one is caught', () => {
  assert.equal(typeof O, 'function')
  const diff = (measured, described) => [...measured.filter((k) => !described.includes(k)).map((k) => `measured, not described: ${k}`), ...described.filter((k) => !measured.includes(k)).map((k) => `described, not measured: ${k}`)]
  const measured = [...O.KEYS, ...O.RUNNER_KEYS], described = Object.keys(A.observables)
  assert.deepEqual(diff(measured, described), [])
  assert.equal(new Set(measured).size, measured.length, 'an observable is listed twice')
  assert.deepEqual(diff([...measured, 'sparkle'], described), ['measured, not described: sparkle'], 'negative control')
  for (const k of described) assert.ok(A.scale[k] > 0, `${k} has no scale`)
})

test('colour math: HCT of the sRGB primaries, and the two contrast measures at their ends', () => {
  const { hct, wcag, apca } = O.math
  for (const [rgb, h, c, t] of [[[255, 0, 0], 27.41, 113.36, 53.23], [[0, 255, 0], 142.14, 108.41, 87.74], [[0, 0, 255], 282.79, 87.23, 32.3], [[119, 119, 119], 209.49, 1.82, 50.03]]) {
    const v = hct(rgb); near(v.h, h, 0.01); near(v.c, c, 0.01); near(v.t, t, 0.01)
  }
  near(hct([255, 255, 255]).t, 100, 1e-6); near(hct([0, 0, 0]).t, 0, 1e-6)
  near(wcag([0, 0, 0], [255, 255, 255]), 21, 1e-9); near(wcag([119, 119, 119], [255, 255, 255]), 4.48, 0.005)
  near(apca([0, 0, 0], [255, 255, 255]), 106.04, 0.01); near(apca([255, 255, 255], [0, 0, 0]), -107.88, 0.01)
  assert.equal(apca([200, 200, 200], [201, 201, 201]), 0)
  // A tone difference of 50 gives at least 4.5:1: grey at tone 50 on white.
  assert.ok(wcag([119, 119, 119], [255, 255, 255]) >= 4.4)
})

test("a page at an archetype's medians scores 0 for it and names it nearest, and a value far outside is listed", () => {
  for (const [name, a] of Object.entries(A.archetypes)) {
    const med = Object.fromEntries(Object.entries(a.bands).map(([f, b]) => [f, b[1]]))
    assert.equal(rank(med, A).find((r) => r.name === name).distance, 0, name)
    assert.match(scoreReport(med, A), /Every given observable is inside its band|## Nearest: /)
  }
  const ed = Object.fromEntries(Object.entries(A.archetypes.editorial.bands).map(([f, b]) => [f, b[1]]))
  assert.match(scoreReport(ed, A), /## Nearest: editorial\n\nEvery given observable is inside its band\./)
  const off = scoreReport({ ...ed, serifShare: 0 }, A)
  assert.match(off, /\| serifShare \| 0 \|/)
})

test('observe.mjs refuses to run without a target and says why, with exit 2', () => {
  const r = spawnSync(process.execPath, [file('./observe.mjs')], { encoding: 'utf8' })
  assert.equal(r.status, 2); assert.match(r.stderr, /^cannot observe: /)
})
