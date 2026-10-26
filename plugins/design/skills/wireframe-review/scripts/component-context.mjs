// Review-specific runtime route remains here; UI contracts are owned by base-ui.
import fs from 'node:fs';
import {loadUI} from './ui-kit.mjs';import {spawnSync} from 'node:child_process';import path from 'node:path';
const outputIndex=process.argv.indexOf('--output');if(outputIndex>=0){const output=path.resolve(process.argv[outputIndex+1]);const resolved=path.join(fs.realpathSync(path.dirname(output)),path.basename(output)),reviewRoot=path.resolve(import.meta.dirname,'..');if(resolved===reviewRoot||resolved.startsWith(reviewRoot+path.sep))throw Error('Keep context output outside the corpus');}
const legacy=process.argv.includes('--runtime')||process.argv.includes('--root');const kit=legacy?null:await loadUI();const r=spawnSync(process.execPath,[legacy?path.resolve(import.meta.dirname,'review-component-context.mjs'):path.join(kit.root,'scripts/component-context.mjs'),...process.argv.slice(2)],{stdio:'inherit'});process.exitCode=r.status??1;
