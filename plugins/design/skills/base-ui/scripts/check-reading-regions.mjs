import fs from 'node:fs';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
import {getAssetBundle} from './api.mjs';import {auditRendered} from './lib/audit-rendered.mjs';
const [runtime,executablePath,artifact,out='/private/tmp/base-ui-reading']=process.argv.slice(2);
const families=JSON.parse(fs.readFileSync(new URL('../references/style/components/contract.json',import.meta.url))).families;
const b=await createRequire(import.meta.url)(runtime).chromium.launch({headless:true,executablePath});const cases=[];
try{for(const width of [320,390,768,1440])for(const colorScheme of ['light','dark']){
 const p=await b.newPage({viewport:{width,height:1000},colorScheme});
 if(artifact)await p.goto('file://'+artifact);else await p.setContent(`<style>${getAssetBundle().css}</style>${fs.readFileSync(new URL('../assets/recipes/reading-region.html',import.meta.url),'utf8')}`);
 await p.evaluate(()=>document.fonts.ready);
 await p.locator('details').evaluateAll(es=>es.forEach(e=>e.open=true));
 const inspect=()=>p.evaluate(auditRendered,{families,retrieved:families.map(f=>f.id)});
 assert.deepEqual((await inspect()).issues,[]);
 if(!artifact){
  await p.locator('.disclosure__body').last().evaluate(e=>{let host=e;for(let i=0;i<4;i++){const d=document.createElement('details');d.className='disclosure__root';d.open=true;d.innerHTML='<summary>Additional source '+i+'</summary><div class="disclosure__body flow__root"></div>';host.append(d);host=d.lastElementChild;}host.innerHTML='<p>This dynamically introduced source has enough detailed explanatory prose to require a usable reading measure at every tested viewport, even after several levels of independent evidence have been expanded.</p>';});
  assert.deepEqual((await inspect()).issues,[],'Dynamic deeper evidence');
 }
 const measure=await p.locator('p').evaluateAll(es=>es.filter(e=>e.getClientRects().length).map(e=>({text:e.textContent.slice(0,30),width:e.clientWidth})));
 assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 if(!artifact && width<=390){
  await p.locator('.reading-flow__root').evaluate(e=>e.classList.remove('reading-flow__root'));
  assert((await inspect()).issues.some(x=>x.code==='PROSE_MEASURE'),'Unadapted nesting must fail even when all individual paddings are correct');
  await p.locator('article').evaluate(e=>e.classList.add('reading-flow__root'));
  await p.locator('p').first().evaluate(e=>e.style.width='10ch');
  assert((await inspect()).issues.some(x=>x.code==='PROSE_MEASURE'),'Narrow custom column must fail inside adaptive region');
  await p.locator('p').first().evaluate(e=>e.style.width='');
  assert.deepEqual((await inspect()).issues,[]);
 }
 if(!artifact && width===1440){
  await p.locator('article').evaluate(e=>e.style.width='280px');
  assert.deepEqual((await inspect()).issues,[],'Narrow region on desktop must adapt');
  await p.locator('article').evaluate(e=>e.style.width='');
 }
 await p.screenshot({path:`${out}/${artifact?'consumer':'recipe'}-${width}-${colorScheme}.png`,fullPage:true});cases.push({width,colorScheme,measure,issues:[]});if(!artifact){
 const prose='A single task card has already paid the outer margin. Its full-width explanation remains valid at narrow widths and with enlarged text; only additional nesting should consume the remaining budget.';
 await p.setContent(`<style>${getAssetBundle().css}</style><main class="page__root"><article class="card__root"><p style="font-size:200%;line-height:1.5">${prose}</p></article></main>`);await p.evaluate(()=>document.fonts.ready);
 assert.deepEqual((await inspect()).issues,[],'Single-card available-width cap must not demand page width');
 if(width<=390){await p.locator('article').evaluate(e=>{const p=e.firstElementChild;e.innerHTML='<section class="card__root"><div class="card__root"></div></section>';e.querySelector('div').append(p);});assert((await inspect()).issues.some(x=>x.code==='PROSE_MEASURE'),'Nested cards must still fail against outer card width');}
 }
 await p.close();
}}finally{await b.close()}
fs.writeFileSync(`${out}/${artifact?'consumer':'recipe'}-checks.json`,JSON.stringify(cases,null,2));console.log('PASS reading-region checks '+JSON.stringify(cases));
