// Release boundary, not an attestation of the reviewer's visual judgment.
import fs from 'node:fs';
import {localAssets} from './lib/local-assets.mjs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {validateReview} from './review-checklist.mjs';
import {makeVisualPlan,findingKeys} from './lib/review-visual-plan.mjs';
import {checkMeasurements} from './review-measurements.mjs';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const catalog=JSON.parse(fs.readFileSync(new URL('../references/review/rubrics.json',import.meta.url)));
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
export function beginReview(artifact,output){
 artifact=path.resolve(artifact);
 const record={schemaVersion:1,binding:{artifact,sha256:hash(fs.readFileSync(artifact)),assets:localAssets(artifact)},scope:{artifact,kind:'ui',task:'',reviewer:'',states:[]},items:catalog.topics.flatMap(t=>t.checks.map(c=>({id:c.id,status:'unreviewed',states:[],evidence:[],note:''})))};
 fs.writeFileSync(output,JSON.stringify(record,null,2)+'\n',{flag:'wx'});return record;
}
export function verifyDelivery(reviewPath){
 reviewPath=path.resolve(reviewPath);
 const p=read(reviewPath),review=validateReview(p),errors=[...review.errors],evidence=[],measurements=[];
 const binding=p.binding;
 if(binding?.assets){try{if(JSON.stringify(localAssets(binding.artifact))!==JSON.stringify(binding.assets))errors.push("Local assets changed since review began; start a new review");}catch(e){errors.push(e.message);}}
 const captureGeometryFailures=[],verifiedCaptures=[];
 if(p.expectedCaptureIds){
  if(!p.captureCompleted)errors.push('Capture matrix did not finish');
  const actual=(p.captures||[]).map(c=>c.id);
  if(new Set(actual).size!==actual.length||p.expectedCaptureIds.some(id=>!actual.includes(id))||actual.some(id=>!p.expectedCaptureIds.includes(id)))errors.push('Capture matrix has missing or unexpected rows');
  const matrix=p.machineStates||p.scope.states;
  if(matrix.length!==p.expectedCaptureIds.length||p.expectedCaptureIds.some(id=>!matrix.some(s=>s.id===id)))errors.push('Declared machine scope differs from planned capture matrix');
  if(p.machineStates){for(const scenario of new Set(matrix.map(s=>s.scenarioId)))for(const width of [320,390,768,1440])for(const scheme of ['light','dark'])for(const scale of [1,2])if(!p.expectedCaptureIds.includes(`${scenario}-${width}-${scheme}-${scale}`))errors.push('Required full matrix row missing: '+scenario);}
 }
 for(const failure of p.captureFailures||[])errors.push('Capture failed: '+failure.id+': '+failure.error);
 for(const capture of p.captures||[]){
  try{
   const file=path.resolve(path.dirname(reviewPath),capture.measurement),data=read(file);
   const screenshot=path.resolve(path.dirname(reviewPath),capture.screenshot);
   if(hash(fs.readFileSync(file))!==capture.measurementSHA256||hash(fs.readFileSync(screenshot))!==capture.screenshotSHA256)throw Error('Capture evidence changed since browser capture');
   if(data.artifact?.sha256!==binding?.sha256||data.state!==capture.id)throw Error('Capture binding/state mismatch');
   verifiedCaptures.push({...capture,findingKeys:findingKeys(data)});
   measurements.push({file,...checkMeasurements(data)});
   if(data.geometry?.issues?.length)captureGeometryFailures.push({state:capture.id,issues:data.geometry.issues});
  }catch(err){errors.push('Capture '+capture.id+': '+err.message);}
 }
 if(p.machineStates){
  const expectedPlan=makeVisualPlan(p.machineStates,verifiedCaptures);
  if(JSON.stringify(p.visualPlan)!==JSON.stringify(expectedPlan))errors.push('Manual inspection plan differs from generated risk-based sample');
  const required=expectedPlan.required.map(s=>s.id),scope=(p.scope.states||[]).map(s=>s.id);
  if(required.some(id=>!scope.includes(id))||scope.some(id=>!p.expectedCaptureIds.includes(id)))errors.push('Declared visual scope omits required samples or includes unknown captures');
  for(const item of p.items||[])for(const id of item.states||[]){const c=(p.captures||[]).find(c=>c.id===id);if(c&&!item.evidence?.some(e=>e.kind==='visual'&&path.resolve(path.dirname(reviewPath),e.ref)===path.resolve(path.dirname(reviewPath),c.screenshot)))errors.push(item.id+': missing matching visual evidence for '+id);}
 }
 if(!binding?.artifact||!binding?.sha256)errors.push('Missing artifact binding: use begin before reviewing');
 else {
  try {if(hash(fs.readFileSync(binding.artifact))!==binding.sha256)errors.push('Artifact changed since review began; begin a new review and recheck');}catch{errors.push('Bound artifact is missing');}
  if(p.scope?.artifact!==binding.artifact)errors.push('scope.artifact must match bound artifact');
 }
 for(const item of p.items||[])for(const e of item.evidence||[]){
  try{
   if(/^[a-z]+:\/\//i.test(e.ref))throw Error('Use preserved local evidence');
   const file=path.resolve(path.dirname(reviewPath),e.ref.split('#')[0].replace(/:\d+(?::\d+)?$/,''));
   const bytes=fs.readFileSync(file);if(!bytes.length)throw Error('Empty evidence');
   if(!evidence.some(v=>v.file===file))evidence.push({file,sha256:hash(bytes)});
   if(e.kind==='measurement'&&!measurements.some(v=>v.file===file)){
    const result=checkMeasurements(JSON.parse(bytes));measurements.push({file,...result});
   }
  }catch(err){errors.push(item.id+': evidence '+e.ref+': '+err.message);}
 }
 if(p.scope?.kind==='ui'){
  for(const state of p.scope.states||[])if(!(p.items||[]).some(i=>['pass','fail'].includes(i.status)&&(i.states||[]).includes(state.id)&&(i.evidence||[]).some(e=>e.kind==='visual')))errors.push('Missing visual evidence for declared state: '+state.id);
  for(const kind of ['contrast','taskAccess'])if(!measurements.some(m=>m.records.some(r=>r.kind===kind)))errors.push('Missing '+kind+' consumer measurement evidence');
 }
 const complete=review.complete&&!errors.length;
 const recognized=measurements.filter(m=>m.records.length);
 const measurementPass=recognized.length>0&&recognized.every(m=>m.status==='pass');
 const accepted=complete&&!captureGeometryFailures.length&&review.acceptance==='passed-in-recorded-scope'&&(p.scope?.kind!=='ui'||measurementPass);
 return {schemaVersion:1,status:!complete?'incomplete':accepted?'accepted':'complete-with-findings',complete,accepted,artifact:binding,review:{file:reviewPath,sha256:hash(fs.readFileSync(reviewPath)),...review},evidence,measurements,captureGeometryFailures,errors,limitations:'File integrity and recorded coverage only; does not authenticate browser execution or visual judgment. Scope and evidence must be inspected independently.'};
}
export function finishReview(reviewPath,receiptPath,releasePath){
 const result=verifyDelivery(reviewPath);
 if(fs.existsSync(receiptPath)||releasePath&&fs.existsSync(releasePath))throw Error('Refusing to overwrite receipt or release');
 if(releasePath&&!result.accepted){result.errors.push('Release refused: review is incomplete or has findings');return result;}
 if(releasePath){for(const asset of result.artifact.assets||[]){const from=path.resolve(path.dirname(result.artifact.artifact),asset.file),to=path.resolve(path.dirname(releasePath),asset.file);if(from!==to){fs.mkdirSync(path.dirname(to),{recursive:true});if(fs.existsSync(to)){if(hash(fs.readFileSync(to))!==asset.sha256)throw Error('Release asset conflict: '+to);}else fs.copyFileSync(from,to,fs.constants.COPYFILE_EXCL);}}fs.copyFileSync(result.artifact.artifact,releasePath,fs.constants.COPYFILE_EXCL);result.release={file:path.resolve(releasePath),sha256:result.artifact.sha256};}
 fs.writeFileSync(receiptPath,JSON.stringify(result,null,2)+'\n',{flag:'wx'});return result;
}
export function deliverySummary(result,report){
 return {status:result.status,complete:result.complete,accepted:result.accepted,artifact:result.artifact,release:result.release,rubric:result.review.counts,report:path.resolve(report),counts:{evidence:result.evidence.length,measurements:result.measurements.length,geometryFailures:result.captureGeometryFailures.length,errors:result.errors.length},errors:result.errors.slice(0,8).map(e=>String(e).slice(0,500)),limitations:result.limitations};
}
if(process.argv[1]===fileURLToPath(import.meta.url))try{
 const [cmd,a,b,c,...rest]=process.argv.slice(2);if(rest.length)throw Error('Unexpected arguments');let result;
 if(cmd==='begin'&&a&&b&&!c){beginReview(a,b);result={status:'unreviewed',review:path.resolve(b),next:'Review references/review/index.md, fill all checks, then finish with a new receipt path'};}
 else if(cmd==='check'&&a&&!b){const full=verifyDelivery(a),report=path.resolve(a)+'.delivery-check.json';fs.writeFileSync(report,JSON.stringify(full,null,2)+'\n');result=deliverySummary(full,report);}
 else if(cmd==='finish'&&a&&b){const full=finishReview(a,b,c);let report=b;if(!fs.existsSync(b)){report=path.resolve(a)+'.delivery-check.json';fs.writeFileSync(report,JSON.stringify(full,null,2)+'\n');}result=deliverySummary(full,report);}
 else throw Error('Usage: review-delivery.mjs begin ARTIFACT NEW_REVIEW.json | check REVIEW.json | finish REVIEW.json NEW_RECEIPT.json [NEW_RELEASE.html]');
 console.log(JSON.stringify(result,null,2));if(cmd!=='begin'&&!result.accepted)process.exitCode=1;
}catch(e){console.error(e.message);process.exitCode=1;}
