/* Trusted caller code; this lifecycle is not a sandbox. */
function createUIRuntime(){
 const states=new Map(),views=new Set();
 function mount({root,definition,stateKey,readOnly=false}){
  if(!root||typeof definition?.reduce!=='function'||typeof definition?.render!=='function'||typeof stateKey!=='string')throw Error('Invalid UI mount');
  if(definition.bind&&(typeof definition.bind!=='function'||definition.bind.length>1))throw Error('bind expects one object argument');
  for(const view of views)if(view.root===root)throw Error('Unmount existing view before remount');
  if(!states.has(stateKey))states.set(stateKey,structuredClone(definition.initialState??{}));
  const view={key:stateKey,root,definition,abort:new AbortController()};views.add(view);
  const paint=()=>{for(const item of views)if(item.key===stateKey)item.definition.render(item.root,structuredClone(states.get(stateKey)));};
  const dispatch=action=>{if(readOnly||!views.has(view))return;states.set(stateKey,structuredClone(definition.reduce(structuredClone(states.get(stateKey)),action)));paint();};
  const on=(type,selector,handler)=>{
   if(typeof type!=='string'||!type.trim()||typeof selector!=='string'||!selector.trim()||typeof handler!=='function')throw Error('on expects (eventType, selector, handler); root is already scoped. Example: on("click", "[data-action]", (event, target, dispatch) => {}).');
   try{root.matches(selector);}catch{throw Error('on expects a valid CSS selector: '+selector);}
   root.addEventListener(type,event=>{if(readOnly)return;const target=event.target.closest?.(selector);if(target&&root.contains(target))handler(event,target,dispatch);},{signal:view.abort.signal});
  };
  const onAction=(action,handler)=>{
   if(typeof action!=='string'||!action.trim()||typeof handler!=='function')throw Error('onAction expects (actionName, handler). Mark the native button with data-action="actionName".');
   on('click','button',(event,button,dispatch)=>{
    if(button.getAttribute('data-action')!==action||button.matches(':disabled')||button.getAttribute('aria-disabled')==='true')return;
    handler(event,button,dispatch);
   });
  };
  const unmount=()=>{if(!views.delete(view))return;view.abort.abort();view.cleanup?.();};
  view.unmount=unmount;
  try{view.cleanup=readOnly?null:definition.bind?.({root,on,onAction,dispatch,signal:view.abort.signal});definition.render(root,structuredClone(states.get(stateKey)));}catch(e){unmount();throw e;}
  return {dispatch,unmount};
 }
 return {mount,unmountAll(){for(const view of [...views])view.unmount();}};
}
function focusWorkflowStep(form,index,{panelSelector='[data-step], [data-stage]'}={}){
 if(!form?.isConnected||!Number.isInteger(index)||index<0)return false;
 const panels=[...form.querySelectorAll(panelSelector)];
 const panel=panels[index];
 const heading=panel?.querySelector('[data-step-heading],h1,h2,h3,h4,h5,h6');
 if(!heading||panel.hidden||!heading.getClientRects().length)return false;
 heading.tabIndex=-1;heading.focus();return heading.ownerDocument.activeElement===heading;
}

// IDs are data, not selector expressions. Descendants only, including detached roots.
function findUIElementById(root,id){
 if(!root||root.nodeType!==1||typeof id!=='string')throw Error('findUIElementById expects (Element, string)');
 return [...root.querySelectorAll('[id]')].find(element=>element.id===id)??null;
}

// Explicit binding: the native number input remains the value/constraint owner.
function bindInputSteppers(root){
 const groups=[...root.querySelectorAll('.input-group__root:has([data-input-step])')];
 const abort=new AbortController();
 const cleanups=[];
 for(const group of groups){
  const input=group.querySelector('input[type=number]');
  if(!input)continue;
  const buttons=[...group.querySelectorAll('[data-input-step]')];
  const sync=()=>buttons.forEach(button=>{
   const probe=input.cloneNode();
   const up=button.dataset.inputStep==='up';
   try{up?probe.stepUp():probe.stepDown();button.disabled=input.matches(':disabled')||input.readOnly||input.step==='any'||(input.value!==''&&probe.value===input.value);}catch{button.disabled=true;}
  });
  for(const button of buttons)button.addEventListener('click',()=>{
   sync();if(button.disabled)return;
   button.dataset.inputStep==='up'?input.stepUp():input.stepDown();
   input.dispatchEvent(new Event('input',{bubbles:true}));
   input.dispatchEvent(new Event('change',{bubbles:true}));sync();
  },{signal:abort.signal});
  input.addEventListener('input',sync,{signal:abort.signal});
  input.addEventListener('change',sync,{signal:abort.signal});
  input.form?.addEventListener('reset',()=>queueMicrotask(sync),{signal:abort.signal});
  const observer=new MutationObserver(sync);observer.observe(input,{attributes:true,attributeFilter:['min','max','step','disabled','readonly','value']});
  cleanups.push(()=>observer.disconnect());sync();
 }
 return ()=>{abort.abort();cleanups.forEach(cleanup=>cleanup());};
}

// One document-wide modality owner; pointer focus remains focusable/editable.
function bindFocusModality(doc=document){
 if(doc.documentElement.hasAttribute('data-focus-modality'))return;
 doc.documentElement.dataset.focusModality='keyboard';
 doc.addEventListener('pointerdown',()=>{doc.documentElement.dataset.focusModality='pointer';},true);
 doc.addEventListener('keydown',event=>{
  if(!event.metaKey&&!event.ctrlKey&&!event.altKey&&!['Shift','Control','Alt','Meta'].includes(event.key))doc.documentElement.dataset.focusModality='keyboard';
 },true);
}
