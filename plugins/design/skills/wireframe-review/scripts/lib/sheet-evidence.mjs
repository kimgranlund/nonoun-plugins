// Pure report compatibility. A compatible reported pass is not an accessibility or efficacy claim.
export function resolveEvidence({inventory,report,unitId,expectedSpecimenId=unitId,expectedCheckIds=[]}) {
 const result=(state,reason,records=[],missing=[])=>({state,reason,unitId,records,missing});
 if(!unitId||!Array.isArray(inventory?.sources)||!/^[0-9a-f]{64}$/.test(inventory.sourceHash)||!/^[0-9a-f]{64}$/.test(inventory.generatorSha256))throw Error('Missing authoritative inventory/unit identity');
 if(!Array.isArray(expectedCheckIds)||new Set(expectedCheckIds).size!==expectedCheckIds.length||expectedCheckIds.some(id=>typeof id!=='string'||!id))throw Error('Invalid required check IDs');
 const inventoryPaths=new Set();for(const input of inventory.sources){if(typeof input.path!=='string'||!input.path||!/^[0-9a-f]{64}$/.test(input.sha256)||inventoryPaths.has(input.path))throw Error('Invalid inventory source identity');inventoryPaths.add(input.path);}
 if(!report)return result('unverified','missing-report');
 if(report.schemaVersion!==1)throw Error('Unsupported sheet evidence schema version');
 if(report.sourceHash!==inventory.sourceHash||report.generatorSha256!==inventory.generatorSha256)return result('stale','source-or-generator-mismatch');
 if(!Array.isArray(report.records))throw Error('Evidence records must be an array');
 const knownSources=new Map(inventory.sources.map(x=>[x.path,x.sha256])),keys=new Set();
 for(const r of report.records){
  if(!r.unitId||!r.specimenId||!r.checkId||!['pass','fail','inconclusive','unverified'].includes(r.outcome))throw Error('Incomplete or invalid evidence record');
  if(!Array.isArray(r.sourceInputs)||r.sourceInputs.length===0)throw Error('Evidence requires relevant source identities');
  for(const input of r.sourceInputs)if(typeof input?.path!=='string'||!input.path||!/^[0-9a-f]{64}$/.test(input.sha256??'')||knownSources.get(input.path)!==input.sha256)return result('stale','relevant-source-mismatch');
  const e=r.environment;
  if(e?.kind!=='source-only'&&!(e?.kind==='browser'&&e.browser?.name&&e.browser?.version&&e.viewport?.width>0&&e.viewport?.height>0&&['light','dark'].includes(e.scheme)&&e.geometry?.tier&&e.geometry?.scale&&e.geometry?.size))throw Error('Incomplete evidence environment');
  const canonical=value=>Array.isArray(value)?value.map(canonical):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])])):value;const key=JSON.stringify(canonical([r.unitId,r.specimenId,r.checkId,e]));if(keys.has(key))throw Error('Duplicate evidence record');keys.add(key);
 }
 const records=report.records.filter(x=>x.unitId===unitId&&x.specimenId===expectedSpecimenId),missing=expectedCheckIds.filter(id=>!records.some(x=>x.checkId===id));
 if(!records.length)return result('unverified','no-unit-evidence',[],missing);
 if(records.some(x=>x.outcome==='fail'))return result('reported-fail','compatible-recorded-failure',records,missing);
 if(missing.length||records.some(x=>x.outcome==='unverified'))return result('unverified','required-checks-unverified',records,missing);
 if(records.some(x=>x.outcome==='inconclusive'))return result('inconclusive','compatible-inconclusive-records',records,missing);
 return result('reported-pass','compatible-scoped-records',records);
}
