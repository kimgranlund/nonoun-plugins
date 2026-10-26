import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {root,createIndex} from './token-index.mjs';
const args=process.argv.slice(2);
if(args.length===1&&args[0]==='--help'){
  console.log('Usage: generate-token-index.mjs [--check | --group color|typography|geometry|layout|profile | --help]\nNo arguments: regenerate the index. Flags: read-only.');
  process.exit(0);
}
if(args.length&&!(args.length===1&&args[0]==='--check')&&!(args.length===2&&args[0]==='--group'))throw Error('Invalid arguments; use --help');
const index=createIndex(),file=path.join(root,'references/style/token-index.json');
if(args[0]==='--check')assert.deepEqual(JSON.parse(fs.readFileSync(file)),index,'Stale token index');
else if(args[0]==='--group'){const key=args[1];if(!Object.hasOwn(index.groups,key))throw Error('Unknown group');console.log(JSON.stringify(index.groups[key],null,2));}
else {throw Error('UI token index is owned by base-ui. Run ../base-ui/scripts/generate-token-index.mjs, verify, seal and synchronize.');}
