import fs from 'node:fs';import path from 'node:path';import vm from 'node:vm';import {compileControls,describeKit,getAssetBundle,validateUI} from './api.mjs';
const [source,destination,scriptPath]=process.argv.slice(2);if(!source||!destination)throw Error('Usage: build.mjs FRAGMENT.html NEW_ARTIFACT.html [CONTROLLER.js]');
if(fs.existsSync(destination+'.review-status.json'))throw Error('Review status sidecar already exists; use a new destination');
const identity=describeKit(),bundle=getAssetBundle(),fragment=fs.readFileSync(source,'utf8'),missing=validateUI({html:fragment}).unknownTokens;if(missing.length)throw Error('Unknown UI tokens: '+missing.join(', '));
const js=bundle.runtime+'\n'+(scriptPath?fs.readFileSync(scriptPath,'utf8'):'');new vm.Script(js);
const safe=s=>s.replace(/<\/script/gi,'<\\/script'),meta=JSON.stringify(identity).replace(/</g,'\\u003c');
const html='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>UI specimen</title><style>'+bundle.css+'</style><body class="product__root">'+compileControls(fragment)+'<script type="application/json" id="base-ui-source">'+meta+'</script><script>'+safe(js)+'</script></body></html>';
fs.mkdirSync(path.dirname(path.resolve(destination)),{recursive:true});fs.writeFileSync(destination,html,{flag:'wx'});console.log(destination);
console.error('Rendered application verification required: run scripts/audit-rendered.mjs on this artifact and audit relevant dynamic states. Build success checks tokens/syntax and declared static anatomy, not dynamic DOM or rendered geometry. See references/rendered-audit.md.');

fs.writeFileSync(destination+'.review-status.json',JSON.stringify({status:'pending-review',artifact:path.resolve(destination),next:'review-session.mjs capture ARTIFACT PLAYWRIGHT PLAN.mjs NEW_EVIDENCE_DIR [CHROME]',contract:'references/review/delivery.md'},null,2)+'\n',{flag:'wx'});
console.error('Draft only: review status persisted at '+destination+'.review-status.json. Use review-session.mjs capture for app-state matrix evidence, inspect and record topic judgments until its status queue is empty, then finish through the delivery gate. See references/review/session.md. For edits, build to a new revision filename and preserve this draft/sidecar.');
