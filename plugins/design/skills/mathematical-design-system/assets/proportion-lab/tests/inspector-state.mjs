import assert from 'node:assert/strict';
import {schema,validate,parseConfig,serialize} from '../dist/runtime/inspector-state.mjs';
const defaults=Object.fromEntries(Object.entries(schema).map(([k,p])=>[k,p.options?.[0]??(p.type?true:0)]));
assert(validate(defaults).every(c=>c.pass));
assert.deepEqual(parseConfig(serialize(defaults),defaults).cfg,defaults);
for(const cfg of [{controlAmount:101},{pageGutter:12},{density:'invalid'}])assert.throws(()=>parseConfig(JSON.stringify({v:3,cfg}),defaults));
for(const text of ['{','{"v":99,"cfg":{}}','{"v":3,"cfg":null}','{"v":3,"cfg":[]}'])assert.throws(()=>parseConfig(text,defaults));
assert.deepEqual(parseConfig('{"v":3,"cfg":{"controlAmount":"50","unknown":1}}',defaults).ignored,['controlAmount','unknown']);
assert(!validate({...defaults,controlAmount:NaN}).every(c=>c.pass));
assert(!validate({...defaults,controlAmount:Infinity}).every(c=>c.pass));
assert(validate({...defaults,controlAmount:100,controlRetained:100}).every(c=>c.pass),'Physical conflicts must not reject valid inputs');
console.log('Inspector configuration checks passed');

for(const key of ['wrapperGuides','centeringGuides','gutterGuides']){
 const cfg={...defaults,[key]:false};assert.deepEqual(parseConfig(serialize(cfg),defaults).cfg,cfg);
}
const oldGuides=parseConfig(JSON.stringify({v:3,cfg:{gutterGuides:false}}),defaults).cfg;
for(const key of ['wrapperGuides','centeringGuides'])assert.equal(oldGuides[key],false);
console.log('PASS independent guide persistence and old Gutters migration');

for(const key of ['avatarInherit','logoInherit'])assert.equal(parseConfig('{"v":3,"cfg":{"mediaInherit":true}}',defaults).cfg[key],true);
assert.equal(parseConfig('{"v":3,"cfg":{"mediaInherit":true,"logoInherit":false}}',defaults).cfg.logoInherit,false);
console.log('PASS legacy global media shape migrates to independent asset settings');

assert.deepEqual(parseConfig(JSON.stringify({v:3,cfg:{compensationGuides:true}}),defaults).cfg,defaults);
assert(!serialize(defaults).includes('compensationGuides'));
