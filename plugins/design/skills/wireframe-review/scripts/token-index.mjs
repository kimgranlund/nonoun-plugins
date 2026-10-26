import {loadUI} from './ui-kit.mjs';
const kit=await loadUI();
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';import {createHash} from 'node:crypto';
import {authoredStyles,inspectStyles} from './token-inspection.mjs';
export const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export const sha=text=>createHash('sha256').update(text).digest('hex');
export const sources={color:'assets/foundation/ultimate-tokens/colors.css',typography:'assets/foundation/ultimate-tokens/typography.css',geometry:'assets/foundation/maison/geometry.css',layout:'assets/foundation/maison/layout.css',profile:'assets/wireframe.css'};
export function createIndex(){return kit.api.createIndex();}
export function tokenCheck(m,index){return inspectStyles([m.css||'',...m.units.flatMap(u=>u.variants.flatMap(v=>authoredStyles(v.html||'')))],index);}
