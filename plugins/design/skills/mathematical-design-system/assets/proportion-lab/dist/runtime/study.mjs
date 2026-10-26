import {paintFormulaSummaries} from './formula-summaries.mjs?v=source-a72d65add853';
import {paintSpacingGuides} from './spacing-guides.mjs?v=source-a72d65add853';
import {createInspectorState} from './inspector-state.mjs?v=source-a72d65add853';
import {createJig} from './jig.mjs?v=source-a72d65add853';
import {resolveGeometry as resolve, resolveButtonPadding, resolveDataRowGeometry, DENSITIES, resolveControlSurface, composeContainer, resolveSpacingRoles} from './scale.mjs?v=source-a72d65add853';
import {resolveMediaRadius, resolvePercentageRadiusGroup, radiusPercentagePresets} from './curvature.mjs?v=source-a72d65add853';
const root=document.getElementById('app'),lab=document.getElementById('lab');
// Comparison navigation stays outside the measured specimens.
root.querySelectorAll('[data-scroll-for]').forEach(nav=>{
 const grid=root.querySelector('#'+nav.dataset.scrollFor);grid.tabIndex=0;grid.setAttribute('role','region');grid.setAttribute('aria-label','Density comparison; scroll horizontally to compare');
 const update=()=>{const max=grid.scrollWidth-grid.clientWidth;nav.querySelector('[data-direction="-1"]').disabled=grid.scrollLeft<=1;nav.querySelector('[data-direction="1"]').disabled=grid.scrollLeft>=max-1;};
 nav.addEventListener('click',e=>{const button=e.target.closest('[data-direction]');if(button)grid.scrollBy({left:Number(button.dataset.direction)*grid.clientWidth*.75,behavior:'smooth'});});grid.addEventListener('scroll',update,{passive:true});new ResizeObserver(update).observe(grid);new MutationObserver(update).observe(grid,{childList:true});
});
// Normalize bare-text specimen buttons to the same explicit label slot anatomy.
root.querySelectorAll('.specimen .button__root').forEach(button=>{for(const node of [...button.childNodes])if(node.nodeType===Node.TEXT_NODE&&node.textContent.trim()){const slot=document.createElement('span');slot.dataset.slot='label';node.replaceWith(slot);slot.append(node);}});
// Data cells own a growing inner slot, separate from row clearance.
root.querySelectorAll('.specimen .table__root th,.specimen .table__root td,.specimen .data-list__root dt,.specimen .data-list__root dd').forEach(cell=>{if(cell.querySelector(':scope > .data-cell-slot'))return;const slot=document.createElement('span');slot.className='data-cell-slot';slot.append(...cell.childNodes);cell.append(slot);});
// Empty optional slots do not reserve wrapper padding or create flex gaps.
root.querySelectorAll('.specimen .button__root > [data-slot]').forEach(slot=>{
 if(!slot.textContent.trim()&&!slot.querySelector('i,svg,img')&&!slot.hasAttribute('data-reserve-space'))slot.remove();
});
const jig=createJig(root);
const defaults={avatarInherit:false,logoInherit:false,slotBoundaries:false,comparisonSelection:'none',tier:'product',scale:'md',size:'md',density:'regular',controlGutter:25,pageGutter:100,groupGutter:50,containerGutter:75,containerAmount:0,controlAmount:0,containerRetained:0,controlRetained:0,radiusFamily:'container',guides:true,marginGuides:true,gutterGuides:true,wrapperGuides:true,centeringGuides:true,voice:'Helvetica',nestedVoice:'Helvetica',nestedMessage:'Select a voice, then apply it.',message:'Activate a button to test its behavior.'};
const inspector=createInspectorState(root,defaults);
const fmt=x=>x===null?'unresolved':Number(x.toFixed(3)).toString();
const containerLevels=['widget','control','group','tile','card','section'];
const containerLabel=k=>k==='control'?'Button / control':k[0].toUpperCase()+k.slice(1);
const voices={Helvetica:'Arial, Helvetica, sans-serif',Georgia:'Georgia, serif',Monospace:'monospace'};
const amount=(s,family=s.radiusFamily)=>Number(s[family+'Amount']);
const retained=(s,family=s.radiusFamily)=>Number(s[family+'Retained']);
const presetName=(s,family=s.radiusFamily)=>Object.entries(radiusPercentagePresets).find(([,p])=>p===amount(s,family)&&retained(s,family)===0)?.[0]??'Custom';
let radiusState=defaults, radiusFrame;
function scheduleRadii(){cancelAnimationFrame(radiusFrame);radiusFrame=requestAnimationFrame(()=>{try{paintRadii(radiusState);paintSpacingGuides(root);root.querySelectorAll('.data-density-cell').forEach(cell=>{for(const [key,selector] of [['table','tbody tr[data-row-kind=multiline]'],['list','dl>div[data-row-kind=multiline]']])cell.querySelector('[data-measured-row='+key+']').textContent=Number(cell.querySelector(selector).getBoundingClientRect().height.toFixed(2))+'px';});inspector.properties();}catch(e){inspector.error("Geometry check failed: "+e.message);}});}
function paintRadii(s){
 const v=resolve(s.tier,s.scale,s.size,s.density);
 // Specimen cards are real Container surfaces; their controls retain independent scopes.
 root.querySelectorAll('.canvas').forEach(el=>{
  const density=el.closest('[data-density]')?.dataset.density??s.density;
  const context=resolve(s.tier,s.scale,s.size,density);
  el.style.setProperty('--canvas-margin',context.containers.card.margin+'px');
  el.style.setProperty('--canvas-gutter',composeContainer(context.containers.card.margin,Number(s.containerGutter)).gutter+'px');
 });
 // Resolve inline budgets before measuring radii and guide rectangles.
 const buttonPadding=[...root.querySelectorAll('.specimen .button__root:not(.listbox__option)')].map(el=>{
  const css=getComputedStyle(el),height=el.getBoundingClientRect().height,slots=[...el.querySelectorAll(':scope > [data-slot]')],labelIndex=slots.findIndex(x=>x.dataset.slot==='label');
  return {el,...resolveButtonPadding({margin:parseFloat(css.getPropertyValue('--surface-margin')),wrapperInset:parseFloat(css.getPropertyValue('--surface-inner'))/6,height,hasLeading:labelIndex>0,hasTrailing:labelIndex>=0&&labelIndex<slots.length-1})};
 });
 buttonPadding.forEach(({el,inlinePadding,labelStart,labelEnd})=>{el.style.setProperty('--button-inline',inlinePadding+'px');el.style.setProperty('--label-start',labelStart+'px');el.style.setProperty('--label-end',labelEnd+'px');});
 root.querySelector('#button-content-values').textContent='Labels use ½n inline padding on both sides for every arrangement and shape. Outer padding stays m. Internal slot gaps and extra compensation are zero.';
 root.querySelectorAll('.specimen [data-slot=icon],.specimen [data-slot=glyph],.spacing-demo[data-rule=composed] [data-slot=icon],.spacing-demo[data-rule=composed] [data-slot=glyph]').forEach(el=>{
  const css=getComputedStyle(el),W=parseFloat(css.getPropertyValue('--slot-padding').trim()||css.getPropertyValue('--wrapper-gutter'))||0,art=el.querySelector('.ph'),I=art?parseFloat(getComputedStyle(art).fontSize):0;
  const conflict=2*W+I>el.getBoundingClientRect().width+.01;
  el.dataset.slotConflict=String(conflict);el.title=conflict?'Square wrapper conflict: artwork plus wrapper padding exceeds square width':'';
 });
 const sharp=amount(s)===0;
 const solve=(elements,n,mode,rootMargin)=>{const frames=elements.map(el=>{const r=el.getBoundingClientRect();return {x:r.left,y:r.top,width:r.width,height:r.height};});return resolvePercentageRadiusGroup({amount:amount(s),retained:retained(s),family:s.radiusFamily,rootMargin,mode,frames});};
 root.querySelector('#radius-bounds').textContent=`${s.radiusFamily==='control'?'Controls: half-height':'Containers: margin'} · Amount ${amount(s)}% · Minimum retained ${retained(s)}% of immediate parent. Root has no floor. 0% amount is Sharp; Pill is exempt.`;
 root.querySelectorAll('.specimen-radius-overlay').forEach(el=>el.remove());
 const measured=el=>{const r=el.getBoundingClientRect();return {x:r.left,y:r.top,width:r.width,height:r.height};};
 const resolveFrames=(frames,n,mode,family,referenceHeights,rootMargin=0,parentRadius)=>resolvePercentageRadiusGroup({amount:amount(s,family),retained:retained(s,family),family,rootMargin,parentRadius,frames,mode,referenceHeights});
 const paintSurface=(el,radius,valid,mode,issues=[])=>{
  el.dataset.radiusMode=mode;el.dataset.radiusConflict=String(!valid);el.dataset.requiredRadius=String(radius);
  el.style.borderRadius=valid?radius+'px':'0px';el.style.cornerShape='round';
  if(el.matches('.listbox__root'))el.style.setProperty('--r-listbox',valid?radius+'px':'0px');
  if(el.matches('.listbox__option')){el.style.setProperty('--r-listbox-option',valid?radius+'px':'0px');el.style.setProperty('--listbox-option-radius',valid?radius+'px':'0px');}
  el.title=`${mode}: required R ${fmt(radius)}px${valid?'':'. Conflict: '+issues.join('; ')}`;
  if(valid)return;
  const host=el.closest('.canvas,.container-cell,.rule-scroll');if(!host)return;
  const r=el.getBoundingClientRect(),h=host.getBoundingClientRect(),w=r.width,height=r.height,R=radius;
  const arcs=R===0?`M0 0H${w}V${height}H0Z`:`M0 ${R} A${R} ${R} 0 0 1 ${R} 0 M${w-R} 0 A${R} ${R} 0 0 1 ${w} ${R} M${w} ${height-R} A${R} ${R} 0 0 1 ${w-R} ${height} M${R} ${height} A${R} ${R} 0 0 1 0 ${height-R}`;
  host.insertAdjacentHTML('beforeend',`<svg class="specimen-radius-overlay" width="${w}" height="${height}" viewBox="0 0 ${w} ${height}" style="left:${r.left-h.left+host.scrollLeft-host.clientLeft}px;top:${r.top-h.top+host.scrollTop-host.clientTop}px" aria-hidden="true"><rect width="${w}" height="${height}" fill="none" stroke="#aaa89f"/><path d="${arcs}" fill="none" stroke="#c9281c" stroke-width="1.5" stroke-dasharray="5 3"/></svg>`);
 };
 const applyStandalone=(el,n,family)=>{el.dataset.radiusFamily=family;const group=el.dataset.comparisonShape?resolvePercentageRadiusGroup({amount:el.dataset.comparisonShape==='sharp'?0:100,retained:0,family,mode:el.dataset.comparisonShape==='pill'?'pill':'standalone',frames:[measured(el)]}):resolveFrames([measured(el)],n,'standalone',family,undefined,parseFloat(getComputedStyle(el).paddingTop)||0);paintSurface(el,group.layers[0].radius,group.valid,'Standalone',group.issues);return group;};
 root.querySelectorAll('.canvas').forEach(el=>applyStandalone(el,v.n,'container'));
 const buttonGroups=[...root.querySelectorAll('#buttons .button__root,#buttons .badge-sample,#button-densities .button__root')].map(el=>applyStandalone(el,v.n,'control'));
 root.querySelector('#button-radius-summary').textContent=`Controls · Standalone · ${amount(s,'control')}% of half-height · ${buttonGroups.filter(g=>!g.valid).length} conflicting controls. Enable guides to inspect dashed required shapes.`;
 const applyNested=(parent,children,n,summary,family)=>{
  parent.dataset.radiusFamily=family;children.forEach(el=>el.dataset.radiusFamily=family);
  const frames=children.map(measured),left=Math.min(...frames.map(f=>f.x)),top=Math.min(...frames.map(f=>f.y));
  const envelope={x:left,y:top,width:Math.max(...frames.map(f=>f.x+f.width))-left,height:Math.max(...frames.map(f=>f.y+f.height))-top};
  const ref=resolveControlSurface(n,parent.closest('[data-density]')?.dataset.density??s.density);
  const listbox=parent.matches('.listbox__root'),rowHeight=parent.matches('[role=menu]')?ref.height:ref.innerHeight;
  const parentFrame=measured(parent),margin=Math.max(0,envelope.x-parentFrame.x);
  const group=resolveFrames([parentFrame,envelope],n,'nested',family,listbox?[ref.height,rowHeight]:undefined,margin);
  const childGroups=frames.map(f=>resolveFrames([f],n,'standalone',family,listbox?[rowHeight]:undefined,0,group.layers[0].radius));
  const issues=[...group.issues,...childGroups.flatMap((g,i)=>g.issues.map(x=>`Child ${i+1}: ${x}`))];
  const valid=issues.length===0;
  parent.dataset.containmentIssues=JSON.stringify(group.issues.filter(x=>!x.includes('physical cap')));
  const outer=group.layers[0];
  paintSurface(parent,outer.radius,outer.physicalExcess<=0.001,'Nested outer',group.issues.filter(x=>x.startsWith('Layer 1:')&&x.includes('physical cap')));
  children.forEach((el,i)=>paintSurface(el,childGroups[i].layers[0].radius,childGroups[i].valid,'Nested row',childGroups[i].issues));
  const displayPx=x=>Number(x.toFixed(2)).toString();
  summary.replaceChildren();
  summary.classList.add('radius-readout');
  const heading=document.createElement('strong');heading.textContent=`${family==='control'?'Controls':'Containers'} · Nested`;
  const metrics=document.createElement('span');metrics.className='radius-readout-values';metrics.textContent=`Outer R ${displayPx(group.layers[0].radius)}px · Inner R ${displayPx(group.layers[1].radius)}px · Inset ${displayPx(group.totalInset)}px`;
  const status=document.createElement('span');status.className='radius-readout-status';status.textContent=valid?'Fits measured frames':`${issues.length} geometry conflicts — enable guides to inspect required shapes`;
  summary.append(heading,metrics,status);
  if(!valid){const list=document.createElement('span');list.className='radius-readout-issues';for(const issue of issues){const line=document.createElement('span');line.textContent=issue.replace(/-?\d+\.\d+/g,x=>displayPx(Number(x)));list.append(line);}summary.append(list);}

 };
 root.querySelectorAll('#menus .listbox__root').forEach(el=>applyNested(el,[...el.querySelectorAll(':scope > .listbox__option')],v.n,root.querySelector('#'+el.id+'-radius-summary'),'control'));
 root.querySelectorAll('#listbox-densities .listbox__root').forEach(el=>applyNested(el,[...el.querySelectorAll(':scope > .listbox__option')],v.n,el.closest('article').querySelector('.listbox-density-radius'),'control'));
 root.querySelectorAll('.tier-demo').forEach((el,i)=>{if(i<2){const context=resolve(i===0?'widget':'product',s.scale,s.size,s.density);applyStandalone(el,context.n,'control');el.parentElement.querySelector('.container-radius-summary').textContent='Control · Standalone outer frame. Internal content wrappers do not create radius scopes.';return;}if(i===2){el.querySelectorAll(':scope > span').forEach(child=>applyStandalone(child,v.n,'control'));el.parentElement.querySelector('.container-radius-summary').textContent=`Layout Group · zero edge margin · gap = ${s.groupGutter}% of margin reference · no radius scope.`;return;}applyNested(el,[...el.querySelectorAll(':scope > span')],resolve(i===0?'widget':i===1?'product':s.tier,s.scale,s.size,s.density).n,el.parentElement.querySelector('.container-radius-summary'),i<2?'control':'container');});
 const card=root.querySelector('#nested-card');
 const cardMargin=v.containers.card.margin;
 const roles=resolveSpacingRoles(cardMargin,{pagePercent:Number(s.pageGutter),groupPercent:Number(s.groupGutter),containerPercent:Number(s.containerGutter),controlUnit:v.n,controlMargin:v.surface.margin,controlPercent:Number(s.controlGutter)});
 card.style.setProperty('--group-gutter',roles.group.gutter+'px');
 root.querySelector('#spacing-role-summary').textContent=`Margin reference ${fmt(cardMargin)}px · Page ${s.pageGutter}%: ${fmt(roles.page.gutter)}px · Container ${s.containerGutter}%: ${fmt(roles.container.gutter)}px · Group ${s.groupGutter}%: ${fmt(roles.group.gutter)}px · Control ${s.controlGutter}% of n: m ${fmt(roles.control.margin)}px / W ${fmt(roles.control.gutter)}px. Ratios derive directly from the reference, never another gutter.`;
 card.style.setProperty('--card-inset',cardMargin+'px');card.style.setProperty('--card-gutter',composeContainer(cardMargin,Number(s.containerGutter)).gutter+'px');
 // Paint measured empty space only; no extra layout surface or focusable nodes.
 card.querySelector('.card-spacing-overlay')?.remove();
 const box=measured(card),items=[...card.children].map(measured);
 const left=Math.min(...items.map(r=>r.x))-box.x,right=Math.max(...items.map(r=>r.x+r.width))-box.x;
 const top=items[0].y-box.y,bottom=items.at(-1).y+items.at(-1).height-box.y;
 const rect=(x,y,w,h,color)=>w>0&&h>0?`<rect data-guide="${color==='#f1cac0'?'margin':'gutter'}" x="${x}" y="${y}" width="${w}" height="${h}" fill="${color}"/>`:'';
 let guides=rect(0,0,box.width,top,'#f1cac0')+rect(0,bottom,box.width,box.height-bottom,'#f1cac0')+rect(0,top,left,bottom-top,'#f1cac0')+rect(right,top,box.width-right,bottom-top,'#f1cac0');
 items.slice(1).forEach((r,i)=>{const y=items[i].y+items[i].height-box.y;guides+=rect(left,y,right-left,r.y-box.y-y,'#d6d6cc');});
 const heading=[...card.querySelector('.nested-heading').children].map(measured);
 const headingGap=heading[1].y-heading[0].y-heading[0].height;
 guides+=rect(heading[0].x-box.x,heading[0].y+heading[0].height-box.y,heading[0].width,headingGap,'#d6d6cc');
 if(headingGap>0)guides+=`<text data-guide="gutter" x="${box.width/2}" y="${heading[0].y+heading[0].height-box.y+headingGap/2}" dominant-baseline="middle" text-anchor="middle">Group ${fmt(headingGap)}px</text>`;
 const buttons=[...card.querySelectorAll('.nested-actions button')].map(measured);
 buttons.slice(1).forEach((r,i)=>{const previous=buttons[i];if(Math.abs(previous.y-r.y)<1)guides+=rect(previous.x+previous.width-box.x,r.y-box.y,r.x-previous.x-previous.width,Math.min(previous.height,r.height),'#d6d6cc');else guides+=rect(left,previous.y+previous.height-box.y,right-left,r.y-previous.y-previous.height,'#d6d6cc');});
 guides+=`<text data-guide="margin" x="${box.width/2}" y="${top/2}" dominant-baseline="middle" text-anchor="middle">M ${fmt(cardMargin)}px</text>`;
 const firstGap=items[1].y-items[0].y-items[0].height;
 if(firstGap>0)guides+=`<text data-guide="gutter" x="${box.width/2}" y="${items[0].y+items[0].height-box.y+firstGap/2}" dominant-baseline="middle" text-anchor="middle">Container ${fmt(firstGap)}px</text>`;
 card.insertAdjacentHTML('beforeend',`<svg class="card-spacing-overlay" width="${box.width}" height="${box.height}" viewBox="0 0 ${box.width} ${box.height}" aria-hidden="true">${guides}</svg>`);
 const cardGroup=resolveFrames([measured(card)],v.n,'standalone','container',undefined,cardMargin);
 card.dataset.radiusFamily='container';
 paintSurface(card,cardGroup.layers[0].radius,cardGroup.valid,'Standalone Container',cardGroup.issues);
 root.querySelector('#nested-card-radius-summary').textContent=`Container card · Standalone · Margin ${fmt(cardMargin)}px × ${amount(s,'container')}% = R ${fmt(cardGroup.layers[0].radius)}px. No Container child surface; retention does not cross into Controls. ${cardGroup.valid?'Fits.':'Conflict: '+cardGroup.issues.join('; ')}`;
 const nestedList=root.querySelector('#nested-listbox');
 applyNested(nestedList,[...nestedList.querySelectorAll(':scope > .listbox__option')],v.n,root.querySelector('#nested-listbox-radius-summary'),'control');
 const nestedButtons=[...root.querySelectorAll('.nested-actions .button__root')].map(el=>applyStandalone(el,v.n,'control'));
 root.querySelector('#nested-buttons-radius-summary').textContent=`Controls · Standalone buttons · ${amount(s,'control')}% of half-height · ${nestedButtons.filter(g=>!g.valid).length} conflicts. Card settings do not affect these controls.`;
 root.querySelectorAll('.density-row .spacing-demo:not([data-rule=group]):not([data-rule=page])').forEach(el=>applyStandalone(el,v.n,el.dataset.rule==='composed'?'control':'container'));
 const mediaConflicts=[];
 root.querySelectorAll('.specimen [data-slot=media],.specimen [data-slot=icon],.specimen [data-slot=glyph],.spacing-demo[data-rule=composed] [data-slot=icon],.spacing-demo[data-rule=composed] [data-slot=glyph]').forEach(el=>{
  const icon=el.dataset.slot!=='media';
  const parent=el.parentElement,shape=icon||s[el.dataset.media+'Inherit']?'control':el.dataset.media==='avatar'?'circle':'intrinsic';
  el.dataset.mediaShape=shape;
  const group=resolveMediaRadius({shape,frame:measured(el),amount:parent.dataset.comparisonShape?(parent.dataset.comparisonShape==='sharp'?0:100):amount(s,'control'),retained:parent.dataset.comparisonShape?0:retained(s,'control'),parentRadius:Number(parent.dataset.requiredRadius)});
  const layer=group.layers[0];paintSurface(el,layer.radius,group.valid,(icon?el.dataset.slot+' wrapper ':'Media ')+shape,group.issues);
  el.title+=` · ${fmt(layer.width)}px media; candidate ${fmt(layer.candidate)}px; parent floor ${fmt(layer.floor)}px`;
  if(!group.valid&&el.closest('#button-density-grid,#listbox-density-grid'))mediaConflicts.push({asset:icon?el.dataset.slot:el.dataset.media,density:el.closest('[data-density]').dataset.density,context:el.closest('#button-density-grid')?'Button':'Listbox',r:layer.radius,w:layer.width,h:layer.height});
 });
 const diagnostics=root.querySelector('#media-diagnostics');
 diagnostics.hidden=!mediaConflicts.length;
 diagnostics.querySelector('summary').textContent=`Slot radius conflicts · ${mediaConflicts.length} — ${mediaConflicts.length?'expand for required radius / cap / excess':'all measured artwork slots fit'}`;
 diagnostics.querySelector('.media-diagnostic-grid').innerHTML=mediaConflicts.map(({asset,density,context,r,w,h})=>{const cap=Math.min(w,h)/2,pad=Math.max(r,4),size=Math.max(w,h)+2*pad;return `<figure><svg viewBox="${-pad} ${-pad} ${size} ${size}" role="img" aria-label="${asset}: required radius ${fmt(r)}px exceeds physical cap ${fmt(cap)}px"><rect width="${w}" height="${h}" fill="none" stroke="#777" stroke-width="0.5"/><path d="M0 ${r} A${r} ${r} 0 0 1 ${r} 0 M${w-r} 0 A${r} ${r} 0 0 1 ${w} ${r} M${w} ${h-r} A${r} ${r} 0 0 1 ${w-r} ${h} M${r} ${h} A${r} ${r} 0 0 1 0 ${h-r}" fill="none" stroke="#c9281c" stroke-width="0.6" stroke-dasharray="2 1"/></svg><figcaption>${context} · ${density} · ${asset}<br>Required R ${fmt(r)}px / cap ${fmt(cap)}px<br>Excess ${fmt(r-cap)}px · frame ${fmt(w)} × ${fmt(h)}px</figcaption></figure>`;}).join('');
 root.querySelectorAll('.density-arrangement').forEach(pair=>{const buttons=[...pair.querySelectorAll('.density-button')],widths=buttons.map(el=>el.getBoundingClientRect().width);const button=buttons[0],slots=[...button.querySelectorAll(':scope > [data-slot]')],label=button.querySelector('[data-slot=label]'),index=slots.indexOf(label),css=getComputedStyle(label),W=parseFloat(getComputedStyle(label).getPropertyValue('--surface-inner'))/6,start=index===0?Math.max(0,parseFloat(css.paddingInlineStart)-W):0,end=index===slots.length-1?Math.max(0,parseFloat(css.paddingInlineEnd)-W):0,both=index===0&&slots.length===1;
 pair.querySelector('.pair-edge-padding').textContent=`Label padding · leading ${fmt(W)}px / trailing ${fmt(W)}px · ½n each`;
 const bc=getComputedStyle(button),m=parseFloat(bc.paddingInlineStart),gap=parseFloat(bc.columnGap)||0;
 const describe=(side,extra,siblings)=>{const occupied=siblings.reduce((sum,slot)=>sum+slot.getBoundingClientRect().width,0),gaps=siblings.length*gap,total=m+occupied+gaps+W+extra;return `${side} ${fmt(total)}px = ${fmt(m)} margin + ${fmt(W)} wrapper${siblings.length?` + ${fmt(occupied)} slot + ${fmt(gaps)} gap`:''}`;};
 pair.querySelector('.pair-total-inset').textContent=`Edge → text\n${describe('Leading',start,slots.slice(0,index))}\n${describe('Trailing',end,slots.slice(index+1))}`;
 pair.querySelector('.pair-widths').textContent=`Width ${fmt(widths[0])} / ${fmt(widths[1])}px · ${Math.abs(widths[0]-widths[1])<0.01?'equal':'mismatch'}`;});
 root.querySelectorAll('.specimen [data-slot]').forEach(el=>{const box=el.getBoundingClientRect(),css=getComputedStyle(el);const label=`${el.dataset.slot} slot · ${fmt(box.width)} × ${fmt(box.height)}px · inline padding ${css.paddingInlineStart} / ${css.paddingInlineEnd}`;el.dataset.spec=label;el.title=['media','icon','glyph'].includes(el.dataset.slot)?el.title+' · '+label:label;});
 root.querySelectorAll('.radius-example').forEach(example=>{
  const context=resolve(s.tier,s.scale,s.size,example.dataset.densityName);
  const elements=[...example.querySelectorAll('[data-radius-layer]')];
  const group=solve(elements,context.n,example.dataset.mode,Number(example.dataset.rootMargin));
  example.dataset.conflict=String(!group.valid);
  const outer=example.querySelector('.radius-parent');
  outer.querySelector('.required-radius-overlay')?.remove();
  outer.style.visibility='';
  outer.style.marginTop='';outer.style.marginBottom='';
  if(!group.valid){
   const box=outer.getBoundingClientRect();
   const paths=elements.map((el,i)=>{
    const rect=el.getBoundingClientRect(),x=rect.left-box.left,y=rect.top-box.top,w=rect.width,h=rect.height,r=group.layers[i].radius;
    if(r===null)return `<g transform="translate(${x} ${y})"><title>Intermediate radius unresolved: ambiguous inset geometry</title><rect width="${w}" height="${h}" fill="none" stroke="#c9281c" stroke-dasharray="2 3"/></g>`;
    // Separate exact quarter circles: never normalize an impossible rounded rectangle.
    const arcs=r===0?`M0 0H${w}V${h}H0Z`:`M0 ${r} A${r} ${r} 0 0 1 ${r} 0 M${w-r} 0 A${r} ${r} 0 0 1 ${w} ${r} M${w} ${h-r} A${r} ${r} 0 0 1 ${w-r} ${h} M${r} ${h} A${r} ${r} 0 0 1 0 ${h-r}`;
    const edges=r===0?'':`${w>=2*r?`M${r} 0H${w-r} M${r} ${h}H${w-r}`:''} ${h>=2*r?`M0 ${r}V${h-r} M${w} ${r}V${h-r}`:''}`;
    const color=['#c9281c','#252525','#8b4e00'][i];
    return `<g transform="translate(${x} ${y})"><title>${['Outer','Middle','Inner'][i]} required radius ${fmt(r)}px</title><rect width="${w}" height="${h}" fill="none" stroke="${color}" stroke-opacity=".3"/><path d="${arcs} ${edges}" fill="none" stroke="${color}" stroke-width="1.5" stroke-dasharray="5 3"/></g>`;
   }).join('');
   outer.insertAdjacentHTML('beforeend',`<svg class="required-radius-overlay" width="${box.width}" height="${box.height}" viewBox="0 0 ${box.width} ${box.height}" role="img" aria-label="Required radii in dashed lines over solid measured frames; overlapping arcs indicate physical conflicts">${paths}</svg>`);
   const overhang=Math.max(0,...group.layers.map(l=>l.radius-l.height));
   outer.style.marginTop=overhang+'px';outer.style.marginBottom=overhang+'px';
  }
  elements.forEach((el,i)=>{el.style.borderRadius=group.valid?group.layers[i].radius+'px':'0px';el.style.cornerShape='round';});
  example.querySelector('.radius-status').textContent=group.valid?(group.mode==='pill'?'Pill · R = min(width, height)/2 · percentage exempt':sharp?'Sharp · exempt':'Fits · candidate and immediate-parent floor'):`Conflict · ${group.issues.map(x=>x.replace(/-?\d+\.\d+/g,n=>Number(Number(n).toFixed(2)))).join('; ')}. Enable guides to inspect required shapes. Dimensions unchanged.`;
  example.querySelector('.radius-values').textContent=group.layers.map((r,i)=>`${['Outer','Middle','Inner'][i]} required R ${fmt(r.radius)}`).join(' · ')+' px';
  example.querySelector('.radius-cap').textContent=group.layers.map((r,i)=>`${['Outer','Middle','Inner'][i]}: ${fmt(r.width)} × ${fmt(r.height)}px · physical cap ${fmt(r.cap)}px ${group.mode==='pill'?'· frame-derived radius':`· candidate ${fmt(r.candidate)}px · parent floor ${fmt(r.floor)}px · ${s.radiusFamily==='control'?'reference H '+fmt(r.referenceHeight):'remaining margin '+fmt(Math.max(0,group.rootMargin-r.inset))}px · outward inset ${fmt(r.offset)}px${group.mode==='nested'?` / ${fmt(group.totalInset)}px`:''}`}`).join('\n');
 });
}
window.addEventListener('resize',scheduleRadii);
const radiusObserver=new ResizeObserver(scheduleRadii);radiusObserver.observe(lab);
document.fonts.ready.then(scheduleRadii);
function reduceCandidate(s,a){if(a.type==='media-toggle')return {...s,[a.key]:!s[a.key]};if(a.type==='media-selection')return {...s,comparisonSelection:a.value};if(a.type==='configuration')return {...s,...a.value};if(a.type==='preset'){const p=radiusPercentagePresets[a.value];return {...s,[a.family+'Amount']:p,[a.family+'Retained']:0};}if(a.type==='dial')return {...s,[a.key]:Number(a.value)};if(a.type==='reset')return {...defaults,message:'Default system restored.'};if(a.type==='card-guide'){const enabled=!s.guides||!s[a.key];return {...s,[a.key]:enabled,guides:enabled?true:s.guides};}if(a.type==='guides')return {...s,guides:!s.guides};if(a.type==='axis')return {...s,[a.key]:a.value};if(a.type==='voice')return {...s,voice:a.value};if(a.type==='nested-voice')return {...s,nestedVoice:a.value};if(a.type==='nested-message')return {...s,nestedMessage:a.value};if(a.type==='message')return {...s,message:a.value};return s;}
const runtime=createUIRuntime();
runtime.mount({root,stateKey:'study',definition:{initialState:inspector.initial,
reduce(s,a){const next=reduceCandidate(s,a);return inspector.accept(next)?next:s;},
render(root,s){radiusState=s;const v=resolve(s.tier,s.scale,s.size,s.density);
for(const key of ['containerAmount','controlAmount','containerRetained','controlRetained'])root.querySelector('#'+key+'Value').textContent=`${s[key]}%`;
root.querySelectorAll('[data-action=radius-preset]').forEach(el=>el.setAttribute('aria-pressed',el.dataset.preset===presetName(s,el.dataset.family)));
// Purpose is fixed per example; scale, size and density follow the live controls.
const widgetExample=resolve('widget',s.scale,s.size,s.density),productExample=resolve('product',s.scale,s.size,s.density);
const cs=resolveControlSurface(productExample.n,s.density),ws=resolveControlSurface(widgetExample.n,s.density);
const containers={...v.containers,widget:resolveControlSurface(widgetExample.n,s.density,Number(s.controlGutter)),control:resolveControlSurface(productExample.n,s.density,Number(s.controlGutter))};
for(const k of containerLevels)if(!['widget','control'].includes(k))containers[k]=composeContainer((k==='group'?v.groupMarginReference:containers[k].margin),Number(s.containerGutter));
containers.group=resolveSpacingRoles(v.groupMarginReference,{groupPercent:Number(s.groupGutter)}).group;
for(const key of ['pageGutter','containerGutter','groupGutter','controlGutter'])root.querySelector('#'+key+'Value').textContent=s[key]+'%';root.style.setProperty('--page-gutter-ratio',Number(s.pageGutter)/100);root.querySelector('#container-spacing-formula').textContent='G = '+fmt(Number(s.containerGutter)/100)+' × M';
const blockHeight=k=>k==='widget'?ws.innerHeight:cs.innerHeight;
for(const key of ['tier','scale','size','density','controlGutter','pageGutter','groupGutter','containerGutter','containerAmount','controlAmount','containerRetained','controlRetained','radiusFamily'])root.querySelector('#'+key).value=s[key];lab.classList.toggle('guides',s.guides);lab.classList.toggle('hide-margins',!s.marginGuides);lab.classList.toggle('hide-gutters',!s.gutterGuides);for(const [key,kind] of [['wrapperGuides','wrappers'],['centeringGuides','centering']])lab.classList.toggle('hide-'+kind,!s[key]);root.querySelectorAll('[data-action=card-guide]').forEach(el=>el.setAttribute('aria-checked',s.guides&&s[el.dataset.key]));root.querySelector('[data-action=guides]')?.setAttribute('aria-pressed',s.guides);root.querySelector('#action-feedback').textContent=s.message;root.querySelector('#nested-feedback').textContent=s.nestedMessage;
root.querySelectorAll('[data-value]').forEach(el=>{el.textContent=fmt(el.dataset.value.split('.').reduce((a,k)=>a[k],v))});
v.table=resolveDataRowGeometry(v.n,s.density,Number(s.controlGutter));
const properties={'--g-unit':v.n,'--g-d':v.d,'--g-margin':v.d,'--g-gutter':v.d,'--g-height':v.surface.height,'--g-compact-height':v.surface.innerHeight,'--g-icon':v.surface.icon,'--g-text':v.type.control,'--g-body-text':v.type.body,'--g-caption-text':v.type.fieldLabel,'--g-table-row-height':v.table.rowHeight,'--g-table-cell-margin':v.table.cellMargin,'--g-table-clearance':v.table.clearance,'--g-table-slot-height':v.table.slotHeight,'--g-table-column-gap':v.table.columnGap};
root.querySelectorAll('#data .specimen').forEach(el=>{for(const [key,value] of Object.entries(properties))if(key.startsWith('--g-table-'))el.style.setProperty(key,value+'px');});
root.querySelectorAll('.specimen').forEach(el=>{for(const key of ['tier','scale','size','density'])el.dataset[key]=s[key];el.style.setProperty('--ui-font',voices[s.voice]);el.style.setProperty('--r-control','0px')});
root.querySelectorAll('.specimen').forEach(el=>{const c=resolveControlSurface(v.n,s.density,Number(s.controlGutter));el.style.setProperty('--surface-height',c.height+'px');el.style.setProperty('--surface-inner',c.innerHeight+'px');el.style.setProperty('--surface-margin',c.margin+'px');el.style.setProperty('--surface-gap',c.slotGap+'px');el.style.setProperty('--surface-icon',c.icon+'px');el.style.setProperty('--surface-glyph',c.glyph+'px');el.style.setProperty('--slot-padding',c.slotPadding+'px');});
root.querySelectorAll('[role=option][data-voice]').forEach(el=>{const selected=el.dataset.voice===(el.closest('#nested-listbox')?s.nestedVoice:s.voice);el.setAttribute('aria-selected',selected);const check=el.querySelector('.check');if(check)check.style.visibility=selected?'visible':'hidden'});
root.querySelector('#measure-rows').innerHTML=containerLevels.map(k=>`<tr><th scope="row">${containerLabel(k)}</th><td>${fmt(containers[k].margin)} px</td><td>${['widget','control'].includes(k)?'L '+fmt(containers[k].labelPadding)+' / gap 0':fmt(containers[k].gutter)} px</td></tr>`).join('');
root.querySelectorAll('#measure-rows th,#measure-rows td').forEach(cell=>{const slot=document.createElement('span');slot.className='data-cell-slot';slot.append(...cell.childNodes);cell.append(slot);});
root.querySelector('#container-grid').innerHTML=containerLevels.map(k=>`<div class="container-cell"><h3>${containerLabel(k)} <span class="eyebrow">${['widget','control'].includes(k)?'Label L = n/2; slot gap 0':(k==='group'?s.groupGutter:s.containerGutter)+'% reference M'}</span></h3><div class="tier-demo" data-role="${k==='group'?'group':['widget','control'].includes(k)?'control':'container'}" data-direction="${['widget','control','group'].includes(k)?'horizontal':'vertical'}" style="--example-height:${blockHeight(k)}px;--margin:${containers[k].margin}px;--gutter:${containers[k].wrapperGap??containers[k].gutter}px;--tier-wrapper:${containers[k].labelPadding??0}px"><span><span class="tier-label" title="Content">Content</span></span><span><span class="tier-label" title="Content">Content</span></span></div><div class="spec"><span>M ${fmt(containers[k].margin)} px</span><span>${['widget','control'].includes(k)?'L '+fmt(containers[k].labelPadding)+' / side · gap 0':'G '+fmt(containers[k].gutter)} px</span><span>Outer H ${fmt(['widget','control','group'].includes(k)?blockHeight(k)+2*containers[k].margin:2*blockHeight(k)+2*containers[k].margin+containers[k].gutter)} px</span></div><p class="note container-radius-summary"></p></div>`).join('');
root.querySelector('#density-comparison').innerHTML=`<table class="spacing-matrix"><caption>Four spacing roles across five densities · selected purpose, scale and size</caption><thead><tr><th scope="col">Density</th><th scope="col">Page<span class="spec">G = ${s.pageGutter}% M</span></th><th scope="col">Containers<span class="spec">G = ${s.containerGutter}% M</span></th><th scope="col">Groups<span class="spec">G = ${s.groupGutter}% reference M<br>No edge padding</span></th><th scope="col">Controls<span class="spec">Icon/glyph W = ${s.controlGutter}% n<br>Label L = ½n · Slot gap 0</span></th></tr></thead><tbody>`+Object.entries(DENSITIES).map(([density,q])=>{
 const r=resolve(s.tier,s.scale,s.size,density),c=composeContainer(r.containers.card.margin,Number(s.containerGutter)),p=resolveControlSurface(r.n,density,Number(s.controlGutter));
 const surface=resolveControlSurface(r.n,density),roles=resolveSpacingRoles(r.containers.card.margin,{pagePercent:Number(s.pageGutter),groupPercent:Number(s.groupGutter),containerPercent:Number(s.containerGutter)});
 const style=`--rule-inner:${r.surface.innerHeight}px;--rule-margin:${p.margin}px;--rule-slot:${p.slotHeight}px;--rule-icon:${p.icon}px;--rule-glyph:${r.surface.glyph}px;--rule-text:${r.type.control}px`;
 return `<tr class="density-row" data-density-name="${density}" ${density===s.density?'data-current="true"':''}><th scope="row">${density[0].toUpperCase()+density.slice(1)}<span class="spec">${density===s.density?'Active · ':''}${q/4*100}% density<br>Reference M ${fmt(c.margin)}px<br>n ${fmt(r.n)}px</span></th><td><div class="rule-scroll"><div class="spacing-demo page-role-demo" data-rule="page" style="${style};--rule-margin:${c.margin}px;--rule-gap:${roles.page.gutter}px"><span class="rule-part">Main</span><span class="rule-part">Aside</span></div></div><p class="spec">M ${fmt(c.margin)} px · G ${fmt(roles.page.gutter)} px</p></td><td><div class="rule-scroll" tabindex="0" role="region" aria-label="${density} container example"><div class="spacing-demo" data-rule="container" style="${style};--rule-margin:${c.margin}px;--rule-gap:${c.gutter}px"><span class="rule-part">A</span><span class="rule-part">B</span></div></div><p class="spec">M ${fmt(c.margin)} px · G ${fmt(c.gutter)} px</p></td><td><div class="rule-scroll"><div class="spacing-demo group-role-demo" data-rule="group" style="${style};--rule-margin:0px;--rule-gap:${roles.group.gutter}px"><span class="rule-part">Save</span><span class="rule-part">Cancel</span></div></div><p class="spec">Edge M 0 · Reference ${fmt(c.margin)} px · G ${fmt(roles.group.gutter)} px</p></td><td><div class="rule-scroll" tabindex="0" role="region" aria-label="${density} composed control example"><div class="spacing-demo" data-rule="composed" style="${style};--rule-gap:${p.wrapperGap}px;--wrapper-gutter:${p.gutter}px;--surface-inner:${p.innerHeight}px;--slot-padding:${p.slotPadding}px"><span class="rule-part rule-icon" data-slot="icon" aria-hidden="true"><i class="ph ph-fill ph-circle"></i></span><span class="rule-part" data-slot="label">Label</span><span class="rule-part rule-glyph" data-slot="glyph" aria-hidden="true"><i class="ph ph-caret-right"></i></span></div></div><p class="spec">m ${fmt(p.margin)} px · Icon/glyph W ${fmt(p.gutter)} px / side<br>Label L ${fmt(p.labelPadding)} px / side · Slot gap 0px<br>Icon–label: ${fmt(p.iconContentSeparation)} px · Label–glyph: ${fmt(p.glyphContentSeparation)} px</p></td></tr>`;
}).join('')+'</tbody></table>';

root.querySelector('#button-density-grid').innerHTML=Object.keys(DENSITIES).map(density=>{
 const r=resolve(s.tier,s.scale,s.size,density),c=resolveControlSurface(r.n,density,Number(s.controlGutter));
 const radius=amount(s,'control')/100*c.height/2,padding=resolveButtonPadding({margin:c.margin,wrapperInset:c.labelPadding,height:c.height});
 const avatar='<span data-slot="media" data-media="avatar" aria-hidden="true"><svg viewBox="0 0 24 24"><rect width="24" height="24" fill="#e8c17f"/><circle cx="12" cy="8" r="4" fill="#252525"/><path d="M3 24v-3a9 9 0 0 1 18 0v3" fill="#252525"/></svg></span>';
 const logo='<span data-slot="media" data-media="logo" aria-hidden="true"><svg viewBox="0 0 24 24"><rect width="24" height="24" fill="#f7f5ee"/><path d="M0 0h8v16h16v8H0z" fill="#252525"/><path d="M12 0h12v12H12z" fill="#c9281c"/></svg></span>';
 const arrangements=[['Label only','<span data-slot="label">Action</span>'],['Icon + label','<span data-slot="icon" aria-hidden="true"><i class="ph ph-fill ph-circle"></i></span><span data-slot="label">Action</span>'],['Label + glyph','<span data-slot="label">Action</span><span data-slot="glyph" aria-hidden="true"><i class="ph ph-caret-right"></i></span>']];
 arrangements.push(['Avatar + label',avatar+'<span data-slot="label">Profile</span>'],['Label + logo','<span data-slot="label">Studio</span>'+logo]);
 return `<article class="button-density-cell" ${density===s.density?'data-current="true"':''}><h3>${density[0].toUpperCase()+density.slice(1)}</h3><div class="canvas specimen density-arrangements" data-tier="${s.tier}" data-scale="${s.scale}" data-size="${s.size}" data-density="${density}" style="--surface-height:${c.height}px;--surface-inner:${c.innerHeight}px;--surface-margin:${c.margin}px;--surface-gap:${c.slotGap}px;--surface-icon:${c.icon}px;--surface-glyph:${c.glyph}px;--slot-padding:${c.slotPadding}px;--ui-font:${voices[s.voice]}">${arrangements.map(([label,slots])=>`<div class="density-arrangement"><p class="sample-label">${label}</p><div class="shape-pair">${['sharp','pill'].map(shape=>`<div class="shape-sample"><span class="shape-name">${shape==='sharp'?'Sharp':'Pill'}</span><button type="button" class="button__root density-button" data-comparison-shape="${shape}" data-action="sample" data-name="${density} · ${label} · ${shape}">${slots}</button></div>`).join('')}</div><p class="pair-edge-padding spec"></p><p class="pair-total-inset spec"></p><p class="pair-widths spec" aria-live="off"></p></div>`).join('')}</div><dl class="primary-readout"><dt>Height</dt><dd>${fmt(c.height)}px</dd><dt>Sharp / Pill R</dt><dd>0 / ${fmt(c.height/2)}px</dd><dt>Margin m</dt><dd>${fmt(c.margin)}px</dd><dt>Slot gap</dt><dd>0px</dd></dl><details class="spacing-breakdown"><summary>Spacing breakdown</summary><p class="spec">Inner S ${fmt(c.innerHeight)}px<br>Icon/glyph budget W ${fmt(c.slotPadding)}px / side<br>Label L ${fmt(c.labelPadding)}px / side<br>Label-only edge-to-text ${fmt(padding.exposedLabelInset)}px<br>Media ${fmt(c.mediaSize)}px square · W 0<br>Media–label ${fmt(c.mediaContentSeparation)}px<br>Label–glyph ${fmt(c.glyphContentSeparation)}px<br>Icon–label ${fmt(c.iconContentSeparation)}px</p></details></article>`;
}).join('');

const listboxGrid=root.querySelector('#listbox-density-grid');
listboxGrid.replaceChildren();
for(const density of Object.keys(DENSITIES)){
 const c=resolveControlSurface(v.n,density,Number(s.controlGutter));
 const article=document.createElement('article');article.className='listbox-density-cell';article.dataset.current=String(density===s.density);
 const buttonCanvas=root.querySelector(`#button-density-grid [data-density="${density}"]`);
 const specimen=document.createElement('div');specimen.className='canvas specimen';
 for(const key of ['tier','scale','size','density'])specimen.dataset[key]=buttonCanvas.dataset[key];
 specimen.style.cssText=buttonCanvas.style.cssText;
 const list=root.querySelector('#listbox').cloneNode(true);list.id=`density-listbox-${density}`;list.setAttribute('aria-label',`${density} typography: icon, avatar and logo`);
 list.querySelectorAll('.content-spacing-overlay,.specimen-radius-overlay').forEach(el=>el.remove());
 list.querySelectorAll('.check').forEach(el=>el.style.visibility='visible');
 list.setAttribute('aria-multiselectable','true');list.querySelectorAll('[role=option]').forEach((el,i)=>{if(s.comparisonSelection!=='current')el.setAttribute('aria-selected',String(s.comparisonSelection==='all'));el.id=`${list.id}-option-${i}`;el.tabIndex=el.getAttribute('aria-selected')==='true'?0:-1;});
 if(!list.querySelector('[tabindex="0"]'))list.querySelector('[role=option]')?.setAttribute('tabindex','0');
 specimen.append(list);
  article.innerHTML=`<h3>${density[0].toUpperCase()+density.slice(1)}</h3><dl class="primary-readout"><dt>Row height</dt><dd>${fmt(c.slotHeight)}px</dd><dt>Reference H</dt><dd>${fmt(c.height)}px</dd><dt>Margin m</dt><dd>${fmt(c.margin)}px</dd><dt>Slot gap</dt><dd>0px</dd></dl><details class="spacing-breakdown"><summary>Spacing breakdown</summary><p class="spec">Icon/glyph budget W ${fmt(c.slotPadding)}px / side<br>Label L ${fmt(c.labelPadding)}px / side<br>Icon ${fmt(c.icon)}px · glyph ${fmt(c.glyph)}px<br>Media ${fmt(c.mediaSize)}px square<br>Media–label ${fmt(c.mediaContentSeparation)}px<br>Icon–label ${fmt(c.iconContentSeparation)}px</p></details>`;
 article.insertBefore(specimen,article.querySelector('.primary-readout'));
 const summary=document.createElement('p');summary.className='note listbox-density-radius';article.append(summary);listboxGrid.append(article);
}

const densities=Object.keys(DENSITIES),modes=['standalone','nested','pill'];
root.querySelector('#radius-comparison').innerHTML=`<table class="radius-matrix"><caption>${s.radiusFamily==='control'?'Controls':'Containers'} · ${presetName(s)} · ${s.scale}/${s.size} · All density levels</caption><colgroup><col class="radius-mode-column"><col span="5"></colgroup><thead><tr><th scope="col" class="radius-mode-corner"><span class="radius-mode-label">Mode</span></th>${densities.map(density=>{const r=resolve(s.tier,s.scale,s.size,density);return `<th scope="col" ${density===s.density?'data-current="true"':''}>${density[0].toUpperCase()+density.slice(1)}${density===s.density?' · Active':''}<span class="spec">Amount ${amount(s)}% · Retained ${retained(s)}% · ${s.radiusFamily==='container'?'Margin '+fmt(r.containers.card.margin)+'px':'Reference H '+fmt(r.surface.height)+'px'}</span></th>`}).join('')}</tr></thead><tbody>${modes.map(mode=>`<tr><th scope="row" class="radius-mode-header"><span class="radius-mode-label">${mode[0].toUpperCase()+mode.slice(1)}</span></th>${densities.map(density=>{const r=resolve(s.tier,s.scale,s.size,density),c=resolveControlSurface(r.n,density),isContainer=s.radiusFamily==='container',m=isContainer?r.containers.card.margin:c.margin,inner=isContainer?8*r.n:c.innerHeight;return `<td ${density===s.density?'data-current="true"':''}><article class="radius-example" data-mode="${mode}" data-density-name="${density}" data-root-margin="${m}" data-family="${s.radiusFamily}"><p class="spec">${isContainer?'Card → inset surface → content surface':'Control → inner surface'} · reference M ${fmt(m)}px</p><div class="radius-parent" data-radius-layer style="--radius-margin:${m/2}px;--radius-child-margin:${m/2}px;--radius-child-height:${inner}px;--radius-font:${r.type.control}px"><div class="radius-child" data-radius-layer><div class="radius-leaf" data-radius-layer>${isContainer?'Card content':'Control content'}</div></div></div><p class="note radius-status" role="status"></p><p class="spec radius-values"></p><p class="spec radius-cap"></p></article></td>`}).join('')}</tr>`).join('')}</tbody></table>`;

lab.classList.toggle('show-slot-boundaries',s.slotBoundaries);lab.classList.toggle('inspection-off',!s.slotBoundaries&&!(s.guides&&['marginGuides','gutterGuides','wrapperGuides','centeringGuides'].some(key=>s[key])));root.querySelectorAll('[data-media-toggle]').forEach(el=>{el.setAttribute(el.getAttribute('role')==='switch'?'aria-checked':'aria-pressed',String(s[el.dataset.mediaToggle]));el.classList.toggle('jig-changed',s[el.dataset.mediaToggle]!==defaults[el.dataset.mediaToggle]);});root.querySelectorAll('[data-media-selection]').forEach(el=>el.setAttribute('aria-pressed',String(s.comparisonSelection===el.dataset.mediaSelection)));
root.querySelector('#data-density-grid').innerHTML=Object.keys(DENSITIES).map(density=>{
 const c=resolveControlSurface(v.n,density,Number(s.controlGutter)),d=resolveDataRowGeometry(v.n,density,Number(s.controlGutter));
 const slot=text=>`<span class="data-cell-slot">${text}</span>`;
 const rows=[['Status','Ready'],['Details','Review the spacing and alignment of this multiline content.']];
 return `<article class="data-density-cell" ${density===s.density?'data-current="true"':''}><h3>${density[0].toUpperCase()+density.slice(1)}</h3><div class="canvas specimen" data-tier="${s.tier}" data-scale="${s.scale}" data-size="${s.size}" data-density="${density}" style="--surface-height:${c.height}px;--surface-inner:${c.innerHeight}px;--surface-margin:${c.margin}px;--surface-gap:${c.slotGap}px;--slot-padding:${c.slotPadding}px;--ui-font:${voices[s.voice]}"><table class="table__root"><caption>Table</caption><thead><tr><th scope="col">${slot('Field')}</th><th scope="col">${slot('Value')}</th></tr></thead><tbody>${rows.map(([label,value],i)=>`<tr data-row-kind="${i?'multiline':'single'}"><th scope="row">${slot(label)}</th><td>${slot(value)}</td></tr>`).join('')}</tbody></table><h4 class="data-list-heading">Data-list</h4><dl class="data-list__root">${rows.map(([label,value],i)=>`<div data-row-kind="${i?'multiline':'single'}"><dt>${slot(label)}</dt><dd>${slot(value)}</dd></div>`).join('')}</dl></div><dl class="primary-readout"><dt>Minimum H</dt><dd>${fmt(d.rowHeight)}px</dd><dt>Inner slot S</dt><dd>${fmt(d.slotHeight)}px</dd><dt>Clearance m</dt><dd>${fmt(d.clearance)}px</dd><dt>Cell padding P</dt><dd>${fmt(d.cellMargin)}px</dd><dt>Column gap E</dt><dd>${fmt(d.columnGap)}px</dd><dt>Table multiline</dt><dd data-measured-row="table"></dd><dt>Data-list multiline</dt><dd data-measured-row="list"></dd></dl></article>`;
}).join('');
paintFormulaSummaries(root,s);jig.sync(s);inspector.sync(s);scheduleRadii();

},bind({on,onAction,dispatch}){jig.bind(dispatch);inspector.bind(dispatch);onAction('media-setting',(e,el)=>dispatch({type:'media-toggle',key:el.dataset.mediaToggle}));onAction('media-selection',(e,el)=>dispatch({type:'media-selection',value:el.dataset.mediaSelection}));on('input','input[type=range]',(e,el)=>dispatch({type:'dial',key:el.id,value:el.value}));onAction('radius-preset',(e,el)=>dispatch({type:'preset',value:el.dataset.preset,family:el.dataset.family}));on('change','select',(e,el)=>dispatch({type:'axis',key:el.id,value:el.value}));onAction('nested-apply',()=>{const voice=radiusState.nestedVoice;dispatch({type:'voice',value:voice});dispatch({type:'nested-message',value:voice+' applied to the specimens.'});});onAction('nested-default',()=>{dispatch({type:'nested-voice',value:'Helvetica'});dispatch({type:'voice',value:'Helvetica'});dispatch({type:'nested-message',value:'Helvetica restored.'});});onAction('card-guide',(e,el)=>dispatch({type:'card-guide',key:el.dataset.key}));onAction('guides',()=>dispatch({type:'guides'}));onAction('reset',()=>dispatch({type:'reset'}));onAction('sample',(e,b)=>dispatch({type:'message',value:b.dataset.name+' button activated.'}));onAction('menu',(e,b)=>{if(b.dataset.command==='compact')dispatch({type:'axis',key:'density',value:'compact'});else dispatch({type:b.dataset.command});});
on('click','[role=option][data-voice]',(e,el)=>{dispatch({type:el.closest('#nested-listbox')?'nested-voice':'voice',value:el.dataset.voice});const target=el.id?document.getElementById(el.id):el;target?.focus();target?.parentElement?.querySelectorAll('[role=option]').forEach(x=>x.tabIndex=x===target?0:-1)});
on('keydown','[role=menuitem],[role=option][data-voice]',(e,el)=>{const nodes=[...el.parentElement.children];let i=nodes.indexOf(el);if(['ArrowDown','ArrowUp','Home','End'].includes(e.key)){e.preventDefault();i=e.key==='Home'?0:e.key==='End'?nodes.length-1:(i+(e.key==='ArrowDown'?1:-1)+nodes.length)%nodes.length;nodes.forEach((x,j)=>x.tabIndex=j===i?0:-1);nodes[i].focus()}else if(el.matches('[role=option]')&&['Enter',' '].includes(e.key)){e.preventDefault();dispatch({type:el.closest('#nested-listbox')?'nested-voice':'voice',value:el.dataset.voice})}});
}}});
