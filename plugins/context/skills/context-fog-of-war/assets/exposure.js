/* Exposure, edits, context inclusion and routing are independent dimensions. */
function sourceExposure(data,id,cursor){
 const events=data.events.filter(e=>e.seq<=cursor),history=events.flatMap(event=>event.exposures.filter(x=>x.sourceId===id).map(exposure=>({event,exposure})));
 const candidates=(data.candidates||[]).filter(c=>c.sourceId===id&&events.some(e=>e.id===c.eventId));
 const full=history.findLast(h=>h.exposure.state==='read'),partial=history.findLast(h=>h.exposure.state==='partial');
 const requested=history.some(h=>h.exposure.state==='discovered'&&h.event.kind==='call');
 const records=(data.contextRecords||[]).filter(r=>r.sourceId===id&&events.some(e=>e.id===r.eventId)).sort((a,b)=>data.events.find(e=>e.id===a.eventId).seq-data.events.find(e=>e.id===b.eventId).seq);
 const latest=records.at(-1),confirmed=records.some(r=>r.status==='included');
 const compact=events.findLast(e=>e.kind==='compaction');
 const at=latest?data.events.find(e=>e.id===latest.eventId):null;
 const retention=at?.seq===cursor?(latest.status==='included'?'Confirmed at this step':'Removed at this step'):compact&&(!at||compact.seq>at.seq)?'Unknown after compaction':'Current retention unknown';
 const state=full?'full':partial?'partial':requested?'requested':history.length||candidates.some(c=>c.kind==='mentioned')?'encountered':candidates.length?'available':'inventoried';
 const label={full:'Full return',partial:'Partial return',requested:'Requested',encountered:'Path only',available:'Available',inventoried:'Inventory only'}[state];
 return {state,label,contents:!!(full||partial),confirmed,retention,edited:history.some(h=>h.exposure.state==='edited'),range:partial&&!full?partial.exposure:null,records,history};
}
function exposureSummary(root,data,id,cursor){
 const status=sourceExposure(data,id,cursor);root.append(payloadNode('h4','Exposure & retention'),payloadNode('p',status.label+(status.edited?' · Edited (does not establish a read)':'')));
 if(status.range?.startLine)root.append(payloadNode('p','Returned lines '+status.range.startLine+'–'+(status.range.endLine||status.range.startLine)));
 root.append(payloadNode('p',(status.confirmed?'Context inclusion recorded historically. ':'No explicit context-inclusion record. ')+status.retention+'.','quiet'));
 for(const record of status.records){root.append(payloadNode('p','Context '+record.status+' · '+record.eventId),payloadNode('pre',record.evidence.excerpt,'readable-output'));}
}
function evidenceIndicators(data,id,position){
 const byId=new Map(data.events.map(e=>[e.id,e])),status=sourceExposure(data,id,position);
 const cite=e=>({eventId:e.id,excerpt:e.evidence.text.slice(0,600)});
 const item=(key,label,state,explanation,evidence=[])=>({key,label,state,explanation,evidence});
 const candidates=(data.candidates||[]).filter(c=>c.sourceId===id&&byId.get(c.eventId).seq<=position&&c.kind==='available');
 const requests=status.history.filter(h=>h.exposure.state==='discovered'&&h.event.kind==='call');
 const returns=status.history.filter(h=>['read','partial'].includes(h.exposure.state));
 const full=returns.findLast(h=>h.exposure.state==='read'),partial=returns.at(-1),ret=full||partial;
 const edits=status.history.filter(h=>h.exposure.state==='edited');
 const links=(data.guidanceEdges||[]).filter(e=>e.sourceIds?.includes(id)&&byId.get(e.to).seq<=position);
 const lastContext=status.records.at(-1),contextAt=lastContext&&byId.get(lastContext.eventId).seq===position;
 // A failed batch does not assign failure to every source. Only an unambiguous single-source call can do so.
 let failure=null;for(const h of requests){if(new Set(h.event.exposures.map(x=>x.sourceId)).size!==1||(h.event.toolCalls?.length||0)>1)continue;for(const link of data.links.filter(l=>l.from===h.event.id&&l.kind==='recorded')){const result=byId.get(link.to);if(result&&result.seq<=position&&eventExecution(result).state==='failed')failure=result;}}
 return [
 item('listed','Listed',candidates.length?'recorded':'unknown',candidates.length?'Offered as an available option in recorded context.':'No available-option listing recorded; a mention alone is not an offered option.',candidates.map(c=>c.evidence)),
 item('requested','Requested',requests.length?'recorded':'unknown',requests.length?'Retrieval requested; this does not establish a successful return.':'No retrieval request recorded by this step.',requests.map(h=>cite(h.event))),
 item('returned','Returned',ret?(full?'recorded':'partial'):failure?'failed':'unknown',ret?(full?'Full content return recorded.':'Partial content return'+(partial.exposure.startLine?' · lines '+partial.exposure.startLine+'–'+(partial.exposure.endLine||partial.exposure.startLine):'')+'.')+(failure?' A separate attempt failed.':''):failure?'An attributable retrieval failed; no content return is recorded.':'No content return recorded by this step.',[...returns.map(h=>cite(h.event)),...(failure?[cite(failure)]:[])]),
 item('context','Context',contextAt?(lastContext.status==='included'?'recorded':'removed'):'unknown',status.retention+(status.confirmed?' · historical inclusion recorded.':'.'),status.records.map(r=>r.evidence)),
 item('referenced','Referenced',links.some(e=>e.kind!=='inferred')?'recorded':links.length?'inferred':'unknown',links.length?'Source-specific reference or influence recorded. Read the relationship evidence; a reference is not proof of causation.':'No source-specific downstream connection recorded by this step.',links.flatMap(e=>e.evidence)),
 item('edited','Edited',edits.length?'recorded':'unknown',edits.length?'Recorded edit; this does not establish a prior read.':'No edit recorded by this step.',edits.map(h=>cite(h.event)))
 ];
}
function eventExecution(event){
 if(event.kind==='call')return {state:'pending',label:'Requested · outcome not yet recorded'};
 if(event.kind!=='result')return {state:'none',label:'No execution status'};
 const calls=event.toolCalls||[];let states=calls.map(c=>c.outcome);
 if(!states.length){let p;try{p=JSON.parse(event.evidence.text);}catch{}let output=p?.output;for(let i=0;i<3&&typeof output==='string';i++){try{output=JSON.parse(output);}catch{break;}}if(typeof output?.exit_code==='number')states=[output.exit_code===0?'succeeded':'failed'];}
 if(!states.length)return {state:'unknown',label:'Outcome unknown'};
 const distinct=new Set(states);if(distinct.size>1)return {state:'mixed',label:'Mixed · '+states.map((s,i)=>'call '+(i+1)+' '+s).join(', ')};
 const state=states[0];return {state,label:{succeeded:'Succeeded',failed:'Failed',pending:'Pending',unknown:'Outcome unknown'}[state]||'Outcome unknown'};
}
