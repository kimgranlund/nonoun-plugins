import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
test('generated preview provenance and current module parity',async()=>{
 const read=p=>readFile(new URL('../'+p,import.meta.url),'utf8');
 const manifest=JSON.parse(await read('system.manifest.json'));
 const source=await read('specimens/source.html'),css=await read('src/app.css'),app=await read('src/app.js');
 const hash=s=>createHash('sha256').update(s).digest('hex');
 assert.equal(manifest.source.fragmentSHA256,hash(source));assert.equal(manifest.source.implementationSHA256,hash(source+css+app));
 const html=await read('dist/index.html');assert.equal(html,await read('specimens/index.html'));
 assert.ok(!html.includes('runtime/study.mjs'));assert.ok(!html.includes('runtime/scale.mjs'));
 const built=await import('../dist/runtime/geometry/index.js');const shared=await import('../../differential-forms/geometry/index.ts');
 for(const density of ['compact','default','loose'])for(const border of [0,2])for(const name of ['resolveControl','resolveChip','resolveCollection','resolveCard','resolveComposite','resolveComposedInput','resolveMultiline'])assert.deepEqual(built[name]({density,border}),shared[name]({density,border}));
});
