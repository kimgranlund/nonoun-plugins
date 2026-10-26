// Build a maintained shell around an authored review.mjs and local preview files.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'..');
const [sourceArg,outArg,...extra]=process.argv.slice(2);
if(!sourceArg||!outArg||extra.length)throw Error('Usage: node scripts/build.mjs SOURCE_DIRECTORY NEW_OUTPUT_DIRECTORY');
const source=fs.realpathSync(sourceArg),out=path.resolve(outArg),kitRoot=path.resolve(root,'../base-ui');
if(fs.existsSync(out)||out===source||out.startsWith(source+path.sep))throw Error('Use a fresh output directory outside the source directory');
if(!fs.existsSync(path.join(source,'review.mjs')))throw Error('Source directory needs review.mjs');
const reserved=['index.html','review-support.mjs','preview.css','ui-kit.lock.json'];
for(const name of reserved)if(fs.existsSync(path.join(source,name)))throw Error('Source uses reserved shell filename: '+name);
let api;try{api=await import(pathToFileURL(path.join(kitRoot,'scripts/api.mjs')))}catch(error){throw Error('Install compatible base-ui beside component-variants: '+error.message)}
const identity=api.describeKit(),lock=JSON.parse(fs.readFileSync(path.join(root,'ui-kit.lock.json')));
for(const key of ['packageId','version','runtimeApiVersion','contentSHA256'])if(identity[key]!==lock[key])throw Error('base-ui lock mismatch; review the kit update and explicitly update ui-kit.lock.json before building');
const read=name=>fs.readFileSync(path.join(root,'assets',name),'utf8');
const css=read('shell.css'),unknown=api.validateUI({css}).unknownTokens;
if(unknown.length)throw Error('Unknown shell tokens: '+JSON.stringify(unknown));
const html=api.compileControls(read('review.html')).replace('/* REVIEW_STYLE */',()=>api.getAssetBundle().foundationCSS+'\n'+css);
// Check literal local module imports and HTML assets. Dynamic URLs still need a browser check.
function checkFiles(dir){for(const entry of fs.readdirSync(dir,{withFileTypes:true})){
  const file=path.join(dir,entry.name);if(entry.isDirectory()){checkFiles(file);continue}
  if(!/\.(?:html|m?js)$/.test(file))continue;
  const text=fs.readFileSync(file,'utf8');
  const refs=[...text.matchAll(/\b(?:from\s*|import\s*(?:\(\s*)?)["'](\.{1,2}\/[^"']+)["']/g),...text.matchAll(/\b(?:src|href)=["'](\.{1,2}\/[^"']+)["']/g)];
  for(const match of refs){const target=path.resolve(path.dirname(file),match[1].split(/[?#]/)[0]);
    const supplied=['review-support.mjs','preview.css'].some(name=>target===path.join(source,name));
    if(!supplied&&(!target.startsWith(source+path.sep)||!fs.existsSync(target)))throw Error(`Missing local asset in ${path.relative(source,file)}: ${match[1]}`);
  }
}}
checkFiles(source);
// Validate before writing. Never replace a prior review or edit component sources.
fs.cpSync(source,out,{recursive:true,errorOnExist:true,force:false});
fs.writeFileSync(path.join(out,'index.html'),html,{flag:'wx'});
fs.copyFileSync(path.join(root,'assets/review-support.mjs'),path.join(out,'review-support.mjs'),fs.constants.COPYFILE_EXCL);
fs.copyFileSync(path.join(root,'assets/preview.css'),path.join(out,'preview.css'),fs.constants.COPYFILE_EXCL);
fs.writeFileSync(path.join(out,'ui-kit.lock.json'),JSON.stringify(identity,null,2)+'\n',{flag:'wx'});
console.log(path.join(out,'index.html'));
