import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';

const root=path.resolve(import.meta.dirname,'..');
const rules=[
  ['interest-invoker',/\b(?:interestfor|interesttarget)\s*=|setAttribute\(\s*['"](?:interestfor|interesttarget)['"]|\binterest-delay(?:-start|-end)?\s*:/i],
  ['customizable-select',/\bappearance\s*:\s*base-select\b|::picker\(\s*select\s*\)|<selectedcontent\b/i],
  ['css-carousel',/::scroll-(?:marker(?:-group)?|button)\b|\bscroll-marker-group\s*:/i]
];
const detect=text=>rules.filter(([,rule])=>rule.test(text)).map(([id])=>id);
const walk=dir=>fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);
const files=walk(path.join(root,'assets')).filter(file=>/\.(html|css|mjs|js)$/.test(file));
const violations=files.flatMap(file=>detect(fs.readFileSync(file,'utf8')).map(primitive=>({file:path.relative(root,file),primitive})));
assert.deepEqual(violations,[],'Experimental primitive adopted without promoting its owned support contract');
const faults=[['interest-invoker','<button interestfor="help">Help</button>'],['interest-invoker',"e.setAttribute('interesttarget','help')"],['customizable-select','select {appearance:base-select}'],['customizable-select','::picker(select) {}'],['css-carousel','li::scroll-marker {}'],['css-carousel','.gallery {scroll-marker-group:after}']];
for(const [id,text] of faults)assert(detect(text).includes(id));
assert.deepEqual(detect('<select><option>Interest in audio</option></select> .list {overflow:auto}'),[]);
console.log(JSON.stringify({files:files.length,violations,faultsDetected:faults.length,sourceHashes:Object.fromEntries(files.map(file=>[path.relative(root,file),createHash('sha256').update(fs.readFileSync(file)).digest('hex')])),scope:'Lexical adoption guard for named primitives in maintained assets. Custom tooltip semantics, computed behavior, generated consumer artifacts and browser/platform accessibility remain separately verified.'},null,2));
