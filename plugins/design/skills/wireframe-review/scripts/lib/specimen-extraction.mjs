// Build-time DOM extraction. No source contract or state is invented here.
export function extractSpecimens(document, registry, contract) {
 if(registry?.version!==1||contract?.version!==1)throw Error('Unsupported specimen/contract version');
 if(registry.source!=='assets/recipes/components.html')throw Error('Unsupported specimen source');
 const families=contract.families;
 if(!Array.isArray(families)||new Set(families.map(f=>f.id)).size!==families.length)throw Error('Duplicate or absent family IDs');
 const keys=Object.keys(registry.specimens||{});
 if(keys.length!==families.length||keys.some(id=>!families.some(f=>f.id===id)))throw Error('Specimen registry must match family IDs');
 const sections=[...document.querySelectorAll('#catalog > section')],focused={},coverage={},fingerprints=new Map();
 const splitSelectors=text=>{
  if(typeof text!=='string'||!text.trim())throw Error('Missing required selector');
  let depth=0,quote='',part='',out=[];
  for(const ch of text){if(quote){part+=ch;if(ch===quote)quote='';continue;}if(ch==='"'||ch==="'"){quote=ch;part+=ch;continue;}if(ch==='('||ch==='[')depth++;if(ch===')'||ch===']')depth--;if(depth<0)throw Error('Invalid selector');if(ch===','&&depth===0){out.push(part.trim());part='';}else part+=ch;}
  out.push(part.trim());if(depth||quote||out.some(x=>!x))throw Error('Invalid selector list');return out;
 };
 for(const [id,spec] of Object.entries(registry.specimens)){
  if(spec.native){if(!['disclosure','overlay'].includes(spec.native)||spec.native!==id)throw Error('Unsupported native specimen');continue;}
  if(!Number.isInteger(spec.section)||spec.section<0)throw Error('Invalid section index: '+id);
  const section=sections[spec.section];if(!section)throw Error('Missing specimen section: '+id);
  const selected=new Set();
  for(const selector of splitSelectors(spec.children)){
   const direct=selector.startsWith(':scope > ')?selector:':scope > '+selector;
   const matches=[...section.querySelectorAll(direct)];if(!matches.length)throw Error('Missing required selector: '+id+' '+selector);
   for(const e of matches)if(e.parentElement!==section)throw Error('Specimen selector must select direct source children');else selected.add(e);
  }
  if(!selected.size)throw Error('Empty specimen: '+id);
  const fingerprint=[...selected].map(e=>e.outerHTML).join('');
  if(fingerprints.has(fingerprint))throw Error('Identical specimens for unrelated families: '+fingerprints.get(fingerprint)+' '+id);fingerprints.set(fingerprint,id);
  const target=section.cloneNode(false);target.removeAttribute('aria-labelledby');
  const heading=document.createElement('h2');heading.textContent=id;target.append(heading);
  for(const child of section.children)if(selected.has(child))target.append(child.cloneNode(true));
  for(const selector of spec.dependencies||[]){const matches=document.querySelectorAll(selector);if(matches.length!==1)throw Error('Missing/ambiguous specimen dependency: '+selector);if(!spec.note)throw Error('Unlabelled cross-component dependency: '+id);const e=matches[0];target.append((e.closest('label')||e).cloneNode(true));}
  if(!Array.isArray(spec.members)||!spec.members.length)throw Error('Missing member metadata: '+id);
  if(new Set(spec.members.map(m=>m.id)).size!==spec.members.length)throw Error('Duplicate member ID: '+id);
  const family=families.find(f=>f.id===id), groups=new Map();coverage[id]=[];
  for(const m of spec.members){
   if(!m.id||!m.name||!Array.isArray(m.classes))throw Error('Invalid member metadata: '+id);
   const matches=[...target.querySelectorAll(m.selector)];if(!matches.length)throw Error('Missing member selector: '+id+' '+m.id);
   const declared=Object.fromEntries(m.classes.map(c=>[c,family.stateApplicability?.classes?.[c]??null]));
   coverage[id].push({id:m.id,name:m.name,selector:m.selector,matches:matches.length,declaredStates:declared,demonstrated:'Source elements present; state-specific demonstration not established by extraction',tested:'unverified',unverifiedStates:declared});
   let top=matches[0];while(top.parentElement!==target)top=top.parentElement;
   const names=groups.get(top)||[];names.push(m.name);groups.set(top,names);
  }
  for(const [top,names] of groups){const h=document.createElement('h3');h.textContent=names.join(' · ');h.dataset.specimenMembers=names.join('|');top.before(h);}
  const wrapper=document.createElement('main');wrapper.id='catalog';wrapper.className='product__root flow__root';wrapper.append(target);
  const ids=[...wrapper.querySelectorAll('[id]')].map(e=>e.id);if(new Set(ids).size!==ids.length)throw Error('Duplicate specimen DOM ID: '+id);
  focused[id]=wrapper.outerHTML;
 }
 return {focused,coverage};
}

