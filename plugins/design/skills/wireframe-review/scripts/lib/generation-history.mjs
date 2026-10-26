import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const required=(v,name)=>{if(typeof v!=='string'||!v.trim())throw Error('Required '+name);return v;};
function pointer(value,selection){
 if(selection==='')return value;
 if(typeof selection!=='string'||!selection.startsWith('/'))throw Error('Invalid JSON pointer');
 for(const raw of selection.slice(1).split('/')){const key=raw.replaceAll('~1','/').replaceAll('~0','~');if(value==null||!Object.hasOwn(value,key))throw Error('Missing evidence selection: '+selection);value=value[key];}
 return value;
}
// Historical data is external evidence, never a current-source verification report.
export function loadGenerationHistory(file,{evidenceRoot=path.dirname(file)}={}){
 const raw=fs.readFileSync(file),input=JSON.parse(raw),root=fs.realpathSync(evidenceRoot);
 if(input.schemaVersion!==1||input.kind!=='historical-generation-results'||!Array.isArray(input.records)||!input.records.length)throw Error('Unsupported/empty generation history');
 const snapshots=new Map(),ids=new Set();
 const read=ref=>{
  required(ref?.path,'evidence path');if(!/^[a-f0-9]{64}$/.test(ref.sha256??''))throw Error('Required evidence SHA-256');
  if(path.isAbsolute(ref.path)||ref.path.split(/[\\/]/).some(p=>p==='..'||p===''))throw Error('Evidence path escapes history bundle');
  const target=fs.realpathSync(path.resolve(root,ref.path));if(!target.startsWith(root+path.sep))throw Error('Evidence symlink escapes history bundle');
  const bytes=fs.readFileSync(target);if(sha(bytes)!==ref.sha256)throw Error('Evidence hash mismatch: '+ref.path);
  snapshots.set(ref.path,{bytes,sha256:ref.sha256});return bytes;
 };
 const records=input.records.map(r=>{
  if(!/^[\w-]+$/.test(r.id??'')||ids.has(r.id))throw Error('Missing/duplicate generation record ID');ids.add(r.id);
  for(const key of ['task','model','reasoningEffort','scope','limitations'])required(r[key],key);
  for(const key of ['task','model','reasoningEffort']){
   const selection=r.scopeEvidence?.[key];if(!selection)throw Error('Required scope evidence: '+key);
   const observed=pointer(JSON.parse(read(selection.source)),selection.pointer);if(observed!==r[key])throw Error('Scope evidence mismatch: '+key);
  }
  if(r.applicability!=='historical-cohort')throw Error('History cannot assert current-source acceptance');
  if(!Array.isArray(r.cohorts)||!r.cohorts.length||!Array.isArray(r.results)||!r.results.length)throw Error('Cohorts and result selections required');
  const cohortIds=new Set();const cohorts=r.cohorts.map(c=>{
   required(c.id,'cohort ID');if(cohortIds.has(c.id))throw Error('Duplicate cohort');cohortIds.add(c.id);
   const manifest=JSON.parse(read(c.manifest));const entries=Object.entries(manifest);
   if(!entries.length||entries.some(([p,h])=>!p||typeof h!=='string'||!/^[a-f0-9]{64}$/.test(h)))throw Error('Invalid frozen corpus manifest');
   return {id:c.id,files:entries.length,manifestPath:'review-inputs/generation-evidence/'+c.manifest.path,manifestSha256:c.manifest.sha256};
  });
  const results=r.results.map(s=>{required(s.label,'result label');const source=JSON.parse(read(s.source));return {label:s.label,value:pointer(source,s.pointer),pointer:s.pointer,path:'review-inputs/generation-evidence/'+s.source.path,sha256:s.source.sha256};});
  return {...Object.fromEntries(['id','task','model','reasoningEffort','scope','limitations','applicability'].map(k=>[k,r[k]])),cohorts,results};
 });
 return {raw,sha256:sha(raw),records,snapshots};
}
