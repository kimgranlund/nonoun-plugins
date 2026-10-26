import fs from 'node:fs';import {createHash} from 'node:crypto';import assert from 'node:assert/strict';
const root=new URL('../',import.meta.url),read=p=>fs.readFileSync(new URL(p,root),'utf8');
const contract=JSON.parse(read('references/semantic-palettes.json')),bytes=read(contract.source),data=JSON.parse(bytes),source=data.bu.source;
assert.equal(data.$extensions['com.ultimate-tokens'].counts.semantic,0);
const declarations=[];
for(const [family,groups] of Object.entries(source))for(const [group,tokens]of Object.entries(groups))for(const [name,token]of Object.entries(tokens)){
 const v=token.$value;assert.equal(v.colorSpace,'srgb');assert(v.components.every(c=>Number.isFinite(c)&&c>=0&&c<=1));assert.equal(v.alpha,1);
 declarations.push(`  --bu-source-${family}-${group}-${name}: color(srgb ${v.components.join(' ')});`);
}
assert.equal(declarations.length,748);
const sourceCSS=read('assets/foundation/semantic-palettes/source.css');
const cssValues=new Map([...sourceCSS.matchAll(/(--bu-source-[\w-]+):\s*color\(srgb ([^)]+)\);/g)].map(m=>[m[1],m[2].trim().split(/\s+/).map(Number)]));
assert.equal(cssValues.size,748);
for(const [family,groups]of Object.entries(source))for(const [group,tokens]of Object.entries(groups))for(const [name,t]of Object.entries(tokens))assert.deepEqual(cssValues.get(`--bu-source-${family}-${group}-${name}`),t.$value.components,'JSON/CSS source mismatch');
let css=sourceCSS+'\n/* Base-ui semantic mappings; generated from references/semantic-palettes.json. */\n:root {\n';
assert.equal(contract.schemaVersion,2);
for(const [intent,family]of Object.entries(contract.intents))for(const [role,{group,light,dark}]of Object.entries(contract.roles)){
 const expected=['solid','hover','active'].includes(role)?'prime':'base';
 assert.equal(group,expected,'Semantic group policy mismatch for '+role);
 assert(source[family][group]?.[light]&&source[family][group]?.[dark],'Unknown source sample');
 css+=`  --ui-palette-${intent}-${role}: light-dark(var(--bu-source-${family}-${group}-${light}),var(--bu-source-${family}-${group}-${dark}));\n`;
}
css+='}\n';
const roots=contract.components.map(c=>'.'+c.class).join(',');
// Reset at every component boundary, including unannotated descendants.
css+=`:where(${roots}) { ${Object.keys(contract.roles).map(r=>`--ui-intent-${r}:initial;`).join('')} }\n`;
for(const intent of Object.keys(contract.intents))css+=`:is(${roots})[data-intent="${intent}"] { ${Object.keys(contract.roles).map(r=>`--ui-intent-${r}:var(--ui-palette-${intent}-${r});`).join('')} }\n`;
css+=`
.button__root[data-intent],.notice__root[data-intent][data-appearance=solid],.badge__root[data-intent][data-appearance=solid] { background:var(--ui-intent-solid);color:var(--ui-intent-on-solid);border-color:var(--ui-intent-solid); }
.button__root[data-intent]:not(:disabled):hover { background:var(--ui-intent-hover);border-color:var(--ui-intent-hover); }
.button__root[data-intent]:not(:disabled):active { background:var(--ui-intent-active);border-color:var(--ui-intent-active); }
.notice__root[data-intent]:not([data-appearance=solid]),.badge__root[data-intent]:not([data-appearance=solid]),.button__root[data-intent]:is([data-appearance=soft],[data-appearance=outline],[data-appearance=ghost]) { background:var(--ui-intent-soft);color:var(--ui-intent-on-soft);border-color:var(--ui-intent-border); }
.button__root[data-intent]:is([data-appearance=soft],[data-appearance=ghost]) { border-color:transparent; }
.button__root[data-intent]:is([data-appearance=soft],[data-appearance=outline],[data-appearance=ghost]):not(:disabled):hover { background:var(--ui-intent-soft-hover); }
.button__root[data-intent]:is([data-appearance=soft],[data-appearance=outline],[data-appearance=ghost]):not(:disabled):active { background:var(--ui-intent-soft-active); }
.button__root[data-intent]:disabled { opacity:1;border-style:dashed;cursor:default; }
.notice__root[data-intent] > :is(p,h2,h3,h4,span) { color:inherit; }
.field__root[data-intent] > :is(input,select,textarea) { border-color:var(--ui-intent-border); }
.field__root[data-intent] > :is(.field__help,.field__error) { color:var(--ui-intent-on-soft);background:var(--ui-intent-soft); }
@media(forced-colors:active) {
 :is(.button__root,.notice__root,.badge__root)[data-intent] { background:Canvas!important;color:CanvasText!important;border-color:CanvasText!important; }
 .button__root[data-intent]:disabled { color:GrayText!important;border-color:GrayText!important; }
 .field__root[data-intent] > :is(input,select,textarea,.field__help,.field__error) { color:CanvasText!important;background:Canvas!important;border-color:CanvasText!important; }
}
`;
const provenance=JSON.stringify({source:contract.source,sha256:createHash('sha256').update(bytes).digest('hex'),cssSource:'assets/foundation/semantic-palettes/source.css',cssSHA256:createHash('sha256').update(sourceCSS).digest('hex'),tokens:declarations.length,semanticOwner:'references/semantic-palettes.json',note:'No source semantics provided; role tones and primary=color-1 alias are base-ui mappings.'},null,2)+'\n';
for(const [path,content]of [['assets/foundation/semantic-palettes/colors.css',css],['assets/foundation/semantic-palettes/provenance.json',provenance]])if(process.argv.includes('--check'))assert.equal(read(path),content,'Stale '+path);else fs.writeFileSync(new URL(path,root),content);
console.log('PASS semantic palette generation: 748 exact source values, 6 mapped intents, explicit Prime accents and Base supporting roles.');
