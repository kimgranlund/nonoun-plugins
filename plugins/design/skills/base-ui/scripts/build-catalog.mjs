import fs from 'node:fs';import path from 'node:path';
import {collectCatalog,describeKit} from './api.mjs';
const [output,playwright,...extra]=process.argv.slice(2);
if(!output||!playwright||extra.length)throw Error('Usage: build-catalog.mjs NEW_JSON PLAYWRIGHT');
if(fs.existsSync(output))throw Error('Output exists; preserve previous evidence');
const kit=describeKit(),catalog=await collectCatalog({playwright});
const serialize=(k,v)=>v instanceof Map?Object.fromEntries(v):v instanceof Set?[...v]:v;
fs.writeFileSync(output,JSON.stringify({schemaVersion:1,kit,scope:'Source-derived UI catalog data; no review delivery status or historical acceptance.',catalog},serialize,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({output,tokens:catalog.tokens.length,families:catalog.components.families.length}));
