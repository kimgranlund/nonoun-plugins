import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import {createRequire}from'node:module';import {spawnSync}from'node:child_process';
import {root,sha}from'./token-index.mjs';import {inspectArtifact}from'./lib/artifact-lint.mjs';
const[input,pw,output,policyPath]=process.argv.slice(2);
if(!output)throw Error('Usage: lint-artifact.mjs HTML_OR_MANIFEST PLAYWRIGHT NEW_REPORT [POLICY_JSON]');
if(fs.existsSync(output))throw Error('Preserve reports; choose a new path');
const bytes=fs.readFileSync(input),policy=policyPath?JSON.parse(fs.readFileSync(policyPath)): {deferredReferences:[]};
if(Object.keys(policy).some(k=>k!=='deferredReferences')||!Array.isArray(policy.deferredReferences))throw Error('Policy requires deferredReferences only');
for(const w of policy.deferredReferences){if(Object.keys(w).sort().join()!==['attribute','document','reason','selector','state','target'].sort().join()||Object.values(w).some(v=>typeof v!=='string'||!v.trim())||!['for','aria-labelledby','aria-describedby','aria-controls','popovertarget'].includes(w.attribute))throw Error('Each deferral requires document, selector, attribute, target, reason and state');}
let html=bytes.toString(),temporary;
if(path.extname(input)==='.json'){
 temporary=fs.mkdtempSync(path.join(os.tmpdir(),'wireframe-lint-build-'));const artifact=path.join(temporary,'artifact.html');
 const result=spawnSync(process.execPath,[path.join(root,'scripts/build.mjs'),input,artifact],{encoding:'utf8'});
 if(result.status!==0)throw Error('Build prerequisite failed: '+result.stderr);html=fs.readFileSync(artifact,'utf8');
}
const contractPath=path.join(root,'references/style/components/contract.json'),contract=JSON.parse(fs.readFileSync(contractPath));
const ownedClasses=[...new Set([...contract.families,...contract.classGroups].flatMap(g=>g.classes))];
const styleSources=['assets/foundation/ultimate-tokens/colors.css','assets/foundation/ultimate-tokens/typography.css','assets/foundation/maison/geometry.css','assets/foundation/maison/layout.css','assets/wireframe.css','assets/shell.css'];
const trustedStyles=styleSources.map(f=>fs.readFileSync(path.join(root,f),'utf8'));
const browser=await createRequire(import.meta.url)(pw).chromium.launch();let result;
try{const context=await browser.newContext({javaScriptEnabled:false});await context.route('**/*',r=>r.abort());const page=await context.newPage();
 result=await page.evaluate(({fn,args})=>(0,eval)('('+fn+')')(args),{fn:inspectArtifact.toString(),args:{html,policy,ownedClasses,trustedStyles}});
 result.browser=browser.version();
}finally{await browser.close();}
const sources=[...styleSources,'scripts/lint-artifact.mjs','scripts/lib/artifact-lint.mjs','references/style/components/contract.json'];
const report={...result,input:{path:path.resolve(input),sha256:sha(bytes)},inspectedHtmlSHA256:sha(html),policy:policyPath?{path:path.resolve(policyPath),sha256:sha(fs.readFileSync(policyPath))}:null,sources:Object.fromEntries(sources.map(f=>[f,sha(fs.readFileSync(path.join(root,f)))])),limitations:['Parsed initial documents only; scripts are not executed','Style warnings are advisory; no cascade, visual, keyboard or accessibility certification','External styles/documents, shadow roots and runtime states need separate verification'],temporaryBuild:temporary||null};
fs.mkdirSync(path.dirname(path.resolve(output)),{recursive:true});fs.writeFileSync(output,JSON.stringify(report,null,2));
const errors=result.findings.filter(f=>f.severity==='error').length;console.log(JSON.stringify({report:output,documents:result.documents.length,errors,warnings:result.findings.filter(f=>f.severity==='warning').length,unverified:result.findings.filter(f=>f.severity==='unverified').length}));if(errors)process.exitCode=1;
