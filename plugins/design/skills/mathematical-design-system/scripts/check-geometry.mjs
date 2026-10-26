// HISTORICAL: pre-Differential Forms model. Current resolvers/tests are in assets/differential-forms/.
import assert from 'node:assert/strict';
import {resolve, resolveRadii, DENSITIES, check, composeControl} from './lib/legacy-scale.mjs';
assert.deepEqual(check(), []);
for(const tier of ['widget','product','content','brand'])for(const scale of ['sm','md','lg'])for(const size of ['sm','md','lg']){
 const v=resolve(tier,scale,size),q=(v.n+35)/32;
 assert.equal(v.type.smallControl,v.n+4);assert.equal(v.type.fieldLabel,v.n+5);
  assert.equal(v.c,v.n/4);assert.equal(v.glyph,1.5*v.n);
 assert.equal(v.type.display,v.type.body*q**3);assert.equal(v.type.heading,v.type.body*q**2);assert.equal(v.type.sectionKicker,v.type.body*9/8);
}
for (const density of Object.keys(DENSITIES)) { const v=resolve('product','md','md',density),r=resolveRadii(v.n,true,density); assert.equal(v.d,DENSITIES[density]*v.c); assert.equal(v.h,2*v.n+2*v.d); assert.equal(r.listboxOption,Math.max(0,r.control-v.d/2)); assert.equal(v.icon,16); assert.equal(v.type.control,14); }
// All 180 contexts preserve margins, match gutters and isolate density from type.
for(const tier of ['widget','product','content','brand'])for(const scale of ['sm','md','lg'])for(const size of ['sm','md','lg'])for(const density of Object.keys(DENSITIES)){
 const v=resolve(tier,scale,size,density), regular=resolve(tier,scale,size);
 for(const [level,factor] of Object.entries({group:1.25,tile:2,card:3,section:4})){
  assert.equal(v[level].margin,factor*v.d);
  assert.equal(v[level].gutter,v[level].margin);
 }
 const expected={widget:0.5,control:1,group:1.25,tile:2,card:3,section:4};
 assert.deepEqual(Object.keys(v.containers),Object.keys(expected));
 let previous=0;
 for(const [level,factor] of Object.entries(expected)){
  assert.equal(v.containers[level].margin,factor*v.d);
  assert.equal(v.containers[level].gutter,factor*v.d);
  assert.ok(v.containers[level].margin>previous);
  previous=v.containers[level].margin;
 }
 assert.deepEqual(v.composition.control,{margin:v.d,gutter:v.d/2});
 assert.deepEqual(v.composition.compactControl,{margin:v.d/2,gutter:v.d/4});
 assert.equal(v.composition.control.gutter*2,v.containers.control.gutter);
 assert.deepEqual(v.type,regular.type);
 assert.equal(v.compactHeight,2*v.n+v.d);
 assert.equal(v.table.clearance,v.d/4);
}
assert.equal(resolve().c,2);assert.equal(resolve().type.display,15*((8+35)/32)**3);

assert.deepEqual(composeControl(0),{margin:0,gutter:0});
assert.deepEqual(composeControl(7.5),{margin:7.5,gutter:3.75});
for(const value of [-1,NaN,Infinity])assert.throws(()=>composeControl(value));

console.log('PASS numerical geometry, composition, density and typography invariants');

{
 const {composeContainer}=await import('./lib/scale.mjs');
 for(const margin of [0,2,8,24,36])for(const percent of [0,50,100,200]){
  const result=composeContainer(margin,percent);
  assert.equal(result.margin,margin);assert.equal(result.gutter,margin*percent/100);
 }
 assert.deepEqual(composeContainer(24),{margin:24,gutter:18});
 for(const percent of [-1,201,NaN,Infinity])assert.throws(()=>composeContainer(24,percent));
 console.log('PASS container gutter ratios, preserved margins, defaults and invalid inputs');
}

{
 const {resolveSpacingRoles}=await import('./lib/scale.mjs');
 const roles=resolveSpacingRoles(24,{controlUnit:8,controlMargin:4,controlGutter:2});
 assert.equal(roles.page.gutter,24);assert.equal(roles.container.gutter,18);
 assert.equal(roles.group.gutter,12);assert.equal(roles.group.margin,0);
 assert.equal(roles.control.gutter,2);
 assert.equal(resolveSpacingRoles(24,{containerPercent:25}).group.gutter,12);
 for(const m of [0,6,24,36]){const r=resolveSpacingRoles(m);assert.equal(r.group.gutter,m*.5);assert.equal(r.container.gutter,m*.75);}
 console.log('PASS spacing roles: direct references, no compounding, group zero edges, independent Controls');
}

