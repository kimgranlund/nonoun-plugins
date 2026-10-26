import {resolveGeometry,resolveButtonPadding,resolveControlSurface,resolveSpacingRoles,DENSITIES} from './scale.mjs?v=source-a72d65add853';
const f=n=>Number(n.toFixed(3));
const px=n=>`${f(n)} px`;
const row=(label,formula,value)=>`<tr><th scope="row">${label}</th><td><code>${formula}</code></td><td>${value}</td></tr>`;
function panel(root,id,rows,context){
 const section=root.querySelector('#'+id);let el=section.querySelector(':scope > .formula-summary');
 if(!el){el=document.createElement('details');el.className='formula-summary';el.open=false;const anchor=section.querySelector(':scope > .study-title')??section.querySelector(':scope > h3');anchor.after(el);}
 el.innerHTML=`<summary>Current formulas <span>${context}</span></summary><div class="formula-table-scroll"><table><thead><tr><th>Quantity</th><th>Formula</th><th>Resolved</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}
export function paintFormulaSummaries(root,s){
 const v=resolveGeometry(s.tier,s.scale,s.size,s.density),c=resolveControlSurface(v.n,s.density,s.controlGutter),q=DENSITIES[s.density];
 const context=`${s.tier} · ${s.scale}/${s.size} · ${s.density} · n=${f(v.n)}px`;
 const control=row('Label inline padding','L = n/2',px(c.labelPadding))+row('Media shape','Opt-in: max(A × media H/2, F × parent R); Sharp = 0',`Avatar ${s.avatarInherit?'Control':'circle'} / logo ${s.logoInherit?'Control':'intrinsic'}`)+row('Media','3n × 3n; padding = 0; media–label = L; no additional slot gap',`${px(c.mediaSize)} square / ${px(c.mediaContentSeparation)} separation`)+row('Inner / frame','S = 3n; H = S + 2m',`${px(c.innerHeight)} / ${px(c.height)}`)+row('Outer margin','m = (q − 2)n/4',`${q} → ${px(c.margin)}`)+row('Artwork budget / slot gap','W = n × Controls%/100; internal slot gap = 0',`${px(c.slotPadding)} per side / 0px`)+row('Label–glyph separation','L + (3n − (n + 6))/2',px(c.glyphContentSeparation))+row('Icon / glyph artwork','I = 2n; J = (n + 6)',`${px(c.icon)} / ${px(c.glyph)}`)+row('Icon / glyph wrapper width','3n × 3n (both square)',`${px(c.iconSlotWidth)} / ${px(c.glyphSlotWidth)}`);
 const bp=resolveButtonPadding({margin:c.margin,wrapperInset:c.labelPadding,height:c.height});
 panel(root,'buttons',control+row('Icon–label separation','n/2 + L; wrappers abut with no added separation',px(c.iconContentSeparation))+row('Label padding','L = n/2 on both edges; no compensation',`outer ${px(bp.inlinePadding)}; label ${px(c.labelPadding)} / side; exposed label inset ${px(bp.exposedLabelInset)}`)+row('Inner chip / badge minimum','3n / 2n',`${px(c.innerHeight)} / ${px(c.icon)}`),context);
 panel(root,'menus',control+row('Menu row','H = S + 2m; label padding L = n/2; no extra label edge padding',`${px(c.height)} row / ${px(c.innerHeight)} slot / ${px(c.margin)} clearance`)+row('Three-item menu frame','2m + 3H + 2E',px(2*c.margin+3*c.height+2*c.slotGap))+row('Three-row listbox frame','2m + 3S + 2E',px(2*c.margin+3*c.innerHeight+2*c.slotGap))+row('Radius references','menu row H/2; listbox row S/2',`${px(c.height/2)} / ${px(c.innerHeight/2)} before radius amount`),context);
 panel(root,'data',row('Minimum row height','H = 3n + 2m; grows for multiline content',px(c.height))+row('Centered inner slot','S = 3n (minimum)',px(c.slotHeight))+row('Cell inline padding','P = m + W',px(c.margin+c.slotPadding))+row('Block clearance','m = (q − 2)n/4',px(c.margin))+row('Column gap','E = m/2; native tables reserve E/2 per facing edge',px(c.slotGap))+row('Divider','one --ui-data-divider per row; no layout thickness','1px paint'),context);
 const roles=resolveSpacingRoles(v.containers.card.margin,{pagePercent:s.pageGutter,containerPercent:s.containerGutter,groupPercent:s.groupGutter,controlUnit:v.n,controlMargin:c.margin,controlPercent:s.controlGutter});
 const structural=['tile','card','section'].map((key,i)=>row(key,`M = ${i+2}d; G = M × Containers%/100`,`${px(v.containers[key].margin)} / ${px(v.containers[key].margin*s.containerGutter/100)}`)).join('');
 const tiers=['widget','product'].map(t=>{const g=resolveGeometry(t,s.scale,s.size,s.density),a=resolveControlSurface(g.n,s.density,s.controlGutter);return row(t==='widget'?'Widget':'Button/control','S = 3n; H = S + 2m; L = n/2; slot gap = 0',`n ${px(g.n)} · S ${px(a.innerHeight)} · H ${px(a.height)} · L ${px(a.labelPadding)} · slot gap 0px`);}).join('');
 panel(root,'containers',tiers+structural+row('Group specimen','reference M = 1.25d; G = M × Groups%/100; edge = 0',`${px(v.groupMarginReference)} reference / ${px(v.groupMarginReference*s.groupGutter/100)} gap`),context);
 panel(root,'nested-composition',row('Card margin / gap','M = 3d; G = M × Containers%/100',`${px(roles.container.margin)} / ${px(roles.container.gutter)}`)+row('Groups inside card','G = card M × Groups%/100; edge = 0',px(roles.group.gutter))+row('Card radius','R = card M × Container amount/100',px(roles.container.margin*s.containerAmount/100))+control,context);
 let densities='',spacing='',radii='';
 for(const density of Object.keys(DENSITIES)){
  const g=resolveGeometry(s.tier,s.scale,s.size,density),a=resolveControlSurface(g.n,density,s.controlGutter),M=g.containers.card.margin;
  const R=s.controlAmount/100*a.height/2,P=resolveButtonPadding({margin:a.margin,wrapperInset:a.labelPadding,height:a.height});
  densities+=row(density,'H = 3n + 2m; R = A × H/2; L = n/2 on both label edges; compensation = 0',`H ${px(a.height)} · R ${px(R)} · outer ${px(P.inlinePadding)} · inset ${px(P.exposedLabelInset)} · L ${px(a.labelPadding)} · slot gap 0px`);
  spacing+=row(density,'Page / Container / Group = M × role%; Control W = n × %; L = n/2; slot gap = 0',`M ${px(M)} → ${px(M*s.pageGutter/100)} / ${px(M*s.containerGutter/100)} / ${px(M*s.groupGutter/100)}; W ${px(a.slotPadding)}, L ${px(a.labelPadding)}, slot gap 0px`);
  const base=s.radiusFamily==='container'?M:a.height/2,A=s[s.radiusFamily+'Amount'];
  radii+=row(density,s.radiusFamily==='container'?'root R = A × card M':'root R = A × H/2',`${A}% × ${px(base)} = ${px(A*base/100)}`);
 }
 panel(root,'listbox-densities',control,`${s.tier} · ${s.scale}/${s.size} · active density; each column resolves its own M and E below`);
 panel(root,'button-densities',densities,`${s.tier} · ${s.scale}/${s.size} · all densities`);
 panel(root,'spacing-rules',spacing,`Page / Containers / Groups / Controls · ${s.pageGutter}% / ${s.containerGutter}% / ${s.groupGutter}% / ${s.controlGutter}%`);
 panel(root,'radius-study',radii+row('Nested candidate',s.radiusFamily==='container'?'C = A × max(0, M − cumulative inset)':'C = A × reference height / 2','Actual layer values appear below')+row('Parent floor','Rchild = max(C, F × required parent R)',`F = ${s[s.radiusFamily+'Retained']}%; Sharp A=0 forces R=0`)+row('Physical validation','R ≤ min(measured width, height)/2','Measured caps and conflicts are reported for every layer below; Pill uses the cap directly'),`${s.radiusFamily} · A=${s[s.radiusFamily+'Amount']}% · all densities`);
}
