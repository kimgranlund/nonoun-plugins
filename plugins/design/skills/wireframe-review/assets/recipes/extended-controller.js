/* Concatenate components.js first. Register one namespaced extended pattern per leaf.
   Data persists per proposal; transient popovers, notifications and edit focus do not. */
function registerExtendedExample(unitId){
 const snapshots=new WeakMap();
 const capture=root=>({controls:[...root.querySelectorAll('input,textarea')].map(e=>({id:e.id,name:e.name,value:e.value,checked:e.checked})),pages:[...root.querySelectorAll('[data-extended=pagination]')].map(e=>e.extendedPage?.()||0),trees:[...root.querySelectorAll('[data-extended=tree] [role=treeitem]')].map(e=>({id:e.getAttribute('aria-labelledby'),expanded:e.getAttribute('aria-expanded'),selected:e.getAttribute('aria-selected')})),rich:[...root.querySelectorAll('[data-extended=rich-text]')].map(e=>({html:e.richTextHTML||null,saved:e.richTextSaved||null}))});
 registerPrototype({unitId,initialState:null,reduce:(state,a)=>a.type==='extended-change'?a.snapshot:state,
 render(root,state){if(!state||!Array.isArray(state.controls)||JSON.stringify(capture(root))===JSON.stringify(state))return;
  const controls=[...root.querySelectorAll('input,textarea')];state.controls.forEach((v,i)=>{const e=controls[i];if(e&&e.id===v.id&&e.name===v.name){e.value=v.value;if(e.type==='checkbox'||e.type==='radio')e.checked=v.checked;}});
  root.querySelectorAll('[data-extended=multiselect] input[type=search]').forEach(e=>e.dispatchEvent(new Event('input',{bubbles:false})));
  root.querySelectorAll('[data-extended=pagination]').forEach((e,i)=>e.extendedSetPage?.(state.pages[i]));
  root.querySelectorAll('[data-extended=tree] [role=treeitem]').forEach(e=>{const n=state.trees.find(n=>n.id===e.getAttribute('aria-labelledby'));if(n){e.setAttribute('aria-selected',n.selected);if(n.expanded!==null){e.setAttribute('aria-expanded',n.expanded);e.querySelector(':scope > ul').hidden=n.expanded!=='true';}}});
  root.querySelectorAll('[data-extended=data-grid] td').forEach(e=>{e.querySelector('span').textContent=e.querySelector('input').value;});
  root.querySelectorAll('[data-extended=rich-text]').forEach((host,i)=>{const saved=state.rich[i],editor=host.querySelector('[data-rich-editor]');editor.replaceChildren();
   // Reconstruct only text, strong, em and br; never inject stored HTML into the page.
   const parsed=new DOMParser().parseFromString(saved?.html||'','text/html');const append=(node,parent)=>{if(node.nodeType===3)parent.append(document.createTextNode(node.textContent));else if(node.nodeType===1){if(['STRONG','EM','BR'].includes(node.tagName)){const el=document.createElement(node.tagName.toLowerCase());parent.append(el);node.childNodes.forEach(n=>append(n,el));}else node.childNodes.forEach(n=>append(n,parent));}};
   if(saved?.html)parsed.body.childNodes.forEach(n=>append(n,editor));else editor.textContent=host.querySelector('textarea').value;host.richTextHTML=saved?.html;host.richTextSaved=saved?.saved;if(saved?.saved)host.querySelector('[role=status]').textContent='Local saved version retained; edits may be unsaved.';
  });snapshots.set(root,JSON.stringify(capture(root)));
 },
 bind({root,on,dispatch,signal}){const cleanup=globalThis.mountExtendedPatterns(root);const changed=()=>queueMicrotask(()=>{if(signal.aborted)return;const snapshot=capture(root),key=JSON.stringify(snapshot);if(snapshots.get(root)!==key){snapshots.set(root,key);dispatch({type:'extended-change',snapshot});}});on('input','input,textarea,[contenteditable]',changed);on('change','input',changed);on('click','button,[role=treeitem]',changed);on('keydown','[role=treeitem],table,[contenteditable]',changed);return cleanup;}
 });
}
