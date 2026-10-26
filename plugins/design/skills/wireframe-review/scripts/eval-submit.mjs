// Atomic admission and sealed inputs; unrestricted same-user bypass is not prevented.
import fs from 'node:fs';import path from 'node:path';import{fileURLToPath}from'node:url';import{spawnSync}from'node:child_process';import{createHash}from'node:crypto';
const[attempt,...args]=process.argv.slice(2);if(!attempt||args.length<3)throw Error('Usage: eval-submit.mjs ATTEMPT_DIR MANIFEST NEW_OUTPUT PLAYWRIGHT [generate options]');
const receipt=path.resolve(attempt,'submission.json');fs.mkdirSync(path.dirname(receipt),{recursive:true});
const fd=fs.openSync(receipt,'wx'),start=Date.now();fs.writeFileSync(fd,JSON.stringify({status:'running',startedAt:new Date(start).toISOString(),args}));fs.closeSync(fd);
const sources=[],hash=b=>createHash('sha256').update(b).digest('hex');let run={status:1},inputChanged=false;
try{
 sources.push({role:'manifest',path:path.resolve(args[0])});const controller=args.indexOf('--controller');if(controller>=0)sources.push({role:'controller',path:path.resolve(args[controller+1])});
 const snapshot=path.resolve(attempt,'submission-source');fs.mkdirSync(snapshot);
 for(const source of sources){const bytes=fs.readFileSync(source.path);source.sha256=hash(bytes);source.snapshot=path.join(snapshot,source.role==='manifest'?'manifest.json':'controller.js');fs.writeFileSync(source.snapshot,bytes,{flag:'wx'});}
 run=spawnSync(process.execPath,[fileURLToPath(new URL('./generate.mjs',import.meta.url)),...args],{stdio:'inherit'});
 inputChanged=sources.some(s=>!fs.existsSync(s.path)||hash(fs.readFileSync(s.path))!==s.sha256);
}catch(error){run={status:1,error};console.error(error.message)}
const result={status:'complete',startedAt:new Date(start).toISOString(),elapsedMs:Date.now()-start,args,sources,inputChanged,exit:run.status,signal:run.signal,error:run.error?.message};const tmp=receipt+'.complete';fs.writeFileSync(tmp,JSON.stringify(result,null,2));fs.renameSync(tmp,receipt);process.exitCode=inputChanged?1:run.status??1;
