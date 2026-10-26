import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {resolveEvidence} from './lib/sheet-evidence.mjs';
const [output,reportFile]=process.argv.slice(2);if(!reportFile)throw Error('Usage: check-sheet-evidence.mjs SHEETS REPORT');const inspected=fs.realpathSync(output),requested=path.resolve(reportFile),target=path.join(fs.realpathSync(path.dirname(requested)),path.basename(requested));if(target===inspected||target.startsWith(inspected+path.sep))throw Error('Checker results must stay outside the inspected output');if(fs.existsSync(target))throw Error('Checker result path already exists; preserve prior evidence');
const inventory=JSON.parse(fs.readFileSync(path.join(output,'inventory.json')));const source=inventory.sources.find(x=>x.path==='assets/wireframe.css');
// Explicit test fixture, never a browser measurement/report to attach to a page.
const record={unitId:'fixture',specimenId:'fixture',checkId:'identity',outcome:'pass',sourceInputs:[{path:source.path,sha256:source.sha256}],environment:{kind:'source-only'}};
const report={schemaVersion:1,sourceHash:inventory.sourceHash,generatorSha256:inventory.generatorSha256,records:[record]};const args={inventory,report,unitId:'fixture',expectedCheckIds:['identity']};let checks=0;const eq=(a,b)=>{assert.equal(a,b);checks++};
eq(resolveEvidence(args).state,'reported-pass');eq(resolveEvidence({...args,report:null}).state,'unverified');
eq(resolveEvidence({...args,report:{...report,sourceHash:'changed'}}).state,'stale');
eq(resolveEvidence({...args,report:{...report,generatorSha256:'changed'}}).state,'stale');
eq(resolveEvidence({...args,expectedCheckIds:['identity','wrapping']}).state,'unverified');
eq(resolveEvidence({...args,unitId:'other'}).state,'unverified');
eq(resolveEvidence({...args,expectedSpecimenId:'wrong'}).state,'unverified');
assert.throws(()=>resolveEvidence({...args,inventory:{...inventory,sourceHash:undefined}}));checks++;
for(const outcome of ['fail','inconclusive','unverified'])eq(resolveEvidence({...args,report:{...report,records:[{...record,outcome}]}}).state,{fail:'reported-fail',inconclusive:'inconclusive',unverified:'unverified'}[outcome]);
eq(resolveEvidence({...args,report:{...report,records:[{...record,sourceInputs:[{path:source.path,sha256:'wrong'}]}]}}).state,'stale');
for(const bad of [{...report,schemaVersion:99},{...report,records:[record,record]},{...report,records:[{...record,outcome:'invented'}]},{...report,records:[{...record,environment:{kind:'browser',browser:{name:'Chromium'}}}]},{...report,records:[{...record,sourceInputs:[]}]}]){assert.throws(()=>resolveEvidence({...args,report:bad}));checks++}
const reordered={...record,environment:{note:'fixture',kind:'source-only'}};assert.throws(()=>resolveEvidence({...args,report:{...report,records:[reordered,{...record,environment:{kind:'source-only',note:'fixture'}}]}}));checks++;
eq(resolveEvidence({...args,report:{...report,records:[{...record,sourceInputs:[{}]}]}}).state,'stale');
eq(resolveEvidence({...args,report:{...report,records:[{...record,sourceInputs:[{path:'unknown'}]}]}}).state,'stale');
assert.throws(()=>resolveEvidence({...args,inventory:{...inventory,sources:[source,source]}}));checks++;
assert.throws(()=>resolveEvidence({...args,expectedCheckIds:['identity','identity']}));checks++;
fs.writeFileSync(reportFile,JSON.stringify({checks,inventorySourceHash:inventory.sourceHash,scope:'Pure compatibility guard, tested against actual generated inventory and explicitly synthetic report fixture. No browser/behavior claim; Attachment behavior requires separate presentation checks.'},null,2),{flag:'wx'});console.log('PASS',checks,'evidence compatibility cases; no fixture attached to pages');
