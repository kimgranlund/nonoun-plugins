import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
export function checkMeasurements(data) {
 const records=[];
 function visit(value,path='$'){
  if(!value||typeof value!=='object')return;
  if(typeof value.scope==='string'&&(value.scope.startsWith('Rendered text in')||value.scope.startsWith('Declared task access only'))){records.push({path,kind:value.scope.startsWith('Rendered')?'contrast':'taskAccess',status:value.status,issues:value.issues?.map(i=>i.code),failed:value.failures?.length,unsupported:value.unsupported?.length});return;}
  for(const [key,child]of Object.entries(value))visit(child,path+'.'+key);
 }
 visit(data);return {status:!records.length?'unreviewed':records.some(r=>r.status!=='pass')?'fail':'pass',records};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const files=process.argv.slice(2);if(!files.length)throw Error('Usage: review-measurements.mjs RESULTS.json [MORE.json ...]');
 const results=files.map(file=>({file,...checkMeasurements(JSON.parse(fs.readFileSync(file,'utf8')))}));
 console.log(JSON.stringify(results,null,2));if(results.some(r=>r.status!=='pass'))process.exitCode=1;
}
