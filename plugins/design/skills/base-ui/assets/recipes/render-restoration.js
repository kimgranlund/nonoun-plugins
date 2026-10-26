// Optional around synchronous descendant replacement in render(root,state).
// Keep stable unique IDs. Deliberate navigation/reset may skip restoration.
// Requires assets/ui-runtime.js. Does not preserve selection ranges or scroll.
function captureUIRestoration(root){
 const active=root.ownerDocument.activeElement;
 return {focused:active!==root&&root.contains(active)&&active.id?active.id:null,
  opened:[...root.querySelectorAll('details[open][id]')].map(el=>el.id)};
}
function restoreUIRestoration(root,snapshot,{fallbackFocusId=null}={}){
 for(const id of snapshot.opened){
  const el=findUIElementById(root,id);
  if(el?.tagName==='DETAILS')el.open=true;
 }
 const el=snapshot.focused===null?null:findUIElementById(root,snapshot.focused);
 const usable=e=>e&&!e.matches(':disabled')&&e.getClientRects().length;
 if(usable(el)){el.focus({preventScroll:true});return {focus:'restored'};}
 if(snapshot.focused!==null&&fallbackFocusId!==null){const fallback=findUIElementById(root,fallbackFocusId);if(usable(fallback)){fallback.focus({preventScroll:true});return {focus:root.ownerDocument.activeElement===fallback?'fallback':'unresolved'};}}
 return {focus:snapshot.focused===null?'not-requested':'unresolved'};
}
// const snapshot=captureUIRestoration(root);
// ... replace descendants using escaped markup or DOM APIs ...
// restoreUIRestoration(root,snapshot);

// Optional fallbackFocusId is chosen by the app for a removed/hidden/disabled trigger.
// Its target must be programmatically focusable (e.g. status tabindex=-1).
// No prior focus inside root means no focus steal, even with a fallback.
