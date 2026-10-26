const $=id=>document.getElementById(id);
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const setButtonLabel=(b,text)=>{let label=b.querySelector('[data-slot=label]');if(!label){label=el('span');label.dataset.slot='label';b.append(label);}label.textContent=text;};
const action=(text,fn)=>{const b=el('button');setButtonLabel(b,text);b.type='button';b.addEventListener('click',fn);return b;};
const escapeHTML=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const message=(text,error=false)=>{$('notice').textContent=text;$('notice').classList.toggle('error',error);$('notice').classList.toggle('sr-only',!error);};
const schemeKey='wireframe-review:color-scheme';
let colorScheme='system';
try{const saved=localStorage.getItem(schemeKey);if(['system','light','dark'].includes(saved))colorScheme=saved;}catch{}
function applyColorScheme(){
  const cssValue=colorScheme==='system'?'light dark':colorScheme;
  document.documentElement.style.colorScheme=cssValue;
  document.querySelectorAll('iframe').forEach(frame=>{if(frame.contentDocument?.documentElement)frame.contentDocument.documentElement.style.colorScheme=cssValue;});
  const title=colorScheme[0].toUpperCase()+colorScheme.slice(1),next={system:'Light',light:'Dark',dark:'System'}[colorScheme];
  $('color-scheme').dataset.scheme=colorScheme;$('color-scheme').setAttribute('aria-label',`Color scheme: ${title}. Switch to ${next}`);$('color-scheme').title=`Color scheme: ${title}. Switch to ${next}`;
}
$('color-scheme').onclick=()=>{colorScheme={system:'light',light:'dark',dark:'system'}[colorScheme];try{localStorage.setItem(schemeKey,colorScheme);}catch{}applyColorScheme();};
applyColorScheme();
const pages=MANIFEST.units.filter(u=>u.kind==='page');
let home=pages.length>0;
let pageId=pages[0]?.id || null, unitId=pageId || MANIFEST.units[0].id, preview='A', view='compare', viewport=MANIFEST.defaultViewport||'desktop', annotate=false;
let review=INITIAL_REVIEW ? clone(INITIAL_REVIEW) : newReview(MANIFEST), editing=null, observers=[];
const storageKey=`wireframe-review:1:${MANIFEST.projectId}:${MANIFEST.revision}`;
function save(){
  review.updatedAt=now();
  try{localStorage.setItem(storageKey,JSON.stringify(review));message('Saved in this browser. Download JSON for a portable backup.');}
  catch{message('Browser storage unavailable. Your review is held in this tab; download JSON before closing.',true);}
}
try{const saved=localStorage.getItem(storageKey);if(saved)review=validateReview(JSON.parse(saved),FEEDBACK_SCHEMA,MANIFEST);}
catch(e){message(`Saved review could not be loaded: ${e.message}. Import a valid backup or continue with this new review.`,true);}
$('project-title').textContent=MANIFEST.title;document.title=`${MANIFEST.title} · Wireframe review`;
$('revision').textContent=`${MANIFEST.projectId} / ${MANIFEST.revision} · Three proposals per decision`;
function options(select,items,value){select.replaceChildren(...items.map(([id,label])=>{const o=el('option',label);o.value=id;return o;}));select.value=value??'';}
function availableUnits(){
  if(!pageId)return MANIFEST.units;
  const page=findUnit(MANIFEST,pageId), ids=new Set([pageId,...page.variants.flatMap(v=>v.composition.map(p=>p.unitId))]);
  return MANIFEST.units.filter(u=>u.kind==='page'||ids.has(u.id));
}
options($('page'),pages.length ? [['','All pages'],...pages.map(p=>[p.id,p.title])] : [['','Standalone decisions']],pageId);
$('page').disabled=!pages.length;
$('viewport').value=viewport;
function select(unit,variantId){
  if(unit.kind!=='page' && pageId && $('apply-scope').value==='page'){
    review.pageOverrides[pageId] ||= {};review.pageOverrides[pageId][unit.id]=variantId;
  }else selectVariant(review,unit.id,variantId);
  save();render();
}
function chosenFor(unit){return unit.kind!=='page' && pageId && $('apply-scope').value==='page' ? review.pageOverrides[pageId]?.[unit.id] || null : review.choices[unit.id].selectedVariant;}
const currentUnitId=()=>view==='selection'&&pageId?pageId:unitId;
let renderRevision=0;
let userScrollRevision=0;
for(const event of ['wheel','touchstart','pointerdown','keydown'])window.addEventListener(event,()=>{userScrollRevision++;},{capture:true,passive:true});
function render(){
  prototypeUnmountAll();
  const revision=++renderRevision,intent=userScrollRevision,canvas=$('canvas');
  const position={x:window.scrollX,y:window.scrollY};
  const containers=[canvas,document.querySelector('.workspace > main'),$('review-panel'),...document.querySelectorAll('dialog')].map(node=>({node,x:node.scrollLeft,y:node.scrollTop}));
  const rows=new Map([...canvas.querySelectorAll('.page-alternatives')].map(row=>[row.dataset.page,row.scrollLeft]));
  const focusId=document.activeElement?.id,focusLabel=document.activeElement?.getAttribute('aria-label');
  canvas.style.minHeight=`${canvas.getBoundingClientRect().height}px`;
  const restore=()=>{
    containers.forEach(({node,x,y})=>node.scrollTo({left:x,top:y,behavior:'instant'}));
    canvas.querySelectorAll('.page-alternatives').forEach(row=>row.scrollTo({left:rows.get(row.dataset.page)||0,behavior:'instant'}));
    window.scrollTo({left:position.x,top:position.y,behavior:'instant'});
  };
  renderContent();
  const focusTarget=focusId?$(focusId):focusLabel?[...document.querySelectorAll('button[aria-label],select[aria-label]')].find(node=>node.getAttribute('aria-label')===focusLabel):null;
  focusTarget?.focus({preventScroll:true});restore();
  const frames=[...canvas.querySelectorAll('iframe')];
  Promise.all(frames.map(frame=>frame.dataset.ready==='true'?Promise.resolve():new Promise(resolve=>frame.addEventListener('load',resolve,{once:true})))).then(()=>requestAnimationFrame(()=>{
    if(revision!==renderRevision)return;
    canvas.style.minHeight='';
    if(intent===userScrollRevision)restore();
  }));
}
function renderContent(){
  const focused=document.activeElement,focusId=focused?.id,focusLabel=focused?.getAttribute('aria-label');
  for(const id of ['unit','view','preview','apply-scope'])$(id).closest('label').hidden=home;
  $('annotate').hidden=home;$('back-compare').hidden=home||view==='compare';
  $('page').value=home?'':pageId||'';
  document.querySelector('.toolbar').hidden=home;
  if(home){observers.forEach(o=>o.disconnect());observers=[];renderHome();renderCurrent();renderSelections();renderComments();applyPanelLayout();return;}

  observers.forEach(o=>o.disconnect());observers=[];
  if(!availableUnits().some(u=>u.id===unitId))unitId=pageId || MANIFEST.units[0].id;
  const unitPicker=$('unit'),available=availableUnits();unitPicker.replaceChildren();
  for(const [label,items] of [['Pages',available.filter(u=>u.kind==='page')],[pageId?'Sections on this page':'Sections and components',available.filter(u=>u.kind!=='page')]]){
    if(!items.length)continue;const group=el('optgroup');group.label=label;
    for(const u of items){const option=el('option',u.title);option.value=u.id;group.append(option);}unitPicker.append(group);
  }
  unitPicker.value=unitId;
  const unit=findUnit(MANIFEST,unitId);if(!unit.variants.some(v=>v.id===preview))preview=unit.variants[0].id;options($('preview'),unit.variants.map(v=>[v.id,v.id]),preview);options($('note-variant'),unit.variants.map(v=>[v.id,v.id]),preview);$('view').querySelector('[value=compare]').textContent=unit.variants.length===1?'Review proposal':'Compare '+unit.variants.map(v=>v.id).join(' / ');$('apply-scope').disabled=!pageId || unit.kind==='page';
  $('preview').disabled=view!=='inspect';$('reviewer').value=review.reviewer;$('summary').value=review.summary;
  $('unit-note-text').value=review.choices[currentUnitId()].note;
  const target=view==='selection' && pageId ? findUnit(MANIFEST,pageId) : unit;
  const selected=review.choices[target.id].selectedVariant;
  $('context').textContent=view==='selection' ? `Assembled choices for ${target.title}. ${selected ? `Page/unit proposal ${selected} selected.` : 'Proposal A is an unreviewed fallback.'} Global leaf choices and page overrides are applied; see the selection ledger.` : `Reviewing ${unit.title}. Previewing a proposal does not select it. ${annotate ? 'Click or keyboard-activate a marked element to annotate.' : 'Enable Annotate to leave element feedback.'}`;
  const canvas=$('canvas');canvas.replaceChildren();canvas.classList.toggle('single',view!=='compare'||unit.variants.length===1);
  const variants=view==='compare' ? unit.variants : [findVariant(target,view==='selection' ? selected || 'A' : preview)];
  for(const variant of variants){
    const card=el('article',undefined,'proposal'),head=el('header');head.append(el('h2',`${variant.id} · ${variant.title}`),el('p',variant.rationale),el('p',`Tradeoff: ${variant.tradeoff}`));
    const buttons=el('div',undefined,'actions');
    if(view!=='selection'){
      const pick=action(chosenFor(unit)===variant.id ? 'Selected' : `Choose ${variant.id}`,()=>select(unit,variant.id));pick.id=`choose-${unit.id}-${variant.id}`;pick.setAttribute('aria-pressed',String(chosenFor(unit)===variant.id));buttons.append(pick);
      const inspect=action('Inspect',()=>{preview=variant.id;view='inspect';$('view').value=view;$('preview').value=preview;render();});buttons.append(inspect);
      const {select:verdict,root:verdictControl}=createSelectControl();verdict.setAttribute('aria-label',`${unit.title} ${variant.id} global verdict`);
      options(verdict,['unreviewed','considered','selected','rejected'].map(s=>[s,s]),review.choices[unit.id].states[variant.id]);
      verdict.addEventListener('change',()=>{setVariantState(review,unit.id,variant.id,verdict.value);save();render();});buttons.append(verdictControl);
    }
    buttons.append(action('Comment on proposal',()=>openNote('unit',target.id,variant.id)));head.append(buttons);card.append(head);
    const parts=target.kind==='page' ? resolveParts(MANIFEST,review,target.id,variant.id,view==='selection') : [{unitId:target.id,variantId:variant.id}];
    makeFrame(card,parts,target.kind==='page' ? target.id : pageId);canvas.append(card);
  }
  renderSelections();renderComments();renderCurrent();applyPanelLayout();
  if(focusId)$(focusId)?.focus({preventScroll:true});else if(focusLabel)[...document.querySelectorAll('button[aria-label],select[aria-label]')].find(b=>b.getAttribute('aria-label')===focusLabel)?.focus({preventScroll:true});
}
function makeFrame(card,parts,contextPage,overview=false){
  const width=viewport==='mobile'?390:1200,wrap=el('div',undefined,'preview-wrap'),frame=el('iframe');frame.title=`Wireframe ${parts.map(p=>`${p.unitId} ${p.variantId}`).join(', ')} ${viewport}`;
  // Trusted parent controller callbacks need scripting enabled in WebKit.
  // Preview CSP still denies all authored scripts, handlers and external code.
  frame.setAttribute('sandbox',prototypeDefinitions.size?'allow-same-origin allow-scripts':'allow-same-origin');frame.style.width=`${width}px`;const well=el('div',undefined,'artifact-well');wrap.append(frame);well.append(wrap);card.append(well);
  let body=parts.map(p=>`<section data-unit-id="${p.unitId}" data-variant-id="${p.variantId}">${findVariant(findUnit(MANIFEST,p.unitId),p.variantId).html}</section>`).join('');
  if(parts.length>1&&body.includes('class="product-sidebar'))body=`<div class="product-layout">${body}</div>`;
  frame.addEventListener('load',()=>{
    const doc=frame.contentDocument;if(!doc)return;doc.querySelectorAll('.scenario-nav a[data-page-id],.marketing-header a[data-page-id],.product-sidebar a[data-page-id]').forEach(link=>{if(link.dataset.pageId===contextPage)link.setAttribute('aria-current','page');});doc.documentElement.style.colorScheme=colorScheme==='system'?'light dark':colorScheme;
    doc.body.classList.toggle('review-mode',annotate&&!overview);
    doc.querySelectorAll('.mh-destinations').forEach(menu=>{menu.open=viewport!=='mobile'&&!menu.closest('.mh-minimal');});
    const navSearch=doc.querySelector('.sidebar-search input');
    if(navSearch){
      const groups=[...doc.querySelectorAll('.sidebar-group')];const openStates=groups.map(g=>g.open);
      navSearch.addEventListener('input',()=>{const q=navSearch.value.trim().toLowerCase();let count=0;
        groups.forEach((group,i)=>{let matches=0;group.querySelectorAll('a').forEach(a=>{a.hidden=!!q&&!a.textContent.toLowerCase().includes(q);if(!a.hidden)matches++;});group.hidden=matches===0;group.open=q?matches>0:openStates[i];count+=matches;});
        doc.querySelector('.sidebar-no-results').hidden=count>0;
      });
      if(viewport==='mobile')doc.querySelector('.sidebar-destinations').open=false;
    }

    if(overview){
      const style=doc.createElement('style');style.textContent='[data-unit-id]{cursor:pointer}[data-unit-id]:hover,[data-unit-id]:focus-visible{outline:var(--m-focus-ring-width) solid var(--ui-focus);outline-offset:calc(-1 * var(--m-focus-ring-offset))}';doc.head.append(style);
      doc.querySelectorAll('[data-unit-id]').forEach(n=>{n.tabIndex=0;n.setAttribute('role','button');n.setAttribute('aria-label',`Review ${titleOf(n.dataset.unitId)} on ${titleOf(contextPage)}`);});
    }
    const resize=()=>{const logicalWidth=viewport==='mobile'?width:Math.max(width,wrap.clientWidth);frame.style.width=`${logicalWidth}px`;const scale=wrap.clientWidth/logicalWidth;const h=Math.max(160,doc.body.scrollHeight,doc.documentElement.scrollHeight);frame.style.height=`${h}px`;frame.style.transform=`scale(${scale})`;wrap.style.height=`${Math.ceil(h*scale)+wrap.offsetHeight-wrap.clientHeight}px`;};
    const onTarget=(event,keyboard=false)=>{
      const node=event.target.closest('[data-review-id]');
      if(overview || !annotate || !node)return;
      const parent=node.closest('[data-unit-id]');if(!parent)return;
      event.preventDefault();event.stopPropagation();
      const box=node.getBoundingClientRect();
      const position=keyboard?{x:.5,y:.5}:{x:Math.max(0,Math.min(1,(event.clientX-box.left)/Math.max(1,box.width))),y:Math.max(0,Math.min(1,(event.clientY-box.top)/Math.max(1,box.height)))};
      openComment({scope:'element',pageId:contextPage,unitId:parent.dataset.unitId,variantId:parent.dataset.variantId,elementId:node.dataset.reviewId,viewport,position},node.textContent.trim().slice(0,240));
    };
    doc.addEventListener('click',event=>{
      if(overview){event.preventDefault();const section=event.target.closest('[data-unit-id]');if(section)goToUnit(section.dataset.unitId,contextPage,section.dataset.variantId);else goToUnit(contextPage);return;}
      if(event.target.closest('.review-pin'))return;
      if(annotate){onTarget(event);event.preventDefault();return;}
      const nav=event.target.closest('[data-page-id]');
      if(nav){event.preventDefault();if(pages.some(p=>p.id===nav.dataset.pageId)){pageId=nav.dataset.pageId;unitId=pageId;$('page').value=pageId;render();}}
      const localLink=event.target.closest('a[href^="#"]:not([data-page-id])');
      if(localLink){const target=doc.getElementById(localLink.getAttribute('href').slice(1));if(target){event.preventDefault();userScrollRevision++;target.scrollIntoView({block:'start'});target.tabIndex=-1;target.focus({preventScroll:true});return;}}
      if(event.target.closest('button[type=button][popovertarget],button[type=button][commandfor]'))return;
      if(event.target.closest('a,button,input[type=file],input[type=submit],input[type=image],input[type=reset]'))event.preventDefault();
    });
    doc.addEventListener('submit',event=>event.preventDefault());
    doc.addEventListener('keydown',event=>{if(overview&&['Enter',' '].includes(event.key)){const section=event.target.closest('[data-unit-id]');if(section){event.preventDefault();goToUnit(section.dataset.unitId,contextPage,section.dataset.variantId);}return;}if(annotate && ['Enter',' '].includes(event.key))onTarget(event,true);});
    if(annotate&&!overview)doc.querySelectorAll('[data-review-id]').forEach(n=>{n.tabIndex=0;n.setAttribute('aria-label',`Annotate ${n.dataset.reviewId}`);});
    if(!overview)review.comments.forEach((c,i)=>{
      const t=c.target;if(t.scope!=='element' || ![viewport,'all'].includes(t.viewport) || (t.pageId && t.pageId!==contextPage))return;
      const node=[...doc.querySelectorAll('[data-review-id]')].find(n=>n.dataset.reviewId===t.elementId && n.closest('[data-unit-id]')?.dataset.unitId===t.unitId && n.closest('[data-variant-id]')?.dataset.variantId===t.variantId);
      if(!node)return;const rect=node.getBoundingClientRect(),pin=doc.createElement('button');pin.className='review-pin';pin.dataset.tier='product';pin.dataset.scale='md';pin.dataset.size='sm';pin.dataset.radius='pill';pin.type='button';pin.textContent=String(i+1);pin.setAttribute('aria-label',`Edit feedback ${i+1}: ${c.text}`);pin.title=c.text;
      pin.style.left=`${rect.left+(t.position?.x??.9)*rect.width-12}px`;pin.style.top=`${Math.max(0,rect.top+(t.position?.y??.1)*rect.height-12)}px`;
      pin.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();editComment(c.id);});doc.body.append(pin);
    });
    const observer=new ResizeObserver(resize);observer.observe(wrap);observer.observe(doc.body);observers.push(observer);resize();prototypeMount(doc,overview||annotate);frame.dataset.ready='true';
  });
  frame.srcdoc=`<!doctype html><html lang="${MANIFEST.language||'en'}" data-tier="product" data-scale="md" data-size="md" data-radius="round"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'none'; style-src 'unsafe-inline'; img-src data:; font-src data:; form-action 'none'; base-uri 'none'"><style>${WIREFRAME_CSS}\n${MANIFEST.css}</style></head><body>${body}</body></html>`;
}
const stateSymbols={unreviewed:'○',considered:'◐',selected:'✓',rejected:'×'};
function badge(text){return el('span',text,'badge');}
function titleOf(id){return MANIFEST.units.find(u=>u.id===id)?.title || '';}
function goToUnit(id,p=null,variant=null){
  home=false;panelTab='current';$('note-scope').value='decision';
  const u=findUnit(MANIFEST,id);
  pageId=u.kind==='page'?id:p || pages.find(page=>page.variants.some(v=>v.composition.some(part=>part.unitId===id)))?.id || null;
  unitId=id;$('page').value=pageId||'';if(variant){preview=variant;view='inspect';}else view='compare';
  $('view').value=view;$('preview').value=preview;render();
}
function effectiveChoice(u){
  const global=review.choices[u.id].selectedVariant,override=pageId&&review.pageOverrides[pageId]?.[u.id];
  const part=pageId&&resolveParts(MANIFEST,review,pageId,null).find(p=>p.unitId===u.id);
  return {value:override||global||part?.variantId||'A',source:override?'This page':global?'Across pages':'Proposal default',explicit:!!(override||global),active:u.kind==='page'||!pageId||!!part};
}
function renderHome(){
  $('context').textContent='All pages · Compare A, B and C in each row. Choose explicitly to record a preference.';
  const canvas=$('canvas'),scrolls=new Map([...canvas.querySelectorAll('.page-alternatives')].map(row=>[row.dataset.page,row.scrollLeft]));
  canvas.replaceChildren();canvas.classList.remove('single');canvas.classList.add('home-canvas');
  $('reviewer').value=review.reviewer;$('summary').value=review.summary;
  for(const page of pages){
    const row=el('section',undefined,'page-map'),identity=el('header',undefined,'page-card-identity'),selected=review.choices[page.id].selectedVariant;
    const open=action(page.title,()=>goToUnit(page.id));open.className='page-title';identity.append(open,badge(selected?`Choice · ${selected}`:'No choice yet'));row.append(identity);
    row.setAttribute('aria-label',`${page.title} alternatives`);
    const alternatives=el('div',undefined,'page-alternatives');alternatives.dataset.page=page.id;
    for(const variant of page.variants){
      const card=el('article',undefined,'proposal home-proposal'),head=el('header');card.dataset.variant=variant.id;card.dataset.selected=String(selected===variant.id);
      head.append(el('h2',`${variant.id} · ${variant.title}`));
      const tools=el('div',undefined,'actions'),choose=action(selected===variant.id?`${variant.id} chosen`:`Choose ${variant.id}`,()=>{selectVariant(review,page.id,variant.id);save();render();$(choose.id)?.focus({preventScroll:true});});
      choose.id=`home-choose-${page.id}-${variant.id}`;choose.setAttribute('aria-label',`Choose ${page.title} proposal ${variant.id}`);choose.setAttribute('aria-pressed',String(selected===variant.id));
      const inspect=action('Inspect',()=>goToUnit(page.id,page.id,variant.id));inspect.setAttribute('aria-label',`Inspect ${page.title} proposal ${variant.id}`);tools.append(choose,inspect);head.append(tools);
      const description=el('dl',undefined,'proposal-description');description.append(el('dt','Approach'),el('dd',variant.rationale),el('dt','Tradeoff'),el('dd',variant.tradeoff));head.append(description);
      const parts=resolveParts(MANIFEST,review,page.id,variant.id,false);
      const {select:picker,root:pickerControl}=createSelectControl();picker.className='sections-picker';picker.setAttribute('aria-label',`Review section on ${page.title} proposal ${variant.id}`);options(picker,[['','Sections'],...parts.map((part,index)=>[String(index),titleOf(part.unitId)])],'');picker.addEventListener('change',()=>{if(picker.value==='')return;const part=parts[Number(picker.value)];goToUnit(part.unitId,page.id,part.variantId);});tools.append(pickerControl);
      card.append(head);makeFrame(card,parts,page.id,true);alternatives.append(card);
    }
    row.append(alternatives);canvas.append(row);alternatives.scrollLeft=scrolls.get(page.id)||0;
  }
}
function renderIntent(){
  const body=$('intent-content');body.replaceChildren();
  const unit=home?null:findUnit(MANIFEST,currentUnitId());
  const levels=[['Whole experience',MANIFEST.intent],...(!home&&pageId&&pageId!==unit?.id?[[titleOf(pageId),findUnit(MANIFEST,pageId)?.intent]]:[]),...(unit?[[unit.title,unit.intent]]:[])].filter(([,intent])=>intent);
  $('intent-context').hidden=!levels.length;
  for(const [title,intent] of levels){const section=el('section');section.append(el('h4',title));const list=el('dl');for(const [key,label] of Object.entries({outcome:'Intended progress',means:'Available support',constraints:'Constraints',uncertainty:'Open questions',evidence:'Evidence to look for'})){if(intent[key])list.append(el('dt',label),el('dd',intent[key]));}section.append(list);body.append(section);}
}
function renderCurrent(){
  renderIntent();
  $('note-scope').querySelector('[value=decision]').disabled=home;
  $('canvas').classList.toggle('home-canvas',home);
  $('review-panel').dataset.scope=home?'global':'context';
  $('unit-note-text').closest('label').hidden=home;
  $('unit-note-text').closest('label').nextElementSibling.hidden=home;
  (home?$('global-summary'):$('handoff-summary')).append($('summary-field'));
  $('note-scope').querySelector('[value=unit]').disabled=home;
  $('note-scope').querySelector('[value=page]').disabled=home||!pageId;
  if(home)$('note-scope').value='site';
  $('note-variant-label').hidden=home||$('note-scope').value!=='unit';
  $('filter').querySelector('[value=current]').textContent=home?'Whole artifact':'Current decision';
  $('filter').querySelector('[value=page]').disabled=home;
  if(home&&$('filter').value==='page')$('filter').value='current';
  setButtonLabel(document.querySelector('[data-panel-section=current] .section-toggle'),home?'Global review':'Current decision');
  $('open-count').textContent=`${review.comments.filter(c=>c.status==='open').length} open`;
  if(home){
    $('current-context').replaceChildren(el('small','GLOBAL','eyebrow'),el('h3',MANIFEST.title));
    const stats=el('div',undefined,'context-chips');stats.append(badge(`${pages.length} pages`),badge(`${MANIFEST.units.length} decisions`));$('current-context').append(stats);$('current-choice').hidden=true;return;
  }
  $('current-choice').hidden=false;
  const u=findUnit(MANIFEST,currentUnitId()),effective=effectiveChoice(u),context=$('current-context');context.replaceChildren();
  context.append(el('small',pageId&&pageId!==unitId?titleOf(pageId):u.kind==='page'?'Page':'Decision','eyebrow'),el('h3',u.title));
  const line=el('div',undefined,'context-chips');line.append(badge(view==='compare'?(u.variants.length===1?'Reviewing one proposal':'Comparing '+u.variants.map(v=>v.id).join(' / ')):view==='selection'?'Assembled page':`Preview ${preview}`),badge(viewport==='mobile'?'Mobile':'Desktop'));context.append(line);
  const box=$('current-choice');box.replaceChildren();const status=el('div',undefined,'effective-choice');status.append(el('strong',effective.value,'variant-token'),el('div',effective.explicit?'Chosen proposal':'Preview fallback'),badge(effective.source));box.append(status);
  if(!effective.active)box.append(el('p','Not used in the selected page composition.','hint'));
  const controls=el('div',undefined,'segments');controls.setAttribute('aria-label',`Choose ${u.title}`);
  for(const {id} of u.variants){const b=action(id,()=>select(u,id));b.setAttribute('aria-label',`Choose ${u.title} proposal ${id}`);b.setAttribute('aria-pressed',String(chosenFor(u)===id));controls.append(b);}box.append(controls);
  box.append(el('p',u.kind==='page'||$('apply-scope').value==='global'?'Changes apply across pages.':`Changes apply only to ${titleOf(pageId)}.`,'field-help'));
  const option=$('note-scope').querySelector('[value=page]');option.disabled=!pageId;
  if(!pageId&&$('note-scope').value==='page')$('note-scope').value='decision';
  $('note-variant').value=preview;
  $('open-count').textContent=`${review.comments.filter(c=>c.status==='open').length} open`;
}
function renderSelections(){
  const list=$('selections');list.replaceChildren();const query=$('decision-search').value.toLowerCase();
  const chosen=MANIFEST.units.filter(u=>review.choices[u.id].selectedVariant).length;
  setButtonLabel($('open-decisions'),`Decisions · ${chosen}/${MANIFEST.units.length}`);
  $('decision-progress').textContent=`${chosen} of ${MANIFEST.units.length} chosen`;$('review-progress').max=MANIFEST.units.length;$('review-progress').value=chosen;
  for(const unit of MANIFEST.units.filter(u=>u.title.toLowerCase().includes(query))){
    const c=review.choices[unit.id],row=el('article',undefined,'decision-row');row.dataset.unit=unit.id;
    const heading=el('div',undefined,'decision-heading'),jump=action(unit.title,()=>goToUnit(unit.id));jump.className='text-action';jump.title=unit.title;heading.append(jump);
    if(c.selectedVariant){const clear=action('Clear',()=>{selectVariant(review,unit.id,null);save();render();});clear.dataset.appearance='ghost';clear.setAttribute('aria-label',`Clear ${unit.title} choice`);heading.append(clear);}row.append(heading);
    const choices=el('div',undefined,'segments variant-states');
    for(const {id} of unit.variants){const state=c.states[id],b=action(`${stateSymbols[state]}  ${id}`,()=>{selectVariant(review,unit.id,id);save();render();});b.id=`decision-${unit.id}-${id}`;b.dataset.state=state;b.setAttribute('aria-label',`${unit.title} proposal ${id}: ${state}. Choose across pages`);b.setAttribute('aria-pressed',String(c.selectedVariant===id));choices.append(b);}row.append(choices);
    for(const [p,overrides] of Object.entries(review.pageOverrides))if(overrides[unit.id]){
      const active=resolveParts(MANIFEST,review,p,null).some(part=>part.unitId===unit.id),local=el('div',undefined,'override-row');local.append(badge(overrides[unit.id]),el('span',titleOf(p)),badge(active?'Page choice':'Inactive'));
      const remove=action('Remove',()=>{delete review.pageOverrides[p][unit.id];save();render();});remove.dataset.appearance='ghost';remove.setAttribute('aria-label',`Remove ${titleOf(p)} override for ${unit.title}`);local.append(remove);row.append(local);
    }list.append(row);
  }
  if(!list.children.length)list.append(el('p','No decisions match your search.','empty-state'));
}
function commentTarget(t){return [t.scope==='site'?'Whole artifact':titleOf(t.pageId),titleOf(t.unitId),t.variantId?`Proposal ${t.variantId}`:'',t.elementId?t.elementId.replace(/[-_]/g,' '):''].filter((x,i,a)=>x&&a.indexOf(x)===i).join(' / ');}
function locateComment(c){
  const t=c.target;if(t.scope==='site'){setPanelTab('handoff');$('summary').focus();return;}
  if(t.viewport!=='all'){viewport=t.viewport;$('viewport').value=viewport;}
  goToUnit(t.unitId||t.pageId,t.pageId,t.variantId);
  const frame=$('canvas').querySelector('iframe');
  frame?.addEventListener('load',()=>{const node=[...frame.contentDocument.querySelectorAll('[data-review-id]')].find(n=>n.dataset.reviewId===t.elementId);if(node){node.tabIndex=-1;node.focus();node.style.outline='var(--m-focus-ring-width) solid var(--ui-focus)';}else frame.focus();},{once:true});
  userScrollRevision++;$('canvas').scrollIntoView({block:'start'});
}
function renderComments(){
  const filter=$('filter').value,list=$('comments');list.replaceChildren();
  const comments=review.comments.filter(c=>filter==='open'?c.status==='open':filter==='page'?c.target.pageId===pageId:filter==='current'?home||c.target.unitId===currentUnitId()||(findUnit(MANIFEST,currentUnitId()).kind==='page'&&c.target.pageId===currentUnitId()):true);
  $('comment-count').textContent=`${comments.length} / ${review.comments.length}`;
  comments.forEach(c=>{
    const card=el('article',undefined,`comment ${c.status}`),meta=el('div',undefined,'context-chips');meta.append(badge(c.status==='resolved'?'✓ Resolved':'○ Open'),badge(c.priority==='must-change'?'Must change':'Suggestion'));card.append(meta,el('h4',commentTarget(c.target)),el('p',c.text));
    if(c.response)card.append(el('p',c.response.message,'response-note'));
    const actions=el('div',undefined,'actions');actions.append(action('Edit',()=>editComment(c.id)),action('Locate',()=>locateComment(c)));card.append(actions);list.append(card);
  });
  if(!comments.length){const empty=el('div',undefined,'empty-state');empty.append(el('strong',review.comments.length?'No matching comments':'No feedback yet'),el('p',review.comments.length?'Other comments remain in your review.':'Add a scoped note or annotate an element in the preview.'));if(review.comments.length)empty.append(action('View all comments',()=>{$('filter').value='all';renderComments();}));list.append(empty);}
}
let panelTab='current';
function setPanelTab(tab){panelTab=tab;applyPanelLayout();$('review-panel').scrollTop=0;}
function applyPanelLayout(){
  $('review-panel').dataset.layout='tabs';
  document.querySelectorAll('[data-panel-section]').forEach(section=>{
    const overview=section.dataset.panelSection==='overview';
    section.hidden=overview?panelTab!=='overview':panelTab==='overview';
    section.querySelector('.section-toggle').hidden=true;
    section.querySelector('.section-body').hidden=false;
  });
  document.querySelectorAll('[data-panel-tab]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.panelTab===panelTab)));
}
const noteDrafts=new Map();
const draftKey=t=>JSON.stringify(t);
function openNote(scope,u=null,v=null){
  openComment({scope,pageId:scope==='site'?null:pageId,unitId:['unit','decision'].includes(scope)?(u||currentUnitId()):null,variantId:scope==='unit'?(v||preview):null,elementId:null,viewport:'all',position:null},'');
}
function openComment(target,quote){
  if(noteDrafts.has(draftKey(target))){editing=clone(noteDrafts.get(draftKey(target)));showEditor(false);return;}
  editing={id:`comment-${globalThis.crypto?.randomUUID?.() || Date.now().toString(36)+'-'+Math.random().toString(36).slice(2)}`,revision:MANIFEST.revision,target,quote,category:'other',priority:'suggestion',text:'',status:'open',createdAt:now(),updatedAt:now(),response:null,migration:null};showEditor(false);
}
function editComment(id){const saved=review.comments.find(c=>c.id===id);editing=clone(noteDrafts.get(draftKey(saved.target))?.id===id?noteDrafts.get(draftKey(saved.target)):saved);showEditor(true);}
function showEditor(existing){
  $('comment-heading').textContent=existing?'Edit feedback':'Add feedback';$('comment-target').textContent=commentTarget(editing.target);
  $('comment-quote').textContent=editing.quote;$('comment-text').value=editing.text;$('category').value=editing.category;$('priority').value=editing.priority;$('status').value=editing.status;
  $('response').textContent=editing.response?`${editing.response.disposition}: ${editing.response.message}`:'';$('delete-comment').hidden=!existing;$('comment-dialog').showModal();$('comment-text').focus();
}
$('comment-form').addEventListener('submit',event=>{
  event.preventDefault();const text=$('comment-text').value.trim();if(!text)return;
  Object.assign(editing,{text,category:$('category').value,priority:$('priority').value,status:$('status').value,updatedAt:now()});
  const candidate=clone(review),index=candidate.comments.findIndex(c=>c.id===editing.id);if(index<0)candidate.comments.push(editing);else candidate.comments[index]=editing;
  try{validateReview(candidate,FEEDBACK_SCHEMA,MANIFEST);review=candidate;noteDrafts.delete(draftKey(editing.target));save();$('comment-dialog').close();render();}catch(e){message(e.message,true);}
});
function retainDraft(){if(editing){Object.assign(editing,{text:$('comment-text').value,category:$('category').value,priority:$('priority').value,status:$('status').value});noteDrafts.set(draftKey(editing.target),clone(editing));message('Draft kept in this tab. Reopen the same note to continue; save it before closing the tab.');}}
$('cancel-comment').onclick=()=>{retainDraft();$('comment-dialog').close();};
$('comment-dialog').addEventListener('cancel',retainDraft);
$('delete-comment').onclick=()=>{if(confirm('Delete this comment?')){review.comments=review.comments.filter(c=>c.id!==editing.id);save();$('comment-dialog').close();render();}};
function exportJSON(){review.schemaVersion='1.1';review.context=reviewContext(MANIFEST);validateReview(review,FEEDBACK_SCHEMA,MANIFEST);return JSON.stringify(review,null,2);}


$('copy').onclick=async()=>{$('feedback-dialog').close();try{const json=exportJSON();try{await navigator.clipboard.writeText(json);message('Feedback JSON copied. Paste it into your agent chat.');}catch{$('json-text').value=json;$('json-dialog').showModal();$('json-text').focus();$('json-text').select();}}catch(e){message(e.message,true);}};
$('download').onclick=()=>{$('feedback-dialog').close();try{const url=URL.createObjectURL(new Blob([exportJSON()],{type:'application/json'}));const a=el('a');a.href=url;a.download=`${MANIFEST.projectId}-${MANIFEST.revision.replace(/[^a-z0-9-]/gi,'-')}-feedback.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);message('Feedback JSON download started. Keep it with this revision.');}catch(e){message(e.message,true);}};
$('import').onclick=()=>{$('feedback-dialog').close();$('import-file').click();};
$('import-file').onchange=async event=>{
  const file=event.target.files[0];event.target.value='';if(!file)return;
  try{if(file.size>5*1024*1024)throw new Error('Review exceeds the 5 MB import limit. Split it with your agent.');const incoming=validateReview(JSON.parse(await file.text()),FEEDBACK_SCHEMA,MANIFEST);
    if(!confirm('Replace the current review with this JSON? Download your current review first if you need both.'))return;
    review=clone(incoming);save();render();message('Imported validated review.');
  }catch(e){message(`Import refused: ${e.message}`,true);}
};

$('page').onchange=()=>{panelTab='current';$('note-scope').value='decision';home=!$('page').value&&pages.length>0;pageId=$('page').value||null;unitId=pageId||MANIFEST.units[0].id;render();};
$('unit').onchange=()=>{unitId=$('unit').value;if(findUnit(MANIFEST,unitId).kind==='page'){pageId=unitId;home=false;panelTab='current';}if(view==='selection'){view='inspect';$('view').value=view;}render();};
$('back-compare').onclick=()=>{view='compare';$('view').value=view;render();$('canvas').querySelector('button')?.focus({preventScroll:true});};
$('view').onchange=()=>{view=$('view').value;render();};$('preview').onchange=()=>{preview=$('preview').value;render();};
$('viewport').onchange=()=>{viewport=$('viewport').value;render();};$('apply-scope').onchange=render;
$('annotate').onclick=()=>{annotate=!annotate;setButtonLabel($('annotate'),`Annotate: ${annotate?'on':'off'}`);$('annotate').setAttribute('aria-pressed',String(annotate));render();};
$('reviewer').oninput=()=>{review.reviewer=$('reviewer').value;save();};$('summary').oninput=()=>{review.summary=$('summary').value;save();};
$('unit-note-text').oninput=()=>{review.choices[currentUnitId()].note=$('unit-note-text').value;save();};
$('note-scope').onchange=()=>{$('note-variant-label').hidden=$('note-scope').value!=='unit';};
$('missing-approach').onclick=()=>openNote(home?'site':'decision');
$('add-note').onclick=()=>{
  const scope=$('note-scope').value;
  if(scope==='unit')openNote('unit',currentUnitId(),$('note-variant').value);else openNote(scope);
};
$('open-decisions').onclick=()=>{setPanelTab('overview');$('decision-search').focus({preventScroll:true});$('review-panel').scrollIntoView({block:'nearest'});};

$('decision-search').oninput=renderSelections;
$('handoff-copy').onclick=()=>$('copy').click();$('handoff-download').onclick=()=>$('download').click();
document.querySelectorAll('[data-panel-tab]').forEach(b=>b.onclick=()=>setPanelTab(b.dataset.panelTab));
document.querySelectorAll('.section-toggle').forEach(b=>b.onclick=()=>{const open=b.getAttribute('aria-expanded')!=='true';b.setAttribute('aria-expanded',String(open));b.querySelector('.disclosure-mark').textContent=open?'−':'+';applyPanelLayout();});
$('filter').onchange=renderComments;
render();

