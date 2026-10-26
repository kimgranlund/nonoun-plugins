// HISTORICAL: pre-Differential Forms model. Current resolvers/tests are in assets/differential-forms/.
// Historical compatibility models. New consumers use curvature.mjs.
// Legacy v1 positional API, retained for existing consumers. New profiles use resolveRadius below.
export function resolveCurvature(n, min, max, width, height, supported=true) {
 const t=Math.min(1,Math.max(0,(n-4)/20));
 const multiplier=min+(max-min)*t;
 const base=Math.max(0,n*multiplier);
 const cap=Math.max(0,Math.min(width,height)/2);
 const saturation=cap>0?Math.min(1,base/cap):0;
 const exponent=supported?1.5-.5*saturation:1;
 const radius=Math.min(cap,base*exponent);
 return {t,multiplier,base,cap,exponent,radius,pill:cap>0&&base>=cap};
}

// Version 4 adds composable surface resolution; the positional API remains compatible.
// lengths scale with n; marginAllowance is a dimensionless ratio.
export const curvatureModelVersion = 11;
export const curvaturePatterns = {default:{curvatureMode:'independent'},listboxOption:{curvatureMode:'inset'},segmentedOption:{curvatureMode:'inset'}};
export function defaultCurvatureProfiles() {
 return {
  sharp:{name:'Sharp',baseline:0,marginAllowance:0},
  crisp:{name:'Crisp',baseline:.1875,marginAllowance:.25},
  balanced:{name:'Balanced',baseline:.5,marginAllowance:1},
  round:{name:'Round',baseline:2,marginAllowance:1}
 };
}
export function resolveRadius(n, profile, margin, width=Infinity, height=Infinity, supported=true, options={}) {
 if (![n,margin,profile.baseline,profile.marginAllowance].every(v=>Number.isFinite(v)&&v>=0)) throw new RangeError('Curvature requires finite nonnegative geometry');
 const curvatureMode=options.curvatureMode??curvaturePatterns.default.curvatureMode;
 if(!['independent','inset'].includes(curvatureMode))throw new RangeError('Unknown curvature mode');
 if(curvatureMode==='inset') {
  const {parentRadius,parentExponent,inset}=options;
  if(![parentRadius,parentExponent,inset].every(v=>Number.isFinite(v)&&v>=0))throw new RangeError('Inset curvature requires parent radius, corner exponent and inset');
  const cap=Math.max(0,Math.min(width,height)/2),radius=nestedRadius(parentRadius,inset,cap);
  return {curvatureMode,baseline:0,allowance:0,target:Math.max(0,parentRadius-inset),cap,radius,exponent:parentExponent,pill:cap>0&&Number.isFinite(cap)&&radius===cap,multiplier:n?radius/n:0};
 }
 const baseline=profile.baseline*n, allowance=profile.marginAllowance*margin;
 const target=baseline+allowance, cap=Math.max(0,Math.min(width,height)/2);
 const radius=Math.min(target,cap), pill=cap>0&&Number.isFinite(cap)&&target>=cap;
 const saturation=cap>0&&Number.isFinite(cap)?Math.min(1,target/cap):0;
 // Radius is the physical length, not multiplied again by corner compensation.
 const exponent=supported?1.5-.5*saturation:1;
 return {curvatureMode,baseline,allowance,target,cap,radius,exponent,pill,multiplier:n?target/n:0};
}
export function nestedRadius(parentRadius, inset, cap=Infinity) {
 return Math.min(cap,Math.max(0,parentRadius-inset));
}

