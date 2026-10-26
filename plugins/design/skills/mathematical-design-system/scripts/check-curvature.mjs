// HISTORICAL: pre-Differential Forms model. Current resolvers/tests are in assets/differential-forms/.
import assert from 'node:assert/strict';
import {resolveCurvature as r} from './lib/legacy-curvature.mjs';
assert.equal(r(4,1,4,100,16).multiplier,1);
assert.equal(r(14,1,4,100,56).multiplier,2.5);
assert.equal(r(24,1,4,200,96).multiplier,4);
assert.equal(r(2,1,4,100,8).t,0);
assert.equal(r(30,1,4,200,120).t,1);
assert.equal(r(14,4,1,100,56).multiplier,2.5);
for(const supported of [true,false])for(let n=4;n<=24;n++)for(const q of [2,3,4,5,6]){
 const h=2*n+q*n/2,cap=h/2,pill=r(n,6,6,4*h,h,supported),sharp=r(n,0,0,4*h,h,supported),v=r(n,1,4,4*h,h,supported);
 assert.equal(pill.radius,cap);assert.equal(pill.exponent,1);assert.equal(pill.pill,true);
 assert.equal(sharp.radius,0);assert.equal(sharp.pill,false);
 assert.ok(v.radius>=0&&v.radius<=cap);assert.ok(v.exponent>=1&&v.exponent<=1.5);
 assert.equal(v.multiplier,r(n,1,4,4*h,4*n,supported).multiplier);
}
assert.equal(r(8,6,6,20,32).radius,10);
assert.equal(r(8,6,6,0,32).radius,0);
console.log('PASS curvature endpoints, interpolation, reversed/equal bounds, all densities, caps, shape transition and round fallback');

