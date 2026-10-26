import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {renderIndex} from './lib/sheets/index-gaps.mjs';
const [sheets,pw,reportFile]=process.argv.slice(2);
if(!sheets||!pw||!reportFile)throw Error('Usage: check-index-source-chain.mjs SHEETS PLAYWRIGHT REPORT');
const stages=['seeds','raw exports','semantic bindings','type/geometry','components','compositions','generated interfaces'];
const paths=[['assets/foundation/ultimate-tokens/source-state.json'],['assets/foundation/ultimate-tokens/colors.css'],['assets/wireframe.css'],['assets/foundation/ultimate-tokens/typography.css','assets/foundation/maison/geometry.css'],['references/style/components/contract.json'],['references/style/composition.md'],['evals/plan.md']];
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const inventory=JSON.parse(fs.readFileSync(path.join(sheets,'inventory.json')));
const fixtures=stages.map((stage,i)=>({id:'source-chain-'+i,stage,manifest:paths[i].map(path=>({path,selectionKey:'whole'})),context:paths[i].map(path=>({path,selectionKey:'whole'})),implementation:paths[i].map(path=>({path,selectionKey:'whole'})),requirementIds:[]}));
const sources=stages.flatMap((stage,i)=>paths[i].map((path,j)=>({id:stage+':'+j,stage,path,selectionKey:'whole'})));
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
const args={inventory:{declarations:[],specimens:[],requirements:[],sources,units:fixtures},entryContext:{excerpts:Object.fromEntries(sources.map(ref=>[ref.path,{whole:'fixture source'}]))},helpers:{esc,code:esc,sourceLink:esc,inspector:(label,body)=>label+body,sourceIdentity:(path,selectionKey)=>({path,selectionKey,sha256:'a'.repeat(64)})}};
assert.ok(renderIndex(args).includes('geometry.css'));
const faults=[];
for(const [name,mutate] of [
 ['omit geometry manifest',a=>a.inventory.units[3].manifest.pop()],
 ['omit geometry source',a=>a.inventory.sources.splice(4,1)],
 ['duplicate geometry source',a=>a.inventory.sources.push({...a.inventory.sources[4],id:'extra'})],
 ['swap component context',a=>a.inventory.units[4].context=a.inventory.units[5].context],
 ['omit implementation source',a=>a.inventory.units[0].implementation=[]],
 ['wrong selection key',a=>a.inventory.units[2].manifest[0].selectionKey='invented']
]) {const altered={...args,inventory:structuredClone(args.inventory)};mutate(altered);assert.throws(()=>renderIndex(altered),/stage source|selection mismatch/);faults.push({name,outcome:'rejected',kind:'renderer-input-mutation'});}
const {chromium}=createRequire(import.meta.url)(pw);const browser=await chromium.launch();const records=[];
try{for(const width of [360,1399]){const context=await browser.newContext({javaScriptEnabled:false,viewport:{width,height:1000}});const page=await context.newPage();await page.goto(pathToFileURL(path.join(sheets,'index.html')).href);for(let i=0;i<stages.length;i++){
 const section=page.locator('#source-chain-'+i);const card=section.locator('[data-chain-stage]');assert.equal(await card.count(),1);
 const text=await card.innerText();assert.ok(!text.includes('Unavailable'));assert.ok(text.includes('Source records: '+paths[i].length));
 for(const source of paths[i])assert.ok(text.includes(source),source);
 assert.equal(await card.locator('li').count(),paths[i].length);assert.equal(await section.locator('details').count(),4);
 const actual=await section.locator('details > summary').allTextContents();assert.deepEqual(actual.map(s=>s.trim()),['Implementation','Manifest','Context','Verification']);
 const overflow=await card.evaluate(el=>el.scrollWidth>el.clientWidth+1);assert.equal(overflow,false);
 records.push({stage:stages[i],width,javaScriptEnabled:false,sources:paths[i],outcome:'pass'});
 }await context.close();}}finally{await browser.close();}
const report={sourceHash:inventory.sourceHash,inventorySha256:sha(fs.readFileSync(path.join(sheets,'inventory.json'))),indexSha256:sha(fs.readFileSync(path.join(sheets,'index.html'))),verifierSha256:sha(fs.readFileSync(new URL(import.meta.url))),records,faults,limits:['Source routing, inventory display and no-JS card fit only.','No generation-transfer, whole-specification or cross-browser acceptance.','Renderer fault controls do not represent browser behavior defects.']};
fs.mkdirSync(path.dirname(reportFile),{recursive:true});fs.writeFileSync(reportFile,JSON.stringify(report,null,2));console.log(JSON.stringify({records:records.length,faults:faults.length,outcome:'pass'}));
