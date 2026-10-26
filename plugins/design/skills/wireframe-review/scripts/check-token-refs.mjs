import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {root,createIndex,tokenCheck} from './token-index.mjs';
const file=process.argv[2];if(!file)throw Error('Usage: check-token-refs.mjs MANIFEST');
const index=JSON.parse(fs.readFileSync(path.join(root,'references/style/token-index.json')));assert.deepEqual(index,createIndex(),'Stale token index; run generate-token-index.mjs');
const unresolved=tokenCheck(JSON.parse(fs.readFileSync(file)),index);console.log(JSON.stringify({file,unresolved},null,2));if(unresolved.length)process.exitCode=1;
