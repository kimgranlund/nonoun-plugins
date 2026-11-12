#!/usr/bin/env node
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const [runtime,outArg]=process.argv.slice(2);
if(!runtime||!outArg)throw Error('Usage: node check-style-contract.mjs PLAYWRIGHT OUTPUT');
const out=resolve(outArg);mkdirSync(out,{recursive:true});
const contractPath=resolve(root,'references/style/contract.json'),contract=JSON.parse(readFileSync(contractPath));
const css=contract.styles.map(p=>readFileSync(resolve(dirname(contractPath),p),'utf8')).join('\n');
const html=`<!doctype html><html data-tier="product" data-scale="md" data-size="md"><meta charset="utf-8"><title>Style contract verification</title><style>${css}
header.bar {padding:var(--m-margin-card) max(var(--ui-section-margin),calc((100% - var(--ui-content-width))/2));display:flex;justify-content:space-between;align-items:center}
.choice {display:flex;align-items:center;gap:var(--g-gutter)} .choice input {width:var(--g-icon);height:var(--g-icon);margin:0;padding:0;flex:none}
.account {position:relative} summary {cursor:pointer;padding:var(--g-margin);margin:0}
.menu {position:absolute;right:0;top:calc(100% + var(--g-margin)/2);padding:var(--m-margin-card);background:var(--ui-surface);border:var(--m-border-thin) solid var(--ui-border);z-index:2}
.account:not([open]) .menu {display:none}
.stack {display:grid;gap:var(--m-gap-stack)} .stack>* {margin:0}
.item {display:grid;grid-template-columns:auto minmax(0,1fr);gap:var(--m-gap-stack);align-items:start}
.icon {display:grid;place-items:center;inline-size:var(--g-icon);block-size:var(--g-icon)}
.icon i {display:block;width:100%;height:100%}.item h3{overflow-wrap:anywhere}
</style><body><header class="bar"><strong>Studio</strong><details class="account"><summary>Account</summary><div class="menu"><a href="#approval">Overview</a></div></details></header><main class="section__root"><div class="stack" id="approval"><h1>Review a proposed direction</h1><article class="card__root stack"><h2>Approval with alternatives</h2><div class="item"><span class="icon" aria-hidden="true"><i class="ph-icon" data-ph="folder"></i></span><div><h3>A long proposal label that wraps without changing its document icon geometry</h3><p>Compare a reversible pilot with a larger release. Sources remain incomplete.</p></div></div><label class="choice"><input type="radio" name="path" checked> Pilot</label><label class="choice"><input type="radio" name="path"> Retain alternate</label><div class="actions__root"><button type="button">Review plan</button><button type="button" disabled>Release unavailable</button></div></article><article class="card__root stack"><h2>Evidence comparison</h2><p>One source supports the pilot; another leaves the audience estimate uncertain.</p><a href="#source">Inspect source</a><p id="source">Synthetic evidence for testing only.</p></article><p>No additional artifacts yet.</p></div></main></body></html>`;
writeFileSync(resolve(out,'style-contract.html'),html);
const {chromium,webkit}=createRequire(import.meta.url)(runtime);const report={fixture:'authored, not model generated',runs:[],negativeControls:[],unavailable:[],modelBenchmark:'not run',blindReview:'not run'};
async function measurements(page){return page.evaluate(()=>{
 const q=s=>document.querySelector(s),rect=e=>e.getBoundingClientRect();
 const icon=q('.icon'),is=getComputedStyle(icon),stack=q('.stack'),sc=getComputedStyle(stack),kids=[...stack.children],bar=q('.bar'),section=q('.section__root'),bs=getComputedStyle(bar),ss=getComputedStyle(section),d=q('.account');
 d.open=false;const before=rect(bar).height;d.open=true;const after=rect(bar).height;
 const gap=rect(q('.menu')).top-rect(q('summary')).bottom,expected=parseFloat(getComputedStyle(q('summary')).paddingTop)/2;d.open=false;
 return {icon:Math.abs(rect(icon).height-parseFloat(is.width))<.1,spacing:Math.abs(rect(kids[1]).top-rect(kids[0]).bottom-parseFloat(sc.rowGap))<.1,menu:before===after&&Math.abs(gap-expected)<.1,alignment:Math.abs(rect(bar).left+parseFloat(bs.paddingLeft)-rect(section).left-parseFloat(ss.paddingLeft))<.1,overflow:document.documentElement.scrollWidth<=innerWidth+1};
});}
for(const [name,engine] of [['chromium',chromium],['webkit',webkit]]){
 let browser;try{browser=await engine.launch();}catch(e){if(name==='chromium')throw e;report.unavailable.push({browser:name,reason:String(e.message).split('\n')[0]});continue;}
 try {const page=await browser.newPage();await page.route('https://cdn.jsdelivr.net/**',r=>r.abort());
 for(const scheme of ['light','dark'])for(const width of [390,900,1600]){await page.setViewportSize({width,height:1000});await page.emulateMedia({colorScheme:scheme});await page.goto(pathToFileURL(resolve(out,'style-contract.html')).href);await page.evaluate(s=>document.documentElement.style.colorScheme=s,scheme);const checks=await measurements(page);assert(Object.values(checks).every(Boolean),JSON.stringify({name,width,scheme,checks}));await page.locator('summary').focus();await page.keyboard.press('Enter');assert(await page.locator('.account').evaluate(e=>e.open));await page.keyboard.press('Enter');assert(!(await page.locator('.account').evaluate(e=>e.open)));await page.locator('input').nth(1).check();assert(await page.locator('input').nth(1).isChecked());await page.screenshot({path:resolve(out,`${name}-${scheme}-${width}.png`),fullPage:true});report.runs.push({browser:name,width,scheme,checks,keyboardDisclosure:true,nativeSelection:true});}
 const mutations=[['icon','.icon{height:150px!important}'],['spacing','.stack>article{margin-top:20px!important}'],['menu','.menu{position:static!important}'],['alignment','.bar{padding-left:0!important}']];
 for(const [key,rule] of mutations){const tag=await page.addStyleTag({content:rule});const checks=await measurements(page);assert.equal(checks[key],false,`Detector missed ${key}`);await tag.evaluate(e=>e.remove());assert((await measurements(page))[key]);report.negativeControls.push({browser:name,defect:key,detected:true,recovered:true});}
 }finally{await browser.close();}
}
writeFileSync(resolve(out,'results.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
