import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const [runtime,executablePath]=process.argv.slice(2);if(!runtime)throw Error('Usage: check-render-restoration.mjs PLAYWRIGHT [CHROME]');
const browser=await createRequire(import.meta.url)(path.resolve(runtime)).chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
try{const p=await browser.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));await p.setContent('<main></main><aside><input id="outside"></aside>');
for(const file of ['assets/ui-runtime.js','assets/recipes/render-restoration.js'])await p.addScriptTag({content:fs.readFileSync(new URL('../'+file,import.meta.url),'utf8')});
const result=await p.evaluate(()=>{
 const root=document.querySelector('main'),checks=[];
 for(const id of ['CUS:1042-billing.email','123','a[b]','a"b','a\\b','雪']){
  root.replaceChildren();const input=document.createElement('input'),details=document.createElement('details');input.id=id;details.id='source:'+id;details.open=true;root.append(input,details);input.focus();
  const snapshot=captureUIRestoration(root);const replacement=input.cloneNode(),replacementDetails=details.cloneNode();replacementDetails.open=false;root.replaceChildren(replacement,replacementDetails);restoreUIRestoration(root,snapshot);
  checks.push(findUIElementById(root,id)===replacement&&document.activeElement===replacement&&replacementDetails.open);
 }
 checks.push(findUIElementById(root,'outside')===null,findUIElementById(root,'missing')===null);
 root.id='root';checks.push(findUIElementById(root,'root')===null);
 const snap=captureUIRestoration(root);root.replaceChildren();restoreUIRestoration(root,snap);checks.push(root.children.length===0);
 const detached=document.createElement('div'),child=document.createElement('input');child.id='x:y';detached.append(child);checks.push(findUIElementById(detached,'x:y')===child);
 const disabled=document.createElement('input');disabled.id='disabled';disabled.disabled=true;root.append(disabled);restoreUIRestoration(root,{focused:'disabled',opened:[]});checks.push(document.activeElement!==disabled);
 const hidden=document.createElement('input');hidden.id='hidden';hidden.hidden=true;root.append(hidden);restoreUIRestoration(root,{focused:'hidden',opened:[]});checks.push(document.activeElement!==hidden);
 const fallback=document.createElement('p');fallback.id='status:a/1';fallback.tabIndex=-1;root.append(fallback);
 checks.push(restoreUIRestoration(root,{focused:'removed',opened:[]},{fallbackFocusId:'status:a/1'}).focus==='fallback',document.activeElement===fallback);
 document.querySelector('#outside').focus();restoreUIRestoration(root,{focused:null,opened:[]},{fallbackFocusId:'status:a/1'});checks.push(document.activeElement.id==='outside');
 checks.push(restoreUIRestoration(root,{focused:'removed',opened:[]},{fallbackFocusId:'outside'}).focus==='unresolved');
 for(const id of ['hidden','disabled'])checks.push(restoreUIRestoration(root,{focused:id,opened:[]},{fallbackFocusId:'status:a/1'}).focus==='fallback');
 return checks;
});assert(result.every(Boolean),JSON.stringify(result));assert.deepEqual(errors,[]);console.log('PASS render-restoration: literal punctuation IDs, replacement focus/open state, root isolation, removed targets, detached roots, disabled/hidden focus targets; explicit scoped completion fallback and no focus steal.');
}finally{await browser.close()}
