import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';
const [before,after,standalone]=process.argv.slice(2);if(!before||!after||!standalone)throw Error('Usage: check-catalog-boundary.mjs BEFORE_SHEETS AFTER_SHEETS STANDALONE_JSON');
const json=p=>JSON.parse(fs.readFileSync(p)),hash=b=>createHash('sha256').update(b).digest('hex');
const a=json(path.join(before,'inventory.json')),b=json(path.join(after,'inventory.json')),kit=json(standalone);
function validate(a,b,kit){
 for(const key of ['tokens','components','pairs','counts','fullPageSpecimens'])assert.deepEqual(b[key],a[key],key+' changed across extraction');
 assert.deepEqual(kit.catalog.tokens,b.tokens);assert.deepEqual(kit.catalog.components.families,b.components);
 assert(!('workRegister' in kit.catalog)&&!('generationHistory' in kit.catalog),'Review data leaked into kit catalog');
 for(const s of b.sources){assert(s.owner==='base-ui'||s.owner==='wireframe-review');assert.equal(hash(fs.readFileSync(path.join(after,'sources',s.path))),s.sha256);assert.equal(hash(fs.readFileSync(path.join(b.sourceRoots[s.owner],s.path))),s.sha256);}
 for(const s of Object.values(b.fullPageSpecimens))assert.equal(hash(fs.readFileSync(path.join(after,s.path))),s.sha256);
}
validate(a,b,kit);
const altered=structuredClone(b);altered.tokens[0].name='--invented-token';assert.throws(()=>validate(a,altered,kit));
const leak=structuredClone(kit);leak.catalog.workRegister={};assert.throws(()=>validate(a,b,leak));
const wrongOwner=structuredClone(b);wrongOwner.sources.find(s=>s.path==='scripts/catalog.mjs').owner='wireframe-review';assert.throws(()=>validate(a,wrongOwner,kit));
console.log(JSON.stringify({pass:true,tokens:b.tokens.length,specimens:Object.keys(b.fullPageSpecimens).length,negativeControls:['token mutation','review-data leakage','wrong source owner'],scope:'Extraction and source parity; no new component behavioral certification'}));
