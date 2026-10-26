import assert from 'node:assert/strict';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import crypto from 'node:crypto';
import {beginReview,verifyDelivery} from './review-delivery.mjs';
import {makeVisualPlan,findingKeys} from './lib/review-visual-plan.mjs';
import {recordJudgments} from './review-session.mjs';
const root=fs.mkdtempSync(path.join(os.tmpdir(),'review-visual-plan-')),app=path.join(root,'app.html'),file=path.join(root,'review.json');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
fs.writeFileSync(app,'<h1>Fixture</h1>');const p=beginReview(app,file);Object.assign(p.scope,{task:'Fixture',reviewer:'Fixture'});
p.machineStates=[];p.captures=[];p.captureFailures=[];p.captureCompleted=true;
for(const scenarioId of ['initial','error'])for(const width of [320,390,768,1440])for(const scheme of ['light','dark'])for(const textScale of [1,2]){
 const id=`${scenarioId}-${width}-${scheme}-${textScale}`,screenshot=id+'.png',measurement=id+'.json';
 p.machineStates.push({id,scenarioId,description:id});fs.writeFileSync(path.join(root,screenshot),'fixture image bytes');
 const data={artifact:p.binding,state:id,geometry:{issues:[]},contrast:{scope:'Rendered text in fixture',status:'pass'},taskAccess:{scope:'Declared task access only fixture',status:'pass'}};
 fs.writeFileSync(path.join(root,measurement),JSON.stringify(data));p.captures.push({id,scenarioId,screenshot,measurement,findingKeys:findingKeys(data),screenshotSHA256:hash(path.join(root,screenshot)),measurementSHA256:hash(path.join(root,measurement))});
}
p.expectedCaptureIds=p.machineStates.map(s=>s.id);p.visualPlan=makeVisualPlan(p.machineStates,p.captures);p.scope.states=p.machineStates.filter(s=>p.visualPlan.required.some(v=>v.id===s.id));
const distinct=[{id:'error-390-light-1',scenarioId:'error',findingKeys:findingKeys({geometry:{issues:[{code:'OPTION_FIT',element:'#first'}]},contrast:{status:'pass'},taskAccess:{status:'pass'}})},{id:'error-768-dark-1',scenarioId:'error',findingKeys:findingKeys({geometry:{issues:[{code:'OPTION_FIT',element:'#second'}]},contrast:{status:'pass'},taskAccess:{status:'pass'}})}];
const distinctPlan=makeVisualPlan(p.machineStates,distinct);assert.ok(distinct.every(c=>distinctPlan.required.some(v=>v.id===c.id)));
assert.equal(p.scope.states.length,6);assert.equal(p.expectedCaptureIds.length,32);fs.writeFileSync(file,JSON.stringify(p));
recordJudgments(file,p.items.map(i=>({id:i.id,status:'pass',states:['initial','error'],note:'Synthetic fixture observation only; not a real design judgment.'})));
assert.equal(verifyDelivery(file).status,'accepted');
let current=JSON.parse(fs.readFileSync(file));assert.ok(current.items.every(i=>i.states.length===6));const pristine=structuredClone(current);
current.items.forEach(i=>{i.states=i.states.filter(id=>id!=='error-320-light-1')});fs.writeFileSync(file,JSON.stringify(current));assert.equal(verifyDelivery(file).status,'incomplete');
current=structuredClone(pristine);current.captures.pop();fs.writeFileSync(file,JSON.stringify(current));assert.match(verifyDelivery(file).errors.join(' '),/missing or unexpected/);
current=structuredClone(pristine);const failed=current.captures.find(c=>c.id==='error-768-dark-1');const result=JSON.parse(fs.readFileSync(path.join(root,failed.measurement)));result.geometry.issues=[{code:'OVERFLOW',selector:'#fixture'}];fs.writeFileSync(path.join(root,failed.measurement),JSON.stringify(result));failed.measurementSHA256=hash(path.join(root,failed.measurement));failed.findingKeys=findingKeys(result);current.visualPlan=makeVisualPlan(current.machineStates,current.captures);current.scope.states=current.machineStates.filter(s=>current.visualPlan.required.some(v=>v.id===s.id));fs.writeFileSync(file,JSON.stringify(current));assert.equal(verifyDelivery(file).status,'incomplete');
recordJudgments(file,[{id:'layout.rails',status:'pass',states:[failed.id],note:'Synthetic observation of added finding representative.'}]);assert.equal(verifyDelivery(file).status,'complete-with-findings');assert.equal(verifyDelivery(file).accepted,false);
current=JSON.parse(fs.readFileSync(file));current.visualPlan.required=current.visualPlan.required.filter(v=>v.id!==failed.id);fs.writeFileSync(file,JSON.stringify(current));assert.match(verifyDelivery(file).errors.join(' '),/plan differs/);
console.log(JSON.stringify({status:'pass',checks:10,scope:'Synthetic bookkeeping tests, not visual acceptance',evidence:root}));
