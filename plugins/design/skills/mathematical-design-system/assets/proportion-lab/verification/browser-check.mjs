import {pathToFileURL,fileURLToPath} from 'node:url';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
import assert from 'node:assert/strict';
const b=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})}),p=await b.newPage({viewport:{width:1280,height:900}});let errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(new URL('../dist/index.html',import.meta.url).href);
const config=async(o)=>p.evaluate(o=>{const data={version:1,...window.proportionStudy.getState(),...o};document.querySelector('#configuration').value=JSON.stringify(data);document.querySelector('#applyConfig').click();},o);
let cases=0;
for(const unit of [3,4,6])for(const border of [0,unit/2])for(const controlDensity of ['compact','default','loose'])for(const inset of [0,1.5]){
 await config({unit,border,controlDensity,inset});
 const failures=await p.evaluate(()=>[...document.querySelectorAll('.df-control')].flatMap(el=>{const s=getComputedStyle(el),height=parseFloat(s.getPropertyValue('--height')),r=el.getBoundingClientRect();const slots=[...el.querySelectorAll('.slot')];return [...(r.height+0.05<height?[`height ${r.height}<${height}`]:[]),...slots.flatMap(slot=>Math.abs(slot.getBoundingClientRect().height-parseFloat(s.getPropertyValue('--slot')))>0.05?['slot shrink']:[])];}));assert.deepEqual(failures,[]);cases++;
}
await config({unit:4,border:0,controlDensity:'default',collectionDensity:'default',cardDensity:'default',inset:0,theme:'light'});
await p.locator('#search').fill('Preserved query');await config({cardDensity:'loose'});assert.equal(await p.locator('#search').inputValue(),'Preserved query');assert.equal(await p.locator('#buttons-content .df-control').first().evaluate(el=>el.getBoundingClientRect().height),32);
await p.locator('#currency-trigger').focus();await p.keyboard.press('Enter');assert.equal(await p.locator('#currency-popup').isVisible(),true);await p.keyboard.press('ArrowDown');await p.keyboard.press('Enter');assert.equal(await p.locator('#currency-trigger .label').textContent(),'EUR');assert.equal(await p.locator('#currency-trigger').evaluate(el=>el===document.activeElement),true);
await p.locator('#search').focus();await p.keyboard.press('ArrowRight');const ring=await p.locator('#search').evaluate(el=>({input:getComputedStyle(el).outlineWidth,wrapper:getComputedStyle(el.parentElement).outlineWidth,style:getComputedStyle(el.parentElement).outlineStyle,offset:getComputedStyle(el.parentElement).outlineOffset}));assert.deepEqual(ring,{input:'0px',wrapper:'3px',style:'solid',offset:'0px'});
await p.locator('[data-action="clear"]').focus();const actionRing=await p.locator('[data-action="clear"]').evaluate(el=>getComputedStyle(el).outlineWidth);assert.equal(actionRing,'3px');
await p.locator('#button-densities').scrollIntoViewIfNeeded();await p.screenshot({path:'/tmp/df-buttons-light.png'});
await config({theme:'dark',border:2,inset:1.5});await p.locator('#menus').scrollIntoViewIfNeeded();await p.screenshot({path:'/tmp/df-dark.png'});
await p.setViewportSize({width:390,height:844});await p.locator('#buttons').scrollIntoViewIfNeeded();await p.screenshot({path:'/tmp/df-narrow.png'});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
assert.deepEqual(errors,[]);console.log(JSON.stringify({geometryCases:cases,keyboardCurrency:true,wrapperFocus:ring,actionRing,narrowNoPageOverflow:true,errors}));await b.close();
