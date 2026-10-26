const payloadNode=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
function payloadReadable(value,depth=0){
 if(depth>8)return typeof value==='string'?value:JSON.stringify(value,null,2);
 if(typeof value==='string'){try{return payloadReadable(JSON.parse(value),depth+1);}catch{return value;}}
 if(value===null||value===undefined)return value===null?'null':'';
 if(Array.isArray(value))return value.map(x=>payloadReadable(x,depth+1)).join('\n\n');
 if(typeof value==='object'){
  if(Object.hasOwn(value,'output'))return payloadReadable(value.output,depth+1);
  if(Object.hasOwn(value,'stdout')||Object.hasOwn(value,'stderr'))return ['stdout','stderr'].filter(k=>value[k]!==undefined&&value[k]!=='').map(k=>k+':\n'+payloadReadable(value[k],depth+1)).join('\n\n');
  if(Array.isArray(value.content))return payloadReadable(value.content,depth+1);
  if(typeof value.text==='string')return payloadReadable(value.text,depth+1);
  if(value.status==='fulfilled'&&Object.hasOwn(value,'value'))return payloadReadable(value.value,depth+1);
  if(value.status==='rejected'&&Object.hasOwn(value,'reason'))return 'Rejected: '+payloadReadable(value.reason,depth+1);
  return JSON.stringify(value,null,2);
 }
 return String(value);
}

function payloadOutput(root,value){root.append(payloadNode('pre',payloadReadable(value)||'(No output)','readable-output'));}
/* Inert payload templates shared by events, batch slots and connection evidence. */
let payloadTabId=0;
function payloadValue(value){if(typeof value==='string'){try{return JSON.parse(value);}catch{}}return value;}
function payloadRecord(event){return payloadValue(event.evidence.text.split('\n\nDecoded tool/output attribution (input order):')[0]);}
function payloadTabs(host,raw){
 const id='payload-'+(++payloadTabId),bar=payloadNode('div',undefined,'wf-tabs'),readable=payloadNode('div',undefined,'wf-flow payload-readable'),json=payloadNode('div',undefined,'payload-json');
 bar.setAttribute('role','tablist');bar.setAttribute('aria-label','Payload view');
 const panels=[readable,json],buttons=['Readable','Raw JSON'].map((label,i)=>{const b=payloadNode('button',label);b.type='button';b.id=id+'-tab-'+i;b.setAttribute('role','tab');b.setAttribute('aria-controls',id+'-panel-'+i);bar.append(b);return b;});
 panels.forEach((p,i)=>{p.id=id+'-panel-'+i;p.setAttribute('role','tabpanel');p.setAttribute('aria-labelledby',buttons[i].id);p.tabIndex=0;});
 function activate(index,focus=false){buttons.forEach((b,i)=>{b.setAttribute('aria-selected',String(i===index));b.tabIndex=i===index?0:-1;panels[i].hidden=i!==index;});if(focus)buttons[index].focus();}
 buttons.forEach((b,i)=>{b.onclick=()=>activate(i);b.onkeydown=e=>{const keys={ArrowRight:(i+1)%2,ArrowLeft:(i+1)%2,Home:0,End:1};if(e.key in keys){e.preventDefault();activate(keys[e.key],true);}};});
 json.append(payloadNode('pre',JSON.stringify(raw,null,2)));host.append(bar,...panels);activate(0);return readable;
}
function payloadFields(root,value){
 value=payloadValue(value);if(!value||typeof value!=='object'){payloadOutput(root,value);return;}
 if(Array.isArray(value)){value.forEach(v=>payloadFields(root,v));return;}
 for(const [key,v] of Object.entries(value)){root.append(payloadNode('h4',({cmd:'Command',command:'Command',cwd:'Working directory',workdir:'Working directory',path:'File path',file_path:'File path',exit_code:'Exit code',wall_time_seconds:'Duration (seconds)',session_id:'Process session'}[key]||key.replaceAll('_',' '))));if(typeof v==='object'&&v!==null)payloadFields(root,v);else root.append(payloadNode('pre',String(v??'null'),'readable-output'));}
}
function payloadTool(root,call,isResult){
 root.append(payloadNode('h4',call.position+' · '+call.tool));
 if(isResult){root.append(payloadNode('p',call.settlement+' · '+call.outcome,'quiet'));if(call.settlement==='pending')root.append(payloadNode('p','Output has not arrived at this event.'));else{const out=payloadValue(call.output);if(out&&typeof out==='object'&&!Array.isArray(out))for(const k of ['exit_code','wall_time_seconds','session_id'])if(k in out)root.append(payloadNode('p',k.replaceAll('_',' ')+': '+out[k],'quiet'));payloadOutput(root,call.output);}}
 else payloadFields(root,call.arguments);
}
const payloadTemplates={
 message(root,event,p){root.append(payloadNode('h4',event.actor+' message'));for(const block of Array.isArray(p?.content)?p.content:[p?.content??p]){if(block&&typeof block==='object'&&typeof block.text==='string')root.append(payloadNode('div',block.text,'payload-prose'));else if(typeof block==='string')root.append(payloadNode('div',block,'payload-prose'));else root.append(payloadNode('p','Non-text content: '+(block?.type||'unknown')+' (inspect Raw JSON)','quiet'));}},
 call(root,event,p){if(event.toolCalls?.length)event.toolCalls.forEach(c=>payloadTool(root,c,false));else{root.append(payloadNode('h4',p?.name||event.label));payloadFields(root,p?.arguments??p?.input??p);}},
 result(root,event,p){if(event.toolCalls?.length)event.toolCalls.forEach(c=>payloadTool(root,c,true));else{root.append(payloadNode('h4','Tool response'));payloadOutput(root,p?.output??p);}},
 compaction(root,event,p){root.append(payloadNode('p','Compaction recorded. Retained context cannot be established from exposure history alone.'));payloadFields(root,p);},
 context(root,event,p){root.append(payloadNode('h4','Context supplied to the harness'));payloadFields(root,p);},
 unknown(root,event,p){root.append(payloadNode('p','Unrecognized payload type. Fields are shown without interpreting their meaning.'));payloadFields(root,p);}
};
function renderPayload(root,event){(payloadTemplates[event.kind]||payloadTemplates.unknown)(root,event,payloadRecord(event));}
