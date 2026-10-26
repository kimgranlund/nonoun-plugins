#!/usr/bin/env node
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';import assert from 'node:assert/strict';
import {compileControls} from './compile-controls.mjs';import {SELECT_INDICATOR} from '../assets/control-markup.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const plain='<label>Workspace<select id="x" name="workspace" data-select-icon="buildings"><option>A<option disabled>B</select></label>';
const compiled=compileControls(plain);assert(compiled.includes('has-leading-icon'));assert(compiled.includes(SELECT_INDICATOR+'</span></label>'));assert(compiled.includes('id="x" name="workspace"'));assert(!compiled.includes('data-select-icon'));assert.equal(compileControls(compiled),compiled);
const untouched='<!-- <select> --> <script>const x="<select>";</script><style>.x:before{content:"<select>"}</style><textarea>&lt;select&gt;</textarea>';
assert.equal(compileControls(untouched),untouched);assert(compileControls('<select title="a > b"><option>A</option></select>').includes('title="a > b"'));
for(const invalid of ['<details class="menu__root">','<select data-leading-icon="gear">','<i data-ph="not-bundled-yet"></i>'])assert.throws(()=>compileControls(invalid));
const patterns=[/function\s+(?:styleSelects|installPrototypeMenus|resolvePrototypeIcons)\b/,/\b(?:styleSelects|installPrototypeMenus|resolvePrototypeIcons)\s*\(/,/https:\/\/cdn\.jsdelivr\.net\/npm\/@phosphor-icons/];
const check=(text,name)=>{for(const re of patterns)assert(!re.test(text),'Removed runtime dependency in '+name);};
for(const name of ['assets/app.mjs','assets/prototype-runtime.js','assets/wireframe.css','assets/shell.css'])check(fs.readFileSync(path.join(root,name),'utf8'),name);
for(const target of process.argv.slice(2)){const files=fs.statSync(target).isDirectory()?fs.readdirSync(target).filter(n=>n.endsWith('.html')).map(n=>path.join(target,n)):[target];for(const file of files)check(fs.readFileSync(file,'utf8'),file);}
// Prove guard patterns reject reintroduction, not just match today's clean files.
for(const text of ['styleSelects(document);','installPrototypeMenus(doc);','resolvePrototypeIcons(doc);','https://cdn.jsdelivr.net/npm/@phosphor-icons/core/a.svg'])assert.throws(()=>check(text,'negative control'));
console.log('PASS compiler anatomy/idempotence/raw text/native attributes and legacy/unknown-icon negative controls');