const {resolveRadius,nestedRadius,defaultCurvatureProfiles}=await import('./lib/legacy-curvature.mjs');
const profiles=defaultCurvatureProfiles();
for(const supported of [true,false])for(const n of [4,6,8,14,24,30])for(const q of [.5,.75,1,1.25,1.5]){
 const d=q*n,h=2*n+2*d;
 const v=resolveRadius(n,profiles.balanced,d,1000,h,supported);
 assert.equal(v.target,.5*n+d);assert.ok(v.radius<=h/2);
 const pill=resolveRadius(n,profiles.round,d,1000,h,supported);
 assert.equal(pill.radius,h/2);assert.equal(pill.exponent,1);assert.ok(pill.pill);
 const chip=resolveRadius(n,profiles.round,d/2,1000,2*n+d,supported);
 assert.equal(chip.radius,(2*n+d)/2);
 assert.equal(resolveRadius(n,profiles.sharp,4*d).radius,0);
 const card=resolveRadius(n,profiles.balanced,3*d);
 assert.ok(Math.abs(nestedRadius(card.radius,3*d)-.5*n)<1e-10);
 assert.equal(nestedRadius(pill.radius,d/2),(2*n+d)/2);
}
assert.equal(resolveRadius(8,profiles.round,8,10,32).radius,5);
assert.equal(resolveRadius(8,profiles.round,8,0,32).radius,0);
assert.throws(()=>resolveRadius(8,{baseline:NaN,marginAllowance:1},8),RangeError);
assert.equal(nestedRadius(2,4),0);
assert.equal(defaultCurvatureProfiles().balanced.baseline,.5);
console.log('PASS v2 schema, units, baseline+margin, nested offsets, all densities, compact and width caps, round fallback');
const {curvaturePatterns}=await import('./lib/legacy-curvature.mjs');
assert.equal(resolveRadius(8,profiles.balanced,32).curvatureMode,'independent');
assert.equal(resolveRadius(8,profiles.balanced,32).radius,36);
assert.equal(resolveRadius(8,profiles.balanced,24).radius,28);
assert.equal(resolveRadius(8,profiles.balanced,16).radius,20);
const option=resolveRadius(8,profiles.balanced,4,Infinity,Infinity,true,{...curvaturePatterns.listboxOption,parentRadius:12,parentExponent:1.125,inset:4});
assert.equal(option.radius,8);assert.equal(option.exponent,1.125);assert.equal(option.curvatureMode,'inset');
assert.throws(()=>resolveRadius(8,profiles.balanced,4,Infinity,Infinity,true,{curvatureMode:'inset'}),RangeError);
assert.throws(()=>resolveRadius(8,profiles.balanced,4,Infinity,Infinity,true,{curvatureMode:'auto'}),RangeError);
console.log('PASS v3 independent defaults, Card/Tile/Section radii, explicit listbox inset, invalid mode/parent validation');
const {resolveSurfaceRadius:surface}=await import('./lib/legacy-curvature.mjs');
for(const n of [4,8,24])for(const d of [n/2,n*.75,n,n*1.25,n*1.5]) {
 const args={n,margin:d,width:1000,height:200,supported:false};
 const parent=surface({...args,profile:profiles.balanced});
 const child=surface({...args,parent,margin:d/2,mode:'inset',inset:d});
 const leaf=surface({...args,parent:child,margin:d/4,mode:'inset',inset:d/2});
 assert.equal(child.profile,profiles.balanced);assert.equal(child.profileSource,'inherited');
 assert.equal(leaf.radius,Math.max(0,parent.radius-d-d/2));
 assert.equal(surface({...args,parent:child}).curvatureMode,'independent');
 assert.equal(surface({...args,parent,profile:profiles.crisp}).profile,profiles.crisp);
 const pill=surface({...args,parent,mode:'override',override:'pill',width:10});
 assert.equal(pill.radius,5);assert.equal(pill.profile,profiles.balanced);
 assert.equal(surface({...args,parent:pill}).radius,parent.radius);
 assert.equal(surface({...args,parent,mode:'override',override:'sharp'}).radius,0);
 assert.equal(surface({...args,parent,mode:'inset',inset:200}).radius,0);
 assert.equal(surface({...args,parent,width:0}).radius,0);
}
assert.equal(surface({n:8,margin:8}).radius,0);
assert.throws(()=>surface({n:8,margin:8,mode:'inset',inset:4}),RangeError);
assert.throws(()=>surface({n:8,margin:8,mode:'override',override:'pill'}),RangeError);
assert.throws(()=>surface({n:8,margin:8,width:NaN}),RangeError);
console.log('PASS v4 profile inheritance, mode isolation, nested composition, local overrides, physical caps and invalid inputs');
for(const n of [4,8,24])for(const q of [.5,.75,1,1.25,1.5]) {
 const args={n,margin:n*q,width:1000,height:1000,profile:profiles.balanced,bounds:{min:.75*n,max:4*n*q},supported:false};
 const p=surface(args), c=surface({...args,profile:undefined,bounds:undefined,parent:p,mode:'inset',inset:n*q});
 assert.equal(c.bounds,p.bounds);assert.ok(c.radius>=.75*n&&c.radius<=4*n*q);
 assert.equal(surface({...args,width:2}).radius,1);
 assert.equal(surface({...args,width:0}).radius,0);
 assert.equal(surface({...args,profile:profiles.sharp}).radius,0);
 assert.equal(surface({...args,mode:'override',override:'pill',width:200}).radius,100);
 const upper=surface({...args,margin:100*n});assert.equal(upper.radius,args.bounds.max);assert.equal(upper.boundEffect,'maximum');
}
const bounded=surface({n:8,margin:8,profile:profiles.balanced,bounds:{min:6,max:32}});
assert.equal(surface({n:8,margin:4,parent:bounded,mode:'inset',inset:8}).radius,6);
assert.throws(()=>surface({n:8,margin:8,bounds:{min:9,max:8}}),RangeError);
assert.throws(()=>surface({n:8,margin:8,bounds:{min:NaN,max:8}}),RangeError);
console.log('PASS v5 inherited bounds, density/scale sweep, minimum and maximum adjustments, physical caps, Sharp/override exemptions and conflicts');
const {resolveRadiusProgression:progress}=await import('./lib/legacy-curvature.mjs');
const chain={bounds:{min:6,max:32},distances:[0,8,12],frames:Array.from({length:3},()=>({width:200,height:200})),profile:profiles.balanced};
const ps=progress(chain);
assert.equal(ps[0].radius,32);assert.equal(ps[2].radius,6);
assert.ok(Math.abs(ps[1].radius-14.666666666666668)<1e-10);
assert.equal(ps[1].t,2/3);
assert.ok(Math.abs((ps[0].radius-ps[1].radius)/8-(ps[1].radius-ps[2].radius)/4)<1e-10);
assert.equal(progress({...chain,profile:profiles.sharp})[0].radius,0);
assert.equal(progress({...chain,frames:[{width:10,height:10},...chain.frames.slice(1)]})[1].radius,ps[1].radius);
assert.equal(progress({...chain,frames:[{width:10,height:10},...chain.frames.slice(1)]})[0].physicalLimited,true);
for(const n of [4,8,24])for(const q of [.5,.75,1,1.25,1.5]){
 const d=n*q,values=progress({...chain,bounds:{min:.375*n,max:4*d},distances:[0,d,1.5*d],frames:chain.frames.map(()=>({width:1000,height:1000}))});
 assert.equal(values[0].radius,4*d);assert.equal(values[2].radius,.375*n);
 assert.ok(values[0].radius>=values[1].radius&&values[1].radius>=values[2].radius);
}
assert.throws(()=>progress({...chain,distances:[0,0,0]}),RangeError);
assert.throws(()=>progress({...chain,distances:[0,12,8]}),RangeError);
assert.throws(()=>progress({...chain,bounds:{min:9,max:6}}),RangeError);
assert.deepEqual(progress({...chain,bounds:{min:6,max:6},distances:[0,0,0]}).map(v=>v.radius),[6,6,6]);
console.log('PASS v6 distance interpolation, endpoints, nonuniform insets, constant slope, cap isolation, density sweep, Sharp and degenerate validation');
const {resolveConcentricRadii:concentric}=await import('./lib/legacy-curvature.mjs');
const concentricInput={bounds:{min:16,max:40},distances:[0,10,15],frames:[{width:200,height:100},{width:180,height:80},{width:170,height:70}],profile:profiles.balanced};
const fitted=concentric(concentricInput);
assert.deepEqual(fitted.layers.map(l=>l.radius),[31,21,16]);assert.equal(fitted.valid,true);
const conflict=concentric({...concentricInput,bounds:{min:16,max:24}});
assert.equal(conflict.valid,false);assert.equal(conflict.layers[0].radius,31);assert.equal(conflict.layers[0].ceilingExcess,7);
const physical=concentric({...concentricInput,frames:concentricInput.frames.map(()=>({width:20,height:20}))});
assert.equal(physical.physicalConflict,true);assert.deepEqual(physical.layers.map(l=>l.radius),[31,21,16]);
assert.equal(concentric({...concentricInput,profile:profiles.sharp}).valid,true);
assert.deepEqual(concentric({...concentricInput,profile:profiles.sharp}).layers.map(l=>l.radius),[0,0,0]);
assert.equal(concentric({...concentricInput,bounds:{min:50,max:40}}).ceilingConflict,true);
assert.equal(concentric({...concentricInput,distances:[0],frames:[{width:100,height:100}]}).layers[0].radius,16);
for(const n of [4,8,24])for(const q of [.5,.75,1,1.25,1.5]){
 const d=q*n, r=concentric({...concentricInput,bounds:{min:2*n,max:4*d},distances:[0,d,1.5*d],frames:Array.from({length:3},()=>({width:1000,height:1000}))});
 assert.equal(r.layers[0].radius-r.layers[1].radius,d);
 assert.equal(r.layers[1].radius-r.layers[2].radius,d/2);
 assert.equal(r.layers[2].radius,2*n);assert.equal(r.ceilingConflict,2*n+1.5*d>4*d);
}
assert.throws(()=>concentric({...concentricInput,distances:[0,15,10]}),RangeError);
console.log('PASS v7 concentric offsets, seed preservation, explicit ceiling/physical conflicts without clamping, Sharp exemption and density sweep');
const {resolveRadiusGroup:group}=await import('./lib/legacy-curvature.mjs');
const boxes=[{x:0,y:0,width:100,height:62},{x:10,y:10,width:80,height:42},{x:15,y:15,width:70,height:32}];
const args={innerRadius:16,ceiling:40,frames:boxes,mode:'concentric'};
assert.deepEqual(group(args).layers.map(l=>l.radius),[31,21,16]);assert.equal(group(args).maxFeasibleSeed,16);assert.equal(group(args).valid,true);
assert.equal(group({...args,innerRadius:17}).valid,false);assert.equal(group({...args,innerRadius:17}).layers[0].radius,32);
assert.equal(group({...args,ceiling:20}).maxFeasibleSeed,5);assert.equal(group({...args,ceiling:20}).valid,false);
assert.deepEqual(group({...args,mode:'standalone'}).layers.map(l=>l.radius),[16,16,16]);
assert.equal(group({...args,frames:[boxes[0],{...boxes[1],x:9},boxes[2]]}).valid,false);
assert.equal(group({...args,innerRadius:3,ceiling:2}).valid,false);
assert.equal(group({...args,sharp:true,ceiling:0}).valid,true);
const inserted=[boxes[0],{x:5,y:5,width:90,height:52},...boxes.slice(1)];
assert.equal(group({...args,frames:inserted}).layers[0].radius,31);
assert.equal(group({...args,frames:inserted}).layers[2].radius,21);
assert.throws(()=>group({...args,frames:[{...boxes[0],width:NaN}]}),RangeError);
console.log('PASS v8 whole-group feasibility, physical/ceiling conflicts, four-edge validation, standalone and inserted-wrapper invariance');
for(const height of [24,28,32,36,40]){
 const p=group({innerRadius:100,ceiling:0,sharp:true,mode:'pill',frames:[{x:0,y:0,width:200,height}]});
 assert.equal(p.layers[0].radius,height/2);assert.equal(p.valid,true);assert.equal(p.maxFeasibleSeed,null);
}
assert.equal(group({innerRadius:3,ceiling:32,mode:'pill',frames:[{x:0,y:0,width:10,height:32}]}).layers[0].radius,5);
assert.equal(group({innerRadius:3,ceiling:32,mode:'pill',frames:[{x:0,y:0,width:0,height:32}]}).layers[0].radius,0);
console.log('PASS v9 Pill dimension response, dial/Sharp exemption, narrow and zero-size frames');
const {resolveEndpointRadiusGroup:endpoint}=await import('./lib/legacy-curvature.mjs');
const ep={innerRadius:16,outerRadius:2,frames:boxes,mode:'interpolated'};
assert.ok(Math.abs(endpoint(ep).layers[1].radius-11.333333333333334)<1e-10);
assert.equal(endpoint(ep).valid,true);
for(const [innerRadius,outerRadius] of [[2,16],[8,8],[0,0],[16,2]]){
 const g=endpoint({...ep,innerRadius,outerRadius});assert.equal(g.layers[0].radius,outerRadius);assert.equal(g.layers[2].radius,innerRadius);
 assert.ok(Math.abs(g.layers[1].radius-(innerRadius+(outerRadius-innerRadius)/3))<1e-10);
}
assert.equal(endpoint({...ep,innerRadius:20}).valid,false);
assert.equal(endpoint({...ep,innerRadius:20}).layers[2].radius,20);
assert.equal(endpoint({...ep,frames:[boxes[0],boxes[0]],innerRadius:8,outerRadius:8}).valid,true);
assert.equal(endpoint({...ep,frames:[boxes[0],boxes[0]]}).valid,false);
assert.equal(endpoint({...ep,mode:'standalone'}).layers[0].radius,16);
assert.equal(endpoint({...ep,mode:'pill'}).layers[0].radius,31);
console.log('PASS v10 independent ascending/descending/equal endpoints, distance interpolation, physical conflicts without clamping, coincident frames and comparison modes');
const nearZeroFrames=[{x:0,y:0,width:100,height:100},{x:-.01,y:-.01,width:100.02,height:100.02},{x:.01,y:.01,width:99.98,height:99.98}];
const tiny=endpoint({innerRadius:10,outerRadius:20,frames:nearZeroFrames});
assert.equal(tiny.valid,false);assert.equal(tiny.layers[1].radius,null);assert.equal(tiny.layers[1].t,null);
const unordered=endpoint({innerRadius:10,outerRadius:20,frames:[{x:0,y:0,width:100,height:100},{x:-.01,y:-.01,width:100.02,height:100.02},{x:1,y:1,width:98,height:98}]});
assert.equal(unordered.valid,false);assert.equal(unordered.layers[1].radius,null);assert.ok(unordered.layers[1].rawT>1);
const tinyOrdered=[{x:0,y:0,width:100,height:100},{x:.005,y:.005,width:99.99,height:99.99},{x:.01,y:.01,width:99.98,height:99.98}];
assert.equal(endpoint({innerRadius:10,outerRadius:20,frames:tinyOrdered}).layers[1].radius,null);
assert.equal(endpoint({innerRadius:10,outerRadius:10,frames:tinyOrdered}).valid,true);
const strictCap=endpoint({innerRadius:10.04,outerRadius:10.04,frames:[{x:0,y:0,width:20,height:20}],mode:'standalone'});
assert.equal(strictCap.valid,false);assert.equal(strictCap.layers[0].radius,10.04);assert.equal(strictCap.layers[0].withinMeasurementTolerance,true);
assert.ok(strictCap.layers[0].physicalExcess>0);
const {resolve:resolveGeometry}=await import('./lib/legacy-scale.mjs');
const {radiusEndpointPresets:calibrated}=await import('./lib/legacy-curvature.mjs');
let presetCases=0;
for(const tier of ['widget','product','content','brand'])for(const scale of ['sm','md','lg'])for(const size of ['sm','md','lg'])for(const density of ['tight','compact','regular','spacious','loose']){
 const {n,d,h}=resolveGeometry(tier,scale,size,density),w=217;
 const frames=[{x:0,y:0,width:w,height:h+3*d},{x:d,y:d,width:w-2*d,height:h+d},{x:1.5*d,y:1.5*d,width:w-3*d,height:h}];
 for(const p of Object.values(calibrated))for(const mode of ['standalone','interpolated','pill']){
  const value=endpoint({innerRadius:p.inner*n,outerRadius:p.outer*n,frames,mode});
  assert.equal(value.valid,true,`${tier}/${scale}/${size}/${density}/${mode}: ${value.issues}`);presetCases++;
 }
}
console.log(`PASS v11 near-zero and unordered interpolation rejection, exact physical caps, and ${presetCases} calibrated preset/mode/axis cases`);