{
 const {resolveSpacingRoles,resolveControlSurface}=await import('./lib/scale.mjs');
 const r=resolveSpacingRoles(24,{pagePercent:150,groupPercent:25,controlUnit:8,controlMargin:4});
 assert.equal(r.page.gutter,36);assert.equal(r.container.gutter,18);assert.equal(r.group.gutter,6);assert.equal(r.control.gutter,2);
 assert.equal(resolveControlSurface(8).gutter,2);
 for(const key of ['pagePercent','groupPercent'])for(const value of [-1,201,NaN])assert.throws(()=>resolveSpacingRoles(24,{[key]:value}));
 console.log('PASS independent Page/Container/Group ratios and Control25% wrapper default');
}
{
 const {resolveSpacingRoles,resolveControlSurface}=await import('./lib/scale.mjs');
 for(const p of [0,25,100,200]){
  const c=resolveControlSurface(8,'regular',p),r=resolveSpacingRoles(24,{controlUnit:8,controlMargin:4,controlPercent:p});
  assert.equal(c.gutter,8*p/100);assert.equal(c.height,32);assert.equal(c.margin,4);
  assert.equal(r.control.gutter,c.gutter);assert.equal(r.container.gutter,18);assert.equal(r.group.gutter,12);assert.equal(r.page.gutter,24);
 }
 for(const p of [-1,201,NaN])assert.throws(()=>resolveControlSurface(8,'regular',p));
 console.log('PASS independent Control gutter slider and unchanged role geometry');
}

// Slot frames and padding are density-independent; gutters remain additional.
for(const tier of ['widget','product','content','brand'])for(const scale of ['sm','md','lg'])for(const size of ['sm','md','lg'])for(const density of Object.keys(DENSITIES)){
 const {resolveGeometry}=await import('./lib/scale.mjs');const {n,surface:c}=resolveGeometry(tier,scale,size,density);
 assert.equal(c.labelPadding,n/2);assert.equal(c.slotHeight,3*n);assert.equal(c.slotPadding,n/4);
 assert.equal(c.mediaSize,3*n);assert.equal(c.mediaSlotWidth,3*n);assert.equal(c.mediaPadding,0);assert.equal(c.mediaInset,0);assert.equal(c.mediaContentSeparation,c.labelPadding);assert.equal(c.iconSlotWidth,3*n);assert.equal(c.glyphSlotWidth,3*n);
 assert.equal(c.contentSeparation,2*c.gutter+c.margin/2);assert.equal(c.height,c.slotHeight+2*c.margin);
}

{const {resolveControlSurface}=await import('./lib/scale.mjs');for(const n of [4,8,13,24])for(const [i,density] of Object.keys(DENSITIES).entries()){const c=resolveControlSurface(n,density);assert.equal(c.slotGap,[0,n/8,n/4,3*n/8,n/2][i]);assert.equal(c.contentSeparation,2*c.slotPadding+c.slotGap);}}

{const {resolveControlSurface,resolveSpacingRoles}=await import('./lib/scale.mjs');for(const density of Object.keys(DENSITIES))for(const p of [0,25,50,200]){const c=resolveControlSurface(8,density,p),r=resolveSpacingRoles(24,{controlUnit:8,controlMargin:c.margin,controlPercent:p});assert.equal(c.slotGap,c.margin/2);assert.equal(r.control.slotGap,c.slotGap);assert.equal(c.slotPadding,8*p/100);}}

// Refactor parity: every supported context retains adopted spacing and typography.
{
 const {resolveGeometry}=await import('./lib/scale.mjs');
 for(const tier of ['widget','product','content','brand'])for(const scale of ['sm','md','lg'])for(const size of ['sm','md','lg'])for(const density of Object.keys(DENSITIES)){
  const old=resolve(tier,scale,size,density),now=resolveGeometry(tier,scale,size,density);
  // Intended change 2026-10-21: product sm/lg units moved; compare those contexts against the legacy context with the same n.
  if(tier==='product'&&old.n!==now.n)continue;
  for(const key of ['n','d','c','type'])assert.deepEqual(now[key],old[key]);
  for(const key of ['tile','card','section'])assert.equal(now.containers[key].margin,old.containers[key].margin);
  assert.equal(now.surface.glyph,now.type.control);assert.equal(now.surface.glyphInset,(now.surface.slotHeight-now.surface.glyph)/2);assert.equal(now.surface.iconSlotWidth,now.surface.slotHeight);assert.equal(now.surface.glyphSlotWidth,now.surface.slotHeight);
  for(const key of ['height','margin','slotPadding','slotGap','innerHeight','icon'])assert.equal(now.surface[key],old.surface[key]);
  assert.equal(now.groupMarginReference,old.containers.group.margin);
  assert.equal('h' in now,false);assert.equal('radius' in now,false);
 }
 console.log('PASS unchanged API fields across 180 contexts (except the intended product sm/lg units); current table model and legacy fields excluded');
}

