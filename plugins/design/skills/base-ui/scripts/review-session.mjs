// Browser evidence workbench. Capture never assigns a rubric judgment.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {beginReview,verifyDelivery} from './review-delivery.mjs';
import {auditRendered} from './lib/audit-rendered.mjs';
import {auditContrast} from './lib/audit-contrast.mjs';
import {auditTaskAccess} from './lib/audit-task-access.mjs';
import {applyTextScale} from './lib/text-scale.mjs';
import {makeVisualPlan,findingKeys} from './lib/review-visual-plan.mjs';
import {detailPlan,detailPacket} from './lib/review-details.mjs';
import {settleReview} from './lib/settle-review.mjs';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const write=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const families=read(fileURLToPath(new URL('../references/style/components/contract.json',import.meta.url))).families;
export async function captureReview({artifact,runtime,output,plan,executablePath}){
 artifact=path.resolve(artifact);output=path.resolve(output);
 if(!plan.task||!plan.reviewer||!plan.states?.length)throw Error('Plan needs task, reviewer and states');
 if(new Set(plan.states.map(s=>s.id)).size!==plan.states.length||plan.states.some(s=>!s.description||!/^[-a-zA-Z0-9_]+$/.test(s.id)))throw Error('States need unique safe IDs and descriptions');
 const widths=plan.widths||[320,390,768,1440];
 if(![320,390,768,1440].every(w=>widths.includes(w))||new Set(widths).size!==widths.length||widths.some(w=>!Number.isInteger(w)||w<1))throw Error('Widths must include320/390/768/1440');
 fs.mkdirSync(output);const reviewPath=path.join(output,'review.json');const review=beginReview(artifact,reviewPath);
 review.scope.task=plan.task;review.scope.reviewer=plan.reviewer;review.captures=[];review.captureFailures=[];review.captureCompleted=false;review.machineStates=[];
 for(const state of plan.states)for(const width of widths)for(const scheme of ['light','dark'])for(const textScale of [1,2])review.machineStates.push({scenarioId:state.id,id:`${state.id}-${width}-${scheme}-${textScale}`,description:`${state.description}; ${width}px ${scheme}, text ${textScale}x`});
 review.expectedCaptureIds=review.machineStates.map(s=>s.id);
 review.visualPlan=makeVisualPlan(review.machineStates,[]);review.scope.states=review.machineStates.filter(s=>review.visualPlan.required.some(v=>v.id===s.id));write(reviewPath,review);
 const pw=createRequire(import.meta.url)(path.resolve(runtime));
 const browser=await pw.chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
 try{for(const state of plan.states)for(const width of widths)for(const scheme of ['light','dark'])for(const textScale of [1,2]){
  const id=`${state.id}-${width}-${scheme}-${textScale}`;
  const page=await browser.newPage({viewport:{width,height:plan.height||844},colorScheme:scheme,offline:true});
  page.setDefaultTimeout(plan.timeoutMs||5000);
  try{
   await page.goto(pathToFileURL(artifact).href);
   await page.evaluate(s=>{document.documentElement.dataset.theme=s;document.documentElement.style.colorScheme=s},scheme);
   await page.evaluate(applyTextScale,textScale);
   if(state.setup)await state.setup(page,{width,scheme,textScale});
   await page.evaluate(s=>{document.documentElement.dataset.theme=s;document.documentElement.style.colorScheme=s},scheme);
   await page.evaluate(applyTextScale,textScale);
   if(state.arrive){await page.evaluate(settleReview);await state.arrive(page,{width,scheme,textScale});}
   const settled=await page.evaluate(settleReview);if(settled.status!=='ready')throw Error('Unsettled state');
   const geometry=await page.evaluate(auditRendered,{families,retrieved:plan.retrieved||[]});
   const contrast=await page.evaluate(auditContrast,{boundarySelectors:state.boundarySelectors||plan.boundarySelectors||[]});
   const taskAccess=await page.evaluate(auditTaskAccess,state.taskAccess||plan.taskAccess||{});
   const detailAnchors=await page.evaluate(({taskSelector,selectors})=>{
    const anchors=[];const add=(el,reason)=>{if(!el)return;const r=el.getBoundingClientRect();if(r.width&&r.height)anchors.push({reason,x:Math.max(0,r.x+scrollX+Math.min(r.width/2,400)),y:Math.max(0,r.y+scrollY+Math.min(r.height/2,300))});};
    if(document.activeElement!==document.body)add(document.activeElement,'focused element');
    try{add(taskSelector?document.querySelector(taskSelector):null,'primary task');}catch{}
    for(const selector of selectors.slice(0,4))try{add(document.querySelector(selector),'machine finding: '+selector);}catch{}
    return anchors;
   },{taskSelector:(state.taskAccess||plan.taskAccess||{}).taskSelector,selectors:geometry.issues.map(i=>i.selector||i.element).filter(Boolean)});
   const screenshot=id+'.png',measurement=id+'.json';
   await page.screenshot({path:path.join(output,screenshot),fullPage:true});
   const result={artifact:review.binding,state:id,width,scheme,textScale,geometry,contrast,taskAccess};write(path.join(output,measurement),result);
   review.captures.push({id,detailAnchors,scenarioId:state.id,findingKeys:findingKeys(result),screenshot,measurement,screenshotSHA256:hash(path.join(output,screenshot)),measurementSHA256:hash(path.join(output,measurement)),geometryIssues:geometry.issues.length,contrast:contrast.status,taskAccess:taskAccess.status});
  }catch(e){review.captureFailures.push({id,error:e.message});}
  finally{await page.close();write(reviewPath,review);}
 }}finally{await browser.close();}
 if(hash(artifact)!==review.binding.sha256)throw Error('Artifact changed during capture; evidence is stale');
 review.visualPlan=makeVisualPlan(review.machineStates,review.captures);review.scope.states=review.machineStates.filter(s=>review.visualPlan.required.some(v=>v.id===s.id));
 review.captureCompleted=true;write(reviewPath,review);
 return sessionStatus(reviewPath);
}
export function sessionStatus(reviewPath){
 const p=read(reviewPath),gate=verifyDelivery(reviewPath);
 const result={review:path.resolve(reviewPath),status:gate.status,captured:p.captures?.length||0,captureFailures:p.captureFailures||[],outstanding:p.items.filter(i=>['unreviewed','blocked'].includes(i.status)).map(i=>({id:i.id,status:i.status,note:i.note})),findings:p.items.filter(i=>i.status==='fail').map(i=>({id:i.id,note:i.note})),measurementFindings:(p.captures||[]).filter(c=>c.geometryIssues||c.contrast!=='pass'||c.taskAccess!=='pass'),missingVisualStates:p.scope.states.filter(s=>!p.items.some(i=>['pass','fail'].includes(i.status)&&i.states.includes(s.id)&&i.evidence.some(e=>e.kind==='visual'))).map(s=>s.id),errors:gate.errors};
 write(reviewPath+'.queue.json',result);
 return {...result,...Object.fromEntries(['captureFailures','outstanding','findings','measurementFindings','missingVisualStates','errors'].flatMap(k=>[[k,result[k].slice(0,8)],[k+'Count',result[k].length]])),fullQueue:reviewPath+'.queue.json'};
}
export function reviewPacket(reviewPath,topicId,page=1){
 const p=read(reviewPath),catalog=read(fileURLToPath(new URL('../references/review/rubrics.json',import.meta.url)));
 const topic=topicId?catalog.topics.find(t=>t.id===topicId):catalog.topics.find(t=>t.checks.some(c=>p.items.some(i=>i.id===c.id&&['unreviewed','blocked'].includes(i.status))));
 if(!topic)throw Error('No matching outstanding topic');
 if(!Number.isInteger(page)||page<1)throw Error('Page must be a positive integer');
 const required=p.visualPlan?.required||p.scope.states.map(s=>({id:s.id,reasons:['Declared visual scope']}));
 const rows=required.map(s=>({...s,...(p.captures||[]).find(c=>c.id===s.id)}));
 return {topic:topic.id,questions:topic.checks.map(c=>({id:c.id,question:c.question,method:c.method,current:p.items.find(i=>i.id===c.id)?.status})),scope:p.visualPlan?.limitation,page,totalPages:Math.ceil(rows.length/4),nextPage:page*4<rows.length?page+1:null,visuals:rows.slice((page-1)*4,page*4).map(c=>({...c,detail:detailPlan(reviewPath,c),screenshot:c.screenshot?path.resolve(path.dirname(reviewPath),c.screenshot):null,measurement:c.measurement?path.resolve(path.dirname(reviewPath),c.measurement):null})),record:'Open the full image for composition, then run each detail.command through the launcher to inspect bounded original-pixel tiles. The default sample targets focus/task/findings plus page edges; its unprovided coverage remains explicit. Request numeric detail pages only when needed. Retain notes across topics. Inspect relevant interactions; record this topic using review-session record. Scenario shorthand attests only the required sample. Findings are not automatic rubric judgments.'};
}
export function recordJudgments(reviewPath,judgments){
 const p=read(reviewPath);if(hash(p.binding.artifact)!==p.binding.sha256)throw Error('Artifact changed; start a new capture');
 if(!Array.isArray(judgments))throw Error('Judgments must be an array');
 for(const j of judgments){
  const old=p.items.find(i=>i.id===j.id);if(!old)throw Error('Unknown rubric '+j.id);
  if(!['pass','fail','na','blocked'].includes(j.status)||!j.note?.trim())throw Error('Judgment needs status and observation');
  const item={...j,states:[],evidence:[]};
  if(['pass','fail'].includes(j.status)){
   if(!Array.isArray(j.states)||!j.states.length)throw Error('List inspected capture IDs or state groups');
   const required=new Set(p.visualPlan?.required.map(s=>s.id)||p.scope.states.map(s=>s.id));
   const selected=(p.captures||[]).filter(c=>j.states.some(s=>s===c.id||(s===c.scenarioId&&required.has(c.id))));
   for(const s of j.states)if(!selected.some(c=>c.id===s||c.scenarioId===s))throw Error('No captured state: '+s);
   item.states=selected.map(c=>c.id);
   for(const c of selected)if(!p.scope.states.some(s=>s.id===c.id))p.scope.states.push(p.machineStates.find(s=>s.id===c.id));
   for(const c of selected)item.evidence.push({kind:'visual',ref:c.screenshot,observation:j.note},{kind:'measurement',ref:c.measurement,observation:'Captured geometry, contrast and declared task access; visual judgment recorded separately.'});
   item.evidence.push(...(j.evidence||[]));
   if(j.status==='fail'&&(!j.severity||!j.diagnosis))throw Error('Failure needs severity and diagnosis');
  }
  p.items[p.items.indexOf(old)]=item;
 }
 // Preserve each prior checkpoint, including changed judgments.
 fs.copyFileSync(reviewPath,reviewPath+'.checkpoint-'+crypto.randomUUID()+'.json');write(reviewPath,p);
 return sessionStatus(reviewPath);
}
if(process.argv[1]===fileURLToPath(import.meta.url))try{
 const [cmd,a,b,c,d,e,...extra]=process.argv.slice(2);let result;
 if(extra.length)throw Error('Unexpected arguments');
 if(cmd==='capture'&&a&&b&&c&&d){const plan=(await import(pathToFileURL(path.resolve(c)).href)).default;result=await captureReview({artifact:a,runtime:b,plan,output:d,executablePath:e});}
 else if(cmd==='detail'&&a&&b&&c)result=await detailPacket({reviewPath:a,captureId:b,runtime:c,page:d&&d!=='sample'?Number(d):'sample',executablePath:e});
 else if(cmd==='status'&&a&&!b)result=sessionStatus(a);
 else if(cmd==='packet'&&a&&!e)result=reviewPacket(a,b,c?Number(c):1);
 else if(cmd==='record'&&a&&b&&!c)result=recordJudgments(a,read(b));
 else throw Error('Usage: review-session.mjs capture APP PLAYWRIGHT PLAN.mjs NEW_DIR [CHROME] | detail REVIEW.json CAPTURE_ID PLAYWRIGHT_PATH [PAGE] [CHROME] | packet REVIEW.json [TOPIC] [PAGE] | status REVIEW.json | record REVIEW.json JUDGMENTS.json');
 console.log(JSON.stringify(result,null,2));
}catch(e){console.error(e.message);process.exitCode=1;}
