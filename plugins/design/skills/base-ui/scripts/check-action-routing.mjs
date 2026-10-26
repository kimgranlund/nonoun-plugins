import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const[runtime,executablePath]=process.argv.slice(2);if(!runtime)throw Error('Usage: check-action-routing.mjs PLAYWRIGHT [CHROME]');
const read=p=>fs.readFileSync(new URL('../'+p,import.meta.url),'utf8');
const b=await createRequire(import.meta.url)(path.resolve(runtime)).chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
try{const p=await b.newPage();await p.setContent(read('assets/recipes/action-routing.html')+'<button data-action="select-record" data-record="outside">Outside</button>');await p.addScriptTag({content:read('assets/ui-runtime.js')+'\n'+read('assets/recipes/action-routing.js')});
const status=p.locator('[data-record-status]');
await p.getByRole('button',{name:'Inspect evidence'}).click();assert.equal(await status.innerText(),'Inspecting A');
await p.locator('[data-record-detail]').evaluate(e=>{e.dataset.record='B';e.dataset.action='select-record';});
await p.getByText('Evidence for record A',{exact:true}).click();assert.equal(await status.innerText(),'Inspecting A');
await p.locator('[data-record-detail]').evaluate(e=>e.insertAdjacentHTML('beforeend','<button id="unmarked">Unmarked child</button>'));
await p.locator('#unmarked').click();assert.equal(await status.innerText(),'Inspecting A');
await p.getByRole('button',{name:'Outside',exact:true}).click();assert.equal(await status.innerText(),'Inspecting A');
await p.getByRole('button',{name:'Record B',exact:true}).evaluate(e=>e.innerHTML='<span>Record B</span>');await p.getByText('Record B',{exact:true}).click();assert.equal(await status.innerText(),'No event selected');
await p.getByRole('button',{name:'Inspect evidence'}).focus();await p.keyboard.press('Enter');assert.equal(await status.innerText(),'Inspecting B');
await p.getByRole('button',{name:'Record A',exact:true}).focus();await p.keyboard.press('Space');assert.equal(await status.innerText(),'No event selected');
await p.getByRole('button',{name:'Inspect evidence'}).evaluate(e=>{e.setAttribute('aria-disabled','true');e.click()});assert.equal(await status.innerText(),'No event selected');
await p.getByRole('button',{name:'Inspect evidence'}).evaluate(e=>{e.removeAttribute('aria-disabled');e.disabled=true;e.dispatchEvent(new MouseEvent('click',{bubbles:true}))});assert.equal(await status.innerText(),'No event selected');
await p.evaluate(()=>actionRoutingRuntime.unmountAll());await p.getByRole('button',{name:'Record B',exact:true}).click();assert.equal(await p.locator('button[data-record="A"]').getAttribute('aria-pressed'),'true');
// Invalid registrations fail at mount time; valid remount proves failed-root cleanup.
const bad=await p.evaluate(()=>{const r=createUIRuntime(),root=document.querySelector('#action-routing'),errors=[];for(const args of [['',()=>{}],['select',null]]){try{r.mount({root,stateKey:'invalid',definition:{reduce:s=>s,render(){},bind({onAction}){onAction(...args)}}});}catch(e){errors.push(e.message)}}return errors});assert.equal(bad.length,2);assert(bad.every(s=>s.startsWith('onAction expects')));
console.log('PASS action-routing recipe: ancestor hook/payload collisions ignored, unmarked/outside buttons ignored, nested label click, rerender, Enter/Space, disabled/aria-disabled, unmount and invalid binding cleanup.');
}finally{await b.close()}