// Composable v4 API. Pass a resolved parent to inherit its profile, not its mode.
export function resolveSurfaceRadius({n, margin, width=Infinity, height=Infinity,
 profile, parent, mode='independent', inset, override, bounds, supported=true}) {
 const resolvedProfile=profile??parent?.profile??defaultCurvatureProfiles().sharp;
 if (![width,height].every(v=>v===Infinity||(Number.isFinite(v)&&v>=0))) throw new RangeError('Invalid surface dimensions');
 if (!['independent','inset','override'].includes(mode)) throw new RangeError('Unknown surface mode');
 const resolvedBounds=bounds??parent?.bounds??{min:0,max:Infinity};
 if(!Number.isFinite(resolvedBounds.min)||resolvedBounds.min<0||!(Number.isFinite(resolvedBounds.max)||resolvedBounds.max===Infinity)||resolvedBounds.max<resolvedBounds.min) throw new RangeError('Radius bounds require 0 ≤ min ≤ max');
 const options=mode==='inset'?{curvatureMode:'inset',parentRadius:parent?.radius,parentExponent:parent?.exponent,inset}:{};
 let result=resolveRadius(n,resolvedProfile,margin,width,height,supported,options);
 if(mode==='override') {
  if(!['sharp','pill'].includes(override)) throw new RangeError('Override requires sharp or pill');
  if(override==='pill'&&!Number.isFinite(result.cap)) throw new RangeError('Pill requires a finite physical cap');
  const radius=override==='sharp'?0:result.cap;
  result={...result,target:radius,radius,exponent:1,pill:radius>0&&radius===result.cap,multiplier:n?radius/n:0};
 }
 const exempt=mode==='override'||(resolvedProfile.baseline===0&&resolvedProfile.marginAllowance===0);
 const boundedTarget=exempt?result.target:Math.max(resolvedBounds.min,Math.min(resolvedBounds.max,result.target));
 const radius=mode!=='override'&&exempt?0:Math.min(result.cap,boundedTarget);
 const boundEffect=exempt?'exempt':boundedTarget>result.target?'minimum':boundedTarget<result.target?'maximum':'within bounds';
 const exponent=mode==='independent'?(supported?1.5-.5*(result.cap>0&&Number.isFinite(result.cap)?Math.min(1,radius/result.cap):0):1):result.exponent;
 return {...result,radius,exponent,boundedTarget,bounds:resolvedBounds,boundEffect,physicalLimited:radius<boundedTarget,pill:result.cap>0&&Number.isFinite(result.cap)&&radius===result.cap,curvatureMode:mode,profile:resolvedProfile,profileSource:profile?'explicit':parent?.profile?'inherited':'default',override:mode==='override'?override:null};
}

// Endpoint progression for a complete nested chain. Distances are cumulative,
// measured from the outermost surface's outer edge, including borders.
export function resolveRadiusProgression({bounds, distances, frames, profile=defaultCurvatureProfiles().sharp}) {
 if(!bounds||![bounds.min,bounds.max].every(Number.isFinite)||bounds.min<0||bounds.max<bounds.min) throw new RangeError('Progression requires finite 0 ≤ min ≤ max');
 if(!Array.isArray(distances)||distances.length<2||distances[0]!==0||distances.some((x,i)=>!Number.isFinite(x)||x<0||(i>0&&x<distances[i-1]))) throw new RangeError('Progression requires ordered cumulative distances starting at zero');
 if(!Array.isArray(frames)||frames.length!==distances.length||frames.some(f=>![f.width,f.height].every(v=>Number.isFinite(v)&&v>=0))) throw new RangeError('Progression requires measured frames');
 if(![profile.baseline,profile.marginAllowance].every(v=>Number.isFinite(v)&&v>=0)) throw new RangeError('Invalid profile');
 const totalInset=distances.at(-1),sharp=profile.baseline===0&&profile.marginAllowance===0;
 if(totalInset===0&&bounds.min!==bounds.max) throw new RangeError('Distinct radius endpoints require positive total inset');
 const slope=totalInset?(bounds.min-bounds.max)/totalInset:0;
 return distances.map((distance,i)=>{
  const t=totalInset?distance/totalInset:0;
  const target=sharp?0:bounds.max+(bounds.min-bounds.max)*t;
  const cap=Math.min(frames[i].width,frames[i].height)/2,radius=Math.min(cap,target);
  return {curvatureMode:'inset',profile,bounds,distance,totalInset,t,slope,target,boundedTarget:target,cap,radius,exponent:1,physicalLimited:radius<target,boundEffect:sharp?'exempt':i===0?'maximum endpoint':i===distances.length-1?'minimum endpoint':'interpolated',pill:cap>0&&radius===cap};
 });
}

