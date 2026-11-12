// Asserts ui-geometry identities on the panel's --ip-* lengths, with ui-geometry's own derive() rows as the oracle.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { panelGeometry } from '../panel-geometry.js';
import { derive, PRESETS } from '../../../../ui-geometry/scripts/derive.mjs';
import { source, target, browserRuntime, sha256 } from '../scripts/build.mjs';

const near = (a, b, why) => assert.ok(Math.abs(a - b) < 1e-6, `${why}: ${a} != ${b}`);
const rowPx = (rows, tier, symbol) => {
  const row = rows.find((r) => r.tier === tier && r.symbol === symbol);
  assert.ok(row, `derive() has no ${tier} row ${symbol}`);
  return row.px;
};
const DENSITIES = ['compact', 'default', 'loose'];

test('controls: h = S + 2I, border deducted once, text at T = 2I, r(κ) as derived', () => {
  for (const n of [12, 14, 16, 18]) for (const density of DENSITIES) {
    const rows = derive({ n, density });
    const gc = rowPx(rows, 'controls', 'g_c');
    for (const border of [0, gc]) {
      const g = panelGeometry({ n, border, controlDensity: density });
      const v = (k) => parseFloat(g[`--ip-${k}`]);
      const at = `n ${n} ${density} b ${border}`;
      for (const value of Object.values(g)) assert.ok(Number.isFinite(parseFloat(value)), at);
      const I = v('padding') + border;
      near(I, rowPx(rows, 'controls', 'I'), `${at} I`);
      near(v('slot'), rowPx(rows, 'controls', 'S'), `${at} S`);
      near(v('height'), v('slot') + 2 * I, `${at} h = S + 2I`);
      near(v('height'), rowPx(rows, 'controls', 'h'), `${at} h`);
      near(border + v('padding') + v('edge-start'), rowPx(rows, 'controls', 'T'), `${at} text at T = 2I`);
      near(v('radius'), rowPx(rows, 'controls', `r  κ=${PRESETS.massimo.softAnchor}`), `${at} r(κ_s)`);
      near(v('radius'), PRESETS.massimo.soft * v('unit'), `${at} r(κ_s) = soft`);
      assert.ok(v('radius') <= v('height') / 2, `${at} r ≤ h/2`);
      near(v('choice-size'), rowPx(rows, 'controls', 'checkbox box'), `${at} checkbox a.md`);
      near(v('choice-radius'), rowPx(rows, 'controls', 'checkbox radius'), `${at} checkbox radius`);
      near(v('font'), n, `${at} F = n`);
      near(v('line'), rowPx(rows, 'unit', 'body-md line'), `${at} body-md line`);
    }
  }
});

test('containers: the panel is a card at d = 2I and R − d = min(r(κ_card), soft)', () => {
  for (const n of [14, 16]) for (const density of DENSITIES) for (const border of [0, 1]) {
    const rows = derive({ n, density });
    const g = panelGeometry({ n, border, cardDensity: density });
    const v = (k) => parseFloat(g[`--ip-${k}`]);
    const at = `n ${n} ${density} b ${border}`;
    const d = v('card-padding') + border, I = rowPx(rows, 'controls', 'I');
    near(d, 2 * I, `${at} d = 2I`);
    near(v('container-radius'), rowPx(rows, 'containers', `R panel (card at 2I)  κ=${PRESETS.massimo.dials.kappa.card}`), `${at} R panel`);
    near(v('container-radius') - d, Math.min(rowPx(rows, 'containers', `R card-0  κ=${PRESETS.massimo.dials.kappa.card}`), PRESETS.massimo.soft * v('unit')), `${at} R − d`);
    near(v('card-gap'), d / 2, `${at} gap = d/2`);
  }
});

test('curvature: r(0) = 0, r(1) = h/2, monotonic in κ', () => {
  const r = (k) => parseFloat(panelGeometry({ controlCurvature: k })['--ip-radius']);
  const h = parseFloat(panelGeometry()['--ip-height']);
  near(r(0), 0, 'r(0)');
  near(r(1), h / 2, 'r(1)');
  for (let k = 0; k < 1; k += 0.125) assert.ok(r(k) <= r(k + 0.125), `r monotonic at κ ${k}`);
});

test('families are independent: card and collection density never change control geometry', () => {
  const controls = ['height', 'slot', 'padding', 'radius', 'font', 'line', 'edge-start'];
  const base = panelGeometry();
  for (const density of DENSITIES) {
    const g = panelGeometry({ cardDensity: density, collectionDensity: density });
    for (const k of controls) assert.equal(g[`--ip-${k}`], base[`--ip-${k}`], `${k} at ${density}`);
  }
  assert.throws(() => panelGeometry({ border: 3 }), RangeError);
  assert.throws(() => panelGeometry({ controlDensity: 'dense' }), RangeError);
  assert.throws(() => panelGeometry({ containerCurvature: 2 }), RangeError);
  assert.throws(() => panelGeometry({ n: 8 }), RangeError);
});

test('geometry-runtime/derive.js is the current browser build of ui-geometry derive.mjs', async () => {
  const text = await readFile(source, 'utf8');
  const provenance = JSON.parse(await readFile(new URL('provenance.json', target)));
  assert.equal(provenance.sha256, sha256(text), 'run npm run build');
  assert.equal(await readFile(new URL('derive.js', target), 'utf8'), browserRuntime(text), 'run npm run build');
  for (const file of [new URL('derive.js', target), new URL('../panel-geometry.js', import.meta.url)]) {
    assert.doesNotMatch(await readFile(file, 'utf8'), /from ['"]node:/, `${file.pathname} must load in a browser`);
  }
});