{
// Adopted percentage model: all contexts, density endpoints, physical conflicts.
const {resolvePercentageRadiusGroup:percent}=await import('./lib/curvature.mjs');
const {resolveGeometry:resolve,resolveControlSurface:surface}=await import('./lib/scale.mjs');
for(const tier of ['widget','product','content','brand'])for(const scale of ['sm','md','lg'])for(const size of ['sm','md','lg'])for(const density of ['tight','compact','regular','spacious','loose']){
 const {n}=resolve(tier,scale,size,density),g=surface(n,density);
 for(const amount of [0,25,50,100]){
  const frames=[{x:0,y:0,width:240,height:g.height},{x:g.margin,y:g.margin,width:240-2*g.margin,height:g.innerHeight}];
  const r=percent({amount,frames});
  assert.equal(r.valid,true);assert.equal(r.layers[0].radius,amount/100*g.height/2);assert.equal(r.layers[1].radius,amount/100*1.5*n);
 }
 assert.equal(g.icon,2*n);assert.equal(g.glyph,n+6);assert.equal(g.innerHeight,3*n);
}
assert.deepEqual(['loose','spacious','regular','compact','tight'].map(d=>surface(8,d).height),[40,36,32,28,24]);
assert.equal(percent({amount:100,frames:[{x:0,y:0,width:10,height:32}],mode:'standalone'}).valid,false);
assert.equal(percent({amount:100,frames:[{x:0,y:0,width:100,height:120}],referenceHeights:[32],mode:'standalone'}).layers[0].radius,16);
assert.throws(()=>percent({amount:101,frames:[]}));
console.log('PASS percentage radius model: 720 axis cases, stable inner/icon/glyph, density heights, listbox reference and width conflicts');

}

