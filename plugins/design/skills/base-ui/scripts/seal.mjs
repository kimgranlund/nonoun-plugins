// Explicit maintainer operation after source edits; not a generation side effect.
import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';const root=path.resolve(import.meta.dirname,'..');
function walk(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>{const p=path.join(dir,e.name);return e.isDirectory()?walk(p):e.isFile()?[p]:[];});}
const files=Object.fromEntries(walk(root).filter(p=>path.basename(p)!=='.DS_Store'&&!['kit.json'].includes(path.relative(root,p))&&!path.relative(root,p).startsWith('resources/reports/')).sort().map(p=>[path.relative(root,p),createHash('sha256').update(fs.readFileSync(p)).digest('hex')]));
fs.writeFileSync(path.join(root,'kit.json'),JSON.stringify({schemaVersion:1,packageId:'local.base-ui',version:'4.0.0',runtimeApiVersion:1,entries:{api:'scripts/api.mjs',context:'scripts/component-context.mjs',build:'scripts/build.mjs'},files},null,2)+'\n');
