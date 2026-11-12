#!/usr/bin/env node
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),leaf=resolve(root,'references/style/select');
const contract=JSON.parse(readFileSync(resolve(leaf,'contract.json')));assert.equal(contract.schemaVersion,1,'Unsupported select contract version');
for(const p of contract.dependencies)assert(existsSync(resolve(leaf,p)),`Missing dependency: ${p}`);
const paths=['assets/recipes/native-select.html','references/style/select/contract.json','references/style/bootstrap.md','assets/control-markup.mjs','scripts/compile-controls.mjs','assets/wireframe.css','assets/foundation/maison/geometry.css','assets/foundation/maison/layout.css','assets/foundation/ultimate-tokens/colors.css'];
const source=readFileSync(resolve(root,'assets/control-markup.mjs'),'utf8');assert(source.includes('export function createSelectControl'), 'Explicit control builder missing');
const observation={schemaVersion:1,generatedBy:{name:'observe-select',version:1},id:contract.id,sources:paths.map(path=>({path,sha256:createHash('sha256').update(readFileSync(resolve(root,path))).digest('hex')})),bindings:{authored:'assets/recipes/native-select.html',compiler:'scripts/compile-controls.mjs',dynamicBuilder:'assets/control-markup.mjs#createSelectControl',presentation:'assets/wireframe.css',discovery:'references/style/discovery.json'},support:{source:'observed',browser:'requires separate check-select-contract report',installedPackage:'not evaluated'}};
const dest=resolve(leaf,'observation.json'),bytes=JSON.stringify(observation,null,2)+'\n';
if(process.argv.includes('--check'))assert.equal(readFileSync(dest,'utf8'),bytes,'Stale select observations; regenerate');else writeFileSync(dest,bytes);
console.log('Select dependency and source observation checks passed');
