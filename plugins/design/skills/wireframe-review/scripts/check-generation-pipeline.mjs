import fs from'node:fs';import path from'node:path';import os from'node:os';import assert from'node:assert/strict';import{spawnSync}from'node:child_process';import{root,sha}from'./token-index.mjs';
const[pw]=process.argv.slice(2);if(!pw)throw Error('Pass Playwright module path');const out=fs.mkdtempSync(path.join('/private/tmp','wireframe-pipeline-')),base=JSON.parse(fs.readFileSync(path.join(root,'assets/example.manifest.json'))),results=[];
function test(name,mutate,expected,extra=[],runtime=pw){const m=structuredClone(base);mutate(m);const input=path.join(out,name+'.json'),dest=path.join(out,name);fs.writeFileSync(input,JSON.stringify(m));const r=spawnSync(process.execPath,[path.join(root,'scripts/generate.mjs'),input,dest,runtime,...extra],{encoding:'utf8'});assert.equal(r.status,expected?1:0,r.stderr);let report;
 if(expected){assert(!fs.existsSync(dest),'Failed pipeline published output');const failure=JSON.parse(r.stderr);report=JSON.parse(fs.readFileSync(path.join(failure.diagnostics,'generation.json')));assert.equal(report.status,'failed');assert(report.error.includes(expected),report.error);}
 else{report=JSON.parse(fs.readFileSync(path.join(dest,'generation.json')));assert.equal(report.artifactSHA256,sha(fs.readFileSync(path.join(dest,'artifact.html'))));assert.deepEqual(report.stages.map(s=>s.name),['compile','artifact-verification','runtime-startup','preventive-lint']);const v=JSON.parse(fs.readFileSync(path.join(dest,'verification.json')));assert.equal(v.inputs.artifact.path,path.join(dest,'artifact.html'));assert(v.checks.every(c=>c.status==='pass'));}
 results.push({name,status:report.status,stages:report.stages.map(s=>({name:s.name,exit:s.exit})),findings:report.findings});return {report,input,dest};}
const variant=m=>m.units.find(u=>u.variants.some(v=>v.html)).variants[0];
const valid=test('valid',()=>{},null);
const anatomy=test('mark-anatomy',m=>variant(m).html+='<label class="choice__root"><input type="checkbox">Pick</label>',null);assert(anatomy.report.findings.warnings.some(f=>f.rule==='choice-mark-anatomy'));

test('compiled-select',m=>variant(m).html+='<label for="pipeline-select">Choice</label><select id="pipeline-select"><option>One</option></select>',null);
test('token-fault',m=>m.css+=' .x{color:var(--md-pipeline-missing,#fff)}','compile failed');
test('reference-fault',m=>variant(m).html+='<label for="pipeline-missing">Missing</label>','preventive-lint failed');
const warning=test('warning',m=>variant(m).html+='<div class="card__root" style="padding:7px">Warning</div>',null);assert(warning.report.findings.warnings.some(f=>f.rule==='owned-geometry-literal'));
const unresolved=test('unverified',m=>variant(m).html+='<iframe src="https://example.invalid/"></iframe>',null);assert(unresolved.report.findings.unverified.some(f=>f.rule==='external-document'));
test('unavailable-browser',()=>{},'runtime-startup failed',[],path.join(out,'nonexistent-playwright'));
const before=sha(fs.readFileSync(path.join(valid.dest,'artifact.html'))),retry=spawnSync(process.execPath,[path.join(root,'scripts/generate.mjs'),valid.input,valid.dest,pw],{encoding:'utf8'});assert.notEqual(retry.status,0);assert.equal(before,sha(fs.readFileSync(path.join(valid.dest,'artifact.html'))));
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({results,existingDeliveryPreserved:true,limits:'Automatic initial-document pipeline only; no application interaction certification'},null,2));console.log('PASS '+results.length+' generation paths; existing delivery preserved. '+out);
