#!/usr/bin/env node
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';
import {compileControls} from './compile-controls.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),[runtime,output]=process.argv.slice(2);
if(!runtime||!output)throw Error('Usage: check-select-contract.mjs PLAYWRIGHT OUTPUT');
execFileSync(process.execPath,[resolve(root,'scripts/observe-select.mjs'),'--check']);
const out=resolve(output);mkdirSync(out,{recursive:true});
const css=['assets/foundation/ultimate-tokens/colors.css','assets/foundation/ultimate-tokens/typography.css','assets/foundation/maison/geometry.css','assets/foundation/maison/layout.css','assets/wireframe.css'].map(p=>readFileSync(resolve(root,p),'utf8')).join('\n');
const html=`<!doctype html><html lang="en" data-tier="product" data-scale="md" data-size="md"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Native select verification</title><style>${css}</style><body><main class="section__root"><h1>Choose a workspace</h1><label>Workspace<select id="outer" data-select-icon="buildings"><option value="a">Studio</option><option value="b">Workshop</option><option disabled value="c">Unavailable</option></select></label><section data-size="sm"><label>Nested size<select id="inner"><option>Personal</option><option>Team</option></select></label></section><label>Unavailable<select disabled><option>Locked</option></select></label></main></body></html>`;
const compiled=compileControls(html);assert.equal(compileControls(compiled),compiled);assert(!compiled.includes('data-select-icon'));writeFileSync(resolve(out,'select.html'),compiled);
const {chromium,webkit,firefox}=createRequire(import.meta.url)(runtime),report={runs:[],negativeControls:[],unavailable:[],limits:['Native popup styling is platform-owned','Bundled decorative glyphs; native popup painting remains platform-owned','No installed-package support claim','Native popup keyboard selection requires manual platform verification']};
for(const [name,engine] of [['chromium',chromium],['firefox',firefox],['webkit',webkit]]){
 let browser;try{browser=await engine.launch();}catch(e){if(name==='chromium')throw e;report.unavailable.push({browser:name,reason:e.message.split('\n')[0]});continue;}
 try{const p=await browser.newPage({javaScriptEnabled:false});await p.route('https://cdn.jsdelivr.net/**',r=>r.abort());
 for(const width of [390,1400])for(const scheme of ['light','dark']){
 await p.setViewportSize({width,height:900});await p.goto(new URL('file://'+resolve(out,'select.html')).href);await p.evaluate(s=>document.documentElement.style.colorScheme=s,scheme);
 const check=()=>p.evaluate(()=>{const a=document.querySelector('#outer'),b=document.querySelector('#inner'),r=a.getBoundingClientRect(),bs=getComputedStyle(b),as=getComputedStyle(a);const slots=[...a.parentElement.querySelectorAll('[data-slot]')];return {wrappers:document.querySelectorAll('.select__root').length===3,geometry:slots.every(s=>{const x=s.getBoundingClientRect();return Math.abs(x.width-x.height)<.1&&Math.abs(x.top+x.height/2-r.top-r.height/2)<.1&&getComputedStyle(s).pointerEvents==='none'&&s.getAttribute('aria-hidden')==='true'}),inheritance:bs.getPropertyValue('--g-icon')!==as.getPropertyValue('--g-icon')&&bs.getPropertyValue('--ui-ink')===as.getPropertyValue('--ui-ink'),name:a.labels[0].textContent.includes('Workspace'),overflow:document.documentElement.scrollWidth<=innerWidth+1};});
 const checks=await check();assert(Object.values(checks).every(Boolean),JSON.stringify(checks));await p.locator('#outer').focus();assert(await p.locator('#outer').evaluate(e=>document.activeElement===e));await p.keyboard.press('Tab');assert(await p.locator('#inner').evaluate(e=>document.activeElement===e));await p.locator('#outer').selectOption('b');assert.equal(await p.locator('#outer').inputValue(),'b');assert(await p.locator('select[disabled]').isDisabled());
 const mutation=await p.evaluateHandle(()=>{const s=document.createElement('style');s.textContent='.select__root [data-slot]{height:120px!important}';document.head.append(s);return s;});assert.equal((await check()).geometry,false);await mutation.evaluate(e=>e.remove());assert((await check()).geometry);report.negativeControls.push({browser:name,width,scheme,stretchedSlotDetected:true});
 await p.screenshot({path:resolve(out,`${name}-${width}-${scheme}.png`),fullPage:true});report.runs.push({browser:name,width,scheme,checks,keyboardFocus:true,nativeValueChange:true});
 }
 }finally{await browser.close();}
}
writeFileSync(resolve(out,'results.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
