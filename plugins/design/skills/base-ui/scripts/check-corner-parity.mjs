import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {getAssetBundle} from './api.mjs';
import {resolve,resolveRadii} from '../../mathematical-design-system/scripts/lib/scale.mjs';
const [runtime,executablePath,out]=process.argv.slice(2);
const pw=createRequire(import.meta.url)(runtime),browser=await pw.chromium.launch({executablePath});
const roles=['control','mark','listbox','listboxOption','group','groupInner','widget','card','layout'];
const tokens=[['--radius','--mark-radius','--listbox-radius','--listbox-option-radius','--group-radius','--group-inner-radius','--widget-radius','--card-radius','--layout-radius'],['--r-control','--r-mark','--r-listbox','--r-listbox-option','--r-group','--r-group-inner','--r-widget','--r-card','--r-layout']];
let cases=0;
try{
 for(const [i,css] of [fs.readFileSync(new URL('../../../../Projects/ui-kit/system/tokens.css',import.meta.url),'utf8'),getAssetBundle().css].entries()){
  const p=await browser.newPage();await p.setContent(`<style>${css}</style><main id="region">${tokens[i].map(t=>`<i style="display:block;width:500px;height:500px;border-radius:var(${t})"></i>`).join('')}<div class="segments__root"><button>A</button><button>B</button></div><input class="radio__control" type="radio"><span class="switch__control"></span></main>`);
  for(const supported of [true,false]){
   // Exercise the round branch explicitly even when this engine supports superellipse.
   await p.evaluate(s=>{document.documentElement.style.setProperty('--corner-scale',s?'1.5':'1');document.documentElement.style.setProperty('--corner-shape',s?'superellipse(1.5)':'round')},supported);
   for(const tier of ['widget','product','content','brand'])for(const scale of ['sm','md','lg'])for(const size of ['sm','md','lg']){
    await p.locator('#region').evaluate((e,v)=>Object.assign(e.dataset,v),{tier,scale,size});
    const actual=await p.locator('#region > i').evaluateAll(es=>es.map(e=>({r:parseFloat(getComputedStyle(e).borderTopLeftRadius),shape:getComputedStyle(e).cornerShape})));
    const expected=resolveRadii(resolve(tier,scale,size).n,supported);
    actual.forEach((v,j)=>{assert.equal(v.r,expected[roles[j]],`${i}/${tier}/${scale}/${size}/${supported}/${roles[j]}`);assert.equal(v.shape,supported?'superellipse(1.5)':'superellipse(1)')});cases++;
   }
  }
  if(i){
   await p.locator('.segments__root').evaluate(e=>e.style.setProperty('--ui-composed-radius','22px'));
   const pair=await p.locator('.segments__root').evaluate(e=>({inner:parseFloat(getComputedStyle(e.firstElementChild).borderTopLeftRadius),offset:parseFloat(getComputedStyle(e).paddingLeft)+parseFloat(getComputedStyle(e).borderLeftWidth)}));assert.equal(pair.inner,22-pair.offset);
   for(const selector of ['.radio__control','.switch__control'])assert.equal(await p.locator(selector).evaluate(e=>getComputedStyle(e).cornerShape),'superellipse(1)');
   assert.equal(await p.locator('.switch__control').evaluate(e=>getComputedStyle(e,'::before').cornerShape),'superellipse(1)');
  }
  await p.close();
 }
 fs.mkdirSync(out,{recursive:true});fs.writeFileSync(out+'/verification.json',JSON.stringify({status:'pass',cases,roles,fallback:'Forced round branch in Chromium; not a separate unsupported engine',nestedOverride:true,circles:true},null,2));console.log(`PASS ${cases} corner contexts, nine roles, supported and round fallback, nested override and circular exceptions`);
}finally{await browser.close()}
