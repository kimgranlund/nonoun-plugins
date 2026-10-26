import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {root,createIndex,tokenCheck,sha} from './token-index.mjs';
import {compileControls} from './compile-controls.mjs';
import {authoredStyles,inspectStyles} from './token-inspection.mjs';

const out=fs.mkdtempSync(path.join(os.tmpdir(),'wireframe-token-membership-'));
const base=JSON.parse(fs.readFileSync(path.join(root,'assets/example.manifest.json')));
for(const u of base.units)for(const v of u.variants)v.html=compileControls(v.html);
const index=createIndex(),results=[];
function run(script,args){const r=spawnSync(process.execPath,[path.join(root,'scripts',script),...args],{encoding:'utf8'});assert.ifError(r.error);assert.equal(r.signal,null);return r;}
const cases=[
 ['known','.probe{color:var(--ui-ink,var(--ui-ink))}',null],
 ['local',':root{--optional-brand:var(--ui-ink)}.probe{color:var(--optional-brand,#fff)}',null],
 ['comment','/* .probe{color:var(--md-invented,#fff)} */',null],
 ['literal-fallback','.probe{color:var(--md-invented,#fff)}','--md-invented'],
 ['nested-fallback','.probe{color:var(--md-invented,var(--ui-ink))}','--md-invented'],
 ['nested-unknown','.probe{color:var(--ui-ink,var(--md-invented,#fff))}','--md-invented'],
 ['plain-unknown','.probe{color:var(--md-invented)}','--md-invented']
];
// Each fault reaches both manifest CSS and variant inline-style authoring paths.
for(const [name,css,missing]of cases)for(const region of ['css','html']){
 const id=name+'-'+region,m=structuredClone(base),dir=path.join(out,id);fs.mkdirSync(dir);
 const html=region==='html'?`<style>${css}</style><span style="color:var(--ui-ink)">Example</span>`:'';
 if(region==='css')m.css=(m.css||'')+'\n'+css;else m.units.find(u=>u.variants.some(v=>v.html)).variants[0].html+=html;
 const mp=path.join(dir,'manifest.json'),artifact=path.join(dir,'artifact.html'),report=path.join(dir,'report.json'),standalone=path.join(dir,'source.html');
 fs.writeFileSync(mp,JSON.stringify(m));fs.writeFileSync(standalone,region==='css'?`<style>${css}</style>`:html);
 assert.deepEqual(tokenCheck(m,index),missing?[missing]:[]);
 const build=run('build.mjs',[mp,artifact]);assert.equal(build.status,missing?1:0,build.stderr);
 const standaloneRun=run('check-standalone-token-refs.mjs',[standalone]);assert.equal(standaloneRun.status,missing?1:0,standaloneRun.stderr);
 assert.deepEqual(JSON.parse(standaloneRun.stdout).unresolved,missing?[missing]:[]);
 if(missing){
  assert(build.stderr.includes('Unresolved token references: '+missing));assert(!fs.existsSync(artifact));
  // Build a valid artifact, then change its embedded manifest to match the fault.
  // This isolates token rejection from artifact-binding and foundation failures.
  const clean=path.join(dir,'clean.json');fs.writeFileSync(clean,JSON.stringify(base));
  const valid=run('build.mjs',[clean,artifact]);assert.equal(valid.status,0,valid.stderr);
  const json=JSON.stringify(m).replace(/</g,'\\u003c');
  fs.writeFileSync(artifact,fs.readFileSync(artifact,'utf8').replace(/const MANIFEST=.*;\n/,()=>`const MANIFEST=${json};\n`));
 }
 const verify=run('verify-artifact.mjs',[mp,artifact,report]);assert.equal(verify.status,missing?1:0,verify.stderr);
 const checks=JSON.parse(fs.readFileSync(report)).checks;
 assert.deepEqual(checks.filter(c=>c.status==='fail').map(c=>c.id),missing?['token-references']:[]);
 results.push({id,expectedUnknown:missing,buildExit:build.status,standaloneExit:standaloneRun.status,verifierExit:verify.status});
}
const snippets='<pre><code>&lt;style&gt;var(--md-invented)&lt;/style&gt;</code></pre><script>const s="var(--md-invented)";</script><!-- <style>.x{color:var(--md-invented)}</style> --><p>var(--md-invented)</p>';
assert.deepEqual(authoredStyles(snippets),[]);
const snippetManifest=structuredClone(base);snippetManifest.units.find(u=>u.variants.some(v=>v.html)).variants[0].html+=snippets;
assert.deepEqual(tokenCheck(snippetManifest,index),[]);
assert.deepEqual(inspectStyles(authoredStyles('<span style="color:var(--md-invented,#fff)">X</span>'),index),['--md-invented']);
const selftest=run('check-standalone-token-refs.mjs',['--selftest']);assert.equal(selftest.status,0,selftest.stderr);
const files=['scripts/token-inspection.mjs','scripts/token-index.mjs','scripts/check-standalone-token-refs.mjs','scripts/check-token-membership.mjs','scripts/build.mjs','scripts/verify-artifact.mjs'];
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({results,snippetExclusion:true,inlineFallbackDetection:true,standaloneSelftest:true,sources:Object.fromEntries(files.map(f=>[f,sha(fs.readFileSync(path.join(root,f)))])),limitations:['Lexical membership only; no browser or cascade verification','Fault artifacts deliberately bind a changed manifest to isolate verifier token rejection']},null,2));
console.log(`PASS ${results.length} real-entry-point cases, snippet exclusion, inline fallback and standalone selftest. Evidence: ${out}`);
