import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';import {createHash} from 'node:crypto';
import {authoredStyles,inspectStyles} from './token-inspection.mjs';
export const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export const sha=text=>createHash('sha256').update(text).digest('hex');
export const sources={color:'assets/foundation/ultimate-tokens/colors.css',typography:'assets/foundation/ultimate-tokens/typography.css',geometry:'assets/foundation/maison/geometry.css',layout:'assets/foundation/maison/layout.css',profile:'assets/wireframe.css',palettes:'assets/foundation/semantic-palettes/colors.css'};
export function createIndex(){return {schemaVersion:1,generatedBy:'token-index/1',groups:Object.fromEntries(Object.entries(sources).map(([group,file])=>{const bytes=fs.readFileSync(path.join(root,file),'utf8');return [group,{source:file,sha256:sha(bytes),names:[...new Set([...bytes.replace(/\/\*[\s\S]*?\*\//g,'').matchAll(/(--[\w-]+)\s*:/g)].map(m=>m[1]))].sort()}]}))};}
