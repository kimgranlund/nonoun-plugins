#!/usr/bin/env node
import {readFileSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateManifest,validateReview} from '../assets/model.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const [input,manifestPath]=process.argv.slice(2);
if(!input){console.error('Usage: node validate.mjs manifest-or-feedback.json [manifest.json]');process.exit(2);}
try{
  const read=p=>JSON.parse(readFileSync(p,'utf8'));
  const ms=read(join(root,'references/manifest.schema.json')),fs=read(join(root,'references/feedback.schema.json'));
  const data=read(input);
  if(Object.prototype.hasOwnProperty.call(data,'units')){validateManifest(data,ms);console.log('PASS manifest shape, proposal identities, compositions, and element IDs');}
  else{const manifest=manifestPath?validateManifest(read(manifestPath),ms):null;validateReview(data,fs,manifest);console.log(manifest?'PASS feedback shape, choices, overrides, revision, and targets':'PASS feedback shape only; supply the matching manifest to check references');}
}catch(e){console.error(e.message);process.exit(1);}
