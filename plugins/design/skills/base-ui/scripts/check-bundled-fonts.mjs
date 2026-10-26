import fs from 'node:fs';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
import {getAssetBundle} from './api.mjs';
const [runtime,executablePath,out='/private/tmp/base-ui-fonts']=process.argv.slice(2);
const manifest=JSON.parse(fs.readFileSync(new URL('../assets/fonts/manifest.json',import.meta.url)));
for(const f of manifest.faces){assert.equal(f.format,'woff2');assert.equal(fs.readFileSync(new URL('../assets/fonts/'+f.file,import.meta.url)).subarray(0,4).toString(),'wOF2');}
const css=getAssetBundle().css;assert(css.includes('data:font/woff2;base64,'));assert(!css.includes('data:font/ttf'));
const browser=await createRequire(import.meta.url)(runtime).chromium.launch({headless:true,executablePath});
try{
 const context=await browser.newContext({offline:true});const p=await context.newPage(),requests=[];p.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url());});
 await p.setContent(`<style>${css}</style><h1 id="display">Bricolage Grotesque offline glyphs</h1><pre id="mono">IBM Plex Mono 0123456789</pre>`);
 const loaded=await p.evaluate(async faces=>{const result=[];for(const f of faces){const weight=f.weight.split(' ')[0];const a=await document.fonts.load(`${f.style} ${weight} 20px "${f.family}"`,'Offline glyphs 0123');result.push({family:f.family,weight:f.weight,style:f.style,count:a.length,status:a.map(x=>x.status)});}await document.fonts.ready;return result;},manifest.faces);
 assert(loaded.every(x=>x.count>0&&x.status.every(s=>s==='loaded')));
 const cdp=await context.newCDPSession(p);await cdp.send('DOM.enable');await cdp.send('CSS.enable');
 async function actual(selector){const {root}=await cdp.send('DOM.getDocument');const {nodeId}=await cdp.send('DOM.querySelector',{nodeId:root.nodeId,selector});return(await cdp.send('CSS.getPlatformFontsForNode',{nodeId})).fonts;}
 const display=await actual('#display'),mono=await actual('#mono');
 assert(display.some(f=>f.isCustomFont&&f.familyName.includes('Bricolage')&&f.glyphCount>0));assert(mono.some(f=>f.isCustomFont&&f.familyName.includes('IBM Plex Mono')&&f.glyphCount>0));
 assert.equal(requests.length,0);
 // A font-family string is not evidence: remove font-face rules while keeping stacks.
 await p.setContent('<h1 id="display" style="font-family:Bricolage Grotesque,system-ui">Bricolage Grotesque offline glyphs</h1>');await p.evaluate(()=>document.fonts.ready);
 const missing=await actual('#display');assert(!missing.some(f=>f.isCustomFont&&f.familyName.includes('Bricolage')));
 const result={result:'PASS offline bundled fonts',faces:loaded,display,mono,networkRequests:requests,missingFaceControl:missing};fs.writeFileSync(`${out}/font-checks.json`,JSON.stringify(result,null,2));console.log(JSON.stringify(result));
}finally{await browser.close()}
