import assert from 'node:assert/strict';
import fs from 'node:fs';
import {elementIds,validateManifest} from '../assets/model.mjs';
const schema=JSON.parse(fs.readFileSync(new URL('../references/manifest.schema.json',import.meta.url)));
const template=JSON.parse(fs.readFileSync(new URL('../assets/minimal.manifest.json',import.meta.url)));
for(const html of [
 '<main data-review-id="request"><style>[data-review-id="request"]{color:red}</style></main>',
 '<!-- <p data-review-id="ghost"> --><main data-review-id="request"></main>',
 '<main title=\'data-review-id="ghost"\' data-review-id="request"></main>',
 '<main data-review-id="request"><script>const x=\'data-review-id="ghost"\';</script><textarea><p data-review-id="ghost"></p></textarea></main>'
]){const m=structuredClone(template);m.units[0].variants[0].html=html;validateManifest(m,schema);assert.deepEqual(elementIds(html),['request']);}
for(const html of ['<main data-review-id="request"><p data-review-id="request"></p></main>','<main><style>[data-review-id="ghost"]{}</style></main>','<main data-review-id=request></main>','<main data-review-id="Bad ID"></main>']){const m=structuredClone(template);m.units[0].variants[0].html=html;assert.throws(()=>validateManifest(m,schema));}
console.log('PASS review-ID attributes, text exclusions and rejection controls');
