#!/usr/bin/env node
// Explicit maintenance. Does not seal the kit or modify a consumer.
import fs from 'node:fs';import path from 'node:path';import {root,updateIconCSS} from './api.mjs';
const args=process.argv.slice(2);if(args.length>1||args.length===1&&args[0]!=='--check')throw Error('Usage: generate-icons.mjs [--check]');
const target=path.join(root,'assets/wireframe.css'),before=fs.readFileSync(target,'utf8'),next=updateIconCSS(before);
if(args.includes('--check')){if(before!==next)throw Error('Stale bundled icons: assets/wireframe.css');}else if(before!==next)fs.writeFileSync(target,next);
console.log('Base UI bundled icon CSS current; cascade position preserved');
