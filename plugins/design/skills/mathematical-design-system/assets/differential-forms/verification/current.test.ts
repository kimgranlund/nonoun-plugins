import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolveControl,resolveChip,resolveCard,resolveComposite,resolveComposedInput,resolveMultiline} from '../geometry/index.ts';
import type {Density} from '../geometry/types.ts';
const root=new URL('../',import.meta.url);
const json=(p:string)=>JSON.parse(readFileSync(new URL(p,root),'utf8'));
test('current defaults agree with contracts',()=>{
 const f=json('contracts/foundations.json');
 assert.equal(f.curvatureDefault,'soft');assert.equal(f.compositeInset.defaultUnits,0);
 assert.equal(resolveControl().radius,12);assert.equal(resolveCard().radius,12);
 assert.equal(resolveComposite().requestedInset,0);assert.equal(resolveComposite().child.radius,0);
});
test('composed input grows to preserve chip and border budgets',()=>{
 for(const [density,chipHeight,inputHeight] of [['compact',20,28],['default',24,32],['loose',32,48]] as const){
  for(const border of [0,1,2]){
   const c=resolveComposedInput({density,border});
   assert.equal(c.height,inputHeight);assert.equal(c.adornment.height,chipHeight);
   assert.equal(c.minWidth,c.height);assert.equal(c.adornment.minWidth,chipHeight);
   assert.ok(c.height>=chipHeight+2*(c.padding+border));
   assert.equal(c.adornment.labelEdge,3);
  }
 }
 const soft=resolveComposedInput();assert.equal(soft.adornment.radiusInline,8);assert.equal(soft.adornment.radiusBlock,8);
 const pill=resolveComposedInput({density:'loose',curvature:'softest'});assert.equal(pill.radius,24);assert.equal(pill.adornment.radiusInline,16);assert.equal(pill.adornment.radiusBlock,16);
});
test('chip popup deducts parent inset while preserving chip slots',()=>{
 for(const density of ['compact','default','loose'] as Density[])for(const border of [0,2])for(const insetUnits of [0,.5,1.5]){
  const p=resolveComposite({childFamily:'chip',density,border,insetUnits});
  assert.equal(p.child.slot,16);assert.equal(p.child.labelEdge,3);
  assert.equal(p.child.height,16+2*(p.child.padding+border));
  assert.equal(p.gap,insetUnits*4);
  assert.equal(p.radius,resolveChip({density,border}).radius);
  if(insetUnits===0)assert.equal(p.child.radius,0);
 }
 const tight=resolveComposite({childFamily:'chip',density:'compact',border:2,insetUnits:1.5});
 assert.equal(tight.child.height,20);assert.equal(tight.singleRowHeight,32);
});
test('multiline uses collection geometry and content growth',()=>{
 for(const [density,inset] of [['compact',4],['default',8],['loose',12]] as const){
  const r=resolveMultiline({density,border:2});assert.equal(r.inset,inset);assert.equal(r.gap,inset);
  assert.equal(r.padding+2,inset);assert.equal(r.minHeight,24+2*inset);
  assert.equal(r.labelEdge,0);assert.equal(r.rowSeparation,2);assert.equal(r.height,'auto');assert.equal(r.radius,12);
 }
 assert.equal(json('contracts/components.json').components['multiline-row'].geometryFamily,'collection');
});
test('snapshot provenance and local build preserve authored content',()=>{
 const source=readFileSync(new URL('specimens/source.html',root));
 assert.equal(createHash('sha256').update(source).digest('hex'),json('system.manifest.json').source.fragmentSHA256);
 assert.ok(readFileSync(new URL('specimens/index.html',root),'utf8').includes(source.toString()));
 assert.ok(source.toString().includes('id="df-currency-list"'));
});
