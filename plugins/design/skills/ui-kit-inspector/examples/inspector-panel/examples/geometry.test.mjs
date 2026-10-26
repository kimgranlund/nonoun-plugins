import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { panelGeometry } from '../panel-geometry.js';
import { resolveControl } from '../../../../mathematical-design-system/assets/differential-forms/geometry/index.ts';
test('independent golden sizes and border conservation across density/unit boundaries', () => {
  for (const unit of [3,4,6]) for (const [i,density] of ['compact','default','loose'].entries()) for (const border of [0,unit/2]) {
    const g=panelGeometry({unit,border,controlDensity:density});
    const number=k=>parseFloat(g[`--ip-${k}`]);
    assert.equal(number('height'),[7,8,10][i]*unit);
    assert.equal(number('slot'),6*unit);
    assert.equal(number('padding')+border,[.5,1,2][i]*unit);
    assert.equal(number('font'),2*unit+6);
    assert.equal(number('edge-start'),1.5*unit);
    assert.equal(number('choice-radius'),unit);
    assert.equal(number('height'),resolveControl({unit,border,density}).height);
    for(const value of Object.values(g)) assert.ok(Number.isFinite(parseFloat(value)));
  }
});
test('parent density never changes control geometry; container Softest is not pill',()=>{
  for(const density of ['compact','default','loose']) {
    const g=panelGeometry({cardDensity:density,collectionDensity:density,containerCurvature:'softest'});
    assert.equal(g['--ip-height'],'32px'); assert.equal(g['--ip-container-radius'],'16px');
  }
  assert.throws(()=>panelGeometry({border:3}),RangeError);
  assert.throws(()=>panelGeometry({controlDensity:'dense'}),RangeError);
});
test('generated source provenance is synchronized',async()=>{
  const provenance=JSON.parse(await readFile(new URL('../geometry-runtime/provenance.json',import.meta.url)));
  for(const [name,hash] of Object.entries(provenance.geometrySHA256)) {
    const src=await readFile(new URL(`../../../../mathematical-design-system/assets/differential-forms/geometry/${name}`,import.meta.url));
    assert.equal(createHash('sha256').update(src).digest('hex'),hash);
  }
});
