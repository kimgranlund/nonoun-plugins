import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {root,sources,createIndex} from './token-index.mjs';

const temp=fs.mkdtempSync(path.join(os.tmpdir(),'token-index-cli-'));
const target=path.join(temp,'references/style/token-index.json');
const script=path.join(temp,'scripts/generate-token-index.mjs');
const run=args=>spawnSync(process.execPath,[script,...args],{encoding:'utf8'});
try {
  for(const relative of ['scripts/generate-token-index.mjs','scripts/token-index.mjs','scripts/token-inspection.mjs',...Object.values(sources)]){
    const destination=path.join(temp,relative);
    fs.mkdirSync(path.dirname(destination),{recursive:true});
    fs.copyFileSync(path.join(root,relative),destination);
  }
  fs.mkdirSync(path.dirname(target),{recursive:true});
  // A stale sentinel makes any accidental regeneration observable.
  const sentinel='{"sentinel":"must remain unchanged"}\n';
  fs.writeFileSync(target,sentinel);
  const cases=[
    {args:['--help'],status:0},
    {args:['--group','color'],status:0},
    {args:['--check'],status:1},
    ...[['--offset','2'],['--limit','20'],['--unknown'],['--group'],['--group','missing'],['--group','toString'],['--check','--help'],['--help','extra'],['--group','color','extra']].map(args=>({args,status:1}))
  ];
  for(const {args,status} of cases){
    const result=run(args);
    assert.equal(result.status,status,`${args}: ${result.stderr}`);
    assert.equal(fs.readFileSync(target,'utf8'),sentinel,`${args} wrote the index`);
    if(args[0]==='--help'&&status===0)assert.match(result.stdout,/Usage:/);
    if(args[0]==='--group'&&status===0)assert.deepEqual(JSON.parse(result.stdout).names,createIndex().groups.color.names.slice(0,80));
  }
  const collected=[];let offset=0;do{const result=run(['--group','color','--offset',String(offset)]);assert.equal(result.status,0,result.stderr);const page=JSON.parse(result.stdout);assert(page.names.length<=80);assert(Buffer.byteLength(result.stdout)<5000);collected.push(...page.names);offset=page.nextOffset;}while(offset!==null);assert.deepEqual(collected,createIndex().groups.color.names);
  assert.equal(run([]).status,0);
  assert.deepEqual(JSON.parse(fs.readFileSync(target)),createIndex());
  assert.equal(run(['--check']).status,0);
  // The sentinel detector must reject the observed legacy help-write defect.
  fs.writeFileSync(target,sentinel);
  fs.writeFileSync(script,"import fs from 'node:fs';import path from 'node:path';import {root,createIndex} from './token-index.mjs';fs.writeFileSync(path.join(root,'references/style/token-index.json'),JSON.stringify(createIndex()));");
  assert.equal(run(['--help']).status,0);
  assert.throws(()=>assert.equal(fs.readFileSync(target,'utf8'),sentinel));
  console.log(`PASS ${cases.length} read-only/invalid CLI cases, regeneration, freshness, and legacy write fault`);
} finally {fs.rmSync(temp,{recursive:true,force:true});}
