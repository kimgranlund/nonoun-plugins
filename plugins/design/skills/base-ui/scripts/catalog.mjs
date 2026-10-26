import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {extractSpecimens,extractNativeSpecimens,extractDedicatedSpecimen,inspectCompositionSpecimen} from './lib/specimen-extraction.mjs';
const root=path.resolve(import.meta.dirname,'..');
// Kit extraction has no review history, work register, or review installation dependency.
export async function collectCatalog({playwright}){
const sources=new Map(),hash=s=>createHash('sha256').update(s).digest('hex');
const read=p=>{const target=fs.realpathSync(path.resolve(root,p));if(!target.startsWith(root+path.sep))throw Error('Source selection escapes kit');const text=fs.readFileSync(target,'utf8');sources.set(p,{path:p,sha256:hash(text),bytes:Buffer.byteLength(text),owner:'base-ui'});return text;};
read('scripts/catalog.mjs');read('scripts/lib/specimen-extraction.mjs');
const index=JSON.parse(read('references/style/token-index.json')),contract=JSON.parse(read('references/style/contract.json'));
const components=JSON.parse(read('references/style/components/contract.json'));
if(components.runtimeAPIReference)read(components.runtimeAPIReference);
const specimenRegistry=JSON.parse(read('references/style/components/specimens.json'));
const context=read('references/style/components/README.md');read('assets/phosphor-license.txt');
const select=JSON.parse(read('references/style/select/contract.json')),menu=JSON.parse(read('references/style/navigation-menu/contract.json'));
const selectRecipe=read('assets/recipes/native-select.html');
const modalAutofocus=read('assets/recipes/modal-autofocus.js');
const compositionRecipes=Object.fromEntries(Object.entries({'sidebar__root':'sidebar','navigation-recipe__root':'review-navigation-recipe','swatch__root':'review-swatch','card__root':'review-card','nav__root':'review-nav','page__flow':'review-page-flow','options__root':'review-options'}).map(([id,file])=>[id,{source:'assets/recipes/'+file+'.html',markup:read('assets/recipes/'+file+'.html')} ]));
const additionalSpecimens=JSON.parse(read('references/style/components/additional-specimens.json'));if(additionalSpecimens.version!==1||!additionalSpecimens.specimens||!Object.keys(additionalSpecimens.specimens).length)throw Error('Unsupported/empty additional specimen registry');
for(const [id,specimen] of Object.entries(additionalSpecimens.specimens)){if(compositionRecipes[id])throw Error('Duplicate specimen '+id);compositionRecipes[id]={source:specimen.source,markup:read(specimen.source)};}

const bootstrap=read('references/style/bootstrap.md'),composition=read('references/style/composition.md');
const product=read('references/style/product-foundation.md');read('references/style/discovery.json');
const sheetSources=[...new Set(Object.values(index.groups).map(g=>g.source))];
const styleSources=sheetSources.map(p=>({path:p,text:read(p)}));
for(const [g,v] of Object.entries(index.groups))if(hash(read(v.source))!==v.sha256)throw Error('Stale token index: '+g);
const css=styleSources.map(x=>x.text).join('\n'),recipe=read('assets/recipes/components.html'),runtime=read('assets/recipes/components.js'),menuRecipe=read('assets/recipes/native-patterns.html');
const {chromium}=createRequire(import.meta.url)(playwright);const browser=await chromium.launch();let tokens,fragments,profileRules,nativeFragments;
try{
 const page=await browser.newPage();await page.setContent('<!doctype html><html lang="en"><body class="product__root" data-tier="product" data-scale="md" data-size="md"></body></html>');
 for(const s of styleSources)await page.addStyleTag({content:s.text});
 tokens=await page.evaluate(({index,styleSources})=>{
  const declarations=new Map();function walk(rules,source,conditions=[]){for(const rule of rules){if(rule.style&&rule.selectorText){for(const name of rule.style){if(!name.startsWith('--'))continue;const list=declarations.get(name)||[];list.push({source,selector:rule.selectorText,conditions,value:rule.style.getPropertyValue(name).trim()});declarations.set(name,list);}}if(rule.cssRules)walk(rule.cssRules,source,[...conditions,rule.conditionText||rule.name||rule.constructor.name]);}}
  [...document.styleSheets].forEach((s,i)=>walk(s.cssRules,styleSources[i].path));
  const probe=document.createElement('span');document.body.append(probe);const canvas=document.createElement('canvas');canvas.width=canvas.height=1;const ctx=canvas.getContext('2d');
  const result=[];for(const [group,data] of Object.entries(index.groups))for(const name of data.names){const rec={name,group,source:data.source,declarations:declarations.get(name)||[],dependsOn:[],resolved:{}};rec.dependsOn=[...new Set(rec.declarations.flatMap(d=>[...d.value.matchAll(/var\((--[\w-]+)/g)].map(m=>m[1])))];for(const scheme of ['light','dark']){document.documentElement.style.colorScheme=scheme;let value=getComputedStyle(document.body).getPropertyValue(name).trim();let color=null,rgba=null,oklch=null;if(group==='color'){probe.style.color=`var(${name})`;color=getComputedStyle(probe).color;ctx.clearRect(0,0,1,1);ctx.fillStyle=color;ctx.fillRect(0,0,1,1);rgba=[...ctx.getImageData(0,0,1,1).data];probe.style.color='oklch(from '+color+' l c h / alpha)';const converted=getComputedStyle(probe).color;const m=converted.match(/^oklch\(([^)]+)\)$/);if(!m)throw Error('OKLCH conversion failed: '+converted);const parts=m[1].split(/\s*\/\s*/),channels=parts[0].trim().split(/\s+/).map(v=>v==='none'?0:Number(v));oklch='oklch('+channels.map((v,i)=>v.toFixed(i===2?4:6)).join(' ')+(parts[1]?' / '+Number(parts[1]).toFixed(4):'')+')';}rec.resolved[scheme]={value,color,rgba,oklch};}result.push(rec);}return result;
 },{index,styleSources});
 for(const t of tokens.filter(t=>!t.resolved.light.value)){
  const fixture=contract.scopedTokens?.[t.name];if(!fixture)continue;
  t.scopedDefault=await page.evaluate(({name,fixture})=>{const e=document.createElement(fixture.tag);for(const [k,v]of Object.entries(fixture.attributes))e.setAttribute(k,v);document.body.append(e);const value=getComputedStyle(e).getPropertyValue(name).trim();e.remove();return {fixture,value,context:'product/md/md; representative component, not global default'};},{name:t.name,fixture});
 }
 profileRules=await page.evaluate(()=>{const out=[];function walk(rules){for(const r of rules){if(r.selectorText&&r.style)out.push({selector:r.selectorText,css:r.cssText});if(r.cssRules)walk(r.cssRules);}}walk(document.styleSheets[document.styleSheets.length-1].cssRules);return out;});
 await page.setContent(recipe);fragments=await page.evaluate(()=>({sections:[...document.querySelectorAll('#catalog > section')].map(e=>e.outerHTML),select:document.querySelector('#filter').closest('.field__root').outerHTML}));
 const extraction=await page.evaluate(({functionSource,registry,contract})=>{const extract=(0,eval)('('+functionSource+')');return extract(document,registry,contract);},{functionSource:extractSpecimens.toString(),registry:specimenRegistry,contract:components});
 fragments.focused=extraction.focused;fragments.coverage=extraction.coverage;
 await page.setContent(menuRecipe);const nativeExtraction=await page.evaluate(({fn,registry,contract})=>{const extract=(0,eval)('('+fn+')');return extract(document,registry,contract);},{fn:extractNativeSpecimens.toString(),registry:specimenRegistry,contract:components});nativeFragments=nativeExtraction.fragments;Object.assign(fragments.coverage,nativeExtraction.coverage);
 const dedicated=async(unitId,sourcePath,contract)=>page.evaluate(({fn,registry,contract,unitId,sourcePath})=>(0,eval)('('+fn+')')(document,registry,contract,unitId,sourcePath),{fn:extractDedicatedSpecimen.toString(),registry:specimenRegistry,contract,unitId,sourcePath});
 const destination=await dedicated('navigation-menu','assets/recipes/native-patterns.html',menu);nativeFragments.menu=destination.markup;fragments.coverage['navigation-menu']=destination.coverage;
 await page.setContent(selectRecipe);const nativeSelect=await dedicated('native-select','assets/recipes/native-select.html',select);fragments.dedicatedSelect=nativeSelect.markup;fragments.coverage['native-select']=nativeSelect.coverage;

 const compositionSignatures=new Set();for(const[id,specimen]of Object.entries(compositionRecipes)){const signature=specimen.markup.trim();if(compositionSignatures.has(signature))throw Error('Duplicate whole composition recipe: '+id);compositionSignatures.add(signature);await page.setContent(specimen.markup);specimen.coverage=await page.evaluate(({fn,id,contract})=>(0,eval)('('+fn+')')(document,id,contract),{fn:inspectCompositionSpecimen.toString(),id,contract:components});}
}finally{await browser.close();}
const registered=new Set([...components.families.flatMap(f=>f.classes),...(menu.classes||[])]);
const profileClasses=[...new Set(profileRules.flatMap(r=>[...r.selector.matchAll(/\.([a-z][a-z0-9-]*__[a-z][a-z0-9-]*)/g)].map(m=>m[1])))].sort();
const unregistered=profileClasses.filter(c=>!registered.has(c));
const classOwners=new Map((components.classGroups||[]).flatMap(g=>g.classes.map(c=>[c,g])));
const unknownClasses=unregistered.filter(c=>!classOwners.has(c));
const gap=[];const addGap=(id,item,missing,owner,impact)=>gap.push({id,item,missing,owner,impact});
for(const [group,data] of Object.entries(index.groups))if(!contract.tokenUsage?.[group])addGap('context-'+group,group+' tokens','The index inventories names and source hashes, but provides no per-token purpose or when/not-for guidance.', 'references/style/token-index.json and domain context owners','Show source declarations and group context; do not invent per-token descriptions.');
if(unknownClasses.length)addGap('unregistered-classes',unknownClasses.join(', '),'Profile CSS classes have no entry in the component-family class registry. They are exposed as declaration-only items below the registered families.','references/style/components/contract.json and assets/wireframe.css','No invented standalone behavior or usage context; documented families may still own some of these classes elsewhere.');
const unresolved=tokens.filter(t=>!t.resolved.light.value&&!t.scopedDefault?.value);if(unresolved.length)addGap('scoped-defaults',unresolved.map(x=>x.name).join(', '),'No value in the documented product/md/md document context. These declarations are scoped to components or require runtime assignment.','assets/wireframe.css','Do not present an arbitrary fallback as a default.');
for(const f of components.families)if(!f.notFor)addGap('not-for-'+f.id,f.id,'No explicit family-specific when-not-to-use field in the source contract.','references/style/components/contract.json#'+f.id,'Source semantics and global limits are shown; absent guidance stays missing.');
addGap('state-matrix','component families','The source catalog does not demonstrate every declared state for every class, such as busy actions and every invalid/disabled combination.','assets/recipes/components.html','Baseline specimen coverage is not complete state coverage.');
addGap('cross-browser','all sheets','Source value resolution and sheet responsive measurements use Chromium. Separate authored-pattern and fallback checks include Firefox/WebKit; installed Safari, assistive technology and complete sheet contrast remain unverified.','references/style/verification.md','No cross-browser or accessibility certification.');

return {index,contract,components,specimenRegistry,context,select,menu,selectRecipe,modalAutofocus,compositionRecipes,bootstrap,composition,product,styleSources,css,recipe,runtime,menuRecipe,tokens,fragments,profileRules,nativeFragments,registered,profileClasses,unregistered,classOwners,unknownClasses,gap,sources:[...sources.values()]};
}