{
 const {resolvePercentageRadiusGroup:r}=await import('./lib/curvature.mjs');
 const frames=[{x:0,y:0,width:200,height:120},{x:24,y:24,width:152,height:72},{x:30,y:30,width:140,height:60}];
 const group=r({family:'container',amount:100,retained:50,rootMargin:24,frames});
 assert.deepEqual(group.layers.map(l=>l.radius),[24,12,6]);
 assert.equal(group.valid,true);
 assert.deepEqual(r({family:'container',amount:0,retained:100,rootMargin:24,frames}).layers.map(l=>l.radius),[0,0,0]);
 const control=r({amount:100,retained:100,frames:[{x:0,y:0,width:200,height:32},{x:4,y:4,width:192,height:24}]});
 assert.deepEqual(control.layers.map(l=>l.radius),[16,16]);assert.equal(control.valid,false);
 assert.equal(r({amount:100,retained:100,mode:'standalone',frames:[{x:0,y:0,width:100,height:24}]}).layers[0].radius,12);
 assert.equal(r({family:'container',amount:100,retained:50,rootMargin:24,frames:[frames[0]],mode:'standalone'}).layers[0].radius,24);
 for(const retained of [-1,101,NaN])assert.throws(()=>r({frames,retained}));
 console.log('PASS retained floors: immediate-parent recurrence, scope isolation, Sharp, margin reference, unclamped physical conflict');
}

