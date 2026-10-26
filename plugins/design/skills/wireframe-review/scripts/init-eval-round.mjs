#!/usr/bin/env node
import {loadUI} from './ui-kit.mjs';
import {readFileSync,writeFileSync,mkdirSync,existsSync,cpSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),[destination,model]=process.argv.slice(2);
if(!destination||!model)throw Error('Usage: init-eval-round.mjs NEW_OUTPUT MODEL_VERSION');
const out=resolve(destination);if(out===root||out.startsWith(root+'/'))throw Error('Evaluation output must be outside the skill');if(existsSync(out))throw Error('Output exists; preserve previous attempts');
const kit=await loadUI();if(out===kit.root||out.startsWith(kit.root+'/'))throw Error('Evaluation output must be outside base-ui');
mkdirSync(out,{recursive:true});
const tasks=JSON.parse(readFileSync(resolve(root,'evals/tasks.json')));
cpSync(root,resolve(out,'frozen-corpus'),{recursive:true});
cpSync(kit.root,resolve(out,'base-ui'),{recursive:true});
const hash=p=>createHash('sha256').update(readFileSync(resolve(root,p))).digest('hex');
writeFileSync(resolve(out,'round.json'),JSON.stringify({protocol:1,model,uiKit:kit.identity,settings:'Record exact sampling configuration before runs',taskHash:hash('evals/tasks.json'),planHash:hash('evals/plan.md'),status:'prepared, not executed'},null,2));
for(const task of tasks.development)for(const condition of ['A','B'])for(let repeat=1;repeat<=3;repeat++){
 const dir=resolve(out,condition,task.id,String(repeat));mkdirSync(dir,{recursive:true});
 writeFileSync(resolve(dir,'task.txt'),task.brief+'\n');writeFileSync(resolve(dir,'result.json'),JSON.stringify({condition,task:task.id,repeat,status:'not run',firstPass:null,corrections:null,contextBytes:null,retrievedPaths:[],checks:null,blindRatings:null},null,2));
}
console.log('Prepared 18 development runs and frozen corpus; holdouts remain unscheduled until candidate freeze.');
