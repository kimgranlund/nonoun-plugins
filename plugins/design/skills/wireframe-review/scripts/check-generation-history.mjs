import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';import {createRequire} from 'node:module';import {pathToFileURL} from 'node:url';
import {loadGenerationHistory} from './lib/generation-history.mjs';
if(process.argv.includes('--help')){console.log('Usage: node scripts/check-generation-history.mjs SHEETS PLAYWRIGHT REPORT\nChecks copied history provenance, selected result bytes, task/model scope, current-applicability separation and no-JS rendering. Includes isolated rejection controls. Not an independent replication of study measurements.');process.exit(0);}
const [out,pw,file]=process.argv.slice(2);if(!file)throw Error('SHEETS PLAYWRIGHT REPORT required');
const root=path.join(out,'review-inputs/generation-evidence'),input=path.join(out,'review-inputs/generation-results.json');
const history=loadGenerationHistory(input,{evidenceRoot:root}),metadata=JSON.parse(fs.readFileSync(path.join(out,'review-inputs.json')));
assert.equal(metadata.generationRecords,history.records.length);assert.equal(metadata.generationApplicability,'historical-cohort');
for(const [p,s]of history.snapshots)assert(metadata.externalInputs.some(e=>e.path==='review-inputs/generation-evidence/'+p&&e.sha256===s.sha256),'External snapshot missing from provenance');
assert(metadata.externalInputs.some(e=>e.path==='review-inputs/generation-results.json'&&e.sha256===history.sha256));
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'generation-history-controls-')),faults=[];
for(const [name,mutate]of [
 ['missing-model',d=>delete d.records[0].model],['false-model',d=>d.records[0].model='other-model'],['false-task',d=>d.records[0].task='other-task'],
 ['false-effort',d=>d.records[0].reasoningEffort='high'],['missing-scope-evidence',d=>delete d.records[0].scopeEvidence],
 ['duplicate-record',d=>d.records.push(d.records[0])],['current-acceptance-claim',d=>d.records[0].applicability='current-source'],
 ['missing-selection',d=>d.records[0].results[0].pointer='/nonexistent'],['stale-evidence',d=>d.records[0].results[0].source.sha256='0'.repeat(64)],
 ['path-escape',d=>d.records[0].results[0].source.path='../outside.json'],['missing-cohort',d=>d.records[0].cohorts=[]],
 ['invalid-manifest',d=>d.records[0].cohorts[0].manifest=d.records[0].results[0].source]
]){const d=JSON.parse(history.raw),p=path.join(temp,name+'.json');mutate(d);fs.writeFileSync(p,JSON.stringify(d));assert.throws(()=>loadGenerationHistory(p,{evidenceRoot:root}),name);faults.push({name,rejected:true,scope:'Importer-input mutation; not study behavior'});}
const engines=createRequire(import.meta.url)(pw),cases=[];
for(const name of ['chromium','firefox','webkit']){const b=await engines[name].launch();try{for(const width of [360,1399]){const page=await b.newPage({javaScriptEnabled:false,viewport:{width,height:1000}});await page.goto(pathToFileURL(path.resolve(out,'index.html')).href);
 assert.equal(await page.locator('[data-generation-scope=historical-cohort]').count(),history.records.length);
 for(const r of history.records){const card=page.locator('#generation-'+r.id);const text=await card.innerText();assert(text.includes(r.task)&&text.includes(r.model)&&text.includes(r.reasoningEffort));assert(text.includes('Historical cohort; current-source transfer unverified'));assert.deepEqual(await card.locator('pre > code').allTextContents(),r.results.map(s=>JSON.stringify(s.value,null,2)));for(const s of r.results)assert.equal(await card.locator(`a[href="${s.path}"]`).count(),r.results.filter(t=>t.path===s.path).length);assert(await card.evaluate(e=>e.scrollWidth<=e.clientWidth+1));}
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert((await page.locator('main').innerText()).includes('Build timestamp (not verification)'));cases.push({engine:name,width,javaScriptEnabled:false,historyRecords:history.records.length,outcome:'pass'});await page.close();}}finally{await b.close();}}
const sha=b=>createHash('sha256').update(b).digest('hex');fs.writeFileSync(file,JSON.stringify({sourceHash:JSON.parse(fs.readFileSync(path.join(out,'inventory.json'))).sourceHash,indexSha256:sha(fs.readFileSync(path.join(out,'index.html'))),historySha256:history.sha256,records:history.records.map(r=>({id:r.id,task:r.task,model:r.model,reasoningEffort:r.reasoningEffort,cohorts:r.cohorts,results:r.results.length})),cases,faults,limits:['Source-selected historical summaries only; no study replication, current generation transfer or full Index acceptance.']},null,2));console.log('PASS historical generation results: six no-JS engine/width cases and twelve rejection controls');