// Adopted concentric chain: seed the inner radius; add actual insets outward.
// Radius is the REQUIRED geometry, never clamped. Consumers must inspect conflicts.
export function resolveConcentricRadii({bounds, distances, frames, profile=defaultCurvatureProfiles().sharp}) {
 if(!bounds||![bounds.min,bounds.max].every(v=>Number.isFinite(v)&&v>=0)) throw new RangeError('Concentric bounds must be finite nonnegative lengths');
 if(!Array.isArray(distances)||distances.length<1||distances[0]!==0||distances.some((x,i)=>!Number.isFinite(x)||x<0||(i>0&&x<distances[i-1]))) throw new RangeError('Expected ordered cumulative insets starting at zero');
 if(!Array.isArray(frames)||frames.length!==distances.length||frames.some(f=>![f.width,f.height].every(v=>Number.isFinite(v)&&v>=0))) throw new RangeError('Expected measured frames');
 if(![profile.baseline,profile.marginAllowance].every(v=>Number.isFinite(v)&&v>=0)) throw new RangeError('Invalid profile');
 const totalInset=distances.at(-1),sharp=profile.baseline===0&&profile.marginAllowance===0;
 const layers=distances.map((distance,index)=>{
  const radius=sharp?0:bounds.min+totalInset-distance;
  const cap=Math.min(frames[index].width,frames[index].height)/2;
  const ceilingExcess=Math.max(0,radius-bounds.max),physicalExcess=Math.max(0,radius-cap);
  return {radius,target:radius,distance,totalInset,cap,ceilingExcess,physicalExcess,exempt:sharp,valid:ceilingExcess===0&&physicalExcess===0};
 });
 return {layers,valid:layers.every(l=>l.valid),ceilingConflict:layers.some(l=>l.ceilingExcess>0),physicalConflict:layers.some(l=>l.physicalExcess>0),requiredOuterRadius:layers[0].radius,totalInset};
}

// Dial presets contain only dimensionless min/max multiples of n.
export const radiusBoundsPresets={
 sharp:{min:0,max:0},crisp:{min:.1875,max:2},
 balanced:{min:.375,max:4},round:{min:2,max:6}
};

// Current group API. Frames are outer border boxes in one coordinate space.
export function resolveRadiusGroup({innerRadius,ceiling,frames,mode='standalone',sharp=false,tolerance=.05}) {
 if(![innerRadius,ceiling,tolerance].every(v=>Number.isFinite(v)&&v>=0)||!['standalone','concentric','pill'].includes(mode)) throw new RangeError('Invalid radius group inputs');
 if(!Array.isArray(frames)||!frames.length||frames.some(f=>![f.x,f.y,f.width,f.height].every(Number.isFinite)||f.width<0||f.height<0)) throw new RangeError('Expected finite border boxes');
 const leaf=frames.at(-1),issues=[];
 const layers=frames.map((f,i)=>{
  const edges=[leaf.x-f.x,leaf.y-f.y,f.x+f.width-leaf.x-leaf.width,f.y+f.height-leaf.y-leaf.height];
  const offset=mode==='concentric'?edges[0]:0;
  if(mode==='concentric'&&!sharp&&(Math.min(...edges)<-tolerance||Math.max(...edges)-Math.min(...edges)>tolerance)) issues.push(`Layer ${i+1}: unequal or negative edge insets`);
  if(mode==='concentric'&&i>0){const p=frames[i-1];if(f.x<p.x-tolerance||f.y<p.y-tolerance||f.x+f.width>p.x+p.width+tolerance||f.y+f.height>p.y+p.height+tolerance)issues.push(`Layer ${i+1}: outside parent`);}
  const cap=Math.min(f.width,f.height)/2,radius=mode==='pill'?cap:sharp?0:innerRadius+offset;
  if(mode!=='pill'&&!sharp&&radius>ceiling+tolerance)issues.push(`Layer ${i+1}: ceiling exceeded by ${radius-ceiling}px`);
  if(radius>cap+tolerance)issues.push(`Layer ${i+1}: physical cap exceeded by ${radius-cap}px`);
  return {radius,offset,cap,width:f.width,height:f.height};
 });
 const maxFeasibleSeed=mode==='pill'?null:Math.min(...layers.map(l=>Math.min(ceiling,l.cap)-l.offset));
 return {mode,layers,valid:issues.length===0,issues,maxFeasibleSeed,innerRadius,ceiling,sharp};
}

