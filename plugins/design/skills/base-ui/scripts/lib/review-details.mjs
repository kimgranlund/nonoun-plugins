// Lossless, lazy inspection windows over the captured image, never a new app state.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const digest=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
export function detailWindows(width,height){
 if(!Number.isInteger(width)||!Number.isInteger(height)||width<1||height<1)throw Error('Invalid image dimensions');
 const windows=[];
 for(let y=0;y<height;y+=760)for(let x=0;x<width;x+=920)windows.push({index:windows.length+1,x,y,width:Math.min(960,width-x),height:Math.min(800,height-y)});
 return windows;
}
export function detailPlan(reviewPath,capture){
 if(!capture?.screenshot)return null;
 const source=path.resolve(path.dirname(reviewPath),capture.screenshot),bytes=fs.readFileSync(source);
 if(bytes.subarray(0,8).toString('hex')!=='89504e470d0a1a0a')throw Error('Detail source must be PNG');
 const width=bytes.readUInt32BE(16),height=bytes.readUInt32BE(20),windows=detailWindows(width,height);
 return {source,width,height,totalTiles:windows.length,totalPages:Math.ceil(windows.length/4),tileLimit:{width:960,height:800},overlap:40,command:`review-session.mjs detail ${JSON.stringify(path.resolve(reviewPath))} ${capture.id} PLAYWRIGHT_PATH sample [CHROME_PATH]`};
}
export async function detailPacket({reviewPath,captureId,runtime,page='sample',executablePath}){
 const review=JSON.parse(fs.readFileSync(reviewPath,'utf8')),capture=review.captures?.find(c=>c.id===captureId);
 if(!capture)throw Error('Unknown captured state: '+captureId);
 if(digest(fs.readFileSync(review.binding.artifact))!==review.binding.sha256)throw Error('Artifact changed; start a new capture');
 const plan=detailPlan(reviewPath,capture),sourceBytes=fs.readFileSync(plan.source);
 if(digest(sourceBytes)!==capture.screenshotSHA256)throw Error('Screenshot evidence changed; start a new capture');
 if(page!=='sample'&&(!Number.isInteger(page)||page<1||page>plan.totalPages))throw Error('Detail page outside coverage');
 const windows=detailWindows(plan.width,plan.height);
 const anchors=capture.detailAnchors||[];
 const chosen=[windows[0]];
 for(const anchor of anchors){const tile=windows.find(w=>anchor.x>=w.x&&anchor.x<w.x+w.width&&anchor.y>=w.y&&anchor.y<w.y+w.height);if(tile&&!chosen.includes(tile)&&chosen.length<4)chosen.push(tile);}
 if(chosen.length<4&&!chosen.includes(windows.at(-1)))chosen.push(windows.at(-1));
 const selected=page==='sample'?chosen:windows.slice((page-1)*4,page*4);
 const pw=createRequire(import.meta.url)(path.resolve(runtime));
 const browser=await pw.chromium.launch({headless:true,...(executablePath?{executablePath}:{})});
 const tiles=[];
 try{
  const tab=await browser.newPage({offline:true});
  const encoded=await tab.evaluate(async({source,windows})=>{
   const img=new Image();img.src=source;await img.decode();
   return windows.map(w=>{const canvas=document.createElement('canvas');canvas.width=w.width;canvas.height=w.height;
    const ctx=canvas.getContext('2d');ctx.drawImage(img,w.x,w.y,w.width,w.height,0,0,w.width,w.height);return canvas.toDataURL('image/png').split(',')[1];});
  },{source:'data:image/png;base64,'+sourceBytes.toString('base64'),windows:selected});
  const directory=path.resolve(path.dirname(reviewPath),'details');fs.mkdirSync(directory,{recursive:true});
  encoded.forEach((value,index)=>{const bytes=Buffer.from(value,'base64'),sha256=digest(bytes),file=path.join(directory,sha256+'.png');
   const reused=fs.existsSync(file)&&digest(fs.readFileSync(file))===sha256;
   if(!reused)fs.writeFileSync(file,bytes);
   tiles.push({...selected[index],path:file,sha256,reused});});
 }finally{await browser.close();}
 return {captureId,source:plan.source,sourceSHA256:capture.screenshotSHA256,image:{width:plan.width,height:plan.height},page,totalPages:plan.totalPages,nextPage:page==='sample'?null:page<plan.totalPages?page+1:null,totalTiles:windows.length,anchors,tiles,coverage:{provided:tiles.map(t=>t.index),unprovidedTileCount:windows.length-selected.length,fullCoverageCommand:plan.command.replace(' sample ', ' 1 '),completeImageOnThisPage:windows.length===selected.length},instruction:'Open each tile at original size. Coordinates are physical image pixels; adjacent tiles overlap by 40px. Keep the full image for composition. Identical tile hashes can reuse observations only within this unchanged capture session; inspect changed regions and judge every scenario. Generated tiles are not inspected evidence or automatic judgments. This is a targeted detail sample, not exhaustive pixel inspection. Record this limitation. Use numeric pages for additional regions when a finding needs them; whole-image detail coverage requires all pages.'};
}
