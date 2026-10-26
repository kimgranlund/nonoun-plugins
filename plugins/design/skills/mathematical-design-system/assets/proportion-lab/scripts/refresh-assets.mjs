// Version the retained preview's CSS/module graph after source edits.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../dist/',import.meta.url));
const files=[];const walk=dir=>{for(const e of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,e.name);if(e.isDirectory())walk(p);else if(/\.(?:css|js|mjs|html)$/.test(p))files.push(p);}};walk(root);files.sort();
const rewrite=(text,revision)=>text.replace(/((?:@import\s+|from\s+|(?:src|href)=)["'])([^"']+)(["'])/g,(all,prefix,url,suffix)=>{
 if(/^(?:https?:|data:|#)/.test(url)||! /\.(?:css|m?js)(?:\?v=[\w.-]+)?$/.test(url))return all;
 return prefix+url.replace(/\?v=[\w.-]+$/,'')+'?v='+revision+suffix;
});
const hash=crypto.createHash('sha256');
for(const p of files)hash.update(path.relative(root,p)).update(rewrite(fs.readFileSync(p,'utf8'),'SOURCE'));
const revision='source-'+hash.digest('hex').slice(0,12);
let changed=0;for(const p of files){const old=fs.readFileSync(p,'utf8'),next=rewrite(old,revision);if(old!==next){changed++;if(!process.argv.includes('--check'))fs.writeFileSync(p,next);}}
if(process.argv.includes('--check')&&changed)throw Error('Stale preview assets: run scripts/refresh-assets.mjs');
console.log(`${process.argv.includes('--check')?'Verified':'Refreshed'} preview asset revision ${revision}`);
