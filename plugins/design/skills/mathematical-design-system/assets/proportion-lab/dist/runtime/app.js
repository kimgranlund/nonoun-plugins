import {resolveControl,resolveLabelEdges,resolveChip,resolveBadge,resolveChoice,resolveComposite,resolveCollection,resolveCard,resolveMultiline,resolveComposedInput,resolveCurvature} from './geometry/index.js';

const defaults={unit:4,border:0,controlDensity:'default',collectionDensity:'default',cardDensity:'default',controlCurve:'soft',containerCurve:'soft',labelEdge:1.5,inset:0,theme:'light',rowState:'actual',guideMargins:false,guideGaps:false,guideSlots:false};
let state={...defaults},voice='Helvetica',appliedVoice='Helvetica',currency='USD';
const densities=['compact','default','loose'];
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const px=n=>`${Math.round(n*100)/100}px`;
const input=(density=state.controlDensity,curvature=state.controlCurve)=>({unit:state.unit,border:state.border,density,curvature,labelEdgeUnits:state.labelEdge});
const vars=g=>`--height:${g.height??0}px;--slot:${g.slot??6*state.unit}px;--pad:${g.padding??g.paddingBlock??0}px;--gap:${g.gap??0}px;--radius:${g.radius}px;--border:${g.border??g.child?.border??state.border}px;--font:${g.fontSize??2*state.unit+6}px;--line:${g.lineHeight??5*state.unit}px;--icon:${g.iconSizes?.sm??g.iconSize??4*state.unit}px;--cell-pad:${g.cellPaddingInline??0}px`;
const icon=(name='circle')=>`<i class="ph ph-${name}" aria-hidden="true"></i>`;
function slot(kind,g){
 if(!kind)return '';
 if(kind==='avatar')return `<span class="slot media avatar" style="border-radius:50%" aria-hidden="true"><svg viewBox="0 0 24 24"><rect width="24" height="24" fill="#d5af6b"/><circle cx="12" cy="8" r="4" fill="#242424"/><path d="M2 24a10 10 0 0 1 20 0" fill="#242424"/></svg></span>`;
 if(kind==='logo')return `<span class="slot media logo" style="border-radius:${px(Math.max(0,g.radius-g.inset))}" aria-hidden="true"><svg viewBox="0 0 24 24"><rect width="24" height="24" fill="#c52c22"/><path d="M0 0h8v16h16v8H0" fill="#242424"/></svg></span>`;
 return `<span class="slot ${kind}" style="border-radius:${px(Math.max(0,g.radius-g.inset))}" aria-hidden="true">${icon(kind==='glyph'?'caret-right':'circle')}</span>`;
}
function control(g,label,opts={}){
 const edges=resolveLabelEdges(g.labelEdge,!!opts.leading,!!opts.trailing,opts.doubleOpposite!==false);
 const tag=opts.tag||'button';
 return `<${tag} ${tag==='button'?'type="button"':''} class="df-control ${opts.chip?'df-chip':''} ${opts.outline?'outlined':'filled'} ${opts.className||''}" style="${vars(g)};--edge-start:${edges.start}px;--edge-end:${edges.end}px" ${opts.attrs||''}>${slot(opts.leading,g)}<span class="label">${esc(label)}</span>${slot(opts.trailing,g)}</${tag}>`;
}
const readout=entries=>`<dl class="readout">${entries.map(([k,v])=>`<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join('')}</dl>`;
const formula=(text,entries)=>`<details class="formula"><summary>Current formulas</summary><p>${esc(text)}</p>${readout(entries)}</details>`;
const set=(id,html)=>{if($(id))$(id).innerHTML=html;};
function buttons(){
 const g=resolveControl(input()),chip=resolveChip(input()),badge=resolveBadge(input()),choice=resolveChoice(input());
 const composed=resolveComposedInput(input()),a=composed.adornment;
 const adorn=(label,attrs='')=>control({...a,radius:a.radiusBlock},label,{chip:true,outline:true,trailing:attrs.includes('currency-trigger')?'glyph':null,attrs});
 set('buttons-content',`${formula('Control: slot = 6u; H = slot + 2 × inset. Padding = inset − border. Label edges are density-independent.',[['Slot',px(g.slot)],['Height',px(g.height)],['Inset',px(g.inset)],['Gap',px(g.gap)],['Label edge',px(g.labelEdge)]])}
 <div class="sample">${control(g,'Action',{leading:'icon',attrs:'data-action="action"'})}${control(g,'Continue',{trailing:'glyph',outline:true,attrs:'data-action="action"'})}${control(chip,'Filter',{chip:true,attrs:'data-action="filter"'})}<span class="df-badge" style="min-height:${px(badge.height)};padding-inline:${px(badge.paddingInline)};border:${px(badge.border)} solid transparent;border-radius:${px(badge.radius)};font-size:${px(badge.fontSize)}">New</span></div>
 <div class="sample choices" style="--choice-border:${px(choice.border)};--choice:${px(choice.artwork)};--checkbox-radius:${px(choice.checkboxRadius)};--switch-width:${px(choice.switchWidth)};--switch-height:${px(choice.switchHeight)}"><label><input type="checkbox"> Notifications</label><label><input type="radio" name="delivery" checked> Daily</label><label><input type="radio" name="delivery"> Weekly</label><label><input type="checkbox" role="switch"> Live preview</label></div>
 <h3>Composed inputs</h3><p class="note">Adornment chips retain their slots. The input grows around them; each action owns its focus indicator.</p>
 <div class="sample inputs">
 <div class="input-example"><label for="amount">Amount</label><div class="input-shell" style="${vars(composed)}"><span class="adornment">${adorn(currency,'id="currency-trigger" aria-haspopup="listbox" aria-expanded="false" aria-controls="currency-popup"')}</span><input class="df-input" id="amount" inputmode="decimal" value="125.00" style="margin-inline:0 ${px(g.labelEdge)}" aria-label="Amount"></div><div id="currency-popup" class="popup" hidden></div></div>
 <div class="input-example"><label for="search">Search</label><div class="input-shell" style="${vars(composed)}"><input class="df-input" id="search" type="text" value="Typography" style="margin-inline:${px(g.labelEdge)} 0"><span class="adornment">${adorn('Clear','data-action="clear"')}</span></div></div>
 <div class="input-example"><label for="quantity">Quantity</label><div class="input-shell" style="${vars(composed)}"><span class="adornment">${adorn('−','data-action="decrement" aria-label="Decrease quantity"')}</span><input class="df-input" id="quantity" type="number" value="2" min="0" max="20"><span class="adornment">${adorn('+','data-action="increment" aria-label="Increase quantity"')}</span></div></div>
 <div class="input-example"><label for="website">Website</label><div class="input-shell" style="${vars(composed)}"><span class="adornment">${control(a,'https://',{tag:'span',chip:true,outline:true})}</span><input class="df-input" id="website" value="example.com"><span class="adornment">${control(a,'.com',{tag:'span',chip:true,outline:true})}</span></div></div></div>
 ${readout([['Composed height',px(composed.height)],['Chip height',px(a.height)],['Chip radius inline / block',`${px(a.radiusInline)} / ${px(a.radiusBlock)}`]])}<p id="button-status" role="status"></p>`);
 document.querySelectorAll('#buttons-content .adornment .df-control').forEach(el=>el.style.borderRadius=`${a.radiusInline}px / ${a.radiusBlock}px`);
}
const arrangements=[['Label only','Action',null,null],['Icon + label','Action','icon',null],['Label + glyph','Action',null,'glyph'],['Avatar + label','Profile','avatar',null],['Label + logo','Studio',null,'logo']];
function densityButtons(){
 set('button-density-grid',densities.map(d=>{
 const g=resolveControl(input(d));
 return `<article class="density-column comparison-cell"><h3>${d}</h3><div class="specimen">${arrangements.map(([name,label,leading,trailing])=>{
 const edges=resolveLabelEdges(g.labelEdge,!!leading,!!trailing);
 return `<div class="arrangement"><p class="caption">${name}</p>${control(g,label,{leading,trailing})}<div class="shape-pair">${['sharpest','softest'].map(curve=>control(resolveControl(input(d,curve)),label,{leading,trailing,outline:true,attrs:`aria-label="${curve==='sharpest'?'Sharp':'Pill'} ${name}"`})).join('')}</div><p class="caption">Sharp / Pill · edge ${px(edges.start)} / ${px(edges.end)}</p></div>`;
 }).join('')}</div>${readout([['Height',px(g.height)],['Slot',px(g.slot)],['Margin',px(g.inset)],['Gap',px(g.gap)],['Radius',px(g.radius)]])}</article>`;
 }).join(''));
}
function listbox(density=state.controlDensity,id='voice-listbox',family='control'){
 const g=resolveComposite({...input(density),insetUnits:state.inset,childFamily:family});
 const labels=family==='chip'?['USD','EUR','GBP']:['Helvetica','Georgia','Monospace'];
 return `<div class="df-composite listbox" id="${id}" role="listbox" aria-label="${family==='chip'?'Currency':'Typeface'}" style="${vars(g)}">${labels.map((label,i)=>{
 const actual=label===(family==='chip'?currency:voice),selected=family==='chip'?actual:state.rowState==='all'||(state.rowState==='actual'&&actual);
 return control(g.child,label,{leading:family==='chip'?null:['icon','avatar','logo'][i],trailing:'glyph',outline:false,className:'listbox-option neutral',attrs:`role="option" aria-selected="${selected}" tabindex="${actual?0:-1}" data-voice="${family==='chip'?'':label}" data-currency="${family==='chip'?label:''}"`});
 }).join('')}</div>`;
}
function listboxes(){
 set('listbox-density-grid',densities.map(d=>{const g=resolveComposite({...input(d),insetUnits:state.inset});return `<article class="density-column comparison-cell"><h3>${d}</h3><div class="specimen">${listbox(d,`voice-${d}`)}</div>${readout([['Child height',px(g.child.height)],['Slot',px(g.child.slot)],['Composite inset',px(g.effectiveInset)],['Gap',px(g.gap)],['Parent / child radius',`${px(g.radius)} / ${px(g.child.radius)}`]])}</article>`;}).join(''));
 const g=resolveComposite({...input(),insetUnits:state.inset});
 set('menus-content',`${formula('Attached composite: effective inset = max(border, requested inset); gap = requested inset. Child inset = max(border, control inset − effective inset). Zero requested inset gives attached children zero curvature.',[['Parent radius',px(g.radius)],['Child radius',px(g.child.radius)],['Child height',px(g.child.height)]])}<div class="comparison-grid"><article><h3>Action menu</h3><div class="df-composite action-menu" role="menu" aria-label="Study actions" style="${vars(g)}">${[['guides','Toggle spacing guides'],['compact','Use compact density'],['restore','Restore defaults']].map(([action,label],i)=>control(g.child,label,{outline:false,className:'neutral',attrs:`role="menuitem" tabindex="${i?'-1':'0'}" data-action="${action}"`})).join('')}</div></article><article><h3>Single-selection listbox</h3>${listbox()}</article></div><p class="note">Arrow keys move; Home / End jump; Enter or Space chooses. Selection changes only the typeface specimen.</p>`);
}
function collection(d,type){
 const c=resolveCollection({...input(d,state.containerCurve)}),m=resolveMultiline({...input(d,state.containerCurve)});
 const style=`${vars({...c,slot:m.slot})};--row-gap:${px(c.rowSeparation)};--cell-pad:${px(c.cellPaddingInline)};--outer-pad:${px(c.outerCellPaddingInline)}`;
 if(type==='table')return `<table class="collection-table" style="${style}"><caption>Geometry values</caption><thead><tr><th scope="col">Token</th><th scope="col">Value</th></tr></thead><tbody>${[['Base unit',px(state.unit)],['Control slot',px(m.slot)],['Multiline row','Content grows naturally while keeping the full text and slot height.']].map(([label,value])=>`<tr><th scope="row"><span class="cell-slot type-body">${label}</span></th><td><span class="cell-slot type-body">${value}</span></td></tr>`).join('')}</tbody></table>`;
 return `<dl class="data-list" style="${style}">${[['Base unit',px(state.unit)],['Control slot',px(m.slot)],['Multiline content','Rows use collection density, with room for a longer description rather than a fixed-height crop.']].map(([label,value])=>`<div class="df-record"><dt><span class="cell-slot type-body">${label}</span></dt><dd><span class="cell-slot type-body">${value}</span></dd></div>`).join('')}</dl>`;
}
function data(){
 set('data-content',`${formula('Collection inset = 1u / 2u / 3u; cell padding = inset / 2 − border; outer cell padding = inset − border. Multiline minimum height = 6u + 2 × collection inset; content may grow.',[['Current collection density',state.collectionDensity],['Current minimum row',px(resolveMultiline(input(state.collectionDensity)).minHeight)]])}<h3>Current collection density</h3><div class="comparison-grid">${collection(state.collectionDensity,'table')}${collection(state.collectionDensity,'list')}</div><h3>Across three densities</h3><div class="comparison-grid">${densities.map(d=>`<article class="density-column"><h3>${d}</h3>${collection(d,'table')}${collection(d,'list')}${readout([['Minimum row',px(resolveMultiline(input(d)).minHeight)],['Cell padding',px(resolveCollection(input(d)).cellPaddingInline)],['Column gap',px(resolveCollection(input(d)).gap)]])}</article>`).join('')}</div>`);
}
function cards(){
 const g=resolveCard(input(state.cardDensity,state.containerCurve));
 set('container-grid',densities.map(d=>{const c=resolveCard(input(d,state.containerCurve));return `<article class="density-column"><h3>${d}</h3><div class="df-card" style="${vars(c)}"><h4 class="type-title">Container</h4><p class="type-body">Ordinary cards keep their own padding and curvature.</p>${control(resolveControl(input()),'Independent control',{outline:true})}</div>${readout([['Inset / gap',px(c.inset)],['Padding',px(c.padding)],['Radius',px(c.radius)]])}</article>`;}).join(''));
 set('nested-content',`<div class="df-card" style="${vars(g)}"><div><h3 class="type-title">Typography settings</h3><p class="type-body">Choose a voice for the specimens.</p></div>${listbox(state.controlDensity,'nested-listbox')}<div class="sample">${control(resolveControl(input()),'Apply voice',{attrs:'data-action="apply-voice"'})}${control(resolveControl(input()),'Use Helvetica',{outline:true,attrs:'data-action="default-voice"'})}</div><p class="type-caption" id="voice-status" role="status">Applied: ${esc(appliedVoice)}</p><p class="type-body" id="typeface-specimen" style="font-family:${appliedVoice==='Georgia'?'Georgia,serif':appliedVoice==='Monospace'?'monospace':'Helvetica,Arial,sans-serif'}">The quick brown fox jumps over the lazy dog.</p></div>${readout([['Card density',state.cardDensity],['Control density',state.controlDensity],['Card inset',px(g.inset)]])}`);
}
function roles(){
 set('density-comparison',`<table class="role-table"><thead><tr><th scope="col">Density</th><th scope="col">Page / card</th><th scope="col">Attached group</th><th scope="col">Collection</th><th scope="col">Control</th></tr></thead><tbody>${densities.map(d=>{const c=resolveCard(input(d,state.containerCurve)),co=resolveComposite({...input(d),insetUnits:state.inset}),r=resolveCollection(input(d,state.containerCurve)),g=resolveControl(input(d));return `<tr><th scope="row">${d}</th><td><div class="df-card" style="${vars(c)}"><h4 class="type-title">Content</h4><p class="type-body">A page brings related content together.</p></div>${readout([['Inset / gap',px(c.inset)]])}</td><td><div class="df-composite" style="${vars(co)}">${control(co.child,'One',{outline:true})}${control(co.child,'Two',{outline:true})}</div>${readout([['Inset',px(co.effectiveInset)],['Gap',px(co.gap)]])}</td><td>${collection(d,'list')}${readout([['Inset',px(r.inset)],['Gap',px(r.gap)]])}</td><td>${control(g,'Action',{leading:'icon'})}${readout([['Inset',px(g.inset)],['Gap',px(g.gap)]])}</td></tr>`;}).join('')}</tbody></table>`);
}
function radii(){
 set('radius-comparison',['sharpest','sharp','default','soft','softest'].map(curve=>{const g=resolveComposite({...input(state.controlDensity,curve),insetUnits:state.inset});return `<article class="comparison-cell"><h3>${curve}</h3><div class="df-composite" style="${vars(g)}">${control(g.child,'First',{outline:true})}${control(g.child,'Second',{outline:true})}</div>${readout([['Outer radius',px(g.radius)],['Child radius',px(g.child.radius)],['Inset',px(g.effectiveInset)]])}</article>`;}).join(''));
}
function validate(candidate){
 if(!['light','dark'].includes(candidate.theme)||!['none','all','actual'].includes(candidate.rowState))throw Error('Unknown theme or listbox appearance.');
 for(const d of [candidate.controlDensity,candidate.collectionDensity,candidate.cardDensity])resolveControl({unit:candidate.unit,border:candidate.border,density:d,curvature:candidate.controlCurve,labelEdgeUnits:candidate.labelEdge});
 resolveCard({unit:candidate.unit,border:candidate.border,density:candidate.cardDensity,curvature:candidate.containerCurve});
 resolveComposite({unit:candidate.unit,border:candidate.border,density:candidate.controlDensity,curvature:candidate.controlCurve,labelEdgeUnits:candidate.labelEdge,insetUnits:candidate.inset});
 for(const k of ['guideMargins','guideGaps','guideSlots'])if(typeof candidate[k]!=='boolean')throw Error('Guide values must be true or false.');
}
function announce(message){if($('status'))$('status').textContent=message;}
function render(){
 const currentFields=[...document.querySelectorAll('#buttons-content input')].map(el=>({value:el.value,checked:el.checked}));
 validate(state);document.documentElement.dataset.theme=state.theme;
 for(const [key,cl]of [['guideMargins','guide-margins'],['guideGaps','guide-gaps'],['guideSlots','guide-slots']])document.body.classList.toggle(cl,state[key]);
 buttons();densityButtons();listboxes();data();cards();roles();radii();
 document.querySelectorAll('#buttons-content input').forEach((el,i)=>{if(currentFields[i]){el.value=currentFields[i].value;el.checked=currentFields[i].checked;}});
 document.querySelectorAll('.df-control,.input-shell,.df-card,.df-composite,.df-record').forEach(el=>{const css=getComputedStyle(el);el.title=`Padding ${css.paddingTop} block / ${css.paddingLeft} inline; gap ${css.gap}; border ${css.borderTopWidth}; radius ${css.borderTopLeftRadius}`;});
 document.querySelectorAll('.slot,.label,.cell-slot').forEach(el=>{const r=el.getBoundingClientRect(),css=getComputedStyle(el);el.title=`Slot ${px(r.width)} × ${px(r.height)}; label edges ${css.marginInlineStart} / ${css.marginInlineEnd}`;});
 for(const [key,value]of Object.entries(state)){const el=$(key);if(el){if(el.type==='checkbox')el.checked=value;else el.value=value;const out=$(`${key}-value`);if(out)out.textContent=typeof value==='number'?String(value):value;}}
 if($('border'))$('border').max=state.unit/2;
 try{localStorage.setItem('proportion-differential-forms-v1',JSON.stringify(state));}catch{}
 announce(`Differential Forms · u ${state.unit}px · border ${state.border}px · independent family densities. Geometry valid.`);
}
for(const key of Object.keys(defaults))$(key)?.addEventListener('input',e=>{
 const next={...state,[key]:e.target.type==='checkbox'?e.target.checked:typeof defaults[key]==='number'?Number(e.target.value):e.target.value};
 if(key==='unit')next.border=Math.min(next.border,next.unit/2);
 try{validate(next);state=next;render();}catch(error){announce(error.message);}
});
$('reset')?.addEventListener('click',()=>{state={...defaults};render();});
$('copyConfig')?.addEventListener('click',async()=>{const text=JSON.stringify({version:1,...state},null,2);$('configuration').value=text;try{await navigator.clipboard.writeText(text);announce('Configuration copied.');}catch{announce('Configuration ready in the text field.');}});
$('applyConfig')?.addEventListener('click',()=>{try{const parsed=JSON.parse($('configuration').value);if(parsed.version!==1)throw Error('Expected configuration version 1.');const next={...defaults};for(const key of Object.keys(defaults))if(key in parsed)next[key]=parsed[key];validate(next);state=next;render();announce('Configuration applied.');}catch(error){announce(`Configuration not applied: ${error.message}`);}});
function currencyPopup(open){
 const popup=$('currency-popup'),trigger=$('currency-trigger');if(!popup)return;
 if(open){popup.innerHTML=listbox(state.controlDensity,'currency-options','chip');popup.hidden=false;trigger.setAttribute('aria-expanded','true');popup.querySelector('[tabindex="0"]').focus();}else{popup.hidden=true;trigger.setAttribute('aria-expanded','false');}
}
document.addEventListener('click',e=>{
 const button=e.target.closest('button');
 if(button?.id==='currency-trigger'){currencyPopup($('currency-popup').hidden);return;}
 if(button?.dataset.currency){currency=button.dataset.currency;currencyPopup(false);const label=$('currency-trigger').querySelector('.label');label.textContent=currency;$('currency-trigger').focus();return;}
 if(button?.dataset.voice){const groupId=button.closest('[role="listbox"]').id;voice=button.dataset.voice;listboxes();cards();$(groupId)?.querySelector(`[data-voice="${voice}"]`)?.focus();return;}
 const action=button?.dataset.action;
 if(action==='guides'){state.guideMargins=!state.guideMargins;state.guideGaps=state.guideMargins;state.guideSlots=state.guideMargins;render();}
 if(action==='compact'){state.controlDensity='compact';render();}
 if(action==='restore'){state={...defaults};render();}
 if(action==='apply-voice'||action==='default-voice'){if(action==='default-voice')voice='Helvetica';appliedVoice=voice;cards();document.querySelector(`[data-action="${action}"]`)?.focus();}
 if(action==='clear'){$('search').value='';$('search').focus();}
 if(action==='increment'||action==='decrement'){const el=$('quantity');action==='increment'?el.stepUp():el.stepDown();el.dispatchEvent(new Event('input',{bubbles:true}));}
 if(action==='action'||action==='filter')$('button-status').textContent=action==='filter'?'Filter toggled.':'Action completed.';
 if(!$('currency-popup')?.hidden&&!e.target.closest('.input-example'))currencyPopup(false);
});
document.addEventListener('keydown',e=>{
 const group=e.target.closest('[role="listbox"],[role="menu"]');
 if(e.key==='Escape'&&!$('currency-popup')?.hidden){currencyPopup(false);$('currency-trigger').focus();return;}
 if(e.key==='Tab'&&!$('currency-popup')?.hidden)currencyPopup(false);
 if(!group)return;const options=[...group.querySelectorAll('[role="option"],[role="menuitem"]')],index=options.indexOf(document.activeElement);let next=index;
 if(e.key==='ArrowDown')next=(index+1)%options.length;else if(e.key==='ArrowUp')next=(index-1+options.length)%options.length;else if(e.key==='Home')next=0;else if(e.key==='End')next=options.length-1;else return;
 e.preventDefault();options.forEach((el,i)=>el.tabIndex=i===next?0:-1);options[next].focus();
});
try{const saved=JSON.parse(localStorage.getItem('proportion-differential-forms-v1')||'null');if(saved){validate(saved);state={...defaults,...saved};}}catch{}
render();
window.proportionStudy={getState:()=>({...state}),render};
