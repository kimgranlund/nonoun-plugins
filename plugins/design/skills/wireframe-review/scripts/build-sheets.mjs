import {loadUI} from './ui-kit.mjs';
const uiKit=await loadUI();
import fs from 'node:fs';
import {loadGenerationHistory} from './lib/generation-history.mjs';
const {renderComponents}=uiKit.api;
import {GUIDE_PATH,validateDemonstrations} from './lib/demonstration-guidance.mjs';
const {renderTokens}=uiKit.api;
import {renderIndex,renderGaps} from './lib/sheets/index-gaps.mjs';
const {renderColors}=uiKit.api;
import {renderInspector as inspector} from './lib/sheet-inspectors.mjs';
import {classifyExportColors} from './lib/color-classification.mjs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=process.argv[2],playwright=process.argv[3];
if(output==='--help'){
 console.log(`Usage: node scripts/build-sheets.mjs OUTPUT PLAYWRIGHT [WORK_REGISTER] [GENERATION_HISTORY]
OUTPUT: fresh writable directory outside the skill; existing specimens cannot be overwritten.
PLAYWRIGHT: absolute path to an installed Playwright module.
WORK_REGISTER: optional JSON planning register; required when reviewing that register.
Copied as an external review input, separate from corpus identity and verification.
GENERATION_HISTORY: optional historical-results bundle; pass - for an absent register.
Result values are selected from hash-verified JSON evidence, never current acceptance.
Produces: index.html, tokens.html, colors.html, components.html, gaps.html,
 inventory.json, gaps.json, source snapshots, shared assets and specimen pages.
Reads: installed token index, source CSS, component contracts and maintained recipes.
Authority: generation reports missing guidance; it does not invent or repair source context.
Before build: node scripts/generate-token-index.mjs --check
After build: node scripts/check-sheets.mjs OUTPUT PLAYWRIGHT
For registered reviews: node scripts/check-sheet-work-register.mjs OUTPUT WORK_REGISTER
Context: references/workflows/reference-sheets.md
For a custom catalog, consume contracts and recipes directly. This CLI has no template
or theme override API. Read implementation only when changing the generator itself.`);
 process.exit(0);
}
if(!output||!playwright)throw Error('Usage: build-sheets.mjs OUTPUT PLAYWRIGHT');
fs.mkdirSync(output,{recursive:true});
const builtAt=new Date().toISOString();
const sources=new Map();const hash=s=>createHash('sha256').update(s).digest('hex');
const read=p=>{const target=path.resolve(root,p);if(!target.startsWith(root+path.sep))throw Error('Source selection escapes corpus');const text=fs.readFileSync(target,'utf8');const owner=sources.get(p)?.owner||'wireframe-review';sources.set(p,{path:p,sha256:hash(text),bytes:Buffer.byteLength(text),owner});return text;};
read('scripts/build-sheets.mjs');read('scripts/lib/generation-history.mjs');read('scripts/lib/color-classification.mjs');read('scripts/lib/sheet-inspectors.mjs');read('scripts/lib/sheets/components.mjs');read('scripts/lib/sheets/tokens.mjs');read('scripts/lib/sheets/colors.mjs');read('scripts/lib/sheets/index-gaps.mjs');read('scripts/lib/specimen-extraction.mjs');
const catalog=await uiKit.api.collectCatalog({playwright});
const {index,contract,components,specimenRegistry,context,select,menu,selectRecipe,modalAutofocus,compositionRecipes,bootstrap,composition,product,styleSources,css,recipe,runtime,menuRecipe,tokens,fragments,profileRules,nativeFragments,registered,profileClasses,unregistered,classOwners,unknownClasses,gap}=catalog;
for(const source of catalog.sources)sources.set(source.path,source);
read('scripts/lib/demonstration-guidance.mjs');
const demonstrationGuide=JSON.parse(read(GUIDE_PATH));
const demonstrationGroups=validateDemonstrations(demonstrationGuide,{registry:specimenRegistry,components,read,hash});
for(const [base,entries] of [['references/style/components',components.families],['references/style/select',[select]],['references/style/navigation-menu',[menu]]])for(const entry of entries){const guide=entry.implementation?.evidence?.guide;if(!guide)continue;const file=path.resolve(root,base,guide.split('#')[0]);if(!file.startsWith(root+path.sep))throw Error('Evidence guide escapes corpus');read(path.relative(root,file));}
read('references/workflows/reference-sheets.md');read('references/artifact-styling.md');
const {chromium}=createRequire(import.meta.url)(playwright);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const id=s=>s.replace(/^--/,'').replace(/[^\w-]/g,'-');
const code=s=>'<pre class="card__root"><code>'+esc(s)+'</code></pre>';
const sourceLink=p=>`<a href="sources/${p}">${esc(p)}</a>`;
const disclosure=(impl,manifest,ctx)=>`<details><summary>Implementation, declaration and context</summary><h3>Implementation</h3>${code(impl)}<h3>Manifest / declaration</h3>${manifest}<h3>Context</h3>${ctx}</details>`;
const tokenCard=t=>{const raw=t.group==='color'&&/-\d{3}$/.test(t.name);const declared=t.declarations.map(d=>`${d.conditions.length?'/* '+d.conditions.join(' / ')+' */\n':''}${d.selector} { ${t.name}: ${d.value}; }`).join('\n');const snippet=t.group==='color'?`.example { color: var(${t.name}); }`:`.example { /* Bind to a compatible CSS property. */\n  --example-value: var(${t.name});\n}`;return `<article class="sheet-item card__root" id="${id(t.name)}" data-item="${esc(t.name)}" data-search="${esc(t.name+' '+t.group)}"><h3><code>${esc(t.name)}</code></h3>${t.group==='color'?`<div class="swatches"><div style="background:${esc(t.resolved.light.color)}" aria-label="Light color sample"></div><div style="background:${esc(t.resolved.dark.color)}" aria-label="Dark color sample"></div></div>`:''}<p class="meta">${esc(t.group)} · ${raw?'palette ramp (name convention)':t.dependsOn.length?'references other declarations':'direct or context-resolved declaration'}</p><dl><dt>Light default</dt><dd>${esc(t.resolved.light.color||t.resolved.light.value||'Not defined in root context')}</dd><dt>Dark default</dt><dd>${esc(t.resolved.dark.color||t.resolved.dark.value||'Not defined in root context')}</dd></dl>${disclosure(snippet,'<p>Authoritative CSS declaration(s): '+sourceLink(t.source)+'</p>'+code(declared),'<p>Dependencies: '+(t.dependsOn.map(n=>`<a href="${tokens.find(x=>x.name===n)?.group==='color'?'colors':'tokens'}.html#${id(n)}">${esc(n)}</a>`).join(', ')||'No var() dependency in declaration')+'</p>'+(t.scopedDefault?'<h4>Representative component context</h4>'+code(JSON.stringify(t.scopedDefault,null,2)):'')+(contract.tokenUsage?.[t.group]?'<p>Source-owned family guidance: '+sourceLink('references/style/contract.json')+'</p>'+code(JSON.stringify(contract.tokenUsage[t.group],null,2)):'<p>Family usage guidance is missing. <a href="gaps.html#context-'+t.group+'">Recorded gap</a>.</p>')+'<p>The binding example is illustrative; this family guidance does not invent a unique purpose for each scale step.</p><p>Default: product / md / md. Non-color values are browser-resolved custom-property expressions; calc() is not necessarily a used pixel length.</p>')}</article>`;};
const colorGroup=(name,items)=>{
 const ramp=name.endsWith('palette');
 const cells=items.map(t=>{
 const step=t.name.match(/-(\d{3})$/)?.[1];
 const original=tokenCard(t);
 const details=original.slice(original.indexOf('<details>'),original.lastIndexOf('</article>'));
 const values='<dl>'+['light','dark'].map(s=>'<dt>'+s+'</dt><dd><code>'+esc(t.resolved[s].oklch)+'</code></dd>').join('')+'</dl>';
 const samples='<button type="button" class="swatch__root color-values-trigger" popovertarget="values-'+id(t.name)+'" style="anchor-name:--anchor-'+id(t.name)+'" aria-label="Values and sources for '+esc(t.name)+'"><span aria-hidden="true" style="background:'+esc(t.resolved.light.oklch)+'"></span><span aria-hidden="true" style="background:'+esc(t.resolved.dark.oklch)+'"></span></button>';
 return '<div class="color-entry" id="'+id(t.name)+'" data-item="'+esc(t.name)+'"><h3>'+esc(ramp?step:t.name.replace('--md-color-',''))+'</h3>'+samples+'<section class="popover__root color-popover" popover="auto" id="values-'+id(t.name)+'" style="position-anchor:--anchor-'+id(t.name)+'" aria-labelledby="title-'+id(t.name)+'"><header class="heading-group__root popover__header"><h3 id="title-'+id(t.name)+'">'+esc(t.name)+'</h3><button type="button" popovertarget="values-'+id(t.name)+'" popovertargetaction="hide">Close</button></header><div class="popover__body flow__root">'+values+details+'</div></section></div>';
 }).join('');
 return '<article class="sheet-item card__root palette-group" data-palette="'+esc(name)+'" data-search="'+esc(name+' '+items.map(t=>t.name).join(' '))+'"><h2>'+esc(name)+'</h2><p>'+items.length+' declarations · light left / dark right</p><div class="palette-grid'+(ramp?' palette-ramp':'')+'">'+cells+'</div></article>';
};
const pages=[['index','Overview'],['tokens','Design tokens'],['colors','Colors'],['components','Components'],['gaps','Gaps']];
const siteCss=`.color-values-trigger{padding:0;width:100%;block-size:auto;min-block-size:var(--g-height);cursor:pointer}.color-popover{inline-size:36rem;min-inline-size:0}.color-popover h3{overflow-wrap:anywhere}.palette-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,200px),1fr));gap:calc(3 * var(--g-inset)) calc(2 * var(--g-inset))}.palette-ramp{grid-template-columns:repeat(auto-fit,minmax(min(100%,calc(8 * var(--g-inset))),1fr))}.color-entry{min-width:0;scroll-margin-top:calc(var(--sheet-header) + 16px)}.color-entry h3{font-size:var(--type-ui-control-md-size);overflow-wrap:anywhere}.color-entry dl{display:block;font-size:var(--type-ui-widget-md-size)}.color-entry dd{margin-block-end:var(--g-inset)}.color-entry details{font-size:var(--type-ui-widget-md-size)}.color-entry .swatch__root>span{min-block-size:calc(8 * var(--g-inset))}.palette-group{content-visibility:visible}#matches:empty{display:none} :root{--sheet-header:96px}html{scroll-padding-top:calc(var(--sheet-header) + 16px)}body{padding-top:calc(var(--sheet-header) + 24px)}.sheet-header{position:fixed;inset:0 0 auto;z-index:10;background:var(--ui-surface);border-bottom:1px solid var(--ui-border)}.sheet-header>div,main{max-width:var(--ui-content-width);margin-inline:auto;padding-inline:24px}.sheet-header>div{display:flex;justify-content:space-between;align-items:center;gap:16px;min-height:80px;padding-block:12px;flex-wrap:wrap}.sheet-header label{display:grid;gap:4px}.sheet-header select{max-width:100%;min-width:10rem}main{padding-bottom:64px}h1{overflow-wrap:anywhere}a{overflow-wrap:anywhere}pre{max-block-size:30rem}code,dd{overflow-wrap:anywhere}details{margin:0}details h3{margin:0}article{scroll-margin-top:calc(var(--sheet-header) + 16px)}.sheet-item{margin-block:0;min-width:0;content-visibility:auto;contain-intrinsic-size:auto 240px}.meta{color:var(--ui-muted)}.tile-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:calc(2 * var(--g-inset))}.tile{display:grid;gap:var(--g-inset);text-decoration:none}.tile strong{font-size:1.2em}.swatches{display:flex;gap:8px}.swatches>div{height:48px;flex:1;border:1px solid var(--ui-border);border-radius:calc(var(--r-control) * var(--ui-corner-factor, 1) * var(--ui-corner-scale, 1.5))}dl{display:grid;grid-template-columns:minmax(6rem,auto) minmax(0,1fr);gap:8px}dd{margin:0}iframe{display:block;width:100%;height:460px;border:0;border-radius:0;background:var(--ui-surface)}.component-entry{content-visibility:visible}.declaration-list{display:grid;gap:var(--g-inset)}.toolbar{display:flex;gap:calc(2 * var(--g-inset));flex-wrap:wrap;margin:0}.toolbar label{flex:1;min-width:min(100%,200px)}[data-work-dispositions] p,[data-work-dispositions] li,[data-work-dispositions] summary{overflow-wrap:anywhere}[data-work-dispositions] [id]{scroll-margin-top:calc(var(--sheet-header) + 16px)}[data-work-filters][hidden],[data-work-group][hidden]{display:none}.gap-record-title{font-weight:600}.gap-record-id,.gap-path{overflow-wrap:anywhere}.gap-status summary{flex-wrap:wrap}.gap-status [data-work-id]{min-inline-size:0}@media(max-width:480px){.sheet-header>div,main{padding-inline:16px}}`;
const catalogCss='.catalog-entry-heading{display:grid;gap:calc(var(--g-inset) / 2);min-inline-size:0}.catalog-entry-heading strong{font-size:var(--type-ui-control-md-size)}[data-component-category],[data-catalog-reference]{scroll-margin-top:calc(var(--sheet-header) + 16px)}.component-entry{content-visibility:visible}[data-component-category] > summary{font-weight:600}';
const siteJs=`(()=>{const workRoot=document.querySelector('[data-work-dispositions]');const filterWork=key=>{if(!workRoot)return;workRoot.querySelectorAll('[data-work-group]').forEach(section=>{section.hidden=key!=='all'&&section.dataset.workGroup!==key;if(!section.hidden&&key!=='all'){const disclosure=section.querySelector(':scope > details');if(disclosure)disclosure.open=true;}});workRoot.querySelectorAll('[data-disposition-count]').forEach(button=>{const current=button.dataset.dispositionCount===key;button.setAttribute('aria-pressed',String(current));button.classList.toggle('secondary',!current);});const button=workRoot.querySelector('[data-disposition-count="'+key+'"]');const status=workRoot.querySelector('[data-filter-status]');if(status&&button)status.textContent=button.dataset.count+' work items shown'+(key==='all'?' across all dispositions':': '+button.textContent.trim());};if(workRoot){workRoot.querySelector('[data-work-filters]').hidden=false;workRoot.querySelectorAll('[data-disposition-count]').forEach(button=>button.addEventListener('click',()=>filterWork(button.dataset.dispositionCount)));filterWork('all');}const revealWork=()=>{if(!workRoot||!location.hash)return;let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}const target=document.getElementById(id);if(!target)return;const group=target.closest('[data-work-group]')?.dataset.workGroup;if(group)filterWork(group);for(let node=target;node;node=node.parentElement)if(node.tagName==='DETAILS')node.open=true;requestAnimationFrame(()=>target.scrollIntoView());};addEventListener('hashchange',revealWork);requestAnimationFrame(revealWork);const fits=new WeakMap();const fit=f=>{const d=f.contentDocument;if(!d?.body||d.URL==='about:blank')return;const previous=fits.get(f);if(previous?.document===d){previous.resize();return;}previous?.observer.disconnect();previous?.hostObserver.disconnect();let pending=0;const measure=()=>{pending=0;if(f.contentDocument!==d||!f.getClientRects().length)return;const height=Math.ceil(d.body.getBoundingClientRect().height+parseFloat(getComputedStyle(d.body).marginTop||0)+parseFloat(getComputedStyle(d.body).marginBottom||0)+2)+'px';if(f.style.height!==height)f.style.height=height;};const resize=()=>{if(!pending)pending=requestAnimationFrame(measure);};const observer=new ResizeObserver(resize);let hostWidth=-1;const hostObserver=new ResizeObserver(entries=>{const width=entries[0].contentRect.width;if(width!==hostWidth){hostWidth=width;resize();}});fits.set(f,{document:d,observer,hostObserver,resize});observer.observe(d.body);hostObserver.observe(f);resize();};document.querySelectorAll('iframe').forEach(f=>{f.addEventListener('load',()=>fit(f));if(f.contentDocument?.readyState==='complete')fit(f);});const nav=document.querySelector('#sheet-nav');nav.onchange=()=>location.href=nav.value;const header=document.querySelector('.sheet-header');new ResizeObserver(()=>document.documentElement.style.setProperty('--sheet-header',header.getBoundingClientRect().height+'px')).observe(header);const scheme=document.querySelector('#scheme');scheme.onchange=()=>{document.documentElement.style.colorScheme=scheme.value;document.querySelectorAll('iframe').forEach(f=>f.contentDocument&&(f.contentDocument.documentElement.style.colorScheme=scheme.value));};document.querySelectorAll('iframe').forEach(f=>f.addEventListener('load',()=>{f.contentDocument.documentElement.style.colorScheme=scheme.value;}));const size=document.querySelector('#geometry-size');if(size)size.onchange=()=>document.querySelectorAll('iframe').forEach(f=>{if(f.contentDocument)f.contentDocument.body.dataset.size=size.value;});document.querySelectorAll('iframe').forEach(f=>f.addEventListener('load',()=>{if(size)f.contentDocument.body.dataset.size=size.value;}));const search=document.querySelector('#search');if(search)search.oninput=()=>{let count=0;document.querySelectorAll('[data-search]').forEach(e=>{e.hidden=!e.dataset.search.toLowerCase().includes(search.value.toLowerCase());if(!e.hidden)count++;});document.querySelector('#matches').textContent=count+' matching items';};const tokenSearch=document.querySelector('#token-search');if(tokenSearch&&search){tokenSearch.addEventListener('input',()=>{search.value=tokenSearch.value;search.dispatchEvent(new Event('input'));});search.addEventListener('input',()=>{tokenSearch.value=search.value;});}})();`+'\n'+read('scripts/lib/sheets/catalog-browser.js');
const page=(key,title,body)=>`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${title} · System sheets</title><link rel="stylesheet" href="foundation.css"><link rel="stylesheet" href="sheets.css"></head><body class="product__root" data-tier="product" data-scale="md" data-size="md"><noscript><style>.sheet-header label,.toolbar,#matches,label[for=token-search],iframe[data-srcdoc]{display:none!important}.sheet-header{position:static}main{padding-block-start:var(--m-inset-card)}</style><nav class="card__root cluster__root" aria-label="Sheet navigation">${pages.map(([k,v])=>`<a href="${k}.html" ${k===key?'aria-current="page"':''}>${v}</a>`).join('')}</nav><p class="card__root">Static reference: source content and native disclosures remain available. Search, display controls and scripted specimen actions require JavaScript.</p></noscript><header class="sheet-header"><div><a href="index.html"><strong>System sheets</strong></a><label for="sheet-nav">Sheet<select id="sheet-nav">${pages.map(([k,v])=>`<option value="${k}.html" ${k===key?'selected':''}>${v}</option>`).join('')}</select></label></div></header><main>${['tokens','index','gaps'].includes(key) ? '' : `<h1>${title}</h1>`}<div class="toolbar"><label for="scheme">Color scheme<select id="scheme"><option value="light dark">System</option><option value="light">Light</option><option value="dark">Dark</option></select></label>${key==='tokens'||key==='colors'||key==='components'?'<label for="search">Find an item<input type="search" id="search" placeholder="Name or family"></label>':''}${key==='components'?'<label for="geometry-size">Geometry size<select id="geometry-size"><option value="sm">Small</option><option value="md" selected>Medium</option><option value="lg">Large</option></select></label>':''}</div><p id="matches" role="status"></p>${body}<footer><hr><p>Source snapshot: <a href="inventory.json">inventory and hashes</a> · <a href="gaps.json">gap data</a></p></footer></main><script src="sheets.js"></script></body></html>`;
fs.writeFileSync(path.join(output,'foundation.css'),css);fs.writeFileSync(path.join(output,'sheets.css'),siteCss+catalogCss);fs.writeFileSync(path.join(output,'sheets.js'),siteJs);
const tokenExcerpts=Object.fromEntries(["references/style/components/contract.json", "assets/foundation/ultimate-tokens/typography.css", "assets/foundation/maison/geometry.css", "references/style/contract.json", "references/style/product-foundation.md", "assets/wireframe.css", "assets/recipes/spacing.html"].map(p=>[p,read(p)]));
const sourceIdentity=(p,selectionKey)=>({path:p,sha256:sources.get(p)?.sha256,selectionKey});
const tokensBody=renderTokens({tokens,index,contract,excerpts:tokenExcerpts,helpers:{esc,code,sourceLink,inspector,tokenCard,sourceIdentity}});
fs.writeFileSync(path.join(output,'tokens.html'),page('tokens','Design tokens',tokensBody));
const colorTokens=tokens.filter(t=>t.group==='color');
const colorKinds=classifyExportColors(read('assets/foundation/ultimate-tokens/colors.css'));
// Pair only the profile's explicitly declared source aliases, not guessed palette-role names.
const aliases=['--ui-surface','--ui-ink','--ui-action','--ui-on-action'];
const pairDefs=[['Profile surface','--ui-surface','--ui-ink'],['Profile action','--ui-action','--ui-on-action']];
let pairs;const b2=await chromium.launch();try{const p=await b2.newPage();await p.setContent('<style>'+css+'</style><body class="product__root"><span id="probe"></span></body>');pairs=await p.evaluate(defs=>{const probe=document.querySelector('#probe'),cv=document.createElement('canvas');cv.width=cv.height=1;const ctx=cv.getContext('2d');const rgb=v=>{probe.style.color=`var(${v})`;const c=getComputedStyle(probe).color;ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);return {color:c,rgba:[...ctx.getImageData(0,0,1,1).data]};};const luminance=v=>v.slice(0,3).map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4;}).reduce((a,x,i)=>a+x*[.2126,.7152,.0722][i],0);return defs.flatMap(([title,bg,fg])=>['light','dark'].map(scheme=>{document.documentElement.style.colorScheme=scheme;const a=rgb(bg),b=rgb(fg),l=[luminance(a.rgba),luminance(b.rgba)];return {title,bg,fg,scheme,background:a.color,foreground:b.color,ratio:a.rgba[3]===255&&b.rgba[3]===255?(Math.max(...l)+.05)/(Math.min(...l)+.05):null};}));},pairDefs);}finally{await b2.close();}
const colorExcerpts=Object.fromEntries(["assets/foundation/ultimate-tokens/colors.css", "references/style/token-index.json", "references/style/contract.json", "references/workflows/reference-sheets.md", "assets/wireframe.css", "assets/foundation/ultimate-tokens/source-state.json", "references/style/product-foundation.md", "assets/recipes/semantic-colors.html", "assets/recipes/semantic-colors.js", "references/style/components/contract.json"].map(p=>[p,read(p)]));
fs.writeFileSync(path.join(output,'semantic-colors.js'),colorExcerpts['assets/recipes/semantic-colors.js']);
const colorsBody=renderColors({tokens,colorKinds,pairs,seedState:JSON.parse(colorExcerpts['assets/foundation/ultimate-tokens/source-state.json']),excerpts:colorExcerpts,helpers:{esc,code,sourceLink,inspector,sourceIdentity}});
fs.writeFileSync(path.join(output,'colors.html'),page('colors','Colors',colorsBody));
const fullPageSpecimens={};
const emitSpecimen=(id,html)=>{if(!/^[a-zA-Z][\w-]*$/.test(id)||fullPageSpecimens[id])throw Error('Invalid/duplicate full-page specimen '+id);const file='specimens/'+id+'.html';fs.mkdirSync(path.join(output,'specimens'),{recursive:true});fs.writeFileSync(path.join(output,file),html,{flag:'wx'});fullPageSpecimens[id]={path:file,sha256:hash(html),scope:'Same source-derived specimen as srcdoc; native full-page fallback, not complete application or state acceptance'};return file;};
const compBody=renderComponents({demonstrationGuide,demonstrationGroups,emitSpecimen,sourceIdentity,css,runtime,compositionRecipes,modalAutofocus,specimenRegistry,components,nativeFragments,fragments,select,menu,selectRecipe:fragments.dedicatedSelect,context,bootstrap,contract,composition,unregistered,profileRules,classOwners,esc,code,sourceLink,disclosure});
fs.writeFileSync(path.join(output,'components.html'),page('components','Components',compBody));
// Review inputs are explicit external inputs, copied separately and excluded from corpus identity.
const reviewInputFile=process.argv[4]==='-'?null:process.argv[4];
const generationHistory=process.argv[5]?loadGenerationHistory(process.argv[5]):null;
const reviewRaw=reviewInputFile?fs.readFileSync(reviewInputFile,'utf8'):null;
const reviewRegister=reviewRaw?JSON.parse(reviewRaw):null;
if(reviewRegister&&!Array.isArray(reviewRegister.items))throw Error('Work register requires items array');
const reviewExcerpts={};
const selectSource=(p,key='whole')=>{const text=read(p);(reviewExcerpts[p]??={})[key]=text;return {path:p,selectionKey:key};};
const skillRef=selectSource('SKILL.md');
const workflowRef=selectSource('references/workflows/reference-sheets.md');
const seedRef=selectSource('assets/foundation/ultimate-tokens/source-state.json');
const colorRef=selectSource('assets/foundation/ultimate-tokens/colors.css');
const bindingRef=selectSource('assets/wireframe.css');
const typeRef=selectSource('assets/foundation/ultimate-tokens/typography.css');
const geometryRef=selectSource('assets/foundation/maison/geometry.css');
const componentRef=selectSource('references/style/components/contract.json');
const compositionRef=selectSource('references/style/composition.md');
const evaluationRef=selectSource('evals/plan.md');
const reviewSources=new Map();
if(reviewRaw){fs.mkdirSync(path.join(output,'review-inputs'),{recursive:true});fs.writeFileSync(path.join(output,'review-inputs/work-register.json'),reviewRaw);reviewSources.set('review-inputs/work-register.json',{sha256:hash(reviewRaw)});}
if(generationHistory){
 const rel='review-inputs/generation-results.json';fs.mkdirSync(path.join(output,'review-inputs'),{recursive:true});fs.writeFileSync(path.join(output,rel),generationHistory.raw);reviewSources.set(rel,{sha256:generationHistory.sha256});
 for(const [p,snapshot]of generationHistory.snapshots){const rel='review-inputs/generation-evidence/'+p;fs.mkdirSync(path.dirname(path.join(output,rel)),{recursive:true});fs.writeFileSync(path.join(output,rel),snapshot.bytes);reviewSources.set(rel,{sha256:snapshot.sha256});}
}
const reviewIdentity=(p,key)=>({path:p,selectionKey:key,sha256:(reviewSources.get(p)||sources.get(p))?.sha256});
const reviewLink=p=>p.startsWith('review-inputs/')?`<a href="${esc(p)}">${esc(p)}</a>`:sourceLink(p);
const reviewHelpers={esc,code,inspector,sourceLink:reviewLink,sourceIdentity:reviewIdentity,excerpts:reviewExcerpts};
const registerItems=reviewRegister?.items||[];
// Source selection preserves original bytes, including the selected JSON object's formatting.
const jsonObjectAt=(raw,start)=>{if(raw[start]!=='{')throw Error('Selection is not an object');let depth=0,quote=false,escape=false;for(let i=start;i<raw.length;i++){const ch=raw[i];if(quote){if(escape)escape=false;else if(ch==='\\')escape=true;else if(ch==='"')quote=false;continue;}if(ch==='"')quote=true;else if(ch==='{')depth++;else if(ch==='}'&&!--depth)return raw.slice(start,i+1);}throw Error('Unterminated source selection');};
const localSelection=ref=>{
 const raw=read(ref.path);let selected=raw;
 if(ref.selectionKey.startsWith('family:')){const name=ref.selectionKey.slice(7),needle='"id": "'+name+'"',where=raw.indexOf(needle);if(where<0)throw Error('Missing family source selection '+name);selected=jsonObjectAt(raw,raw.lastIndexOf('{',where));if(JSON.parse(selected).id!==name)throw Error('Mismatched family source selection');}
 else if(ref.selectionKey.startsWith('tokenUsage:')){const name=ref.selectionKey.slice(11),where=raw.indexOf('"tokenUsage"');if(where<0)throw Error('Missing token usage');const usage=jsonObjectAt(raw,raw.indexOf('{',where));const key=usage.indexOf('"'+name+'"');if(key<0)throw Error('Missing token usage domain '+name);selected=jsonObjectAt(usage,usage.indexOf('{',key));}
 else if(ref.selectionKey!=='whole')throw Error('Unsupported source selection key');
 (reviewExcerpts[ref.path]??={})[ref.selectionKey]=selected;return ref;
};
const unitMap={'entry-context':'index.html#source-chain-6','token-domain':'tokens.html#tokens-geometry','color-example':'colors.html#md-color-neutral-500',...Object.fromEntries([...components.families.map(f=>f.id),'native-select','navigation-menu'].map(id=>['component:'+id,'components.html#'+id]))};
// External evidence is copied separately from corpus source identity. Long status logs stay in the register.
const evidenceIndex={schemaVersion:1,scope:'Recorded evidence references,not verification claims; consult each report identity and limitations.',registerSHA256:reviewRaw?hash(reviewRaw):null,items:[]};
const evidenceRoot=reviewInputFile?path.dirname(path.resolve(reviewInputFile)):null;
const workRegister=registerItems.map(w=>{
 const candidates=[w.resolutionEvidence,w.resolution?.report,...(w.evidence?.match(/evidence\/[A-Za-z0-9][A-Za-z0-9._/-]*\.(?:json|md|html)/g)??[])].filter(Boolean);
 const links=[],unresolved=[];
 for(const ref of [...new Set(candidates)]){
  if(!/^evidence\/[-\w./]+\.(json|md|html)$/.test(ref)||ref.split('/').includes('..')){unresolved.push(ref);continue;}
  const file=path.resolve(evidenceRoot,ref);if(!fs.existsSync(file)||!fs.statSync(file).isFile()){unresolved.push(ref);continue;}
  // Limit entry links; original references remain verbatim in the snapshot/index.
  if(links.length>=3)continue;
  const href='review-inputs/work-evidence/'+ref,bytes=fs.readFileSync(file),sha256=hash(bytes);
  fs.mkdirSync(path.dirname(path.join(output,href)),{recursive:true});fs.writeFileSync(path.join(output,href),bytes);reviewSources.set(href,{sha256});
  links.push({href,label:path.basename(path.dirname(ref))+'/'+path.basename(ref),sha256,originalReference:ref});
 }
 evidenceIndex.items.push({id:w.id,links,unresolvedReferences:unresolved,originalEvidence:w.evidence??null,resolution:w.resolution??null,acceptedSubpartLimitations:w.acceptedSubpartLimitations??[]});
 return {...w,sourceIds:[w.id,...(w.id.startsWith('G-')?[w.id.slice(2)]:[])],evidenceLinks:links};
});
const evidenceIndexRaw=JSON.stringify(evidenceIndex,null,2);fs.mkdirSync(path.join(output,'review-inputs'),{recursive:true});fs.writeFileSync(path.join(output,'review-inputs/evidence-index.json'),evidenceIndexRaw);reviewSources.set('review-inputs/evidence-index.json',{sha256:hash(evidenceIndexRaw)});
const registerFindings=registerItems.map(w=>{
 const key='record:'+w.id;(reviewExcerpts['review-inputs/work-register.json']??={})[key]=JSON.stringify(w,null,2);
 if(!w.classification||!w.normalizedStatus||!Array.isArray(w.sourceSelections))throw Error('Work register requires explicit classification/status/source selections: '+w.id);
 const ref={path:'review-inputs/work-register.json',selectionKey:key},local=w.sourceSelections.map(localSelection);
 return {id:w.id,classification:w.classification,affectedUnitIds:w.affectedUnitIds,expectation:w.acceptance,observed:w.title,evidence:w.evidence,owner:w.owner,action:w.correctiveAction,acceptance:w.acceptance,status:w.status,normalizedStatus:w.normalizedStatus,generationStatus:w.generationStatus,scope:{source:w.source,completeInRegister:w.complete,qualification:'Recorded work status; historical evidence is not current generated-page acceptance.'},implementation:local,manifest:[ref],context:local,sourceObservations:gap.filter(g=>workRegister.find(record=>record.id===w.id).sourceIds.includes(g.id))};
});
const findings=registerFindings;
const documentationUpdates=JSON.parse(read('references/reports/documentation-updates.json'));
if(documentationUpdates.schemaVersion!==1 || !Array.isArray(documentationUpdates.records))throw Error('Unsupported documentation updates');
const updateIds=new Set();
const updatesBody=`<section id="recent-system-updates" class="section__flow"><header class="heading-group__root"><h2>Recent changes and remaining questions</h2><p>${esc(documentationUpdates.scope)}</p></header>${documentationUpdates.records.map(record=>{
 if(!record.id || updateIds.has(record.id))throw Error('Duplicate/missing documentation update');updateIds.add(record.id);
 const report=read(record.report);if(hash(report)!==record.sha256)throw Error('Documentation report identity mismatch: '+record.id);
 return `<details class="disclosure__root" data-documentation-update="${esc(record.id)}"><summary>${esc(record.title)} <span class="meta">${esc(record.status)}</span></summary><div class="flow__root"><p>${esc(record.summary)}</p><p>Preserved report: ${sourceLink(record.report)}</p><p class="meta">This summary reports the linked evidence; it does not independently reproduce the experiment.</p></div></details>`;
}).join('')}<div class="flow__root"><h3>Still outside a complete verification claim</h3><ul>${documentationUpdates.remaining.map(item=>`<li>${esc(item)}</li>`).join('')}</ul><p>${esc(documentationUpdates.next)}</p></div></section>`;
const gapsBody=renderGaps({findings,workRegister:reviewRegister?workRegister:undefined,rawObservations:gap,reviewUnitMap:unitMap,sharedContext:[workflowRef],snapshot:{builtAt,registerSHA256:reviewRaw?hash(reviewRaw):null},helpers:reviewHelpers});
fs.writeFileSync(path.join(output,'gaps.html'),page('gaps','Gaps and delivery status',gapsBody.replace('<section data-work-group="open"',updatesBody+'<section data-work-group="open"')));
const stageBindings=[['seeds',seedRef,[seedRef]],['raw exports',colorRef,[colorRef]],['semantic bindings',bindingRef,[bindingRef]],['type/geometry',typeRef,[typeRef,geometryRef]],['components',componentRef,[componentRef]],['compositions',compositionRef,[compositionRef]],['generated interfaces',evaluationRef,[evaluationRef]]];
const chainSources=stageBindings.flatMap(([stage,ref,local])=>local.map((selection,i)=>({id:stage+':'+i,stage,...selection}))); 
const chainUnits=stageBindings.map(([stage,ref,local],i)=>({id:'source-chain-'+i,stage,manifest:local,context:local,implementation:local,requirementIds:[]}));
const observedSpecimens=[...components.families.map(f=>({id:f.id,demonstrated:Boolean(nativeFragments[f.id]||fragments.focused[f.id])})),{id:'native-select',demonstrated:Boolean(selectRecipe)},{id:'navigation-menu',demonstrated:Boolean(nativeFragments.menu)},...Object.entries(compositionRecipes).map(([id,specimen])=>({id,kind:'contextual-class-specimen',demonstrated:Boolean(specimen.coverage?.matches)}))];
const capabilityCoverage={sourceMemberSelections:fragments.coverage,contextualClassSelections:Object.fromEntries(Object.entries(compositionRecipes).map(([id,specimen])=>[id,specimen.coverage])),limits:['Source selection establishes displayed members, not all declared state demonstrations.','All state transitions remain unverified until matching artifact-bound check evidence is attached.','Evaluation-plan context is not an executed generation evaluation.']};
const overview=renderIndex({inventory:{declarations:tokens.map(t=>({id:t.name,available:t.declarations.length>0})),specimens:observedSpecimens,requirements:registerItems.map(w=>({id:w.id})),sources:chainSources,units:chainUnits,sourceHash:hash(JSON.stringify([...sources.values()])),generatorHash:hash(fs.readFileSync(fileURLToPath(import.meta.url))),builtAt},entryContext:{excerpts:reviewExcerpts,sources:[skillRef,workflowRef]},routes:[skillRef],seedState:{sources:[seedRef]},capabilityCoverage,evaluations:generationHistory?.records,helpers:reviewHelpers});
fs.writeFileSync(path.join(output,'index.html'),page('index','Design system reference',overview.replace('<section class="section__flow"><h2>Inventory and evidence</h2>',updatesBody+'<section class="section__flow"><h2>Inventory and evidence</h2>')));
fs.writeFileSync(path.join(output,'review-inputs.json'),JSON.stringify({generationRecords:generationHistory?.records.length??0,generationApplicability:generationHistory?'historical-cohort':'unavailable',builtAt,registerIdentity:reviewRaw?{sha256:hash(reviewRaw),path:'review-inputs/work-register.json'}:null,dispositionCounts:workRegister.reduce((counts,w)=>{const key=w.normalizedStatus==='open'?'open':w.normalizedStatus==='canonical-complete'?'completed':'accepted';counts[key]++;return counts;},{open:0,accepted:0,completed:0}),externalInputs:[...reviewSources].map(([path,v])=>({path,...v})),excludedFromCorpusIdentity:true,workItems:registerItems.length,counts:{complete:registerItems.filter(w=>w.complete===true).length,remaining:registerItems.filter(w=>w.complete!==true).length},findingIds:findings.map(f=>f.id),rawSourceFindingCount:gap.length,rawSourceFindingIds:gap.map(g=>g.id),classificationAuthority:'explicit work-register classification field',limits:['Register status is historical/scoped; current output verification not attached.','Specimen registry membership is not observed demonstration.','Evaluation plan is context, not executed evaluation evidence.']},null,2));
// Build-time semantic grouping: spacing belongs to immediate layout parents.
const layoutBrowser=await chromium.launch();try{const p=await layoutBrowser.newPage();for(const [key] of pages){
 const file=path.join(output,key+'.html');await p.setContent(fs.readFileSync(file,'utf8').replace(/<script\b(?=[^>]*\bsrc=["\'](?:sheets|semantic-colors)\.js["\'])[^>]*><\/script>/g,''));
 await p.evaluate((selectRecipe)=>{
  const make=(tag,cls)=>{const e=document.createElement(tag);e.className=cls;return e;};
  const indicator=new DOMParser().parseFromString(selectRecipe,'text/html').querySelector('[data-slot=indicator]');
  for(const select of document.querySelectorAll('select')){if(select.closest('.select__root'))continue;const wrap=make('span','select__root');select.before(wrap);wrap.append(select,indicator.cloneNode(true));}
  const main=document.querySelector('main');const ownedFlow=main.querySelector(':scope > .page__flow');if(ownedFlow?.hasAttribute('data-work-dispositions')){main.setAttribute('data-work-dispositions','');main.classList.add('gap-status');}if(ownedFlow)ownedFlow.replaceWith(...ownedFlow.childNodes);const original=[...main.children];main.classList.add('page__flow');
  const intro=make('div','section__flow');intro.dataset.rhythm='intro';main.prepend(intro);
  for(const e of original.slice(0,3))intro.append(e);
  if(original[3]?.tagName==='P')intro.append(original[3]);
  const introTitle=intro.querySelector(':scope > h1');if(introTitle){const heading=make('header','heading-group__root');introTitle.before(heading);heading.append(introTitle);for(const child of [...intro.children])if(child.tagName==='P'&&child.id!=='matches')heading.append(child);}
  let section=null,content=null;
  const start=()=>{section=make('section','section__flow');section.dataset.rhythm='section';content=make('div','flow__root');section.append(content);main.append(section);};
  for(const e of original.filter(e=>e.parentElement===main)){
   if(e.tagName==='FOOTER'){e.classList.add('flow__root');main.append(e);section=null;continue;}
   if(e.tagName==='SECTION'){e.classList.add('section__flow');main.append(e);const items=make('div','flow__root');for(const c of [...e.children])if(c.tagName!=='H2')items.append(c);e.append(items);section=null;continue;}
   if(e.tagName==='H2'){start();const heading=make('header','heading-group__root');heading.append(e);section.prepend(heading);continue;}
   if(!section)start();
   const heading=section.querySelector(':scope > header');
   if(e.tagName==='P'&&heading&&content.childElementCount===0&&heading.childElementCount===1){heading.append(e);}else content.append(e);
  }
  for(const article of main.querySelectorAll('.sheet-item')){
   article.classList.add('flow__root');const heading=article.firstElementChild;
   if(heading?.matches('h2,h3')){const group=make('header','heading-group__root');article.prepend(group);group.append(heading);while(group.nextElementSibling?.tagName==='P')group.append(group.nextElementSibling);}
  }
  for(const details of [...main.querySelectorAll('details')].reverse()){
   const children=[...details.children].filter(e=>e.tagName!=='SUMMARY');if(!children.length)continue;
   const panel=make('div','section__flow disclosure__body sheet-disclosure-body');let group=null;
   for(const e of children){if(e.tagName==='H3'){group=make('section','heading-group__root');panel.append(group);}if(group)group.append(e);else panel.append(e);}
   details.append(panel);
  }
 },selectRecipe);
 if(key==='components'){
  for(const frame of await p.locator('iframe').all()){
   const src=await frame.getAttribute('srcdoc');const probe=await layoutBrowser.newPage({viewport:{width:960,height:900}});
   await probe.setContent(src);const height=await probe.evaluate(()=>Math.ceil(document.body.getBoundingClientRect().height+2));await probe.close();
   await frame.evaluate((e,h)=>{e.style.height=h+'px';e.dataset.specimen='true';e.dataset.srcdoc=e.getAttribute('srcdoc');e.removeAttribute('srcdoc');},height);
  }
 }
 const normalized=await p.content();fs.writeFileSync(file,normalized.replace('</body>','<script src="sheets.js"></script>'+ (key==='colors'?'<script src="semantic-colors.js" defer></script>':'')+'</body>'));
}}finally{await layoutBrowser.close();}
for(const [p] of sources){const dest=path.join(output,'sources',p);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.copyFileSync(path.join(sources.get(p).owner==='base-ui'?uiKit.root:root,p),dest);}
const inventory={demonstrationGuidance:{path:GUIDE_PATH,members:demonstrationGuide.members.map(m=>({id:m.id,family:m.family,selectionKey:'members:'+m.id})),scope:'Authored instructions and source identities; observed states remain unverified'},fullPageSpecimens,renderedDependencies:{'colors.html':['semantic-colors.js'],'components.html':Object.values(fullPageSpecimens).map(s=>s.path)},generatorSha256:hash(fs.readFileSync(fileURLToPath(import.meta.url))),extraction:'CSS declarations extracted with Chromium CSSOM; serialization may normalize formatting. Source snapshots preserve original bytes.',scope:'All declarations indexed in installed wireframe-review token-index; source component families and dedicated select/menu contracts',sourceRoot:root,sourceRoots:{'base-ui':uiKit.root,'wireframe-review':root},uiKit:uiKit.identity,sourceHash:hash(JSON.stringify([...sources.values()])),sources:[...sources.values()],counts:{tokens:tokens.length,colors:colorTokens.length,families:components.families.length,dedicated:2,gaps:gap.length},defaults:{tier:'product',scale:'md',size:'md'},tokens,components:components.families,compositionFamilies:contract.families,profileClasses,unregistered,pairs,compositionSpecimens:Object.fromEntries(Object.entries(compositionRecipes).map(([id,specimen])=>[id,{source:specimen.source,ownerGroup:classOwners.get(id)?.id,coverage:specimen.coverage}])),exampleCoverage:{liveFamilyPreviews:components.families.length+2,compositionPreviews:Object.keys(compositionRecipes).length,compositionReferences:Object.keys(contract.families).length,declarationOnlyUtilities:unregistered.length-Object.keys(compositionRecipes).length}};
fs.writeFileSync(path.join(output,'inventory.json'),JSON.stringify(inventory,null,2));fs.writeFileSync(path.join(output,'gaps.json'),JSON.stringify(gap,null,2));console.log(JSON.stringify({output,...inventory.counts,sourceHash:inventory.sourceHash}));
