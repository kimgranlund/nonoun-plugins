import {test} from 'node:test';
import assert from 'node:assert/strict';
import {resolveControl,resolveChip,resolveLabelEdges,resolveComposite,resolveComposedInput,resolveCollection,resolveCard,resolveMultiline,resolveChoice} from '../../differential-forms/geometry/index.ts';
test('defaults and independent expected control geometry',()=>{
 for(const [density,inset,height,gap] of [['compact',2,28,0],['default',4,32,4],['loose',8,40,8]]){
  const g=resolveControl({density});
  assert.equal(g.slot,24);assert.equal(g.inset,inset);assert.equal(g.height,height);assert.equal(g.gap,gap);assert.equal(g.labelEdge,6);assert.equal(g.radius,12);
 }
 assert.equal(resolveChip().labelEdge,3);
 assert.deepEqual(resolveLabelEdges(6,false,false),{start:6,end:6});
 assert.deepEqual(resolveLabelEdges(6,true,false),{start:0,end:12});
 assert.deepEqual(resolveLabelEdges(6,true,false,false),{start:0,end:6});
});
test('border conservation, preserved slots, attached-only subtraction and growth',()=>{
 for(const unit of [3,4,6])for(const border of [0,unit/2])for(const density of ['compact','default','loose'])for(const insetUnits of [0,1.5]){
  const input={unit,border,density,insetUnits};const c=resolveControl(input),x=resolveComposite(input),a=resolveComposedInput(input);
  assert.equal(c.height,c.slot+2*(c.padding+border));assert.equal(c.slot,6*unit);
  assert.equal(x.gap,insetUnits*unit);assert.equal(x.child.slot,c.slot);
  assert.equal(x.singleRowHeight,x.child.height+2*(x.padding+border));
  assert.ok(x.singleRowHeight>=c.height);
  if(insetUnits===0)assert.equal(x.child.radius,0);
  assert.ok(a.height>=c.height);assert.ok(a.height>=a.adornment.height+2*c.inset);
  const card=resolveCard(input),rows=resolveCollection(input),multi=resolveMultiline(input);
  assert.equal(card.padding+border,card.inset);assert.equal(rows.paddingBlock+border,rows.inset);
  assert.equal(multi.height,'auto');assert.equal(multi.minHeight,6*unit+2*rows.inset);
  assert.equal(resolveChoice(input).checkboxRadius,unit);
 }
});
test('invalid domains remain explicit',()=>{
 assert.throws(()=>resolveControl({unit:2}));assert.throws(()=>resolveControl({border:3}));
 assert.throws(()=>resolveComposite({insetUnits:2}));
});
