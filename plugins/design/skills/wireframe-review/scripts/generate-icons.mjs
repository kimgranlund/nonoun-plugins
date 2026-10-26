#!/usr/bin/env node
// Review-shell paint only; base-ui owns glyph compilation and assets.
import fs from 'node:fs';import path from 'node:path';import {loadUI,reviewRoot} from './ui-kit.mjs';
const args=process.argv.slice(2);if(args.length>1||args.length===1&&args[0]!=='--check')throw Error('Usage: generate-icons.mjs [--check]');
const kit=await loadUI(),target=path.join(reviewRoot,'assets/shell.css'),before=fs.readFileSync(target,'utf8'),next=kit.api.updateIconCSS(before);
if(args.includes('--check')){if(before!==next)throw Error('Stale bundled icons: assets/shell.css');}else if(before!==next)fs.writeFileSync(target,next);
console.log('Review-shell bundled icon CSS current; cascade position preserved');
