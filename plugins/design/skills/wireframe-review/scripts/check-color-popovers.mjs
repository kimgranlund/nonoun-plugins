import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const [out,runtime]=process.argv.slice(2),pw=createRequire(import.meta.url)(runtime),cases=[];
for(const engine of ['chromium','firefox','webkit']){
 const b=await pw[engine].launch();
 try{const p=await b.newPage({javaScriptEnabled:false,colorScheme:'dark'});
 p.setDefaultTimeout(5000);
 for(const width of [360,1399]){
 console.log('Checking',engine,width);
  await p.setViewportSize({width,height:1000});
  await p.goto(pathToFileURL(path.join(out,'colors.html')).href);
  const trigger=p.locator('.color-values-trigger').first();
  await trigger.scrollIntoViewIfNeeded();await trigger.focus();const before=await trigger.boundingBox();await p.keyboard.press('Space');
  const panel=p.locator('.color-popover:popover-open');await panel.waitFor({state:'visible'});
  assert.equal((await trigger.boundingBox()).y,before.y);
  const details=panel.locator('details').first();await details.locator(':scope > summary').click();
  const contained=await details.evaluate(e=>{
   const s=getComputedStyle(e),r=e.getBoundingClientRect(),summary=e.querySelector(':scope > summary'),body=e.querySelector(':scope > .disclosure__body'),br=body.getBoundingClientRect();
   return parseFloat(s.borderTopWidth)>0&&parseFloat(s.borderRadius)>0&&getComputedStyle(summary).borderTopWidth==='0px'&&br.left>=r.left&&br.right<=r.right&&br.bottom<=r.bottom&&parseFloat(getComputedStyle(body).paddingLeft)>0;
  });assert(contained,'Expanded disclosure must share one outer container');
  const r=await panel.boundingBox();assert(r.x>=-1&&r.x+r.width<=width+1&&r.y>=-1&&r.y+r.height<=1001,JSON.stringify({engine,width,r}));
  await p.keyboard.press('Escape');assert.equal(await panel.count(),0);assert(await trigger.evaluate(e=>e===document.activeElement));
  await trigger.click();const close=panel.getByRole('button',{name:'Close',exact:true});await close.focus();await p.keyboard.press('Enter');await panel.waitFor({state:'hidden'});assert.equal(await panel.count(),0,engine+' '+width+' Close');
  await trigger.click();const pointerClose=panel.getByRole('button',{name:'Close',exact:true});await pointerClose.scrollIntoViewIfNeeded();await p.waitForTimeout(200);await pointerClose.click();await panel.waitFor({state:'hidden'});
  await trigger.click();const outside={x:2,y:2};assert(await panel.evaluate((e,pt)=>!e.contains(document.elementFromPoint(pt.x,pt.y)),outside),'Dismissal pointer must be outside the panel');await p.mouse.click(outside.x,outside.y);await panel.waitFor({state:'hidden'});assert.equal(await panel.count(),0);
  cases.push({engine,width,pageScripts:false,containedDisclosure:true});
 }
 await p.locator('.color-values-trigger').first().click();
 const d=p.locator('.color-popover:popover-open details').first();if(!await d.evaluate(e=>e.open)){await d.locator(':scope > summary').focus();await p.keyboard.press('Enter');}
 await p.screenshot({path:path.join(out,'popover-'+engine+'.png')});
 // Negative control: a header-only border cannot satisfy whole-panel containment.
 await d.evaluate(e=>e.style.border='0');
 assert.equal(await d.evaluate(e=>parseFloat(getComputedStyle(e).borderTopWidth)),0);
 }finally{await b.close();}
}
fs.writeFileSync(path.join(out,'popover-verification.json'),JSON.stringify({cases,negativeControls:3,limits:['Playwright engines; no assistive-technology audit']},null,2));
console.log('PASS six no-JS color popover/disclosure cases and three containment negative controls');
