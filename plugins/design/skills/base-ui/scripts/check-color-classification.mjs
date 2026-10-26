import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{classifyExportColors}from'./lib/color-classification.mjs';
const root=path.resolve(import.meta.dirname,'..'),css=fs.readFileSync(path.join(root,'assets/foundation/ultimate-tokens/colors.css'),'utf8'),map=classifyExportColors(css);
for(const family of['primary','neutral','danger']){
 for(const suffix of['050','prime','prime-dimmest','scrim-100'])assert.equal(map.get(`--md-color-${family}-${suffix}`).kind,'primitive');
 for(const suffix of['disabled','on-surface','on-neutral']){const name=`--md-color-${family}-${suffix}`;if(map.has(name))assert.equal(map.get(name).kind,'semantic');}
}
assert.equal(map.get('--md-color-white').kind,'shared');assert.equal(map.size,291);
const unknown=classifyExportColors(':root {\n--md-color-primary-surprise: #fff;\n}');assert.equal(unknown.get('--md-color-primary-surprise').kind,'shared');
const identical=classifyExportColors('/* Primary, semantic roles */\n--md-color-primary-disabled: light-dark(#fff,#fff);');assert.equal(identical.get('--md-color-primary-disabled').kind,'semantic');
if(process.argv[2]){const html=fs.readFileSync(path.resolve(process.argv[2],'colors.html'),'utf8');for(const f of['primary','neutral','danger']){const match=html.match(new RegExp('data-palette="'+f+' primitives"[\\s\\S]*?</article>'));assert(match,`${f} primitive group missing`);assert(match[0].includes(`--md-color-${f}-prime`));const semantic=html.match(new RegExp('data-palette="'+f+' semantic"[\\s\\S]*?</article>'));assert(semantic&&!semantic[0].includes(`data-item="--md-color-${f}-prime"`),'prime misclassified as semantic');}}
console.log('PASS source-defined primitive/semantic categories, unknown/equal-value controls and optional sheet membership');