export function extractNativeSpecimens(document, registry, contract) {
 if(registry?.version!==1||contract?.version!==1)throw Error('Unsupported native specimen/contract version');
 const required=selector=>{const elements=document.querySelectorAll(selector);if(elements.length!==1)throw Error('Missing/ambiguous native source selector: '+selector);return elements[0];};
 const navigation=required('[data-native-navigation]');
 const menu=[required('style').outerHTML,navigation.outerHTML,required('#native-overview').outerHTML,required('#native-preferences').outerHTML].join('');
 const fragments={menu},coverage={};
 for(const id of ['disclosure','overlay']){
  const spec=registry.specimens[id];if(spec?.native!==id)throw Error('Missing native registry owner: '+id);
  const section=required(id==='overlay'?'[data-native-dialog]':'[data-native-accordion]').cloneNode(true);
  if(!Array.isArray(spec.members)||!spec.members.length)throw Error('Missing native member metadata: '+id);
  if(new Set(spec.members.map(m=>m.id)).size!==spec.members.length)throw Error('Duplicate native member ID');
  const family=contract.families.find(f=>f.id===id);if(!family)throw Error('Missing native contract: '+id);
  coverage[id]=spec.members.map(m=>{const matches=section.querySelectorAll(m.selector);if(!matches.length)throw Error('Missing native member selector: '+id+' '+m.id);return {id:m.id,name:m.name,selector:m.selector,matches:matches.length,declaredStates:Object.fromEntries(m.classes.map(c=>[c,family.stateApplicability?.classes?.[c]??null])),demonstrated:'Source elements present; opening and state transitions require behavioral verification',tested:'unverified'};});
  const h=section.querySelector('h2');if(!h)throw Error('Missing native specimen heading');h.textContent=spec.members.map(m=>m.name).join(' · ');
  const ids=[...section.querySelectorAll('[id]')].map(e=>e.id);if(new Set(ids).size!==ids.length)throw Error('Duplicate native specimen DOM ID');
  fragments[id]=section.outerHTML;
 }
 return {fragments,coverage};
}

export function extractDedicatedSpecimen(document,registry,contract,unitId,sourcePath) {
 if(registry?.version!==1||contract?.schemaVersion!==1)throw Error('Unsupported dedicated source version');
 if(!['native-select','navigation-menu'].includes(unitId)||contract.id!==unitId)throw Error('Unknown/misrouted dedicated owner');
 if(Object.keys(registry.dedicated||{}).sort().join(',')!=='native-select,navigation-menu')throw Error('Unsupported dedicated registry IDs');
 const spec=registry.dedicated?.[unitId];if(!spec||spec.source!==sourcePath)throw Error('Missing/misrouted dedicated source');
 if(!Array.isArray(spec.requiredSelectors)||!spec.requiredSelectors.length||new Set(spec.requiredSelectors).size!==spec.requiredSelectors.length)throw Error('Empty/duplicate dedicated selector list');
 const required=selector=>{const matches=document.querySelectorAll(selector);if(matches.length!==1)throw Error('Missing/ambiguous dedicated selector: '+selector);return matches[0];};
 for(const selector of spec.requiredSelectors)required(selector);
 if(!Array.isArray(spec.members)||!spec.members.length||new Set(spec.members.map(m=>m.id)).size!==spec.members.length)throw Error('Empty/duplicate dedicated member registry');
 const coverage=spec.members.map(m=>{if(!m.id||!m.name||!m.selector)throw Error('Invalid dedicated member');const e=required(m.selector);if(!e.outerHTML.trim())throw Error('Empty dedicated member');return {id:m.id,name:m.name,selector:m.selector,matches:1,declaredStates:contract.states??null,declaredBehavior:contract.behavior??null,demonstrated:'Source element present; state transitions require matching behavior evidence',tested:'unverified'};});
 let markup;
 if(unitId==='native-select'){
  const select=required('.select__root > select');if(!select.options.length)throw Error('Empty native options');
  const label=required('label[for="'+select.id+'"]');if(!label.textContent.trim())throw Error('Empty select name');
  const heading=document.createElement('h3');heading.textContent=spec.members[0].name;markup=heading.outerHTML+required('.field__root').outerHTML;
 }else{
  const section=required('[data-native-navigation]').cloneNode(true);
  for(const panel of section.querySelectorAll('[popover]')){const triggers=[...section.querySelectorAll('[popovertarget]')].filter(e=>e.getAttribute('popovertarget')===panel.id);if(triggers.length!==1||!panel.getAttribute('aria-label')||!panel.querySelector('a[href]'))throw Error('Missing/ambiguous dedicated panel dependency');for(const link of panel.querySelectorAll('a[href^="#"]'))required(link.getAttribute('href'));}
  const h=section.querySelector('h2');if(!h)throw Error('Missing dedicated heading');h.textContent=spec.members.map(m=>m.name).join(' · ');
  markup=required('style').outerHTML+section.outerHTML+required('#native-overview').outerHTML+required('#native-preferences').outerHTML;
 }
 const container=document.createElement('div');container.innerHTML=markup;const ids=[...container.querySelectorAll('[id]')].map(e=>e.id);if(new Set(ids).size!==ids.length)throw Error('Duplicate dedicated DOM ID');
 return {markup,coverage};
}

// Whole contextual recipes retain their exact source bytes; this guard validates anatomy and ownership.
export function inspectCompositionSpecimen(doc,id,contract){
 if(contract?.version!==1)throw Error('Unsupported composition contract version');
 if(typeof id!=='string'||!/^[a-z][a-z0-9-]*__[a-z][a-z0-9-]*$/.test(id))throw Error('Invalid composition class ID');
 const owners=(contract.classGroups??[]).filter(g=>g.classes?.includes(id));
 if(owners.length!==1)throw Error('Missing/ambiguous composition class ownership: '+id);
 const matches=doc.querySelectorAll('.'+id).length;if(!matches)throw Error('Missing composition class anatomy: '+id);
 const ids=[...doc.querySelectorAll('[id]')].map(e=>e.id);if(new Set(ids).size!==ids.length)throw Error('Duplicate composition DOM IDs: '+id);
 return{id,ownerGroup:owners[0].id,matches,demonstrated:'Source class anatomy only',tested:'unverified'};
}
