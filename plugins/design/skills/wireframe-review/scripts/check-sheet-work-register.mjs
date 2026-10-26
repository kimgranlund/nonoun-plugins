import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';

export function checkWorkRegister(out,expectedFile){
 const expected=fs.readFileSync(expectedFile),register=JSON.parse(expected);
 assert(Array.isArray(register.items)&&register.items.length>0,'Expected a nonempty work register');
 const ids=register.items.map(i=>i.id);
 assert(ids.every(id=>typeof id==='string'&&/^[\w-]+$/.test(id)),'Invalid register ID');
 assert.equal(new Set(ids).size,ids.length,'Duplicate register ID');
 const inputs=JSON.parse(fs.readFileSync(path.join(out,'review-inputs.json')));
 const external=inputs.externalInputs.find(i=>i.path==='review-inputs/work-register.json');
 assert(external,'Required work register omitted from sheet build');
 const copied=fs.readFileSync(path.join(out,external.path));
 assert(expected.equals(copied),'Work register snapshot differs from expected input');
 assert.equal(external.sha256,createHash('sha256').update(expected).digest('hex'),'Invalid external input hash');
 assert.equal(inputs.excludedFromCorpusIdentity,true,'External review input must remain separate from corpus identity');
 assert.equal(inputs.workItems,ids.length,'Missing work items');
 assert.deepEqual(inputs.counts,{complete:register.items.filter(i=>i.complete===true).length,remaining:register.items.filter(i=>i.complete!==true).length},'Incorrect work completion counts');
 for(const id of ids){
  assert(inputs.findingIds.includes(id),'Missing finding: '+id);
  assert(fs.readFileSync(path.join(out,'gaps.html'),'utf8').includes('id="'+id+'"'),'Missing rendered finding: '+id);
 }
 return {workItems:ids.length,counts:inputs.counts,sha256:external.sha256,scope:'Exact external register and rendered finding coverage; recorded completion is not current artifact acceptance.'};
}
if(process.argv[1]&&fs.realpathSync(process.argv[1])===fs.realpathSync(fileURLToPath(import.meta.url))){
 if(process.argv[2]==='--help'){console.log('Usage: node scripts/check-sheet-work-register.mjs SHEETS EXPECTED_WORK_REGISTER\nRead-only completeness check for registered reviews. Source-only catalogs do not satisfy this scope.');}
 else {const [out,input]=process.argv.slice(2);if(!out||!input)throw Error('Usage: check-sheet-work-register.mjs SHEETS EXPECTED_WORK_REGISTER');console.log(JSON.stringify(checkWorkRegister(out,input),null,2));}
}
