import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {execFileSync} from 'node:child_process';import{createRequire}from'node:module';import{pathToFileURL}from'node:url';import{newReview,validateReview,selectVariant,resolveParts}from'../assets/model.mjs';
const[runtime,out]=process.argv.slice(2);if(!runtime||!out)throw Error('Usage: check-proposal-count.mjs PLAYWRIGHT OUTPUT');const root=path.resolve(import.meta.dirname,'..');fs.mkdirSync(out,{recursive:true});const pw=createRequire(import.meta.url)(runtime),evidence=[];
for(const count of [1,2,3]){const m=JSON.parse(fs.readFileSync(path.join(root,'assets/example.manifest.json')));m.units=[m.units.find(u=>u.id==='hero')];m.units[0].variants=m.units[0].variants.slice(0,count);m.interactions=[];const file=path.join(out,`manifest-${count}.json`),html=path.join(out,`artifact-${count}.html`);fs.writeFileSync(file,JSON.stringify(m));execFileSync(process.execPath,[path.join(root,'scripts/build.mjs'),file,html]);const r=newReview(m);selectVariant(r,'hero','A');validateReview(JSON.parse(JSON.stringify(r)),JSON.parse(fs.readFileSync(path.join(root,'references/feedback.schema.json'))),m);if(count===1){const bad=structuredClone(r);bad.choices.hero.states.B='selected';assert.throws(()=>validateReview(bad,JSON.parse(fs.readFileSync(path.join(root,'references/feedback.schema.json'))),m));}
for(const name of ['chromium','firefox','webkit']){const b=await pw[name].launch();try{const p=await b.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(pathToFileURL(path.resolve(html)).href);assert.equal(await p.locator('.proposal').count(),count);assert.equal(await p.locator('#preview option').count(),count);assert.equal(await p.locator('#note-variant option').count(),count);await p.locator('#view').selectOption('inspect');await p.locator('#preview').selectOption(['A','B','C'][count-1]);assert.equal(await p.locator('.proposal').count(),1);await p.locator('#view').selectOption('compare');assert.equal(await p.locator('.proposal').count(),count);assert.deepEqual(errors,[]);evidence.push({name,count,rendered:true,roundTrip:true});}finally{await b.close()}}}
// Mixed page/leaf counts exercise both global choices and page overrides.
const mixed=JSON.parse(fs.readFileSync(path.join(root,'assets/example.manifest.json')));
const counts={home:2,header:1,hero:3,proof:2,footer:1};
for(const unit of mixed.units){unit.variants=unit.variants.slice(0,counts[unit.id]||1);for(const variant of unit.variants)for(const part of variant.composition||[])if(!['A','B','C'].slice(0,counts[part.unitId]||1).includes(part.variantId))part.variantId='A';}
const mixedFile=path.join(out,'manifest-mixed.json'),mixedHtml=path.join(out,'artifact-mixed.html');
fs.writeFileSync(mixedFile,JSON.stringify(mixed));execFileSync(process.execPath,[path.join(root,'scripts/build.mjs'),mixedFile,mixedHtml]);
const feedbackSchema=JSON.parse(fs.readFileSync(path.join(root,'references/feedback.schema.json'))),review=newReview(mixed);
selectVariant(review,'home','B');selectVariant(review,'hero','C');review.pageOverrides.home={proof:'A'};
validateReview(JSON.parse(JSON.stringify(review)),feedbackSchema,mixed);
assert.equal(resolveParts(mixed,review,'home','B').find(x=>x.unitId==='hero').variantId,'C');
assert.equal(resolveParts(mixed,review,'home','B').find(x=>x.unitId==='proof').variantId,'A');
const invalid=structuredClone(review);invalid.pageOverrides.home.header='B';assert.throws(()=>validateReview(invalid,feedbackSchema,mixed));
for(const name of ['chromium','firefox','webkit']){
 const browser=await pw[name].launch();try{
  const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(pathToFileURL(path.resolve(mixedHtml)).href);
  await page.locator('#page').selectOption('home');
  for(const [id,count]of Object.entries(counts)){
   await page.locator('#unit').selectOption(id);await page.locator('#view').selectOption('compare');
   assert.equal(await page.locator('.proposal').count(),count,id);assert.equal(await page.locator('#preview option').count(),count,id);
   await page.locator('#view').selectOption('inspect');await page.locator('#preview').selectOption(['A','B','C'][count-1]);
   assert.equal(await page.locator('.proposal').count(),1);
   await page.locator('#view').selectOption('selection');assert.equal(await page.locator('.proposal').count(),1);
  }
  assert.deepEqual(errors,[]);evidence.push({name,mixedCounts:counts,roundTrip:true,globalSelection:true,pageOverride:true,invalidOverrideRejected:true});
 }finally{await browser.close()}
}
fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify(evidence,null,2));console.log('PASS twelve proposal-count browser cases including mixed page/leaf composition and feedback round trips');
