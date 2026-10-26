import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)(process.argv[2]);const browser=await chromium.launch();
try{const page=await browser.newPage();await page.goto('http://127.0.0.1:8741/');await page.waitForSelector('#button-density-grid button');await page.waitForTimeout(600);await page.evaluate(()=>{const e=document.querySelector('#controlAmount');e.value=100;e.dispatchEvent(new Event('input',{bubbles:true}));});
for(const [density,height,margin]of [['tight',24,0],['compact',28,2],['regular',32,4],['spacious',36,6],['loose',40,8]]){
 await page.locator('#density-trigger').click();await page.locator('#density-popup').getByRole('option',{name:density[0].toUpperCase()+density.slice(1),exact:true}).click();await page.waitForTimeout(100);
 const measured=await page.evaluate(()=>({rows:[...document.querySelectorAll('#menu > [role=menuitem]')].map(e=>{const label=e.querySelector('[data-slot=label]'),s=getComputedStyle(e);return {radius:parseFloat(s.borderTopLeftRadius),height:e.getBoundingClientRect().height,slot:label.getBoundingClientRect().height,padding:parseFloat(s.paddingTop),inline:parseFloat(s.paddingLeft),wrapper:parseFloat(getComputedStyle(label).paddingLeft)}}),selection:document.querySelector('#listbox .listbox__option').getBoundingClientRect().height}));
 for(const row of measured.rows)assert.deepEqual(row,{radius:height/2,height,slot:24,padding:margin,inline:margin,wrapper:2});assert.equal(measured.selection,24);
}
console.log('PASS five-density full menu rows; fixed slots, clearance, no compensation, selection rows unchanged');
}finally{await browser.close()}
