// Dependency and preservation checks; browser behavior needs a rendered artifact.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
const root=path.resolve(import.meta.dirname,'..'),work=fs.mkdtempSync('/private/tmp/component-variants-build-check-');
const fixture=path.join(work,'component-variants'),source=path.join(work,'source');
fs.mkdirSync(source);fs.writeFileSync(path.join(source,'review.mjs'),'export default {};\n');fs.writeFileSync(path.join(source,'preview.html'),'<p>Baseline stays unchanged</p>');
for(const file of ['scripts/build.mjs','assets/review.html','assets/shell.css','assets/preview.css','assets/review-support.mjs','ui-kit.lock.json']){const target=path.join(fixture,file);fs.mkdirSync(path.dirname(target),{recursive:true});fs.copyFileSync(path.join(root,file),target)}
fs.symlinkSync(path.resolve(root,'../base-ui'),path.join(work,'base-ui'),'dir');
const run=name=>spawnSync(process.execPath,[path.join(fixture,'scripts/build.mjs'),source,path.join(work,name)],{encoding:'utf8'});
let result=run('valid');assert.equal(result.status,0,result.stderr);
assert.equal(fs.readFileSync(path.join(work,'valid/preview.html'),'utf8'),fs.readFileSync(path.join(source,'preview.html'),'utf8'));
assert(fs.readFileSync(path.join(work,'valid/review-support.mjs')).equals(fs.readFileSync(path.join(root,'assets/review-support.mjs'))));
const original=fs.readFileSync(path.join(work,'valid/index.html'));assert.notEqual(run('valid').status,0);assert(fs.readFileSync(path.join(work,'valid/index.html')).equals(original));
fs.writeFileSync(path.join(source,'index.html'),'reserved');assert.notEqual(run('reserved').status,0);assert(!fs.existsSync(path.join(work,'reserved')));fs.unlinkSync(path.join(source,'index.html'));
fs.writeFileSync(path.join(source,'bad.mjs'),"import {phosphorIcon} from '../review-support.mjs';");assert.match(run('bad-import').stderr,/Missing local asset/);assert(!fs.existsSync(path.join(work,'bad-import')));fs.writeFileSync(path.join(source,'bad.mjs'),"import {phosphorIcon} from './review-support.mjs';");assert.equal(run('supplied-import').status,0);fs.unlinkSync(path.join(source,'bad.mjs'));
const lockFile=path.join(fixture,'ui-kit.lock.json'),lock=fs.readFileSync(lockFile,'utf8');fs.writeFileSync(lockFile,lock.replace(/"contentSHA256": "[^"]+"/,'"contentSHA256": "wrong"'));result=run('mismatch');assert.notEqual(result.status,0);assert.match(result.stderr,/lock mismatch/);assert(!fs.existsSync(path.join(work,'mismatch')));fs.writeFileSync(lockFile,lock);
fs.unlinkSync(path.join(work,'base-ui'));result=run('missing');assert.notEqual(result.status,0);assert.match(result.stderr,/Install compatible base-ui/);assert(!fs.existsSync(path.join(work,'missing')));
console.log('PASS build, unchanged preview/helper, no overwrite, reserved name, lock mismatch and missing-kit guards. Evidence: '+work);
