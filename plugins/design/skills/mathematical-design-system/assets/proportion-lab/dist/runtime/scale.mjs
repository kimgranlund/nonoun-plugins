// Current coefficient authority. Historical outputs live in legacy-scale.mjs.
export const CFG = {
  ladder: [4, 24],                                   // allowed n; Regular h = 4n
  // n0 a k g. Product (2026-10-21) keeps a constant size step k = 2 at every scale (even shoulders: H 20/28/36, 24/32/40, 28/36/44
  // at Regular); content and brand keep scale-dependent steps k + g·s = 1, 2, 3. Previous product row [8, 2, 2, 1] lives in legacy-scale.mjs.
  tiers: { widget: [6, 1, 1, 0], product: [8, 1, 2, 0], content: [11, 3, 2, 1], brand: [15, 4, 2, 1] },
  linear: { body: [12, 1], control: [11, 1], fieldLabel: [10, 1], groupKicker: [10, 1], smallControl: [9, 1] },             // px at n=5, px per step
  Q: [1.25, 1 / 32],                                 // heading ratio at n=5, per step
  kicker: 9 / 8, titleBump: { sm: 0, md: 1, lg: 2 }, floor: 9,
};
const STEPS = ["sm", "md", "lg"], IX = { sm: -1, md: 0, lg: 1 };
const rung = (t, sc, sz) => { const [n0, a, k, g] = CFG.tiers[t], s = IX[sc], z = IX[sz]; return n0 + a * s + k * z + g * s * z; };
export const CONTAINER_FACTORS = {tile:2,card:3,section:4};
export const DENSITIES={tight:2,compact:3,regular:4,spacious:5,loose:6};

/** Current geometry only. Percentages are 0…200; lengths remain unrounded. */
export function resolveGeometry(tier='product',scale='md',size='md',density='regular') {
 if(!(tier in CFG.tiers)||!(scale in IX)||!(size in IX)||!(density in DENSITIES))throw new RangeError('Invalid geometry context');
 const n=rung(tier,scale,size);
 if(n<4||n>24)throw new RangeError('Unit outside supported ladder');
 const d=n*DENSITIES[density]/4,c=n/4;
 const lin=r=>CFG.linear[r][0]+CFG.linear[r][1]*(n-5),body=lin('body'),Q=CFG.Q[0]+CFG.Q[1]*(n-5);
 const surface=resolveControlSurface(n,density);
 const containers=Object.fromEntries(Object.entries(CONTAINER_FACTORS).map(([key,factor])=>[key,{margin:factor*d}]));
 return {tier,scale,size,density,n,d,c,surface,containers,groupMarginReference:1.25*d,
  type:{display:body*Q**3,heading:body*Q**2,subhead:body*Q,sectionKicker:body*CFG.kicker,title:body+CFG.titleBump[size],body,control:lin('control'),fieldLabel:lin('fieldLabel'),groupKicker:lin('groupKicker'),smallControl:lin('smallControl')},
  table:resolveDataRowGeometry(n,density)};
}
// Adopted surface geometry: density changes clearance, never inner/icon/glyph size.
export function resolveControlSurface(n,density='regular',gutterPercent=25) {
 if(!Number.isFinite(n)||n<=0||!(density in DENSITIES))throw new RangeError('Invalid surface context');
 const innerHeight=3*n, margin=(DENSITIES[density]-2)*n/4;
 // slotGap E remains the collection row/column budget. Internal Control wrappers abut with no extra separation.
 const slotPadding=composeContainer(n,gutterPercent).gutter,gutter=slotPadding,slotGap=margin/2,wrapperGap=0;
 const labelPadding=n/2;
 return {labelPadding,mediaSize:innerHeight,mediaSlotWidth:innerHeight,mediaPadding:0,mediaInset:0,mediaContentSeparation:labelPadding,innerHeight,slotHeight:innerHeight,slotPadding,iconSlotWidth:innerHeight,iconInset:n/2,iconContentSeparation:n/2+labelPadding,glyphSlotWidth:innerHeight,glyphInset:(3*n-(n+6))/2,glyphContentSeparation:(3*n-(n+6))/2+labelPadding,slotGap,wrapperGap,contentSeparation:2*slotPadding+slotGap,margin,gutter,height:innerHeight+2*margin,icon:2*n,glyph:n+6};
}

export function composeContainer(margin,gutterPercent=75) {
 if(!Number.isFinite(margin)||margin<0||!Number.isFinite(gutterPercent)||gutterPercent<0||gutterPercent>200)throw new RangeError('Container spacing requires nonnegative margin and 0…200% gutter');
 return {margin,gutter:margin*gutterPercent/100};
}

// Every role derives from M directly; Groups borrow M without adding edge padding.
export const SPACING_ROLES=Object.freeze({page:100,container:75,group:50,control:25});
export function resolveSpacingRoles(marginReference,{pagePercent=100,containerPercent=75,groupPercent=50,controlPercent=25,controlMargin=0,controlUnit=0,controlGutter=composeContainer(controlUnit,controlPercent).gutter}={}) {
 if(![marginReference,controlMargin,controlGutter].every(v=>Number.isFinite(v)&&v>=0))throw new RangeError('Invalid spacing reference');
 return {page:composeContainer(marginReference,pagePercent),container:composeContainer(marginReference,containerPercent),group:{margin:0,marginReference,gutter:composeContainer(marginReference,groupPercent).gutter},control:{margin:controlMargin,marginReference:controlUnit,gutter:controlGutter,slotPadding:controlGutter,slotGap:controlMargin/2}};
}

/** Label inline padding: pass labelPadding L=n/2 as wrapperInset.
 * Every occupied label uses L on both sides. No compensation or slot gap. */
export function resolveButtonPadding({margin,wrapperInset,height,hasLeading=false,hasTrailing=false,slotGap=margin/2}) {
 if(![margin,wrapperInset,height,slotGap].every(v=>Number.isFinite(v)&&v>=0)||typeof hasLeading!=='boolean'||typeof hasTrailing!=='boolean')throw new RangeError('Invalid button padding inputs');
 const edgePadding=0;
 const compensation=0; // Retired compatibility alias.
 const labelStart=wrapperInset,labelEnd=wrapperInset;
 return {inlinePadding:margin,edgePadding,compensation,labelGap:0,wrapperGap:0,labelStart,labelEnd,exposedLabelInset:margin+wrapperInset+compensation};
}

/** Shared minimum row geometry; multiline content may grow beyond rowHeight. */
export function resolveDataRowGeometry(n,density='regular',gutterPercent=25){
 const c=resolveControlSurface(n,density,gutterPercent);
 return {cellMargin:c.margin+c.slotPadding,clearance:c.margin,rowHeight:c.height,slotHeight:c.slotHeight,columnGap:c.slotGap};
}
