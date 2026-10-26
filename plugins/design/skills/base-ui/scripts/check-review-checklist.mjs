import assert from 'node:assert/strict';
import fs from 'node:fs';
import {validateReview} from './review-checklist.mjs';
const catalog=JSON.parse(fs.readFileSync(new URL('../references/review/rubrics.json',import.meta.url)));
const record={schemaVersion:1,scope:{artifact:'fixture.html@sha256:test',kind:'ui',task:'Review fixture',reviewer:'fixture',states:[{id:'wide',description:'1440 light selected'}]},items:catalog.topics.flatMap(t=>t.checks.map(c=>({id:c.id,status:'pass',states:['wide'],note:'Fixture observation',evidence:[{kind:'visual',ref:'fixture.png',observation:'Fixture only; no actual visual acceptance claimed.'}]})))};
assert.equal(validateReview(record).acceptance,'passed-in-recorded-scope');
const mutate=f=>{const r=structuredClone(record);f(r);return validateReview(r)};
assert.equal(mutate(r=>r.items.pop()).valid,false);
assert.equal(mutate(r=>r.items[0].id=r.items[1].id).valid,false);
assert.equal(mutate(r=>r.items[0].evidence=[]).valid,false);
assert.equal(mutate(r=>r.items[0].states=['unseen']).valid,false);
assert.equal(mutate(r=>r.items[0].status='unreviewed').acceptance,'unverified');
assert.equal(mutate(r=>{r.items[0].status='blocked';r.items[0].note='Browser unavailable'}).complete,false);
assert.equal(mutate(r=>{r.items[0].status='na';r.items[0].note=''}).valid,false);
const failed=mutate(r=>Object.assign(r.items[0],{status:'fail',severity:'major',diagnosis:{owner:'parent grid',cause:'center alignment',confidence:'confirmed',repair:'group task controls',recheck:'inspect wrapped controls'}}));
assert.equal(failed.complete,true);assert.equal(failed.acceptance,'changes-needed');
assert.equal(mutate(r=>r.items[0].status='fail').valid,false);
console.log('PASS review checklist: complete failure remains changes-needed; missing evidence, unknown states, omitted/duplicate checks and unsupported acceptance rejected. Fixtures test record integrity, not visual quality.');

// CLI must never silently discard requested review topics.
const {spawnSync}=await import('node:child_process');
const cli=(...args)=>spawnSync(process.execPath,[new URL('./review-checklist.mjs',import.meta.url).pathname,...args],{encoding:'utf8'});
const batch=cli('show','purpose','layout','content');assert.equal(batch.status,0);assert.equal(JSON.parse(batch.stdout).topics.length,3);
assert.equal(JSON.parse(cli('show','purpose').stdout).id,'purpose');
assert.notEqual(cli('show','purpose','no-such-topic').status,0);
console.log('PASS multi-topic CLI, single-topic compatibility and invalid topic rejection');
