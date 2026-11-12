// Dependency and preservation checks; browser behavior needs a rendered artifact.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
const root=path.resolve(import.meta.dirname,'..'),work=fs.mkdtempSync('/private/tmp/component-variants-build-check-');
const fixture=path.join(work,'component-variants'),source=path.join(work,'source');
fs.mkdirSync(source);fs.writeFileSync(path.join(source,'review.mjs'),'export default {};\n');fs.writeFileSync(path.join(source,'preview.html'),'<p>Baseline stays unchanged</p>');
for(const dir of ['scripts','assets'])fs.cpSync(path.join(root,dir),path.join(fixture,dir),{recursive:true});
const geometry=path.join(work,'ui-geometry');fs.symlinkSync(path.resolve(root,'../ui-geometry'),geometry,'dir');
const run=name=>spawnSync(process.execPath,[path.join(fixture,'scripts/build.mjs'),source,path.join(work,name)],{encoding:'utf8'});
let result=run('valid');assert.equal(result.status,0,result.stderr);
assert.equal(fs.readFileSync(path.join(work,'valid/preview.html'),'utf8'),fs.readFileSync(path.join(source,'preview.html'),'utf8'));
assert(fs.readFileSync(path.join(work,'valid/review-support.mjs')).equals(fs.readFileSync(path.join(root,'assets/review-support.mjs'))));
assert(!fs.existsSync(path.join(work,'valid/ui-kit.lock.json')));
// Geometry in the page is the derive output, not a copied number.
const index=fs.readFileSync(path.join(work,'valid/index.html'),'utf8');
const rows=JSON.parse(spawnSync(process.execPath,[path.join(geometry,'scripts/derive.mjs'),'--json','--n','14','--density','default','--kappa','0.75','--kappa-card','0.5','--card','4'],{encoding:'utf8'}).stdout);
const px=(tier,symbol)=>rows.find(r=>r.tier===tier&&r.symbol===symbol).px;
assert(index.includes(`--g-height: ${px('controls','h')}px;`));assert(index.includes(`--g-inset: ${px('controls','I')}px;`));assert(index.includes(`--r-card: ${px('containers','R card-3  κ=0.5')}px;`));
assert.match(index,/<span class="select__root"><select id="theme">[\s\S]*?<\/select><span data-slot="indicator"/);assert.match(index,/\.select__root\{position:relative/);assert(!index.includes('.select-control'));assert.match(index,/\.select__root \[data-slot="indicator"\]\{position:absolute/);assert.match(index,/--md-color-primary:/);assert.match(index,/--type-body-lg-size:/);assert.match(index,/@font-face \{ font-family:"IBM Plex Mono"/);
const original=fs.readFileSync(path.join(work,'valid/index.html'));assert.notEqual(run('valid').status,0);assert(fs.readFileSync(path.join(work,'valid/index.html')).equals(original));
fs.writeFileSync(path.join(source,'index.html'),'reserved');assert.notEqual(run('reserved').status,0);assert(!fs.existsSync(path.join(work,'reserved')));fs.unlinkSync(path.join(source,'index.html'));
fs.writeFileSync(path.join(source,'bad.mjs'),"import {phosphorIcon} from '../review-support.mjs';");assert.match(run('bad-import').stderr,/Missing local asset/);assert(!fs.existsSync(path.join(work,'bad-import')));fs.writeFileSync(path.join(source,'bad.mjs'),"import {phosphorIcon} from './review-support.mjs';");assert.equal(run('supplied-import').status,0);fs.unlinkSync(path.join(source,'bad.mjs'));
const shell=path.join(fixture,'assets/shell.css'),shellText=fs.readFileSync(shell,'utf8');fs.writeFileSync(shell,shellText+'\nbody{gap:var(--not-in-kit)}');result=run('unknown-token');assert.notEqual(result.status,0);assert.match(result.stderr,/Unknown shell tokens: \["--not-in-kit"\]/);assert(!fs.existsSync(path.join(work,'unknown-token')));fs.writeFileSync(shell,shellText);
fs.unlinkSync(geometry);result=run('missing-geometry');assert.notEqual(result.status,0);assert.match(result.stderr,/Missing ui-geometry/);assert(!fs.existsSync(path.join(work,'missing-geometry')));fs.symlinkSync(path.resolve(root,'../ui-geometry'),geometry,'dir');
fs.rmSync(path.join(fixture,'assets/kit'),{recursive:true});result=run('missing-kit');assert.notEqual(result.status,0);assert.match(result.stderr,/Missing vendored kit/);assert(!fs.existsSync(path.join(work,'missing-kit')));
console.log('PASS build, derived geometry, unchanged preview/helper, no overwrite, reserved name, unknown token, missing ui-geometry and missing-kit guards. Evidence: '+work);
