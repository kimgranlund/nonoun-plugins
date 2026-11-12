// The UI kit this skill owns: foundation CSS, bundled fonts and icons, runtime, control markup and contracts.
import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';
import {bundledFontCSS} from './lib/font-css.mjs';
import {rewriteIconCSS} from './lib/icon-css.mjs';
import {compileControls} from './compile-controls.mjs';import {createIndex,sources} from './token-index.mjs';
export {compileControls,createIndex};
export const root=path.resolve(import.meta.dirname,'..');
const sha=b=>createHash('sha256').update(b).digest('hex');
// Files whose bytes reach every compiled artifact; the identity changes when any of them does.
const identityFiles=()=>[...Object.values(sources),'assets/fonts/manifest.json','assets/ui-runtime.js','assets/control-markup.mjs'];
function readBytes(relative){const f=fs.realpathSync(path.resolve(root,relative));if(!f.startsWith(root+path.sep))throw Error('Kit source escapes root');return fs.readFileSync(f);}
export function readSource(relative){return readBytes(relative).toString('utf8');}
export function describeKit(){return {packageId:'wireframe-review/kit',runtimeApiVersion:1,contentSHA256:sha(JSON.stringify(Object.fromEntries(identityFiles().map(p=>[p,sha(readBytes(p))]))))};}
export function getAssetBundle(){const fonts=bundledFontCSS();return {css:fonts+'\n'+Object.values(sources).map(readSource).join('\n'),foundationCSS:fonts+'\n'+[sources.color,sources.typography,sources.geometry,sources.layout,sources.palettes].map(readSource).join('\n'),runtime:readSource('assets/ui-runtime.js'),controlMarkup:readSource('assets/control-markup.mjs').replace(/^export /gm,''),sources};}
export function updateIconCSS(css){const icons=Object.fromEntries(fs.readdirSync(path.join(root,'assets/icons')).filter(n=>n.endsWith('.svg')).map(n=>[n,readSource('assets/icons/'+n)]));return rewriteIconCSS(css,icons);}
export {collectCatalog} from './catalog.mjs';
export {renderComponents} from './lib/sheets/components.mjs';
export {renderTokens} from './lib/sheets/tokens.mjs';
export {renderColors} from './lib/sheets/colors.mjs';
