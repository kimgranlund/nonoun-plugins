import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {root,createIndex} from './token-index.mjs';
import {authoredStyles,inspectStyles} from './token-inspection.mjs';
export {inspectStyles} from './token-inspection.mjs';
const args=process.argv.slice(2),index=JSON.parse(fs.readFileSync(path.join(root,'references/style/token-index.json')));
assert.deepEqual(index,createIndex(),'Stale token index; run generate-token-index.mjs');
if(args[0]==='--selftest'){
 assert.deepEqual(inspectStyles(['.x{color:var(--md-color-on-primary,var(--ui-ink))}'],index),['--md-color-on-primary']);
 assert.deepEqual(inspectStyles(['.x{color:var(--md-color-on-danger,#fff)}'],index),['--md-color-on-danger']);
 assert.deepEqual(inspectStyles([':root{--local-color:var(--ui-ink)}.x{color:var(--local-color)}'],index),[]);
 assert.deepEqual(inspectStyles(['/* color:var(--missing) */ .x{color:var(--ui-ink)}'],index),[]);
 console.log('PASS standalone token membership: nested/literal fallback negatives, local declarations and comment exclusion');
}else{
 if(!args.length)throw Error('Usage: check-standalone-token-refs.mjs HTML_OR_CSS [CSS ...] | --selftest');
 const styles=[];
 for(const file of args){const text=fs.readFileSync(file,'utf8');if(path.extname(file)==='.css')styles.push(text);else {
  styles.push(...authoredStyles(text));
 }}
 const unresolved=inspectStyles(styles,index);
 console.log(JSON.stringify({files:args,unresolved,limits:'Pass every linked CSS file explicitly. Runtime-injected styles, cascade resolution, scoped availability, semantic pairing and contrast require separate checks.'},null,2));
 if(unresolved.length)process.exitCode=1;
}
