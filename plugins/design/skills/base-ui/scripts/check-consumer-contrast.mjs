import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {auditContrast} from './lib/audit-contrast.mjs';
const [runtime,out,executable]=process.argv.slice(2);
if(!runtime||!out)throw Error('Usage: check-consumer-contrast.mjs PLAYWRIGHT OUTPUT [CHROMIUM_EXECUTABLE]');
const {chromium}=createRequire(import.meta.url)(runtime);
const browser=await chromium.launch(executable?{executablePath:executable}:{}),page=await browser.newPage(),tests=[];
async function test(name,html,check){await page.setContent('<style>body{background:white;color:black;font:16px Arial} p{margin:8px}</style>'+html);const result=await page.evaluate(auditContrast);assert.deepEqual(result.summary,{status:result.status,...result.counts});check(result);tests.push({name,result});}
try{
await test('black on white passes','<p>Readable</p>',r=>{assert.equal(r.status,'pass');assert.equal(r.measurements[0].ratio,21)});
await test('equal foreground/background fails','<p style="color:white">Invisible</p>',r=>{assert.equal(r.status,'fail');assert.equal(r.failures[0].ratio,1)});
await test('partial-alpha foreground fails','<p style="color:rgba(0,0,0,.3)">Faint</p>',r=>{assert.equal(r.status,'fail');assert(r.measurements[0].foreground[0]>175)});
await test('partial-alpha backgrounds compose','<div style="background:black"><p style="background:rgba(255,255,255,.5);color:black">Composite</p></div>',r=>{assert.equal(r.status,'pass');assert(Math.abs(r.measurements[0].background[0]-128)<1)});
await test('large text threshold','<p style="font-size:24px;color:#888">Large</p><p style="color:#888">Normal</p>',r=>{assert(r.measurements[0].pass);assert(!r.measurements[1].pass);assert.equal(r.measurements[0].threshold,3)});
await test('gradient unverified','<p style="background:linear-gradient(white,black)">Unknown</p>',r=>{assert.equal(r.status,'incomplete');assert.equal(r.unsupported.length,1)});
await test('opaque child covers ancestor gradient','<div style="background:linear-gradient(white,black)"><p style="background:white">Known</p></div>',r=>assert.equal(r.status,'pass'));
await test('group opacity unverified','<div style="opacity:.5"><p>Unknown</p></div>',r=>assert.equal(r.status,'incomplete'));
await test('disabled explicit exclusion','<button disabled style="color:white;background:white">Unavailable</button><p>Available</p>',r=>{assert.equal(r.status,'pass');assert.equal(r.excluded.length,1)});
await test('hidden content omitted','<p hidden>Hidden</p><details><summary>Visible</summary><p>Collapsed</p></details>',r=>assert.deepEqual(r.measurements.map(m=>m.text),['Visible']));
await test('native selected value measured','<select style="color:black;background:white"><option>Selected</option><option>Unselected</option></select>',r=>{assert.equal(r.measurements.length,1);assert.equal(r.measurements[0].text,'Selected')});
await test('generated text unverified','<style>p:before{content:"Generated"}</style><p>Text</p>',r=>assert.equal(r.status,'incomplete'));
await test('empty scope incomplete','<div></div>',r=>assert.equal(r.status,'incomplete'));
await page.setContent('<p>Text</p>');const missing=await page.evaluate(auditContrast,{rootSelector:'#missing'});assert.equal(missing.status,'incomplete');tests.push({name:'missing root incomplete',result:missing});
await page.setContent('<style>body{background:white}button{appearance:none;color:black;background:white;border:1px solid black}</style><button id="edge">Edge</button>');
let edge=await page.evaluate(auditContrast,{boundarySelectors:['#edge']});assert(edge.boundaryMeasurements[0].pass);tests.push({name:'explicit visible boundary passes',result:edge});
await page.addStyleTag({content:'#edge{border-color:white}'});edge=await page.evaluate(auditContrast,{boundarySelectors:['#edge']});assert(!edge.boundaryMeasurements[0].pass);tests.push({name:'invisible boundary fails',result:edge});
await page.addStyleTag({content:'#edge{appearance:auto}'});edge=await page.evaluate(auditContrast,{boundarySelectors:['#edge']});assert.equal(edge.status,'incomplete');tests.push({name:'native boundary unsupported',result:edge});
fs.mkdirSync(out,{recursive:true});
await page.setContent('<style>body{margin:20px;background:white}input{width:160px;height:40px;box-sizing:border-box;font:16px Arial;color:black;background:white}#number{appearance:auto;border:2px solid black}</style><input id="number" type="number" value="12"><input id="default-number" type="number" value="12">');
edge=await page.evaluate(auditContrast,{boundarySelectors:['#number']});assert.equal(edge.status,'pass');assert.equal(edge.boundaryMeasurements[0].fillRatio,null);tests.push({name:'native number opaque CSS border passes without certifying fill',result:edge});
const screenshot=await page.screenshot({path:path.join(out,'native-number-authored-border.png')});
const {PNG}=createRequire(import.meta.url)(path.resolve(runtime,'../pngjs'));
const png=PNG.sync.read(screenshot),box=await page.locator('#number').boundingBox(),pixel=(x,y)=>{const i=(Math.floor(y)*png.width+Math.floor(x))*4;return [...png.data.slice(i,i+4)];};
const pixels={left:pixel(box.x,box.y+box.height/2),right:pixel(box.x+box.width-1,box.y+box.height/2),top:pixel(box.x+box.width/2,box.y),bottom:pixel(box.x+box.width/2,box.y+box.height-1),outside:pixel(box.x-1,box.y+box.height/2)};
for(const side of ['left','right','top','bottom'])assert.deepEqual(pixels[side],[0,0,0,255]);assert.deepEqual(pixels.outside,[255,255,255,255]);tests.push({name:'Chromium screenshot confirms four CSS outer border pixels',screenshot:'native-number-authored-border.png',box,pixels});
edge=await page.evaluate(auditContrast,{boundarySelectors:['#default-number']});assert.equal(edge.status,'incomplete');tests.push({name:'default native number edge remains unsupported',result:edge});
await page.addStyleTag({content:'#number{border-color:white;background:black;color:white}'});edge=await page.evaluate(auditContrast,{boundarySelectors:['#number']});assert.equal(edge.status,'fail');assert.equal(edge.boundaryMeasurements[0].fillRatio,null);tests.push({name:'native number invisible border fails despite contrasting CSS fill',result:edge});
await page.addStyleTag({content:'#number{border-color:rgba(0,0,0,.5)}'});edge=await page.evaluate(auditContrast,{boundarySelectors:['#number']});assert.equal(edge.status,'incomplete');tests.push({name:'native number translucent border remains unsupported',result:edge});
for(const type of ['date','text','textarea']){
  const field=type==='textarea'?'<textarea id="field">Note</textarea>':`<input id="field" type="${type}" value="${type==='date'?'2026-10-15':'Location'}">`;
  await page.setContent(`<style>body{margin:20px;background:white}#field{appearance:auto;width:200px;height:40px;box-sizing:border-box;border:2px solid black;background:white;color:black;font:16px Arial}</style>${field}`);
  edge=await page.evaluate(auditContrast,{boundarySelectors:['#field']});assert.equal(edge.status,'pass');assert.equal(edge.boundaryMeasurements[0].fillRatio,null);
  const shot=await page.screenshot({path:path.join(out,`native-${type}-authored-border.png`)}),parsed=PNG.sync.read(shot),b=await page.locator('#field').boundingBox();
  const sample=(x,y)=>{const i=(Math.floor(y)*parsed.width+Math.floor(x))*4;return [...parsed.data.slice(i,i+4)];};
  const sampled={left:sample(b.x,b.y+b.height/2),right:sample(b.x+b.width-1,b.y+b.height/2),top:sample(b.x+b.width/2,b.y),bottom:sample(b.x+b.width/2,b.y+b.height-1),outside:sample(b.x-1,b.y+b.height/2)};
  for(const side of ['left','right','top','bottom'])assert.deepEqual(sampled[side],[0,0,0,255]);assert.deepEqual(sampled.outside,[255,255,255,255]);
  tests.push({name:`native ${type} opaque CSS border measured and screenshot confirmed`,result:edge,screenshot:`native-${type}-authored-border.png`,box:b,pixels:sampled});
  await page.addStyleTag({content:'#field{border:2px dashed black}'});edge=await page.evaluate(auditContrast,{boundarySelectors:['#field']});assert.equal(edge.status,'incomplete');tests.push({name:`native ${type} dashed edge unsupported`,result:edge});
  await page.addStyleTag({content:'#field{border:2px solid rgba(0,0,0,.5)}'});edge=await page.evaluate(auditContrast,{boundarySelectors:['#field']});assert.equal(edge.status,'incomplete');tests.push({name:`native ${type} translucent edge unsupported`,result:edge});
}
const listboxFixture=(fill)=>`<style>.combobox__list > [role=option]{position:relative;isolation:isolate;padding:8px;color:white}.combobox__list > [role=option]::before{content:"";position:absolute;z-index:-1;inset:1px;background:${fill}}</style><div class="combobox__list"><div role="option">Selected</div></div>`;
await test('isolated inset listbox background passes',listboxFixture('black'),r=>assert.equal(r.status,'pass'));
await test('isolated inset listbox equal pair fails',listboxFixture('white'),r=>assert.equal(r.status,'fail'));
await test('partially covered listbox stays unverified',listboxFixture('black')+'<style>[role=option]::before{right:95%!important}</style>',r=>assert.notEqual(r.status,'pass'));
fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify(tests,null,2));console.log(`PASS ${tests.length} consumer text-contrast fixtures (includes negative and unsupported cases)`);
}finally{await browser.close()}
