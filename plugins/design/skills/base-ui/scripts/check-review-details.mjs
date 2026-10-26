import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {detailWindows,detailPacket,detailPlan} from './lib/review-details.mjs';
const [runtime,executablePath]=process.argv.slice(2),dir=fs.mkdtempSync(path.join(os.tmpdir(),'review-detail-'));
const artifact=path.join(dir,'app.html'),source=path.join(dir,'long.png'),reviewPath=path.join(dir,'review.json');
fs.writeFileSync(artifact,'detail fixture');
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const pw=createRequire(import.meta.url)(path.resolve(runtime));
const browser=await pw.chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
try{const tab=await browser.newPage({viewport:{width:1440,height:800}});await tab.setContent('<style>body{margin:0;background:#123456;height:5000px}div{position:absolute;top:4900px;width:100%;height:100px;background:#abcdef}</style><div></div>');await tab.screenshot({path:source,fullPage:true});}finally{await browser.close();}
const capture={id:'initial',screenshot:'long.png',screenshotSHA256:hash(source),detailAnchors:[{reason:'primary task',x:1100,y:3300}]};
fs.writeFileSync(reviewPath,JSON.stringify({binding:{artifact,sha256:hash(artifact)},captures:[capture]}));
const windows=detailWindows(1440,5000);assert.ok(windows.every(w=>w.width<=960&&w.height<=800));
for(let y=0;y<5000;y++)assert.ok(windows.filter(w=>w.x===0).some(w=>y>=w.y&&y<w.y+w.height),'no uncovered vertical pixels');
assert.equal(windows[0].width-windows[1].x,40);
const plan=detailPlan(reviewPath,capture);assert.ok(plan.command.includes(' sample '));assert.equal(plan.height,5000);
const sample=await detailPacket({reviewPath,captureId:'initial',runtime,executablePath});assert.ok(sample.tiles.length<=4);assert.ok(sample.coverage.unprovidedTileCount>0);assert.ok(sample.tiles.some(w=>1100>=w.x&&1100<w.x+w.width&&3300>=w.y&&3300<w.y+w.height));
assert.equal(fs.readdirSync(path.join(dir,'details')).length,new Set(sample.tiles.map(t=>t.sha256)).size);
const again=await detailPacket({reviewPath,captureId:'initial',runtime,executablePath});assert.ok(again.tiles.every(t=>t.reused));
const last=await detailPacket({reviewPath,captureId:'initial',runtime,executablePath,page:plan.totalPages});assert.equal(last.nextPage,null);assert.ok(last.tiles.some(t=>t.y+t.height===5000));
for(const tile of [...sample.tiles,...last.tiles]){const bytes=fs.readFileSync(tile.path);assert.equal(bytes.readUInt32BE(16),tile.width);assert.equal(bytes.readUInt32BE(20),tile.height);assert.equal(hash(tile.path),tile.sha256);}
const pixelBrowser=await pw.chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
try{const tab=await pixelBrowser.newPage();const tile=last.tiles.at(-1);const pixel=await tab.evaluate(async source=>{const img=new Image();img.src=source;await img.decode();const c=document.createElement('canvas');c.width=img.width;c.height=img.height;const ctx=c.getContext('2d');ctx.drawImage(img,0,0);return [...ctx.getImageData(img.width-1,img.height-1,1,1).data];},'data:image/png;base64,'+fs.readFileSync(tile.path).toString('base64'));assert.deepEqual(pixel,[171,205,239,255]);}finally{await pixelBrowser.close();}
await assert.rejects(()=>detailPacket({reviewPath,captureId:'initial',runtime,page:99,executablePath}),/outside coverage/);
fs.appendFileSync(source,'tampered');await assert.rejects(()=>detailPacket({reviewPath,captureId:'initial',runtime,executablePath}),/evidence changed/);
console.log(JSON.stringify({status:'pass',checks:13,evidence:dir,scope:'Lossless bounded detail windows, coverage, targeting, deduplication and stale evidence rejection; no visual judgments'}));
