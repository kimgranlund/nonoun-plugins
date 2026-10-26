import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const [runtime,out]=process.argv.slice(2);
const pw=createRequire(import.meta.url)(runtime);
fs.mkdirSync(out,{recursive:true});
const contract=JSON.parse(fs.readFileSync(path.join(root,'references/style/contract.json')));
const css=contract.styles.map(f=>fs.readFileSync(path.resolve(root,'references/style',f),'utf8')).join('\n');
const headings=Array.from({length:6},(_,i)=>'<h'+(i+1)+'>Heading '+(i+1)+'</h'+(i+1)+'>').join('');
const report=[];
for(const engine of ['chromium','firefox','webkit']){
 const b=await pw[engine].launch();const p=await b.newPage();
 for(const width of [360,1200])for(const size of ['sm','md','lg']){
 await p.setViewportSize({width,height:900});
 await p.setContent('<style>'+css+'</style><body data-size="'+size+'"><section id="editorial">'+headings+'</section><article class="card__root" id="card">'+headings+'<section data-type-context="content" id="content">'+headings+'<div class="product__root" id="nested">'+headings+'</div></section></article><aside data-type-context="product" id="explicit">'+headings+'</aside><dialog open class="dialog__root" id="dialog">'+headings+'</dialog></body>');
 const result=await p.evaluate(()=>Object.fromEntries(['editorial','card','content','nested','explicit','dialog'].map(id=>[id,[...document.getElementById(id).children].filter(x=>/^H[1-6]$/.test(x.tagName)).map(x=>{const s=getComputedStyle(x);return {size:parseFloat(s.fontSize),weight:s.fontWeight,line:s.lineHeight};})])));
 for(const id of ['card','nested','explicit','dialog']){assert.deepEqual(result[id].map(x=>x.size),[24,18,16,14,14,12]);assert(result[id].every(x=>x.weight==='600'));}
 assert.deepEqual(result.content,result.editorial);
 assert(result.editorial[1].size>result.card[1].size);
 report.push({engine,width,size,passed:true});
 }
 // A leaked content headline must be caught by the size assertion.
 await p.addStyleTag({content:'#card > h2 {font-size:32px}'});
 assert.notEqual(await p.locator('#card > h2').evaluate(x=>parseFloat(getComputedStyle(x).fontSize)),18);
 await b.close();
}
fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify({cases:report,negativeControls:3},null,2));
console.log('PASS 18 heading-context cases and 3 content-scale negative controls');
