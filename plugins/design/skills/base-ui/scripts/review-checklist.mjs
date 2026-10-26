// Records review coverage; cannot certify the truth of a visual judgment.
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
const catalog=JSON.parse(fs.readFileSync(new URL('../references/review/rubrics.json',import.meta.url),'utf8'));
const all=catalog.topics.flatMap(t=>t.checks);
const text=v=>typeof v==='string'&&v.trim().length>0;
export function validateReview(p){
 const errors=[];const need=(ok,msg)=>{if(!ok)errors.push(msg)};
 need(p?.schemaVersion===1,'schemaVersion must be 1');
 for(const k of ['artifact','task','reviewer'])need(text(p?.scope?.[k]),'scope.'+k+' required');
 need(['ui','image'].includes(p?.scope?.kind),'scope.kind must be ui or image');
 const states=Array.isArray(p?.scope?.states)?p.scope.states:[];
 need(states.length>0,'scope.states required');
 const stateIds=states.map(s=>s.id);need(new Set(stateIds).size===states.length,'duplicate state IDs');
 for(const s of states)need(text(s.id)&&text(s.description),'each state needs id and description');
 const items=Array.isArray(p?.items)?p.items:[];const ids=items.map(i=>i.id);
 need(ids.length===all.length&&new Set(ids).size===all.length&&all.every(c=>ids.includes(c.id)),'items must contain every catalog check exactly once');
 for(const i of items){
  const prefix=i.id+': ';
  need(['unreviewed','pass','fail','na','blocked'].includes(i.status),prefix+'invalid status');
  if(i.status==='unreviewed')continue;
  need(text(i.note),prefix+'review observation or reason required');
  if(['na','blocked'].includes(i.status))continue;
  need(Array.isArray(i.states)&&i.states.length>0&&i.states.every(s=>stateIds.includes(s)),prefix+'known reviewed state IDs required');
  need(Array.isArray(i.evidence)&&i.evidence.length>0&&i.evidence.every(e=>['visual','dom','interaction','measurement','source'].includes(e.kind)&&text(e.ref)&&text(e.observation)),prefix+'evidence kind, ref and observation required');
  if(i.status==='fail'){
   need(['blocker','major','minor'].includes(i.severity),prefix+'severity required');
   for(const k of ['owner','cause','repair','recheck'])need(text(i.diagnosis?.[k]),prefix+'diagnosis.'+k+' required (state unknown if not established)');
   need(['confirmed','hypothesis','unknown'].includes(i.diagnosis?.confidence),prefix+'diagnosis confidence required');
  }
 }
 const counts=Object.fromEntries(['unreviewed','pass','fail','na','blocked'].map(s=>[s,items.filter(i=>i.status===s).length]));
 return {valid:!errors.length,complete:!errors.length&&!counts.unreviewed&&!counts.blocked,acceptance:errors.length?'invalid':counts.unreviewed||counts.blocked?'unverified':counts.fail?'changes-needed':'passed-in-recorded-scope',counts,errors};
}
function main(){
 const [cmd,arg,...extra]=process.argv.slice(2);
 if(extra.length && cmd!=='show')throw Error('Unexpected extra arguments');
 if(cmd==='topics'){console.log(catalog.topics.map(t=>`${t.id}: ${t.title} — ${t.when}`).join('\n'));return;}
 if(cmd==='show'){const ids=[arg,...extra];const topics=ids.map(id=>{const t=catalog.topics.find(t=>t.id===id);if(!t)throw Error('Unknown topic: '+id);return t;});const output=JSON.stringify(topics.length===1?topics[0]:{topics},null,2);if(Buffer.byteLength(output)>12000)throw Error('Review batch exceeds12000 bytes; request fewer topics');console.log(output);return;}
 if(cmd==='init'){
  if(!arg)throw Error('Provide a new output JSON path');
  fs.writeFileSync(arg,JSON.stringify({schemaVersion:1,scope:{artifact:'',kind:'ui',task:'',reviewer:'',states:[]},items:all.map(c=>({id:c.id,status:'unreviewed',states:[],evidence:[],note:''}))},null,2)+'\n',{flag:'wx'});console.log(arg);return;
 }
 if(cmd==='check'){
  const result=validateReview(JSON.parse(fs.readFileSync(arg,'utf8')));console.log(JSON.stringify(result,null,2));if(result.acceptance!=='passed-in-recorded-scope')process.exitCode=1;return;
 }
 throw Error('Usage: review-checklist.mjs topics | show TOPIC | init NEW.json | check REVIEW.json');
}
if(process.argv[1]===fileURLToPath(import.meta.url)){try{main()}catch(e){console.error(e.message);process.exitCode=1}}
