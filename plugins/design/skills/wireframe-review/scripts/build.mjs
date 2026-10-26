#!/usr/bin/env node
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import vm from 'node:vm';
import {staticReview} from './static-review.mjs';
import {loadUI,takeKitOption} from './ui-kit.mjs';
import {dirname,resolve,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {authoredStyles,inspectStyles} from './token-inspection.mjs';
import {validateManifest,validateReview} from '../assets/model.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const args=process.argv.slice(2), kitPath=takeKitOption(args), ci=args.indexOf('--controller');
let controllerPath=null;if(ci>=0){controllerPath=args[ci+1];if(!controllerPath)throw Error('--controller requires a JavaScript file');args.splice(ci,2);}
const [source,destination,reviewPath]=args;
if(!source||!destination){console.error('Usage: node build.mjs manifest.json wireframes.html [review.json] [--controller controller.js]');process.exit(2);}
try{
  const kit=await loadUI(kitPath),bundle=kit.api.getAssetBundle(),compileControls=kit.api.compileControls; 
  const read=p=>readFileSync(join(root,p),'utf8'),manifestSchema=JSON.parse(read('references/manifest.schema.json')),feedbackSchema=JSON.parse(read('references/feedback.schema.json'));
  const manifest=validateManifest(JSON.parse(readFileSync(source,'utf8')),manifestSchema);
  const unknown=inspectStyles([manifest.css||'',...manifest.units.flatMap(u=>u.variants.flatMap(v=>authoredStyles(v.html||'')))],kit.api.createIndex());if(unknown.length)throw Error(`Unresolved token references: ${unknown.join(', ')}. Read scripts/generate-token-index.mjs --group before rebuilding.`);
  for(const unit of manifest.units)for(const variant of unit.variants)variant.html=compileControls(variant.html);
  const review=reviewPath?validateReview(JSON.parse(readFileSync(reviewPath,'utf8')),feedbackSchema,manifest):null;
  const json=value=>JSON.stringify(value).replace(/</g,'\\u003c').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');
  const declarations=`const UI_KIT=${json(kit.identity)};\nconst MANIFEST=${json(manifest)};\nconst FEEDBACK_SCHEMA=${json(feedbackSchema)};\nconst INITIAL_REVIEW=${json(review)};\nconst WIREFRAME_CSS=${json(bundle.css)};\n`;
  const controller=controllerPath?readFileSync(controllerPath,'utf8'):'';
  const script=declarations+bundle.controlMarkup+'\n'+bundle.runtime+'\n'+read('assets/review-runtime-adapter.js')+'\n'+controller+'\n'+read('assets/model.mjs').replace(/^export /gm,'')+'\n'+read('assets/app.mjs');
  new vm.Script(script,{filename:'assembled-wireframe.js'});
  const safeScript=script.replace(/<\/script/gi,'<\\/script');
  new vm.Script(safeScript,{filename:'escaped-wireframe.js'});
  const html=compileControls(read('assets/shell.html')).replace('@@STYLE@@',()=>bundle.foundationCSS+'\n'+read('assets/shell.css')).replace('@@SCRIPT@@',()=>safeScript).replace('@@STATIC@@',()=>staticReview(manifest,bundle.css));
  const localized=html.replace('<html lang="en"',`<html lang="${manifest.language||'en'}"`);
  mkdirSync(dirname(resolve(destination)),{recursive:true});writeFileSync(destination,localized);
  console.log(`Compiled draft (delivery requires generate.mjs): ${resolve(destination)} (${manifest.units.length} decision units, ${manifest.units.reduce((n,u)=>n+u.variants.length,0)} proposals)`);
}catch(e){console.error(e.message);process.exit(1);}
