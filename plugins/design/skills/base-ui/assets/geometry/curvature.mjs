// Current radius policy: Standalone / Nested / Pill. No historical endpoint models.
function validateRadiusFrames(frames,mode) {
 if(!['standalone','nested','pill'].includes(mode))throw new RangeError('Invalid radius mode');
 if(!Array.isArray(frames)||!frames.length||frames.some(f=>![f.x,f.y,f.width,f.height].every(Number.isFinite)||f.width<0||f.height<0))throw new RangeError('Expected measured border boxes');
 const issues=[],leaf=frames.at(-1),totalInset=leaf.x-frames[0].x,tolerance=.05;
 const layers=frames.map((f,i)=>{
  const edges=[leaf.x-f.x,leaf.y-f.y,f.x+f.width-leaf.x-leaf.width,f.y+f.height-leaf.y-leaf.height];
  if(mode==='nested'){
   if(Math.min(...edges)<-tolerance||Math.max(...edges)-Math.min(...edges)>tolerance)issues.push(`Layer ${i+1}: unequal or negative edge insets`);
   if(i){const p=frames[i-1];if(f.x<p.x-tolerance||f.y<p.y-tolerance||f.x+f.width>p.x+p.width+tolerance||f.y+f.height>p.y+p.height+tolerance)issues.push(`Layer ${i+1}: outside parent`);}
  }
  return {width:f.width,height:f.height,cap:Math.min(f.width,f.height)/2,offset:mode==='nested'?edges[0]:0};
 });
 return {mode,layers,totalInset,issues,valid:!issues.length};
}
export const radiusPercentagePresets={sharp:0,crisp:25,balanced:50,round:100};
export function resolvePercentageRadiusGroup({amount=0,retained=0,family='control',rootMargin=0,parentRadius,frames,referenceHeights,mode='nested'}) {
 if(![amount,retained].every(v=>Number.isFinite(v)&&v>=0&&v<=100))throw new RangeError('Radius percentages must be 0…100');
 if(!['control','container'].includes(family)||!Number.isFinite(rootMargin)||rootMargin<0)throw new RangeError('Invalid radius family or margin');
 if(parentRadius!==undefined&&(!Number.isFinite(parentRadius)||parentRadius<0))throw new RangeError('Invalid parent radius');
 if(referenceHeights && (referenceHeights.length!==frames.length||referenceHeights.some(h=>!Number.isFinite(h)||h<0)))throw new RangeError('Invalid reference heights');
 const group=validateRadiusFrames(frames,mode);
 const layers=[];
 group.layers.forEach((layer,i)=>{
  const referenceHeight=referenceHeights?.[i]??layer.height;
  const inset=mode==='nested'?frames[i].x-frames[0].x:0;
  const candidate=amount/100*(family==='container'?Math.max(0,rootMargin-inset):referenceHeight/2);
  const immediateParent=i>0&&mode==='nested'?layers[i-1].radius:parentRadius;
  const floor=immediateParent===undefined?0:retained/100*immediateParent;
  // Sharp is explicit even when an external parent radius is supplied; Pill is exempt.
  const radius=mode==='pill'?layer.cap:amount===0?0:Math.max(candidate,floor);
  const physicalExcess=Math.max(0,radius-layer.cap);
  layers.push({...layer,radius,candidate,floor,parentRadius:immediateParent??null,referenceHeight,inset,physicalExcess});
 });
 const issues=[...group.issues,...layers.flatMap((l,i)=>l.physicalExcess>0.001?[`Layer ${i+1}: required R ${l.radius}px exceeds physical cap ${l.cap}px`]:[])];
 return {...group,layers,issues,valid:issues.length===0,amount,retained,family,rootMargin};
}

/** Opt-in media shape uses the owning row/button's required radius, not a Container ancestor. */
export function resolveMediaRadius({shape='intrinsic',frame,amount=0,retained=0,parentRadius}) {
 if(!['intrinsic','circle','control'].includes(shape))throw new RangeError('Invalid media shape');
 if(shape==='control'&&parentRadius===undefined)throw new RangeError('Control media requires its immediate parent radius');
 const group=resolvePercentageRadiusGroup({frames:[frame],family:'control',mode:shape==='circle'?'pill':'standalone',amount:shape==='control'?amount:0,retained:shape==='control'?retained:0,parentRadius:shape==='control'?parentRadius:undefined});
 return {...group,shape,clips:shape!=='intrinsic'};
}
