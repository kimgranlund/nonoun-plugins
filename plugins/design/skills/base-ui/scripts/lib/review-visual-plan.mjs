// Risk-based manual sample; the full mechanical matrix remains a separate obligation.
export function findingKeys(data){
 const keys=[];
 for(const issue of data.geometry?.issues||[])keys.push('geometry:'+String(issue.code||issue.type||issue.message||JSON.stringify(issue))+':'+(issue.selector||issue.element||''));
 for(const kind of ['contrast','taskAccess'])if(data[kind]?.status!=='pass'){
  keys.push(kind+':'+data[kind]?.status);
  for(const issue of [...(data[kind]?.failures||[]),...(data[kind]?.issues||[]),...(data[kind]?.unsupported||[])])keys.push(kind+':'+(issue.code||issue.kind||'finding')+':'+(issue.selector||issue.element||'')+':'+(issue.reason||issue.reasons?.join(',')||''));
 }
 return [...new Set(keys)].sort();
}
export function makeVisualPlan(matrixStates,captures){
 const required=new Map(),scenarios=[...new Set(matrixStates.map(s=>s.scenarioId))];
 const add=(id,reason)=>{if(!required.has(id))required.set(id,[]);required.get(id).push(reason)};
 for(const scenario of scenarios){add(`${scenario}-320-light-1`,'Narrow normal composition for each functional scenario');add(`${scenario}-1440-dark-2`,'Wide doubled-text composition in the opposite scheme for each functional scenario')}
 if(scenarios.length){add(`${scenarios[0]}-390-dark-1`,'Initial phone composition in dark scheme');add(`${scenarios[0]}-768-light-2`,'Initial intermediate-width doubled-text composition')}
 const seen=new Set();
 for(const c of captures)for(const key of c.findingKeys||[]){const identity=c.scenarioId+':'+key;if(!seen.has(identity)){seen.add(identity);add(c.id,'Representative machine finding: '+key)}}
 return {version:1,strategy:'risk-based-manual-sample',limitation:'Manual inspection covers only these selected captures, not the full responsive matrix. All machine rows remain required and every machine failure blocks acceptance. Additional visual inspection may be recorded by exact capture ID.',required:[...required].map(([id,reasons])=>({id,reasons}))};
}
