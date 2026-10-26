import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import assert from 'node:assert/strict';
const [runtime,executablePath]=process.argv.slice(2);if(!runtime)throw Error('Usage: check-runtime-binding.mjs PLAYWRIGHT [CHROME]');
const browser=await createRequire(import.meta.url)(path.resolve(runtime)).chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
try{const p=await browser.newPage();await p.setContent('<main id="app"></main>');await p.addScriptTag({content:fs.readFileSync(new URL('../assets/ui-runtime.js',import.meta.url),'utf8')});
const result=await p.evaluate(()=>{
 const root=document.querySelector('#app'),runtime=createUIRuntime(),errors=[];
 const base={initialState:{count:0},reduce(s){return {count:s.count+1}},render(r,s){r.innerHTML='<button data-action><span>Increment</span></button><output>'+s.count+'</output>'}};
 for(const args of [[root,'click',()=>{}],['click','[',()=>{}],['click','',()=>{}],['click','button',null]]){
  try{runtime.mount({root,stateKey:'bad',definition:{...base,bind({on}){on(...args)}}});errors.push('missed');}catch(e){errors.push(e.message);}
 }
 // Failed mounts must release the root; bind-before-render delegation must work.
 const mount=runtime.mount({root,stateKey:'valid',definition:{...base,bind({on}){on('click','[data-action]',(event,target,dispatch)=>dispatch({type:'increment'}));}}});
 window.bindingProbe={mount,runtime};return errors;
});assert(result.every(x=>x.startsWith('on expects')),JSON.stringify(result));
await p.locator('button span').click();assert.equal(await p.locator('output').innerText(),'1');await p.locator('button').click();assert.equal(await p.locator('output').innerText(),'2');
await p.evaluate(()=>window.bindingProbe.mount.unmount());await p.locator('button').click();assert.equal(await p.locator('output').innerText(),'2');
console.log('PASS: wrong signature/selector/handler fail early; failed mount cleanup; delegated nested clicks survive rerender; unmount removes listener.');
}finally{await browser.close();}
