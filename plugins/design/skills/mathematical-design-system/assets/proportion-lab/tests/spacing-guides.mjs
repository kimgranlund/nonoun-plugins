import assert from 'node:assert/strict';
import {slotGuideRegions} from '../dist/runtime/spacing-guides.mjs';
import {resolveControlSurface,resolveButtonPadding,DENSITIES} from '../dist/runtime/scale.mjs';
const overlaps=(a,b)=>Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x)>1e-8&&Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y)>1e-8;
for(const n of [4,8,13,24])for(const density of Object.keys(DENSITIES))for(const pct of [0,25,50,100,200]){
 const c=resolveControlSurface(n,density,pct),S=c.slotHeight,box={left:0,top:0,right:S,bottom:S,width:S,height:S};
 assert.deepEqual(slotGuideRegions({box,left:0,right:0,base:0,art:box}),[],'Full-size media has no internal spacing guides');
 for(const size of [c.icon,c.glyph]){
  const inset=(S-size)/2,art={left:inset,top:inset,right:S-inset,bottom:S-inset};
  const regions=slotGuideRegions({box,left:c.slotPadding,right:c.slotPadding,base:c.slotPadding,art});
  assert(Math.abs(regions.reduce((sum,r)=>sum+r.width*r.height,0)-(S*S-size*size))<1e-7);
  for(const [i,r] of regions.entries()){
   assert(!overlaps(r,{x:art.left,y:art.top,width:size,height:size}));
   assert(!regions.slice(i+1).some(other=>overlaps(r,other)));
   assert.notEqual(r.space,'compensation');
  }
 }
 for(const hasLeading of [false,true])for(const hasTrailing of [false,true]){
  const p=resolveButtonPadding({margin:c.margin,wrapperInset:c.labelPadding,height:c.height,hasLeading,hasTrailing});
  const labelBox={left:0,top:0,right:200+2*c.labelPadding,bottom:S,width:200+2*c.labelPadding,height:S};
  const regions=slotGuideRegions({box:labelBox,left:p.labelStart,right:p.labelEnd,base:c.labelPadding,gapLeft:0,gapRight:0});
  const compensation=regions.filter(r=>r.space==='compensation').reduce((sum,r)=>sum+r.width,0);
  const gap=regions.filter(r=>r.space==='gutter').reduce((sum,r)=>sum+r.width,0);
  assert.equal(compensation,0);
  assert.equal(p.compensation,0);
  assert.equal(p.labelStart,c.labelPadding);
  assert.equal(p.labelEnd,c.labelPadding);
  assert.equal(gap,0,'No extra separation inside label wrappers');
  assert.equal(p.wrapperGap,0);
 }
}
console.log('PASS empty-space partitions, fixed artwork, infeasible wrapper budgets, uniform half-unit labels and zero slot separation');
