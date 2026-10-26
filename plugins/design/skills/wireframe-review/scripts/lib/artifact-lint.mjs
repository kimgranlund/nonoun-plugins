// Executed in a browser inspection context, never in the authored application.
export function inspectArtifact({html,policy={deferredReferences:[]},ownedClasses=[],trustedStyles=[]}){
 const findings=[],documents=[],used=new Set(),deferred=policy.deferredReferences||[];
 const add=(rule,severity,document,selector,detail)=>findings.push({rule,severity,document,selector,detail});
 function inspect(source,key,depth){
  if(depth>12){add('document-depth','unverified',key,'','Nested document limit reached');return;}
  const doc=new DOMParser().parseFromString(source,'text/html');documents.push(key);
  const locator=e=>e.id?'#'+CSS.escape(e.id):e.tagName.toLowerCase()+(e.classList.length?'.'+[...e.classList].map(CSS.escape).join('.'):'');
  const ids=new Map();for(const e of doc.querySelectorAll('[id]')){if(ids.has(e.id))add('duplicate-id','error',key,locator(e),'ID occurs more than once in this document');ids.set(e.id,e);}
  for(const e of doc.querySelectorAll('[for], [aria-labelledby], [aria-describedby], [aria-controls], [popovertarget]')){
   for(const attr of ['for','aria-labelledby','aria-describedby','aria-controls','popovertarget']){
    if(!e.hasAttribute(attr)||(attr==='for'&&e.localName!=='label'))continue;
    const raw=e.getAttribute(attr).trim(),targets=attr.startsWith('aria-')?raw.split(/\s+/).filter(Boolean):[raw];
    if(!targets.length||!raw){add('empty-reference','error',key,locator(e),attr+' is empty');continue;}
    for(const id of targets){const target=ids.get(id);
     if(!target){
      const waiver=deferred.findIndex(w=>w.document===key&&w.attribute===attr&&w.target===id&&e.matches(w.selector));
      if(waiver>=0){used.add(waiver);add('deferred-reference','unverified',key,locator(e),`${attr} -> ${id}: ${deferred[waiver].reason}; verify state: ${deferred[waiver].state}`);}
      else add('missing-reference','error',key,locator(e),`${attr} -> ${id} is missing`);
     }else if(attr==='popovertarget'&&!target.hasAttribute('popover'))add('popover-target-type','error',key,locator(e),`${id} has no popover attribute`);
     else if(attr==='for'&&!target.matches('button,input:not([type="hidden"]),meter,output,progress,select,textarea')){
      add('label-target-type',target.localName.includes('-')?'unverified':'error',key,locator(e),`${id} is not a known native labelable target; custom elements require runtime verification`);
     }
    }
   }
  }
  for(const e of doc.querySelectorAll('input[type=checkbox],input[type=radio]')){
   if(!e.closest('.choice__root,.choice__card,.switch__root,.card__root,.product__root'))continue;
   const expected=e.type==='radio'?'radio__control':'checkbox__control';
   if(!e.classList.contains(expected)&&!(e.type==='checkbox'&&e.closest('.switch__root')))add('choice-mark-anatomy','warning',key,locator(e),'Native '+e.type+' in a product composition lacks '+expected+'; read the choices family and use its exact input anatomy');
  }
  const unknownOwners=new Set();
  const owners=new Set(ownedClasses),governed=e=>[...e.classList].some(c=>owners.has(c));
  function declarations(style,e,source,trusted=false){
   if(!governed(e)){if(!trusted&&[...style].some(p=>/^(padding|gap|row-gap|column-gap|border-radius)(-|$)/.test(p)))unknownOwners.add(locator(e));return;}
   for(const property of [...style]){
    const value=style.getPropertyValue(property);
    if(trusted&&/^(0(?:px|rem|em)?\s*)+$/.test(value.trim()))continue;
    if((property==='border-radius'||property.startsWith('border-')&&property.endsWith('-radius')||/^(padding|gap|row-gap|column-gap)(-|$)/.test(property))&&/\b\d*\.?\d+(px|rem|em)\b/.test(value)&&!value.includes('var(')){
     add('owned-geometry-literal','warning',key,locator(e),`${source}: ${property}: ${value}; check the component geometry owner before overriding`);
    }
   }
  }
  for(const e of doc.querySelectorAll('[style]'))declarations(e.style,e,'inline style');
  const trustedRules=new Set();
  function collect(rules){for(const r of rules){if(r.selectorText&&r.style)trustedRules.add(r.cssText);if(r.cssRules)collect(r.cssRules);}}
  for(const css of trustedStyles){const sheet=new CSSStyleSheet();sheet.replaceSync(css);collect(sheet.cssRules);}
  function walk(rules,source){for(const rule of rules){if(rule.selectorText&&rule.style){let elements;try{elements=doc.querySelectorAll(rule.selectorText);}catch{continue;}for(const e of elements)declarations(rule.style,e,source+' '+rule.selectorText,trustedRules.has(rule.cssText));}if(rule.cssRules)walk(rule.cssRules,source);}}
  for(const [i,e]of [...doc.querySelectorAll('style')].entries()){
   const sheet=new CSSStyleSheet();try{sheet.replaceSync(e.textContent);walk(sheet.cssRules,'style['+i+']');}catch{add('css-inspection','unverified',key,'style','Stylesheet could not be inspected');}
  }
  if(unknownOwners.size)add('unknown-style-owner','unverified',key,'',`${unknownOwners.size} custom geometry selectors outside recognized component checks: ${[...unknownOwners].slice(0,12).join(', ')}. Warning counts do not measure fidelity`);
  // This is a structural risk warning, not a claim about computed cascade or layout.
  for(const parent of doc.querySelectorAll('.flow__root,.section__flow,.field__root,.heading-group__root'))for(const child of parent.children){
   if([...child.style].some(p=>p.startsWith('margin')&&!/^(0(?:px|rem|em)?|auto)$/.test(child.style.getPropertyValue(p).trim())))add('gap-plus-child-margin','warning',key,locator(child),'Inline child margin competes with a governed parent gap; review spacing ownership');
  }
  for(const e of doc.querySelectorAll('link[rel="stylesheet"]'))add('external-stylesheet','unverified',key,locator(e),'Linked styles are not fetched: '+e.getAttribute('href'));
  for(const [i,frame]of [...doc.querySelectorAll('iframe')].entries()){
   if(frame.hasAttribute('srcdoc'))inspect(frame.getAttribute('srcdoc'),key+'/iframe['+i+']',depth+1);
   else add('external-document','unverified',key,locator(frame),'Non-srcdoc frame requires separate inspection');
  }
 }
 inspect(html,'root',0);
 for(let i=0;i<deferred.length;i++)if(!used.has(i))add('unused-deferral','error',deferred[i].document,deferred[i].selector,'Deferral does not match a missing reference; remove stale exception');
 return {documents,findings};
}
