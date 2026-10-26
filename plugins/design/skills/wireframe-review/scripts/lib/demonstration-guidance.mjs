import path from 'node:path';
export const GUIDE_PATH='references/style/components/demonstrations.json';
export function validateDemonstrations(guide,{registry,components,read,hash}){
 const fail=s=>{throw Error('Demonstration guide: '+s);};
 if(guide.schemaVersion!==1||!Array.isArray(guide.members)||!guide.sourceBindings||!Array.isArray(guide.limits))fail('unsupported envelope');
 const expected=new Map();for(const [family,unit] of [...Object.entries(registry.specimens),...Object.entries(registry.dedicated)])for(const member of unit.members){if(expected.has(member.id))fail('duplicate registry member');expected.set(member.id,{family,member,source:['disclosure','overlay'].includes(family)?path.posix.normalize(path.posix.join('references/style/components',components.nativeRecipe)):unit.source||registry.source});}
 const bindings=new Map();for(const [key,b] of Object.entries(guide.sourceBindings)){if(!b.path||!b.kind||hash(read(b.path))!==b.sha256)fail('stale dependency '+key);bindings.set(key,b);}
 const binding=(key,kind)=>{const b=bindings.get(key);if(!b||b.kind!==kind)fail('missing/wrong '+kind+' dependency '+key);return b;};
 const groups=new Map(),seen=new Set();for(const m of guide.members){const e=expected.get(m.id);if(!e||seen.has(m.id))fail('unknown/duplicate member '+m.id);seen.add(m.id);if(m.family!==e.family||m.memberSelector!==e.member.selector||m.source!==e.source)fail('member source routing '+m.id);
 if(m.instructionAuthority!=='authored-guide'||m.capability?.status!=='declared-maintained-example'||m.observations?.status!=='unverified'||m.observations?.compatibleExternalReportsRequired!==true)fail('authored/observed authority '+m.id);
 if(!Array.isArray(m.operate)||!Array.isArray(m.inspect)||!m.inspect.length||[...m.operate,...m.inspect].some(v=>typeof v!=='string'||!v.trim()))fail('missing instructions '+m.id);
 if(!Array.isArray(m.ownerSelectors)||!Array.isArray(m.requiredPeers))fail('missing owner/peer identities '+m.id);
 const d=m.dependencies;if(!d||!Array.isArray(d.styles)||!d.styles.length||!Array.isArray(d.optionalRuntime))fail('dependency shape '+m.id);
 if(binding(d.recipe,'recipe').path!==m.source)fail('recipe routing '+m.id);d.styles.forEach(k=>binding(k,'stylesheet'));if(d.controller)binding(d.controller,'application-controller');d.optionalRuntime.forEach(r=>{binding(r.sourceKey,'optional-runtime');if(!r.purpose)fail('optional runtime purpose');});
 const authority=binding(d.authority?.sourceKey,'contract'),selection=d.authority.selectionKey;if(m.capability.authoritySourceKey!==d.authority.sourceKey||m.capability.selectionKey!==selection)fail('capability authority routing '+m.id);
 if(['native-select','navigation-menu'].includes(m.family)){if(selection!=='whole'||authority.path!==('references/style/'+(m.family==='native-select'?'select':'navigation-menu')+'/contract.json'))fail('dedicated authority '+m.id);}else if(authority.path!=='references/style/components/contract.json'||selection!=='families:'+m.family||!components.families.some(f=>f.id===m.family))fail('family authority '+m.id);
 if(['details','dialog','native-select','account-panel','team-panel'].includes(m.id)&&(!m.platformBoundary||d.controller))fail('native boundary/controller '+m.id);
 if(m.id==='dialog'&&!d.optionalRuntime.some(r=>binding(r.sourceKey,'optional-runtime').path==='assets/recipes/modal-autofocus.js'))fail('missing optional dialog caret helper');
 const list=groups.get(m.family)||[];list.push(m);groups.set(m.family,list);
 }
 if(seen.size!==expected.size)fail('missing member instructions');if(binding(guide.sourceRegistryKey,'registry').path!==guide.sourceRegistry)fail('registry identity');return groups;
}
