import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=fs.mkdtempSync(path.join(os.tmpdir(),'wireframe-spacing-'));
const contract=JSON.parse(fs.readFileSync(path.join(root,'references/style/contract.json')));
const css=contract.styles.map(p=>fs.readFileSync(path.resolve(root,'references/style',p),'utf8')).join('\n');
const recipe=fs.readFileSync(path.join(root,'assets/recipes/spacing.html'),'utf8');
const html=`<!doctype html><html><meta name="viewport" content="width=device-width"><style>${css}\nbody{padding:16px}.card__root{max-width:760px;margin:auto}</style><body>${recipe}</body></html>`;
fs.writeFileSync(path.join(out,'index.html'),html);
const {chromium}=createRequire(import.meta.url)(process.argv[2]);const browser=await chromium.launch();const results=[];
try{
 const page=await browser.newPage();
 for(const width of [360,1200]) for(const [size,unit] of [["sm",5.5],["md",8],["lg",10]]) {
  await page.setViewportSize({width,height:1000});await page.setContent(html);
  await page.locator('body').evaluate((e,s)=>{e.dataset.tier='product';e.dataset.size=s;},size);
  const measure=()=>page.evaluate(()=>{
   const el=s=>document.querySelector(s), rect=e=>e.getBoundingClientRect(), gap=(a,b)=>rect(b).top-rect(a).bottom;
   const fields=el('[data-part=fields]'),panel=el('.card__root'),opts=el('.options__root'),status=el('[data-part=status]');
   return {margin:parseFloat(getComputedStyle(panel).paddingLeft),content:gap(fields.children[0],fields.children[1]),after:gap(fields,el('[data-part=direction]')),heading:gap(el('#scope-title'),fields),footer:gap(el('[data-part=direction]'),el('footer')),field:gap(el('.field__root').children[0],el('.field__root').children[1]),options:gap(opts.children[0],opts.children[1]),status:gap(status.children[0],status.children[1]),inline:parseFloat(getComputedStyle(el('.cluster__root')).columnGap),nestedPadding:parseFloat(getComputedStyle(fields.children[1]).paddingLeft),overflow:document.documentElement.scrollWidth>innerWidth};
  });
  const valid=m=>Math.abs(m.margin-unit*4)<.6&&Math.abs(m.content-unit*2)<.6&&['after','heading','footer'].every(k=>Math.abs(m[k]-unit*3)<.6)&&['field','options','status','inline'].every(k=>Math.abs(m[k]-unit)<.6)&&m.nestedPadding===0&&!m.overflow;
  const baseline=await measure();assert(valid(baseline),JSON.stringify({width,unit,baseline}));
  for(const [selector,property,value] of [['.card__root','gap',`${unit*2}px`],['[data-part=fields]','gap','0px'],['.options__root','gap',`${unit*4}px`],['.card__root','padding',`${unit*8}px`],['[data-part=collections]','margin-top',`${unit}px`]]) {
   await page.locator(selector).evaluate((e,[p,v])=>e.style.setProperty(p,v),[property,value]);assert(!valid(await measure()),`missed mutation ${selector}/${property}`);await page.locator(selector).evaluate((e,p)=>e.style.removeProperty(p),property);assert(valid(await measure()));
  }
  results.push({width,unit,baseline,negativeControls:5});
 }
 await page.screenshot({path:path.join(out,'spacing.png'),fullPage:true});
}finally{await browser.close();}
fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({results,limitations:['Chromium only','Product tier at medium scale with small, medium and large sizes','Authored recipe, not generation efficacy']},null,2));
console.log(`PASS ${results.length} spacing cases, ${results.length*5} negative controls: ${out}`);
