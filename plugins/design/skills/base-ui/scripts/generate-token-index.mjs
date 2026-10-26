import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {root,createIndex} from './token-index.mjs';
const args=process.argv.slice(2);const paginated=args.includes('--offset')||args.includes('--limit');let offset=0,limit=80;for(const flag of ['--offset','--limit']){const i=args.indexOf(flag);if(i>=0){const value=Number(args[i+1]);if(!Number.isInteger(value)||value<0||(flag==='--limit'&&(value<1||value>80)))throw Error('Invalid pagination; limit1–80, offset>=0');if(flag==='--offset')offset=value;else limit=value;args.splice(i,2);}}
if(args.length===1&&args[0]==='--help'){
  console.log('Usage: generate-token-index.mjs [--check | --group color|typography|geometry|layout|profile|palettes [--offset N] [--limit N] | --help]\nNo arguments: regenerate the index. Flags: read-only.');
  process.exit(0);
}
if(args.length&&!(args.length===1&&args[0]==='--check')&&!(args.length===2&&args[0]==='--group'))throw Error('Invalid arguments; use --help');
if(paginated&&args[0]!=='--group')throw Error('Pagination requires --group');
const index=createIndex(),file=path.join(root,'references/style/token-index.json');
if(args[0]==='--check')assert.deepEqual(JSON.parse(fs.readFileSync(file)),index,'Stale token index');
else if(args[0]==='--group'){const key=args[1];if(!Object.hasOwn(index.groups,key))throw Error('Unknown group');const group=index.groups[key],names=group.names.slice(offset,offset+limit);console.log(JSON.stringify({...group,names,total:group.names.length,offset,nextOffset:offset+names.length<group.names.length?offset+names.length:null}));}
else {fs.writeFileSync(file,JSON.stringify(index,null,2)+'\n');console.log('Generated token index');}