export const radiusEndpointPresets={sharp:{inner:0,outer:0},crisp:{inner:.1875,outer:.5},balanced:{inner:.375,outer:1},round:{inner:1,outer:2}};
// Independent endpoints; radius order is unrestricted. Never clamp computed radii.
export function resolveEndpointRadiusGroup({innerRadius,outerRadius,frames,mode='interpolated',tolerance=.05}) {
 if(![innerRadius,outerRadius,tolerance].every(v=>Number.isFinite(v)&&v>=0)||!['standalone','interpolated','pill'].includes(mode)) throw new RangeError('Invalid endpoint group inputs');
 if(!Array.isArray(frames)||!frames.length||frames.some(f=>![f.x,f.y,f.width,f.height].every(Number.isFinite)||f.width<0||f.height<0)) throw new RangeError('Expected measured border boxes');
 const issues=[],leaf=frames.at(-1),totalInset=leaf.x-frames[0].x;
 const interpolated=mode==='interpolated',distinct=innerRadius!==outerRadius;
 const ambiguous=interpolated&&totalInset<=tolerance;
 if(ambiguous&&distinct)issues.push('Distinct endpoints require total inset greater than measurement tolerance');
 let previousOffset=Infinity;
 const layers=frames.map((f,i)=>{
  const edges=[leaf.x-f.x,leaf.y-f.y,f.x+f.width-leaf.x-leaf.width,f.y+f.height-leaf.y-leaf.height];
  if(interpolated&&(Math.min(...edges)<0||Math.max(...edges)-Math.min(...edges)>tolerance))issues.push(`Layer ${i+1}: unequal or negative edge insets`);
  if(interpolated&&i>0){const p=frames[i-1];if(f.x<p.x||f.y<p.y||f.x+f.width>p.x+p.width||f.y+f.height>p.y+p.height)issues.push(`Layer ${i+1}: outside parent`);}
  const offset=interpolated?edges[0]:0;
  const rawT=interpolated&&!ambiguous?offset/totalInset:null;
  const ordered=!interpolated||(offset>=0&&offset<=totalInset&&offset<=previousOffset);
  if(!ordered)issues.push(`Layer ${i+1}: interpolation position outside ordered [0,1] domain`);
  previousOffset=offset;
  const t=ordered?rawT:null,cap=Math.min(f.width,f.height)/2;
  // Preserve known endpoints, but never invent a middle radius for ambiguous geometry.
  const radius=mode==='pill'?cap:!interpolated?innerRadius:i===0?outerRadius:i===frames.length-1?innerRadius:!distinct?innerRadius:t===null?null:innerRadius+(outerRadius-innerRadius)*t;
  const physicalExcess=radius===null?null:Math.max(0,radius-cap);
  const withinMeasurementTolerance=physicalExcess>0&&physicalExcess<=tolerance;
  if(physicalExcess>0)issues.push(`Layer ${i+1}: physical cap exceeded by ${physicalExcess}px${withinMeasurementTolerance?' (within measurement tolerance; still not an exact fit)':''}`);
  return {radius,offset,t,rawT,cap,physicalExcess,withinMeasurementTolerance,width:f.width,height:f.height};
 });
 return {mode,layers,totalInset,innerRadius,outerRadius,valid:issues.length===0,issues};
}

// Percentage of half-height. Optional reference heights keep listboxes independent
// of row count. Actual border boxes still determine feasibility, without clamping.
export const radiusPercentagePresets={sharp:0,crisp:25,balanced:50,round:100};
export function resolvePercentageRadiusGroup({amount=0,retained=0,family='control',rootMargin=0,parentRadius,frames,referenceHeights,mode='interpolated'}) {
 if(![amount,retained].every(v=>Number.isFinite(v)&&v>=0&&v<=100))throw new RangeError('Radius percentages must be 0…100');
 if(!['control','container'].includes(family)||!Number.isFinite(rootMargin)||rootMargin<0)throw new RangeError('Invalid radius family or margin');
 if(parentRadius!==undefined&&(!Number.isFinite(parentRadius)||parentRadius<0))throw new RangeError('Invalid parent radius');
 if(referenceHeights && (referenceHeights.length!==frames.length||referenceHeights.some(h=>!Number.isFinite(h)||h<0)))throw new RangeError('Invalid reference heights');
 const group=resolveEndpointRadiusGroup({innerRadius:0,outerRadius:0,frames,mode});
 const layers=[];
 group.layers.forEach((layer,i)=>{
  const referenceHeight=referenceHeights?.[i]??layer.height;
  const inset=mode==='interpolated'?frames[i].x-frames[0].x:0;
  const candidate=amount/100*(family==='container'?Math.max(0,rootMargin-inset):referenceHeight/2);
  const immediateParent=i>0&&mode==='interpolated'?layers[i-1].radius:parentRadius;
  const floor=immediateParent===undefined?0:retained/100*immediateParent;
  // Sharp is explicit even when an external parent radius is supplied; Pill is exempt.
  const radius=mode==='pill'?layer.cap:amount===0?0:Math.max(candidate,floor);
  const physicalExcess=Math.max(0,radius-layer.cap);
  layers.push({...layer,radius,candidate,floor,parentRadius:immediateParent??null,referenceHeight,inset,physicalExcess});
 });
 const issues=[...group.issues,...layers.flatMap((l,i)=>l.physicalExcess>0?[`Layer ${i+1}: required R ${l.radius}px exceeds physical cap ${l.cap}px`]:[])];
 return {...group,layers,issues,valid:issues.length===0,amount,retained,family,rootMargin};
}
