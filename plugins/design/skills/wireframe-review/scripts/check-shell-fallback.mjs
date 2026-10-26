#!/usr/bin/env node
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {execFileSync} from 'node:child_process';import {createRequire} from 'node:module';import {pathToFileURL} from 'node:url';
const [runtime,out]=process.argv.slice(2);if(!runtime||!out)throw Error('Usage: check-shell-fallback.mjs PLAYWRIGHT OUTPUT');
const root=path.resolve(import.meta.dirname,'..'),pw=createRequire(import.meta.url)(runtime);fs.mkdirSync(out,{recursive:true});
const manifest=JSON.parse(fs.readFileSync(path.join(root,'assets/example.manifest.json')));
// Mixed counts and escaped author text; retain page compositions unchanged.
manifest.title='Static <review> & proposals';manifest.units.find(u=>u.id==='home').variants=manifest.units.find(u=>u.id==='home').variants.slice(0,2);
const input=path.join(out,'manifest.json'),artifact=path.join(out,'artifact.html');fs.writeFileSync(input,JSON.stringify(manifest));execFileSync(process.execPath,[path.join(root,'scripts/build.mjs'),input,artifact]);
const expected=manifest.units.reduce((n,u)=>n+u.variants.length,0),results=[];
for(const engine of ['chromium','firefox','webkit']){
 const browser=await pw[engine].launch();try{
  for(const width of [390,1399])for(const colorScheme of ['light','dark']){
   const page=await browser.newPage({javaScriptEnabled:false,viewport:{width,height:900},colorScheme});await page.goto(pathToFileURL(path.resolve(artifact)).href);
   assert.equal(await page.locator('.static-review h1').textContent(),manifest.title);assert.equal(await page.locator('.static-proposal').count(),expected);assert.equal(await page.locator('.toolbar').isVisible(),false);assert.equal(await page.locator('.workspace').isVisible(),false);
   for(let i=0;i<expected;i++){
    const details=page.locator('.static-proposal').nth(i);await details.locator('summary').click();assert.equal(await details.getAttribute('open'),'');
    const frame=await (await details.locator('iframe').elementHandle()).contentFrame();await frame.waitForSelector('body');assert.ok((await frame.locator('body').innerText()).trim().length>0);
    const border=await details.evaluate(el=>getComputedStyle(el).borderTopWidth);assert.notEqual(border,'0px');
    await details.locator('summary').click();
   }
   // Page composition must render the actual source leaf text in its declared order.
   const first=page.locator('.static-proposal').first();await first.locator('summary').click();const frame=await (await first.locator('iframe').elementHandle()).contentFrame();
   const ordered=manifest.units[0].variants[0].composition.map(part=>manifest.units.find(u=>u.id===part.unitId).variants.find(v=>v.id===part.variantId).html);
   assert.ok(ordered.length>1);assert.equal(await frame.locator('body').evaluate(el=>el.innerHTML),ordered.join('\n'));
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert.ok(await frame.evaluate(()=>getComputedStyle(document.body).fontFamily.length>0));
   if(engine==='chromium'&&width===390&&colorScheme==='dark')await page.screenshot({path:path.join(out,'mobile.png')});
   results.push({engine,width,colorScheme,proposals:expected,nativeDisclosure:true,composition:true,hiddenInactiveChrome:true});await page.close();
  }
  const page=await browser.newPage();await page.goto(pathToFileURL(path.resolve(artifact)).href);await page.locator('#canvas iframe').first().waitFor();assert.equal(await page.locator('.static-review').count(),0);assert.equal(await page.locator('.workspace').isVisible(),true);await page.close();
 }finally{await browser.close()}
}
fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify({results,artifactBytes:fs.statSync(artifact).size,scriptEnabledEngines:3},null,2));console.log(`PASS ${results.length} no-script cases and three script-enabled checks; ${expected} proposals; ${fs.statSync(artifact).size} bytes`);
