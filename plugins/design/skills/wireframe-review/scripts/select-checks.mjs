import fs from 'node:fs';import path from 'node:path';import {fileURLToPath}from'node:url';import {root,sha}from'./token-index.mjs';
export function selectChecks(files){
 const checks=new Map(),manual=[];const add=(command,stage,file)=>{if(!checks.has(command))checks.set(command,{command,stage,reasons:[]});checks.get(command).reasons.push(file);};
 for(const file of files){let matched=false;const route=(condition,command,stage)=>{if(condition){matched=true;add(command,stage,file);}};
  route(/run-ui-check|check-ui-check-routing|references\/checks/.test(file),'node scripts/check-ui-check-routing.mjs','source');
  route(/ui-kit|ui-runtime|review-runtime-adapter|ui-compatibility|ui-kit.lock/.test(file),'node scripts/check-ui-kit.mjs PLAYWRIGHT NEW_OUTPUT','browser');
  route(/scripts\/(generate|check-generation-pipeline)\.mjs/.test(file),'node scripts/check-generation-pipeline.mjs PLAYWRIGHT','browser-parser');
  route(/workflow|assets\/recipes\/components\.(js|html)/.test(file),'node scripts/check-workflow-patterns.mjs PLAYWRIGHT NEW_OUTPUT','browser');
  route(/workflow|assets\/recipes\/components\.js/.test(file),'node scripts/check-workflow-controller.mjs PLAYWRIGHT NEW_OUTPUT','browser');
  route(/extended|assets\/recipes\/components\.(js|html)/.test(file),'node scripts/check-extended-patterns.mjs PLAYWRIGHT NEW_OUTPUT','browser');
  route(/extended|assets\/recipes\/components\.js/.test(file),'node scripts/check-extended-controller.mjs PLAYWRIGHT NEW_OUTPUT','browser');
  route(file.endsWith('.md'),'node scripts/check-corpus-graph.mjs','source');
  route(/token-(inspection|index)|token-membership|standalone-token-refs|verify-artifact|scripts\/build\.mjs/.test(file),'node scripts/check-token-membership.mjs','source');
  route(/artifact-lint|lint-artifact|select-checks|check-preventive/.test(file),'node scripts/check-preventive-lint.mjs PLAYWRIGHT','browser-parser');
  route(file.startsWith('assets/foundation/')||file==='assets/wireframe.css','node scripts/check-spacing.mjs PLAYWRIGHT','browser');
  route(file.startsWith('assets/foundation/')||file==='assets/wireframe.css','node scripts/check-heading-context.mjs PLAYWRIGHT OUTPUT','browser');
  route(file==='assets/wireframe.css'||file.startsWith('assets/foundation/'),'node scripts/check-components.mjs PLAYWRIGHT OUTPUT','browser');
  route(file.startsWith('assets/recipes/'),'node scripts/lint-artifact.mjs CHANGED_HTML PLAYWRIGHT NEW_REPORT','browser-parser');
  route(file==='references/style/components/contract.json','node scripts/check-implementation-ownership.mjs','source');
  if(file.startsWith('assets/recipes/')||file==='assets/wireframe.css'||file.startsWith('assets/foundation/'))manual.push({file,reason:'Also select affected state/behavior checks from references/workflows/build-checks.md; this selector is not an exhaustive dependency graph.'});
  if(!matched)manual.push({file,reason:'Unmapped change: consult references/workflows/build-checks.md before claiming coverage.'});
 }
 return {checks:[...checks.values()],manualReview:manual};
}
// Reuse eligibility requires caller-supplied complete dependencies and exact environment identity.
// It never changes report status or infers that a previous observation passed.
export function reuseEligibility(record,environment){
 if(!record||record.status!=='pass'||!record.scope||record.environment!==environment||!record.dependencies?.some(d=>d.kind==='source')||!record.dependencies?.some(d=>d.kind==='fixture'))return {eligible:false,reason:'Missing passing scope, source/fixture dependencies or matching environment'};
 const changed=[];for(const d of record.dependencies){if(!d.path||!d.sha256||!path.isAbsolute(d.path)||!fs.existsSync(d.path)||!fs.statSync(d.path).isFile()||sha(fs.readFileSync(d.path))!==d.sha256)changed.push(d.path||'(missing path)');}
 return {eligible:changed.length===0,changed,scope:record.scope,limitation:'Eligibility only for declared scope and dependencies; completeness must be reviewed. A report hash alone is insufficient.'};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const args=process.argv.slice(2),i=args.indexOf('--reuse');let reuse;
 if(i>=0){const[record,environment]=args.splice(i,3).slice(1);if(!environment)throw Error('--reuse RECORD_JSON ENVIRONMENT_ID');reuse=reuseEligibility(JSON.parse(fs.readFileSync(record)),environment);}
 if(!args.length)throw Error('Usage: select-checks.mjs SKILL_RELATIVE_CHANGED_PATH... [--reuse RECORD_JSON ENVIRONMENT_ID]');
 const files=args.map(f=>path.isAbsolute(f)?path.relative(root,f):f.replace(/^\.\//,''));
 console.log(JSON.stringify({...selectChecks(files),reuse,authority:'references/workflows/build-checks.md',limits:'Advisory selection only; commands are not executed and no previous result is marked passed.'},null,2));
}
