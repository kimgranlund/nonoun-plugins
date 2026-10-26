(() => {
'use strict';
const $ = id => document.getElementById(id);
let data=null, cursor=-1, selectedSource=null, timer=null, decisionId=null, selectedTool=null;
const expandedBatches=new Set();
let atlas=null;const story=createFogStory();const diagnostics=createFogDiagnostics();const charts=createFogCharts();const workflow=createFogWorkflow();
const symbols={inventoried:'○',discovered:'◌',partial:'◐',read:'●',edited:'✎'};
const node=(tag,text,cls)=>{const e=document.createElement(tag); if(text!==undefined)e.textContent=text; if(cls)e.className=cls; return e;};
function stop(){clearInterval(timer);timer=null;$('play').textContent='Play';}
function validate(d){
 if(!d||![1,2].includes(d.schemaVersion)||!d.session||typeof d.session.title!=='string'||!d.coverage||typeof d.coverage.inventory!=='string'||!Array.isArray(d.coverage.warnings)||!d.coverage.warnings.every(x=>typeof x==='string')||!Array.isArray(d.sources)||!Array.isArray(d.events)||!Array.isArray(d.links))throw Error('Expected a hydrated Context Fog-of-War v1/v2 session.');
 const ids=new Set(), events=new Set();
 for(const e of d.events){if(e.toolCalls!==undefined){if(!Array.isArray(e.toolCalls))throw Error('Invalid tool calls');for(const c of e.toolCalls){if(!c||!['position','tool','arguments','output'].every(k=>typeof c[k]==='string')||!['pending','fulfilled','rejected'].includes(c.settlement)||!['pending','succeeded','failed','unknown'].includes(c.outcome))throw Error('Invalid tool call detail');}}}
 for(const s of d.sources){if(!s||typeof s.id!=='string'||typeof s.path!=='string'||typeof s.inventoried!=='boolean'||ids.has(s.id))throw Error('Invalid or duplicate source');ids.add(s.id);}
 d.events.forEach((e,i)=>{if(!e||typeof e.id!=='string'||events.has(e.id)||e.seq!==i||!['message','call','result','compaction','context','unknown'].includes(e.kind)||typeof e.label!=='string'||typeof e.actor!=='string'||typeof e.timestamp!=='string'||!e.evidence||typeof e.evidence.text!=='string'||!Number.isInteger(e.evidence.traceLine)||e.evidence.traceLine<1||!Array.isArray(e.exposures))throw Error('Invalid event at position '+i);events.add(e.id);for(const x of e.exposures){if(!ids.has(x.sourceId)||!['discovered','partial','read','edited'].includes(x.state)||typeof x.basis!=='string')throw Error('Invalid exposure reference');for(const k of ['startLine','endLine'])if(k in x&&(!Number.isInteger(x[k])||x[k]<1))throw Error('Invalid line range');if(x.endLine<x.startLine)throw Error('Reversed line range');}});
 for(const l of d.links)if(!events.has(l.from)||!events.has(l.to)||!['recorded','inferred'].includes(l.kind)||typeof l.reason!=='string')throw Error('Invalid evidence connection');
 for(const c of d.contextRecords||[]){const e=d.events.find(e=>e.id===c.eventId);if(!ids.has(c.sourceId)||!e||!['included','removed'].includes(c.status)||c.evidence?.eventId!==c.eventId||!c.evidence.excerpt||!e.evidence.text.includes(c.evidence.excerpt))throw Error('Invalid context evidence');}
 for(const c of d.candidates||[]){const e=d.events.find(e=>e.id===c.eventId);if(!ids.has(c.sourceId)||!e||!['available','mentioned'].includes(c.kind)||c.evidence?.eventId!==c.eventId||!e.evidence.text.includes(c.evidence.excerpt))throw Error('Invalid candidate evidence');}
 const fields=['decisions','guidanceEdges','findings'];
 for(const name of fields){if(d.schemaVersion===2&&!Array.isArray(d[name]))throw Error('v2 requires '+name);if(d[name]!==undefined&&!Array.isArray(d[name]))throw Error('Invalid '+name);}
 const unique=(items)=>{const seen=new Set();for(const item of items){if(!item||typeof item.id!=='string'||!item.id||seen.has(item.id))throw Error('Invalid analysis ID');seen.add(item.id);}return seen;};
 const ds=unique(d.decisions||[]), es=unique(d.guidanceEdges||[]);unique(d.findings||[]);
 const byId=new Map(d.events.map(e=>[e.id,e]));
 for(const name of fields)for(const item of d[name]||[]){
  if(!Array.isArray(item.evidence)||!item.evidence.length)throw Error('Analysis requires evidence');
  for(const c of item.evidence)if(!c||!byId.has(c.eventId)||typeof c.excerpt!=='string'||!c.excerpt||!byId.get(c.eventId).evidence.text.includes(c.excerpt))throw Error('Evidence excerpt does not match its event');
  const required=name==='decisions'?['question','answer']:name==='guidanceEdges'?['explanation']:['title','category','observation','hypothesis','improvement','target','verification','status'];
  for(const k of required)if(typeof item[k]!=='string'||!item[k])throw Error('Invalid analysis field '+k);
  if(name==='decisions'&&(!Array.isArray(item.edgeIds)||item.edgeIds.some(id=>!es.has(id))))throw Error('Invalid decision path');
  if(name==='guidanceEdges'&&item.sourceIds!==undefined&&(!Array.isArray(item.sourceIds)||!item.sourceIds.length||item.sourceIds.some(id=>!ids.has(id))))throw Error('Invalid guidance source');
  if(name==='guidanceEdges'&&(!byId.has(item.from)||!byId.has(item.to)||byId.get(item.from).seq>byId.get(item.to).seq||!['explicit','observed','inferred'].includes(item.kind)))throw Error('Invalid guidance edge');
  if(name==='findings'&&(!ds.has(item.decisionId)||!['routing','lookup','dependency','coverage','guidance'].includes(item.category)||!['proposed','applied-unverified','verified-in-session'].includes(item.status)))throw Error('Invalid finding');
 }

}
function load(d){validate(d);stop();selectedTool=null;expandedBatches.clear();data=d;cursor=d.events.length-1;selectedSource=null;decisionId=d.decisions?.[0]?.id||null;$('decision-search').value='';$('search').value='';try{const stored=JSON.parse(localStorage.getItem('context-fog-camera:v1:'+location.pathname+':'+(d.session.id||d.session.trace||'report')))?.view;if(stored){if(Number.isInteger(stored.cursor))cursor=Math.max(0,Math.min(d.events.length-1,stored.cursor));$('search').value=typeof stored.timelineSearch==='string'?stored.timelineSearch:'';$('decision-search').value=typeof stored.decisionSearch==='string'?stored.decisionSearch:'';}}catch{}$('error').hidden=true;$('session-title').textContent=d.session.title;$('subtitle').textContent=d.session.repo+' · '+d.session.trace;$('scrub').max=Math.max(0,d.events.length-1);$('coverage').replaceChildren(node('p',d.coverage.inventory));const ul=node('ul');for(const w of d.coverage.warnings)ul.append(node('li',w));$('coverage').append(ul);story.load(d);diagnostics.load(d);charts.load(d);workflow.load(d);render();renderAnalysis();}
function seek(i){stop();selectedTool=null;cursor=Math.max(0,Math.min(data.events.length-1,i));selectedSource=null;render();}
function history(id){const found=[];for(let i=0;i<=cursor;i++)for(const x of data.events[i].exposures)if(x.sourceId===id)found.push({event:data.events[i],exposure:x});return found;}
function state(id){const h=history(id);let state='inventoried';let step=null;for(const {event,exposure:x} of h){if(x.state==='edited')state='edited';else if(x.state==='read'||state!=='read'&&state!=='edited'&&(x.state==='partial'||state!=='partial'))state=x.state;step=event.seq+1;}return {state,step};}
function jumpButton(event,label){const b=node('button',label||event.label,'wf-button secondary');b.type='button';b.onclick=()=>seek(event.seq);return b;}
function toolRowLabel(call){
 try{const args=JSON.parse(call.arguments);for(const key of ['cmd','command','path','file_path','filename','uri','url']){const value=args?.[key];if(typeof value==='string'&&value.trim())return value.trim().replace(/\s+/g,' ');if((key==='cmd'||key==='command')&&Array.isArray(value)&&value.every(x=>typeof x==='string'))return value.join(' ');}}catch{}
 return call.tool;
}
function readableOutput(value,depth=0){
 if(depth>8)return typeof value==='string'?value:JSON.stringify(value,null,2);
 if(typeof value==='string'){try{return readableOutput(JSON.parse(value),depth+1);}catch{return value;}}
 if(value===null||value===undefined)return value===null?'null':'';
 if(Array.isArray(value))return value.map(x=>readableOutput(x,depth+1)).join('\n\n');
 if(typeof value==='object'){
  if(Object.hasOwn(value,'output'))return readableOutput(value.output,depth+1);
  if(Object.hasOwn(value,'stdout')||Object.hasOwn(value,'stderr'))return ['stdout','stderr'].filter(k=>value[k]!==undefined&&value[k]!=='').map(k=>k+':\n'+readableOutput(value[k],depth+1)).join('\n\n');
  if(Array.isArray(value.content))return readableOutput(value.content,depth+1);
  if(typeof value.text==='string')return readableOutput(value.text,depth+1);
  if(value.status==='fulfilled'&&Object.hasOwn(value,'value'))return readableOutput(value.value,depth+1);
  if(value.status==='rejected'&&Object.hasOwn(value,'reason'))return 'Rejected: '+readableOutput(value.reason,depth+1);
  return JSON.stringify(value,null,2);
 }
 return String(value);
}
function rawDisclosure(root,label,text){const box=node('details',undefined,'wf-disclosure raw-output');const body=node('div',undefined,'wf-disclosure-body wf-flow');body.append(node('pre',text));box.append(node('summary',label),body);root.append(box);}
function outputText(root,value){const text=readableOutput(value);root.append(node('pre',text===''?'(No output)':text,'readable-output'));}
function selectTool(event,index){stop();cursor=event.seq;selectedSource=null;selectedTool={eventId:event.id,index};render();}
function inspect(){const host=$('inspector');host.replaceChildren();
 const current=data.events[cursor];if(!current){host.append(node('p','Load a session with events to begin.'));return;}
 const raw=selectedSource?{source:data.sources.find(s=>s.id===selectedSource),exposures:history(selectedSource),candidates:(data.candidates||[]).filter(c=>c.sourceId===selectedSource&&data.events.find(e=>e.id===c.eventId).seq<=cursor)}:selectedTool?.eventId===current.id?{toolCall:current.toolCalls?.[selectedTool.index],output:payloadValue(current.toolCalls?.[selectedTool.index]?.output),event:current,recordedPayload:payloadRecord(current)}:{event:current,recordedPayload:payloadRecord(current)};
 const root=payloadTabs(host,raw);
 const toolEvent=data.events[cursor];const tool=selectedTool?.eventId===toolEvent?.id?toolEvent.toolCalls?.[selectedTool.index]:null;
 if(tool){root.append(node('h3',tool.tool),node('p',tool.position+' · '+tool.outcome),node('p','Promise state: '+tool.settlement,'quiet'),node('p',data.session.trace+' : line '+toolEvent.evidence.traceLine,'quiet'),node('h3','Tool arguments'));
 payloadFields(root,tool.arguments);root.append(node('h3',tool.settlement==='rejected'?'Rejection reason':'Matching output'));
 if(tool.settlement==='pending')root.append(node('p','Output has not arrived at this event.'));else{outputText(root,tool.output);}
 const link=data.links.find(l=>l.kind==='recorded'&&(l.from===toolEvent.id||l.to===toolEvent.id));const other=link?data.events.find(e=>e.id===(link.from===toolEvent.id?link.to:link.from)):null;
 if(other){const ix=other.toolCalls?.findIndex(x=>x.position===tool.position&&x.tool===tool.tool);if(ix>=0){const jump=node('button',tool.settlement==='pending'?'Jump to matching result':'Jump to original call','wf-button secondary');jump.type='button';jump.onclick=()=>selectTool(other,ix);root.append(jump);}}
 return;}

 if(selectedSource){const source=data.sources.find(s=>s.id===selectedSource);root.append(node('h3',source.path),node('p',source.inventoried?'Present in supplied snapshot inventory.':'Referenced in trace; absent from supplied inventory.','quiet'));exposureSummary(root,data,source.id,cursor);const candidates=(data.candidates||[]).filter(c=>c.sourceId===source.id&&data.events.find(e=>e.id===c.eventId).seq<=cursor);for(const c of candidates){const event=data.events.find(e=>e.id===c.eventId);root.append(jumpButton(event,'Candidate '+c.kind+' · event '+(event.seq+1)),node('p','Visible path option; evaluation and rejection are not established.','quiet'));rawDisclosure(root,'Exact candidate evidence',c.evidence.excerpt);}
 const h=history(source.id);root.append(node('p',h.length+' exposure record(s) up to this step.'));for(const {event,exposure:x} of h){root.append(jumpButton(event,`${event.seq+1} · ${x.state}${x.startLine?' · lines '+x.startLine+'–'+(x.endLine||x.startLine):''}`),node('p',x.basis,'quiet'));}if(!h.length)root.append(node('p','No recorded exposure by this point.'));return;}
 const e=data.events[cursor];if(!e){root.append(node('p','Load a session with events to begin.'));return;}
 root.append(node('h3',e.label),node('p',`${e.actor} · ${e.timestamp||'Timestamp unavailable'}`,'quiet'),node('p',`${data.session.trace} : line ${e.evidence.traceLine}`,'quiet'));
 if(e.kind==='compaction')root.append(node('p','Compaction recorded. Prior exposure remains in history; retention is unknown.'));
 for(const x of e.exposures){const s=data.sources.find(s=>s.id===x.sourceId);root.append(node('p',`${symbols[x.state]} ${x.state} · ${s.path}${x.startLine?' : '+x.startLine+'–'+(x.endLine||x.startLine):''}`),node('p',x.basis,'quiet'));}
 const connections=data.links.filter(l=>(l.from===e.id||l.to===e.id)&&data.events.find(x=>x.id===l.from).seq<=cursor&&data.events.find(x=>x.id===l.to).seq<=cursor);
 if(connections.length){root.append(node('h3','Evidence connections'));for(const l of connections){const other=data.events.find(x=>x.id===(l.from===e.id?l.to:l.from));root.append(jumpButton(other,`${l.kind==='inferred'?'⇢ Inferred':'→ Recorded'} · ${other.seq+1}`),node('p',l.reason,'quiet'));}}
 const candidates=(data.candidates||[]).filter(c=>c.eventId===e.id);if(candidates.length){root.append(node('h3','Visible path options'));for(const c of candidates){const source=data.sources.find(s=>s.id===c.sourceId);const button=node('button',source.path,'wf-button secondary');button.type='button';button.onclick=()=>{selectedSource=c.sourceId;render();};root.append(button);}}
 renderPayload(root,e);
}
function render(){if(!data)return;$('scrub').value=Math.max(0,cursor);$('position').textContent=`${cursor+1} / ${data.events.length}`;for(const id of ['play','prev','next','scrub'])$(id).disabled=!data.events.length;$('prev').disabled=cursor<=0;$('next').disabled=cursor>=data.events.length-1;
 const query=$('search').value.toLowerCase();const timeline=$('timeline');timeline.replaceChildren();
 for(const e of data.events){if(query&&!JSON.stringify(e).toLowerCase().includes(query))continue;
 const row=node('div',undefined,'timeline-row');const b=node('button',undefined,'event'+(e.seq>cursor?' future':''));b.type='button';b.dataset.eventId=e.id;b.setAttribute('aria-current',e.seq===cursor?'step':'false');
 let title=e.label;
 if(e.kind==='message'){let snippet='';try{const payload=JSON.parse(e.evidence.text);snippet=(payload.content||[]).map(x=>x.text||'').join(' ').replace(/\s+/g,' ').trim().slice(0,140);}catch{}title=e.actor.charAt(0).toUpperCase()+e.actor.slice(1)+' message'+(snippet?' ('+snippet+')':'');}
 b.title=title+(e.seq>cursor?' · upcoming':'');b.setAttribute('aria-label',(e.seq+1)+': '+title+' ['+e.kind+']');
 b.append(node('span',(e.seq+1)+':','event-number'),node('span',title,'event-title'),node('span','['+e.kind+']'+((data.candidates||[]).filter(c=>c.eventId===e.id).length?' ['+(data.candidates||[]).filter(c=>c.eventId===e.id).length+' paths]':''),'event-tag'));b.onclick=()=>seek(e.seq);
 const inspectButton=node('button','⋯','timeline-inspect');inspectButton.type='button';inspectButton.title='Inspect event '+(e.seq+1);inspectButton.setAttribute('aria-label','Inspect event '+(e.seq+1));inspectButton.onclick=()=>{seek(e.seq);$('inspector').scrollIntoView({block:'center'});$('inspector').focus({preventScroll:true});};row.append(b,inspectButton);timeline.append(row);
 const batches=new Map();(e.toolCalls||[]).forEach((c,index)=>{if(!c.position.startsWith('Promise.'))return;const batch=c.position.split(' slot ')[0];if(!batches.has(batch))batches.set(batch,[]);batches.get(batch).push({c,index});});
 for(const [batch,children] of batches){const key=e.id+':'+batch;const detail=node('details',undefined,'wf-disclosure timeline-batch');detail.open=expandedBatches.has(key);const failures=children.filter(x=>x.c.outcome==='failed').length;detail.append(node('summary',batch+' · '+children.length+' calls'+(failures?' · '+failures+' failed':'')));const body=node('div',undefined,'wf-disclosure-body wf-flow');
 for(const {c,index} of children){const child=node('button',undefined,'batch-child');child.type='button';const slot=c.position.split(' slot ')[1];const label=toolRowLabel(c);child.title=c.tool+' · '+label;child.setAttribute('aria-label',slot+': '+label+' ['+c.outcome+']');child.setAttribute('aria-pressed',String(selectedTool?.eventId===e.id&&selectedTool.index===index));child.append(node('span',slot+': '+label,'event-title'),node('span','['+c.outcome+']','event-tag'));child.onclick=()=>selectTool(e,index);body.append(child);}
 detail.append(body);detail.ontoggle=()=>{if(detail.open)expandedBatches.add(key);else expandedBatches.delete(key);};timeline.append(detail);}

 }
 if(!timeline.children.length)timeline.append(node('p','No matching events.'));
 const map=$('map');map.replaceChildren();const groups=new Map();let exposed=0;
 for(const s of data.sources){const st=state(s.id);if(st.state!=='inventoried')exposed++;if(!s.inventoried&&st.state==='inventoried')continue;const dir=s.path.includes('/')?s.path.slice(0,s.path.lastIndexOf('/'))||'/':'Repository root';if(!groups.has(dir))groups.set(dir,[]);groups.get(dir).push({s,st});}
 for(const [dir,items] of [...groups].sort((a,b)=>a[0].localeCompare(b[0]))){const section=node('section',undefined,'directory');section.append(node('h3',dir));const tiles=node('div',undefined,'tiles');for(const {s,st} of items.sort((a,b)=>a.s.path.localeCompare(b.s.path))){const b=node('button',undefined,'source');b.type='button';b.dataset.state=st.state;b.setAttribute('aria-pressed',String(selectedSource===s.id));b.append(node('span',s.path.split('/').pop()),node('small',`${symbols[st.state]} ${st.state}${st.step?' · #'+st.step:''}`));b.title=s.path;b.onclick=()=>{selectedTool=null;selectedSource=s.id;render();};tiles.append(b);}section.append(tiles);map.append(section);}
 $('stats').textContent=`${exposed} sources encountered · ${data.events.slice(0,cursor+1).filter(e=>e.kind==='compaction').length} compactions`;
 $('map-count').textContent=`${data.sources.filter(s=>s.inventoried).length} inventoried`;
 if(!map.children.length)map.append(node('p','No inventoried or exposed sources.'));inspect();atlas?.render(data,cursor,selectedSource);
}

function citations(parent, evidence){
 for(const c of evidence){const event=data.events.find(e=>e.id===c.eventId);const box=node('details',undefined,'citation wf-disclosure');const body=node('div',undefined,'wf-disclosure-body wf-flow');body.append(node('pre',c.excerpt));box.append(node('summary','Evidence · event '+(event.seq+1)+' · trace line '+event.evidence.traceLine),body);const jump=jumpButton(event,'Inspect this event →');jump.addEventListener('click',()=>{$('inspector').scrollIntoView({block:'center'});$('inspector').focus({preventScroll:true});});body.append(jump);parent.append(box);}
}
function renderAnalysis(){
 const list=$('decision-list'), detail=$('decision-detail');list.replaceChildren();detail.replaceChildren();
 const all=data?.decisions||[];const query=$('decision-search').value.toLowerCase();
 if(!all.length){detail.append(node('p','No decision analysis has been hydrated for this report. The replay remains available below.'));return;}
 const filtered=all.filter(d=>JSON.stringify(d).toLowerCase().includes(query));
 for(const d of filtered){const b=node('button',d.question,'event');b.type='button';b.setAttribute('aria-pressed',String(d.id===decisionId));b.onclick=()=>{decisionId=d.id;renderAnalysis();};list.append(b);}
 if(!filtered.length)list.append(node('p','No matching decisions.'));
 const d=all.find(x=>x.id===decisionId);if(!d)return;
 detail.append(node('h3',d.question),node('p',d.answer));citations(detail,d.evidence);
 const path=node('ol',undefined,'decision-path');
 for(const id of d.edgeIds){const edge=data.guidanceEdges.find(e=>e.id===id);const item=node('li',undefined,'wf-flow');const from=data.events.find(e=>e.id===edge.from),to=data.events.find(e=>e.id===edge.to);item.append(node('strong',edge.kind.toUpperCase()+' · '+(from.seq+1)+' → '+(to.seq+1)),node('p',edge.explanation));citations(item,edge.evidence);path.append(item);}
 if(path.children.length){detail.append(node('h3','Decision trace'),path);}else detail.append(node('p','The trace does not establish the intermediate route.'));
 const findings=(data.findings||[]).filter(f=>f.decisionId===d.id);
 detail.append(node('h3','Routing diagnoses & guidance improvements'));
 if(!findings.length)detail.append(node('p','No evidence-backed routing problem identified for this decision.'));
 for(const f of findings){const box=node('article',undefined,'finding');box.append(node('h4',f.title),node('p',f.category+' · '+f.status.replaceAll('-',' '),'quiet'));
 for(const [label,key] of [['Observed','observation'],['Possible explanation','hypothesis'],['Guidance target','target'],['Improvement','improvement'],['Verify with','verification']]){const section=node('div');section.append(node('strong',label),node('p',f[key]));box.append(section);}citations(box,f.evidence);detail.append(box);}
}
$('decision-search').oninput=renderAnalysis;

$('load').onchange=async event=>{try{const file=event.target.files[0];if(file)load(JSON.parse(await file.text()));}catch(error){$('error').textContent=error.message;$('error').hidden=false;}event.target.value='';};
$('scrub').oninput=()=>seek(Number($('scrub').value));$('prev').onclick=()=>seek(cursor-1);$('next').onclick=()=>seek(cursor+1);$('search').oninput=()=>render();
$('play').onclick=()=>{if(timer){stop();return;}if(!data||!data.events.length)return;if(cursor===data.events.length-1)cursor=-1;$('play').textContent='Pause';timer=setInterval(()=>{cursor++;selectedSource=null;selectedTool=null;render();if(cursor>=data.events.length-1)stop();},1000);};
atlas=createFogAtlas({selectEvent:seek,selectSource:id=>{selectedTool=null;selectedSource=id;render();}});
window.fogChartTimeline=id=>{const e=data.events.find(e=>e.id===id);if(!e)return;$('search').value='';render();$('report-panel').hidden=false;$('report-toggle').setAttribute('aria-expanded','true');const target=[...$('timeline').querySelectorAll('[data-event-id]')].find(n=>n.dataset.eventId===id);target?.scrollIntoView({block:'center'});target?.focus({preventScroll:true});};
window.fogShowDiagnostic=ids=>{const seqs=ids.map(id=>data.events.find(e=>e.id===id)?.seq).filter(Number.isInteger);if(!seqs.length)return;if(Math.max(...seqs)>cursor)seek(Math.max(...seqs));atlas.showDiagnostic(ids);};
try{const initial=JSON.parse($('fog-data').textContent);if(initial&&typeof initial==='object')load(initial);else for(const id of ['play','prev','next','scrub'])$(id).disabled=true;}catch(error){$('error').textContent=error.message;$('error').hidden=false;}
})();
