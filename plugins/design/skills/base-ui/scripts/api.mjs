import {bundledFontCSS} from './lib/font-css.mjs';
import {rewriteIconCSS} from './lib/icon-css.mjs';
import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';
import {compileControls} from './compile-controls.mjs';import {createIndex,sources} from './token-index.mjs';import {authoredStyles,inspectStyles} from './token-inspection.mjs';
export {compileControls,createIndex};
export const root=path.resolve(import.meta.dirname,'..');
const sha=b=>createHash('sha256').update(b).digest('hex');
function readBytes(relative){const f=fs.realpathSync(path.resolve(root,relative));if(!f.startsWith(root+path.sep))throw Error('Kit source escapes root');return fs.readFileSync(f);}
export function readSource(relative){return readBytes(relative).toString('utf8');}
export function describeKit(){const d=JSON.parse(readSource('kit.json'));if(d.schemaVersion!==1||d.packageId!=='local.base-ui'||d.runtimeApiVersion!==1)throw Error('Incompatible base-ui descriptor/API');for(const [p,h]of Object.entries(d.files))if(sha(readBytes(p))!==h)throw Error('base-ui integrity mismatch: '+p);return {packageId:d.packageId,version:d.version,runtimeApiVersion:d.runtimeApiVersion,contentSHA256:sha(JSON.stringify(d.files))};}
export function getAssetBundle(){const fonts=bundledFontCSS();return {css:fonts+'\n'+Object.values(sources).map(readSource).join('\n'),foundationCSS:fonts+'\n'+[sources.color,sources.typography,sources.geometry,sources.layout,sources.palettes].map(readSource).join('\n'),runtime:readSource('assets/ui-runtime.js'),controlMarkup:readSource('assets/control-markup.mjs').replace(/^export /gm,''),sources};}
export function getComponentContext(ids){const common=JSON.parse(readSource('references/style/components/contract.json'));const dedicated={'native-select':'references/style/select/contract.json','navigation-menu':'references/style/navigation-menu/contract.json'};return ids.map(id=>{const record=common.families.find(f=>f.id===id);if(record)return record;if(dedicated[id])return JSON.parse(readSource(dedicated[id]));throw Error('Unknown component: '+id);});}
export function validateUI({html='',css=''}){return {unknownTokens:inspectStyles([css,...authoredStyles(html)],createIndex()),scope:'Lexical token membership only; geometry, behavior, accessibility and rendered states require affected checks.'};}

export function updateIconCSS(css){const icons=Object.fromEntries(fs.readdirSync(path.join(root,'assets/icons')).filter(n=>n.endsWith('.svg')).map(n=>[n,readSource('assets/icons/'+n)]));return rewriteIconCSS(css,icons);}

export {collectCatalog} from './catalog.mjs';
export {renderComponents} from './lib/sheets/components.mjs';
export {renderTokens} from './lib/sheets/tokens.mjs';
export {renderColors} from './lib/sheets/colors.mjs';
