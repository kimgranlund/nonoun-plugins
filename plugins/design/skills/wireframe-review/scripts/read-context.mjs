import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';
const args=process.argv.slice(2);const once=args.includes('--once');if(once)args.splice(args.indexOf('--once'),1);const usage='Usage: read-context.mjs CORPUS_ROOT RELATIVE_FILE APPEND_JSONL [START_LINE END_LINE MAX_BYTES | --section "Exact heading" [MAX_BYTES]] [--once]';
if(args[0]==='--help'){console.log(usage);process.exit(0);}
const[rootArg,relative,log,startArg='1',endArg,maxArg='12000']=args;if(!log)throw Error(usage);
const section=startArg==='--section'?endArg:null;if(startArg==='--section'&&!section)throw Error('Section heading required');
const root=fs.realpathSync(rootArg),source=fs.realpathSync(path.resolve(root,relative));if(source!==root&&!source.startsWith(root+path.sep))throw Error('Source escapes corpus root');const logPath=path.join(fs.realpathSync(path.dirname(path.resolve(log))),path.basename(log));if(logPath===root||logPath.startsWith(root+path.sep))throw Error('Keep read logs outside the corpus');const bytes=fs.readFileSync(source),text=bytes.toString('utf8');if(text.includes('\u0000'))throw Error('Text files only');const lines=text.split('\n');let start=Number(startArg),end=endArg?Number(endArg):lines.length;const max=Number(maxArg);
if(section){
 const headings=[];let fence=null;
 for(let i=0;i<lines.length;i++){
  const code=lines[i].match(/^ {0,3}(`{3,}|~{3,})/);
  if(code){if(!fence)fence=code[1];else if(code[1][0]===fence[0]&&code[1].length>=fence.length)fence=null;continue;}
  if(fence)continue;
  const h=lines[i].match(/^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$/);if(h)headings.push({line:i+1,level:h[1].length,title:h[2]});
 }
 const matches=headings.filter(h=>h.title===section);if(matches.length!==1)throw Error('Section must match exactly one Markdown heading');
 const h=matches[0];start=h.line;end=(headings.find(n=>n.line>h.line&&n.level<=h.level)?.line||lines.length+1)-1;
}
if(!Number.isInteger(start)||start<1||start>lines.length||!Number.isInteger(end)||end<start||!Number.isInteger(max)||max<1)throw Error('Invalid read bounds');const selected=lines.slice(start-1,end).join('\n');const sourceSHA256=crypto.createHash('sha256').update(bytes).digest('hex');if(once&&fs.existsSync(log)){const prior=fs.readFileSync(log,'utf8').trim().split('\n').filter(Boolean).map(l=>JSON.parse(l)).find(r=>r.path===path.relative(root,source)&&r.sourceSHA256===sourceSHA256&&r.requested.start===start&&r.requested.end===end&&!r.truncated&&typeof r.content==='string');if(prior){process.stdout.write(JSON.stringify({version:1,path:prior.path,reused:true,sourceSHA256,returnedSHA256:prior.returnedSHA256,returnedBytes:0,priorReturnedBytes:prior.returnedBytes,requested:prior.requested,contentAlreadyReturnedInSession:true,scope:'Reuse this same session log only; no content omitted on a changed source or incomplete read.'})+'\n');process.exit(0);}}let content=selected;if(Buffer.byteLength(content)>max){content=Buffer.from(content).subarray(0,max).toString('utf8');while(Buffer.byteLength(content)>max)content=content.slice(0,-1);}const sha=s=>crypto.createHash('sha256').update(s).digest('hex');const record={version:1,path:path.relative(root,source),requested:{start,end,maxBytes:max,...(section?{section}:{})},availableLines:lines.length,returnedBytes:Buffer.byteLength(content),truncated:content!==selected,sourceSHA256:sha(bytes),returnedSHA256:sha(content),content,transportTruncation:'unknown: inspect tool response separately',tokenCount:null};fs.appendFileSync(log,JSON.stringify(record)+'\n');process.stdout.write(JSON.stringify(record,null,2)+'\n');
