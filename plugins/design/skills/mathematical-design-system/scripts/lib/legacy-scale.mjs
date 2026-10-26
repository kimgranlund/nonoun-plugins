// HISTORICAL: pre-Differential Forms model. Current resolvers/tests are in assets/differential-forms/.
// Historical compatibility API. New consumers use scale.mjs.
// Reference implementation. Edit CFG to change the system; resolve() and check() follow.
const CFG = {
  ladder: [4, 24],                                   // allowed n; Regular h = 4n
  tiers: { widget: [6, 1, 1, 0], product: [8, 2, 2, 1], content: [11, 3, 2, 1], brand: [15, 4, 2, 1] }, // n0 a k g
  linear: { body: [12, 1], control: [11, 1], fieldLabel: [10, 1], groupKicker: [10, 1], smallControl: [9, 1] },             // px at n=5, px per step
  Q: [1.25, 1 / 32],                                 // heading ratio at n=5, per step
  kicker: 9 / 8, titleBump: { sm: 0, md: 1, lg: 2 }, floor: 9,
  levels: { tile: [2, 2, 2], card: [3, 3, 3], section: [4, 4, 4] },                                 // margin/gutter × d; legacy radius × n
};
const STEPS = ["sm", "md", "lg"], IX = { sm: -1, md: 0, lg: 1 };
const ROLES = ["display", "heading", "subhead", "sectionKicker", "title", "body", "control", "fieldLabel", "groupKicker", "smallControl"];
const rung = (t, sc, sz) => { const [n0, a, k, g] = CFG.tiers[t], s = IX[sc], z = IX[sz]; return n0 + a * s + k * z + g * s * z; };
export const CONTAINER_FACTORS = {widget:0.5,control:1,group:1.25,tile:2,card:3,section:4};
export const DENSITIES={tight:2,compact:3,regular:4,spacious:5,loose:6};
// Margin is border-inclusive. Consumers count slot spacing or explicit gap once.
export function composeControl(margin) {
  if (!Number.isFinite(margin) || margin < 0) throw new Error('Control margin must be finite and nonnegative');
  return {margin, gutter:margin/2};
}
function at(n, size = "md", density="regular") {
  if(!(density in DENSITIES))throw new Error(`Unknown density: ${density}`);
  const d=n*DENSITIES[density]/4;
  const c = n / 4, lin = (r) => CFG.linear[r][0] + CFG.linear[r][1] * (n - 5);
  const body = lin("body"), Q = CFG.Q[0] + CFG.Q[1] * (n - 5);
  const box = ([m, g, r]) => ({ margin: m * d, gutter: g * d, radius: r * n });
  const containers=Object.fromEntries(Object.entries(CONTAINER_FACTORS).map(([level,factor])=>[level,{margin:factor*d,gutter:factor*d}]));
  return { n, d, density, surface:resolveControlSurface(n,density), containers, composition:{control:composeControl(d),compactControl:composeControl(d/2)}, h: 2*n+2*d, compactHeight:2*n+d, margin: d, gutter: d, icon: 2 * n, radius: n, c, glyph: 2 * n - 2 * c,
    type: { display: body * Q ** 3, heading: body * Q ** 2, subhead: body * Q, sectionKicker: body * CFG.kicker,
      title: body + CFG.titleBump[size], body, control: lin("control"), fieldLabel: lin("fieldLabel"), groupKicker: lin("groupKicker"), smallControl: lin("smallControl") },
    table:{cellMargin:1.25*d,clearance:d/4,rowHeight:2*n+2.5*d}, group: { margin: 1.25*d, gutter: 1.25*d, radius: n + c }, ...Object.fromEntries(Object.entries(CFG.levels).map(([l, v]) => [l, box(v)])) };
}
export function resolve(tier = "product", scale = "md", size = "md", density="regular") {
  const n = rung(tier, scale, size);
  if (!Number.isFinite(n) || n < CFG.ladder[0] || n > CFG.ladder[1]) throw new Error(`${tier}/${scale}/${size}: n=${n} is off the ladder`);
  const geometry=at(n, size, density);
  return { tier, scale, size, ...geometry, widget:geometry.tile, layout:geometry.section }; // legacy aliases preserved; the new small widget is containers.widget
}
// resolve() returns base geometry. Apply the browser corner treatment once,
// then subtract physical offsets; offsets and margins are never scaled.
export function resolveRadii(n, supported = true, density = "regular") {
  if (!(density in DENSITIES)) throw new Error(`Unknown density: ${density}`);
  const d=n*DENSITIES[density]/4;
  const k = supported ? 1.5 : 1, c = n / 4, control = k * n;
  const group = k * (n + c);
  return {k, control, mark:control / 2, listbox:control,
    listboxOption:Math.max(0, control - d / 2), group,
    groupInner:Math.max(0, group - d / 4), tile:k * 2 * n, widget:k * 2 * n,
    card:k * 3 * n, section:k * 4 * n, layout:k * 4 * n};
}
// Contract: every check must pass after any change to CFG. Returns the failures.
export function check() {
  const bad = [], all = Object.keys(CFG.tiers).flatMap((t) => STEPS.flatMap((s) => STEPS.map((z) => [t, s, z])));
  for (const [t, s, z] of all) { const n = rung(t, s, z); if (!Number.isFinite(n) || n < CFG.ladder[0] || n > CFG.ladder[1]) bad.push(`M1 ${t}/${s}/${z} n=${n} off the ladder`); }
  if (bad.length) return bad;
  for (const t in CFG.tiers) for (const x of STEPS) for (const i of [0, 1]) {
    if (rung(t, x, STEPS[i]) >= rung(t, x, STEPS[i + 1])) bad.push(`M2 ${t}/${x}: size ${STEPS[i]}→${STEPS[i + 1]} doesn't grow`);
    if (rung(t, STEPS[i], x) >= rung(t, STEPS[i + 1], x)) bad.push(`M2 ${t}: scale ${STEPS[i]}→${STEPS[i + 1]} doesn't grow at size ${x}`);
  }
  const order = ROLES.filter((r) => r !== "title");
  for (let n = CFG.ladder[0]; n <= CFG.ladder[1]; n++) {
    const v = at(n), w = n > CFG.ladder[0] ? at(n - 1) : null;
    order.slice(1).forEach((r, i) => { if (v.type[order[i]] < v.type[r]) bad.push(`M3 h${4 * n}: ${order[i]} < ${r}`); });
    for (const z of STEPS) { const u = at(n, z).type; if (!(u.title === u.body + CFG.titleBump[z])) bad.push(`M4 h${4 * n}/${z}: title = body + size bump fails`); }
    if (ROLES.some(r => v.type[r] < CFG.floor - (r === "smallControl" ? 1 : 0))) bad.push(`M5 h${4 * n}: type below role floor`);
    const chain = [v.margin, v.group.margin, v.tile.margin, v.card.margin, v.section.margin];
    if (!chain.every((m, i) => !i || chain[i - 1] < m)) bad.push(`M6 h${4 * n}: margins don't nest ${chain.join(" < ")}`);
    for (const l of ["group", "tile", "card", "section"]) {
      if (v[l].gutter !== v[l].margin) bad.push(`M6 h${4 * n}: ${l} gutter ≠ margin`);
      if (v[l].margin - v.margin < v.c) bad.push(`M8 h${4 * n}: a control doesn't fit in ${l}`);
      if (![v[l].margin, v[l].gutter].every(Number.isFinite)) bad.push(`M7 h${4 * n}: ${l} not finite`);
    }
    if (ROLES.some((r) => !Number.isFinite(v.type[r]))) bad.push(`M7 h${4 * n}: type is not finite`);
    if (!(v.glyph > 0)) bad.push(`M9 h${4 * n}: glyph ${v.glyph}`);
    if (w) ROLES.forEach((r) => { if (v.type[r] < w.type[r]) bad.push(`M10 h${4 * (n - 1)}→h${4 * n}: ${r} shrinks`); });
  }
  return bad;
}
export { CFG };

// Adopted surface geometry: density changes clearance, never inner/icon/glyph size.
export function resolveControlSurface(n,density='regular',gutterPercent=25) {
 if(!Number.isFinite(n)||n<=0||!(density in DENSITIES))throw new RangeError('Invalid surface context');
 const innerHeight=3*n, margin=(DENSITIES[density]-2)*n/4;
 const slotPadding=composeContainer(n,gutterPercent).gutter,gutter=slotPadding,slotGap=margin/2;
 return {innerHeight,slotHeight:innerHeight,slotPadding,iconSlotWidth:2*n+2*slotPadding,glyphSlotWidth:1.5*n+2*slotPadding,slotGap,contentSeparation:2*slotPadding+slotGap,margin,gutter,height:innerHeight+2*margin,icon:2*n,glyph:1.5*n};
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
