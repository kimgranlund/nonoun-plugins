import fs from 'node:fs';import path from 'node:path';import {spawnSync} from 'node:child_process';import {loadUI} from './ui-kit.mjs';
export async function runUICheck(name){
 const kit=await loadUI(),registry=JSON.parse(kit.api.readSource('references/checks.json'));
 if(!registry.checks.some(x=>x.script===name))throw Error('Unregistered base-ui check: '+name);
 const script=path.join(kit.root,'scripts',name);
 if(process.argv.slice(2).length===1&&process.argv[2]==='--describe-route'){console.log(JSON.stringify({owner:'base-ui',script,kit:kit.identity}));return;}
 const result=spawnSync(process.execPath,[script,...process.argv.slice(2)],{stdio:'inherit',env:process.env});
 if(result.error)throw result.error;
 if(result.signal)throw Error('UI check terminated by '+result.signal);
 process.exitCode=result.status??1;
}
