import test from 'node:test';
import assert from 'node:assert/strict';
import {resolveControl,resolveChip,resolveBadge,resolveChoice,resolveComposite,resolveCard,resolveCollection,resolveLabelEdges} from '../geometry/index.ts';
import type {Density,Curvature} from '../geometry/types.ts';
const densities:Density[]=['compact','default','loose'];
const curves:Curvature[]=['sharpest','sharp','default','soft','softest'];
test('font and default golden values',()=>{
 for(const [unit,font] of [[3,12],[3.5,13],[4,14],[4.5,15],[5,16]]) assert.equal(resolveControl({unit}).fontSize,font);
 const c=resolveControl(); assert.equal(c.height,32);assert.equal(c.slot,24);assert.equal(c.labelEdge,6);
 assert.equal(resolveChip().height,24);assert.equal(resolveChip().labelEdge,3);assert.equal(resolveBadge().height,16);
 assert.equal(resolveCard().inset,18);assert.equal(resolveCollection().inset,8);
});
test('border conservation across supported families',()=>{
 for(const unit of [3,3.5,4,4.5,5,6])for(const density of densities)for(const border of [0,unit/4,unit/2]){
 const c=resolveControl({unit,density,border}); assert.equal(c.slot+2*(c.padding+border),c.height);
 assert.equal(c.height,resolveControl({unit,density}).height);
 const chip=resolveChip({unit,density,border});assert.equal(chip.slot+2*(chip.padding+border),chip.height);
 const badge=resolveBadge({unit,density,border},37);assert.equal(badge.width,resolveBadge({unit,density},37).width);
 assert.equal(badge.paddingInline+border,.5*unit);
 const row=resolveCollection({unit,density,border});assert.equal(2*(row.cellPaddingInline+border),row.gap);
 const choice=resolveChoice({unit,density,border});assert.equal(choice.switchHeight-2*(border+choice.switchPadding),choice.switchThumb);
 }
});
test('composites conserve slots at extremes and zero inset wins',()=>{
 for(const unit of [3,4,6])for(const density of densities)for(const border of [0,unit/2])for(const insetUnits of [0,.5,1,1.5])for(const curvature of curves){
 const p=resolveComposite({unit,density,border,insetUnits,curvature});
 assert.equal(p.child.slot,6*unit);assert.ok(p.child.padding>=0);assert.equal(p.child.height,p.child.slot+2*(p.child.padding+border));
 assert.equal(p.gap,insetUnits*unit);assert.ok(p.child.radius<=p.child.height/2);
 if(insetUnits===0)assert.equal(p.child.radius,0);
 }
 const p=resolveComposite({unit:4,density:'compact',border:2,insetUnits:1.5});assert.equal(p.child.height,28);assert.equal(p.singleRowHeight,40);
});
test('exposed-edge rules and density independence',()=>{
 assert.deepEqual(resolveLabelEdges(6,false,false),{start:6,end:6});assert.deepEqual(resolveLabelEdges(6,true,false),{start:0,end:12});
 assert.deepEqual(resolveLabelEdges(6,false,true),{start:12,end:0});assert.deepEqual(resolveLabelEdges(6,true,true),{start:0,end:0});
 assert.deepEqual(resolveLabelEdges(6,true,false,false),{start:0,end:6});
 for(const density of densities){assert.equal(resolveControl({density}).labelEdge,6);assert.equal(resolveChip({density}).labelEdge,3);}
});
test('curvature and primitive exceptions',()=>{
 for(const curvature of curves){assert.equal(resolveChoice({curvature}).checkboxRadius,4);assert.ok(resolveChip({curvature}).radius<=resolveChip({curvature}).height/2);}
 assert.equal(resolveControl({curvature:'softest'}).radius,16);assert.equal(resolveChip({curvature:'softest'}).radius,12);assert.equal(resolveCard({curvature:'softest'}).radius,16);
});
test('invalid geometry is rejected rather than silently normalized',()=>{
 assert.throws(()=>resolveControl({unit:0}),RangeError);assert.throws(()=>resolveControl({border:3}),RangeError);
 assert.throws(()=>resolveComposite({insetUnits:2}),RangeError);assert.throws(()=>resolveBadge({},-1),RangeError);
});