// Product keeps the md shoulder distance at every scale; content and brand step 1, 2, 3 by scale.
{
 const {resolveGeometry}=await import('./lib/scale.mjs');
 const n=(t,sc,sz)=>resolveGeometry(t,sc,sz).n,H=(t,sc,sz)=>resolveGeometry(t,sc,sz).surface.height;
 assert.deepEqual(['sm','md','lg'].map(sc=>['sm','md','lg'].map(sz=>H('product',sc,sz))),[[20,28,36],[24,32,40],[28,36,44]]);
 for(const sc of ['sm','md','lg'])assert.equal(n('product',sc,'md')-n('product',sc,'sm'),2),assert.equal(n('product',sc,'lg')-n('product',sc,'md'),2);
 for(const t of ['content','brand'])for(const [sc,step] of [['sm',1],['md',2],['lg',3]])assert.equal(n(t,sc,'md')-n(t,sc,'sm'),step),assert.equal(n(t,sc,'lg')-n(t,sc,'md'),step);
 assert.equal(n('product','md','md'),8);
 // Its own legacy n still resolves the same spacing and type (parity by unit, not by context).
 for(const sc of ['sm','md','lg'])for(const sz of ['sm','md','lg'])for(const density of Object.keys(DENSITIES)){
  const now=resolveGeometry('product',sc,sz,density),same=['widget','product','content','brand'].flatMap(t=>['sm','md','lg'].flatMap(a=>['sm','md','lg'].map(b=>resolve(t,a,b,density)))).find(v=>v.n===now.n);
  if(same){const {title,...rest}=now.type,{title:_t,...restSame}=same.type;assert.deepEqual(rest,restSame);assert.equal(title,now.type.body+{sm:0,md:1,lg:2}[sz]);assert.equal(now.d,same.d);}
 }
 console.log('PASS product even shoulders (20/28/36, 24/32/40, 28/36/44), content/brand steps 1/2/3, default n 8');
}

{
 const {resolveButtonPadding,resolveControlSurface}=await import('./lib/scale.mjs');
 for(const n of [4,8,13,24])for(const density of Object.keys(DENSITIES))for(const percentage of [0,25,100,200])for(const amount of [0,25,50,100])for(const hasLeading of [false,true])for(const hasTrailing of [false,true]){
  const c=resolveControlSurface(n,density,percentage),radius=amount/100*c.height/2;
  const p=resolveButtonPadding({margin:c.margin,wrapperInset:c.labelPadding,height:c.height,radius,hasLeading,hasTrailing});
  assert.equal(p.inlinePadding,c.margin);
  assert.equal(p.compensation,0);
  assert.equal(p.labelStart,c.labelPadding+(hasLeading?0:p.compensation));
  assert.equal(p.labelEnd,c.labelPadding+(hasTrailing?0:p.compensation));
  assert.equal(p.wrapperGap,0);assert.equal(c.wrapperGap,0);assert.equal(p.labelGap,0);
  assert.equal(p.exposedLabelInset,c.margin+c.labelPadding+p.edgePadding);
 }
 const p=resolveButtonPadding({margin:4,wrapperInset:4,height:32,hasLeading:true});
 assert.equal(p.labelStart,4);assert.equal(p.labelEnd,4);assert.equal(p.inlinePadding,4);
 // Icon artwork-to-text separation is centering n/2 plus label padding L.
 const c8=resolveControlSurface(8);assert.equal(c8.iconInset+p.labelStart,c8.iconContentSeparation);
 assert.throws(()=>resolveButtonPadding({margin:4,wrapperInset:2,radius:16}),RangeError);
 console.log('PASS radius-independent uniform label padding, zero added slot separation, zero wrapper gap, half-unit label inline padding');
}
