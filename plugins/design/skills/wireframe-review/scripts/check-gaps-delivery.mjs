import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {groupWorkItems,renderGaps} from './lib/sheets/index-gaps.mjs';
const [out,registerFile,pw,reportFile]=process.argv.slice(2);
if(!reportFile)throw Error('Usage: check-gaps-delivery.mjs OUTPUT WORK_REGISTER PLAYWRIGHT REPORT');
if(fs.existsSync(reportFile)||path.resolve(reportFile).startsWith(path.resolve(out)+path.sep))throw Error('Preserve reports; write a new report outside the inspected output');
const hash=b=>createHash('sha256').update(b).digest('hex');
const raw=fs.readFileSync(registerFile),register=JSON.parse(raw),groups=groupWorkItems(register.items),captured=fs.readFileSync(path.join(out,'review-inputs/work-register.json')),inputs=JSON.parse(fs.readFileSync(path.join(out,'review-inputs.json')));
function sameSnapshot(candidate){assert(candidate.equals(captured),'Canonical register changed since capture; reconcile or rebuild affected output before publication');assert.equal(inputs.registerIdentity.sha256,hash(candidate));}
sameSnapshot(raw);
const faults=[];const rejected=(name,run)=>{assert.throws(run);faults.push(name);};
rejected('duplicate work item',()=>groupWorkItems([...register.items,register.items[0]]));
rejected('unknown normalized status',()=>groupWorkItems([{...register.items[0],normalizedStatus:'passed-ish'}]));
rejected('contradictory completion flag',()=>groupWorkItems([{...register.items[0],normalizedStatus:'open',complete:true}]));
rejected('intervening canonical register change',()=>sameSnapshot(Buffer.from(raw+' ')));
const helpers={esc:v=>String(v).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;'),sourceLink:p=>`<a href="sources/${p}">${p}</a>`};
rejected('omitted rendered item',()=>renderGaps({findings:[],workRegister:[register.items[0]],helpers}));
const inventory=JSON.parse(fs.readFileSync(path.join(out,'inventory.json')));
for(const name of ['scripts/build-sheets.mjs','scripts/lib/sheets/index-gaps.mjs','references/workflows/reference-sheets.md']){const source=inventory.sources.find(s=>s.path===name);assert(source);assert.equal(hash(fs.readFileSync(path.join(inventory.sourceRoot,name))),source.sha256);assert.equal(hash(fs.readFileSync(path.join(out,'sources',name))),source.sha256);}
const html=fs.readFileSync(path.join(out,'gaps.html'),'utf8');
for(const match of html.matchAll(/href="([^"]+)"/g)){
 const href=match[1];if(/^https?:/.test(href))continue;
 const [name,anchor]=href.split('#');const target=path.resolve(out,name||'gaps.html');assert(fs.existsSync(target),'Missing link '+href);
 if(anchor&&target.endsWith('.html'))assert(fs.readFileSync(target,'utf8').includes('id="'+anchor+'"'),'Missing anchor '+href);
}
const evidenceIndex=JSON.parse(fs.readFileSync(path.join(out,'review-inputs/evidence-index.json')));
assert.deepEqual(evidenceIndex.items.map(i=>i.id),register.items.map(i=>i.id));assert.equal(evidenceIndex.registerSHA256,hash(raw));
for(const item of evidenceIndex.items)for(const link of item.links)assert.equal(hash(fs.readFileSync(path.join(out,link.href))),link.sha256);
const browser=await createRequire(import.meta.url)(pw).chromium.launch(),records=[];const url=pathToFileURL(path.join(out,'gaps.html')).href;
const overflow=async p=>assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Horizontal page overflow');
try{
 for(const width of [360,1399])for(const javaScriptEnabled of [true,false]){
  const p=await browser.newPage({viewport:{width,height:900},javaScriptEnabled});const errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(url);
  const observed=await p.locator('[data-work-id]').evaluateAll(es=>es.map(e=>({id:e.dataset.workId,group:e.dataset.disposition})));
  assert.equal(observed.length,register.items.length);assert.equal(new Set(observed.map(r=>r.id)).size,register.items.length);
  for(const [group,items]of Object.entries(groups)){assert.deepEqual(observed.filter(r=>r.group===group).map(r=>r.id),items.map(i=>i.id));assert.equal(await p.locator(`[data-disposition-count="${group}"]`).getAttribute('data-count'),String(items.length));}
  assert.equal(await p.locator('#accepted-limitations').evaluate(e=>e.open),false);assert.equal(await p.locator('#completed-work').evaluate(e=>e.open),false);assert.equal(await p.locator('wbr').count(),0);await overflow(p);
  if(javaScriptEnabled)await p.screenshot({path:path.join(path.dirname(reportFile),`default-${width}.png`),fullPage:false});
  // Reach the archive summary with native sequential Tab, not a painted focus imitation.
  await p.locator('a:visible').first().focus();let reached=false;
  for(let i=0;i<40;i++){await p.keyboard.press('Tab');if(await p.locator('#accepted-limitations > summary').evaluate(e=>e===document.activeElement)){reached=true;break;}}
  assert(reached,'Archive summary reachable by native Tab');const focus=await p.locator('#accepted-limitations > summary').evaluate(e=>{const s=getComputedStyle(e);return{outline:s.outlineStyle,width:parseFloat(s.outlineWidth)};});assert(focus.outline!=='none'&&focus.width>0,'Visible disclosure focus styling');await p.keyboard.press('Enter');assert(await p.locator('#accepted-limitations').evaluate(e=>e.open));
  for(const [group,container]of [['accepted','accepted-limitations'],['completed','completed-work']]){
   const item=groups[group][0];if(!item)continue;
   if(javaScriptEnabled){await p.goto(url+'#'+item.id);await p.waitForFunction(id=>{const e=document.getElementById(id);return e?.open&&e.parentElement.closest('details')?.open;},item.id);}
   else{if(!await p.locator('#'+container).evaluate(e=>e.open))await p.locator('#'+container+' > summary').click();await p.locator('#'+item.id+' > summary').click();}
   assert(await p.locator('#'+item.id).evaluate(e=>e.open));assert(await p.locator('#'+item.id+' > summary').isVisible());await overflow(p);
   if(javaScriptEnabled)await p.screenshot({path:path.join(path.dirname(reportFile),`expanded-${group}-${width}.png`),fullPage:false});
  }
  if(javaScriptEnabled){const aliasItem=register.items.find(i=>i.id==='G-cross-browser');if(aliasItem){await p.goto(url+'#cross-browser');await p.waitForFunction(()=>document.getElementById('G-cross-browser').open);assert(await p.locator('#accepted-limitations').evaluate(e=>e.open));}}
  assert.deepEqual(errors,[]);records.push({width,javaScriptEnabled,scheme:await p.evaluate(()=>matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'),geometry:await p.locator('body').evaluate(e=>({...e.dataset})),workItems:observed.length,focus,outcome:'pass'});await p.close();
 }
 // Current register has no open work. Exercise all dispositions with explicitly synthetic content.
 const fixture=[
  {id:'fixture-open',title:'A long actionable title '+('nested-path/').repeat(20),normalizedStatus:'open',complete:false,classification:'missing coverage',status:'A required observation is absent.',correctiveAction:'Observe the named outcome.',owner:'Fixture owner',acceptance:'The named observation is recorded.',sourceIds:[]},
  {id:'fixture-accepted',title:'An explicitly accepted fixture limitation',normalizedStatus:'accepted-limitation',complete:true,classification:'missing coverage',sourceIds:[],resolution:{kind:'accepted-limitation',scope:'Synthetic unverified condition only.',userAnswer:'Fixture decision'}},
  {id:'fixture-completed',title:'A completed fixture task',normalizedStatus:'canonical-complete',complete:true,classification:'planning/specification',sourceIds:[]}
 ];
 const body=renderGaps({findings:fixture,workRegister:fixture,rawObservations:[{id:'fixture-source',item:'Unmapped fixture observation',missing:'Synthetic missing source.'}],snapshot:{builtAt:'fixture',registerSHA256:hash(raw)},helpers});
 for(const width of [360,1399]){const p=await browser.newPage({viewport:{width,height:900}});await p.goto(url);await p.locator('main').evaluate((e,html)=>e.innerHTML=html,body);assert(await p.locator('#fixture-open').isVisible());assert.equal(await p.locator('[data-disposition-count="open"]').getAttribute('data-count'),'1');assert((await p.locator('#fixture-open').innerText()).includes('Observe the named outcome.'));await overflow(p);await p.screenshot({path:path.join(path.dirname(reportFile),`synthetic-open-${width}.png`)});await p.close();}
}finally{await browser.close();}
sameSnapshot(fs.readFileSync(registerFile));
fs.writeFileSync(reportFile,JSON.stringify({browser:{name:'Chromium',version:browser.version()},checkerSHA256:hash(fs.readFileSync(import.meta.filename)),counts:Object.fromEntries(Object.entries(groups).map(([key,rows])=>[key,rows.length])),records,faults,registerSHA256:hash(raw),outputInputs:Object.fromEntries(['gaps.html','sheets.css','sheets.js','inventory.json','review-inputs.json'].map(f=>[f,hash(fs.readFileSync(path.join(out,f)))])),evidenceLinkItems:evidenceIndex.items.filter(i=>i.links.length).length,missingEvidenceLinkItems:evidenceIndex.items.filter(i=>!i.links.length).map(i=>i.id),scope:'Gaps disposition/count/anchor/snapshot and narrow/desktop presentation only. Four Chromium JS/no-JS contexts,synthetic open-work presentation,retained legacy deep link and negative controls. No component,generation or accessibility certification.'},null,2));console.log('PASS gaps delivery',JSON.stringify({counts:Object.fromEntries(Object.entries(groups).map(([key,rows])=>[key,rows.length])),faults:faults.length,contexts:records.length}));