{
 const {resolvePercentageRadiusGroup:current}=await import('./lib/curvature.mjs');
 const {resolvePercentageRadiusGroup:legacy}=await import('./lib/legacy-curvature.mjs');
 for(const family of ['container','control'])for(const amount of [0,25,50,100])for(const retained of [0,50,100])for(const mode of ['standalone','nested','pill']){
  const options={family,amount,retained,rootMargin:24,frames:[{x:0,y:0,width:120,height:80},{x:8,y:8,width:104,height:64},{x:16,y:16,width:88,height:48}],mode};
  const a=current(options),b=legacy({...options,mode:mode==='nested'?'interpolated':mode});
  assert.equal(a.valid,b.valid);assert.deepEqual(a.layers.map(l=>[l.radius,l.candidate,l.floor,l.cap]),b.layers.map(l=>[l.radius,l.candidate,l.floor,l.cap]));
 }
 assert.throws(()=>current({frames:[{x:0,y:0,width:32,height:32}],mode:'interpolated'}));
 console.log('PASS Nested rename parity and obsolete-mode rejection');
}

const {resolveMediaRadius}=await import('./lib/curvature.mjs');
for(const n of [4,8,13,24])for(const q of [2,3,4,5,6])for(const amount of [0,25,50,100])for(const retained of [0,50,100]){
 const S=3*n,parentRadius=amount/100*(q+4)*n/4,frame={x:0,y:0,width:S,height:S};
 const result=resolveMediaRadius({shape:'control',frame,amount,retained,parentRadius});
 const expected=amount===0?0:Math.max(amount/100*S/2,retained/100*parentRadius);
 assert.equal(result.layers[0].radius,expected);assert.equal(result.valid,expected<=S/2);
 assert.equal(resolveMediaRadius({shape:'circle',frame,amount,retained,parentRadius}).layers[0].radius,S/2);
 assert.equal(resolveMediaRadius({shape:'intrinsic',frame,amount,retained,parentRadius}).clips,false);
}
assert.throws(()=>resolveMediaRadius({shape:'control',frame:{x:0,y:0,width:24,height:24}}));
assert.throws(()=>resolveMediaRadius({shape:'other',frame:{x:0,y:0,width:24,height:24}}));
console.log('PASS media opt-in, intrinsic/circular defaults, Sharp and retained-parent conflicts');
