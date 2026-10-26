/* Workflow status is an evidence assertion, never inferred from graph geometry. */
function createFogWorkflow(){
 const $=id=>document.getElementById(id),panel=$('workflow-panel');let data,opener;const backgrounds=()=>[document.querySelector("main"),$("chart-panel")];
 const el=(tag,text,cls)=>{const n=document.createElement(tag);n.textContent=text;if(cls)n.className=cls;return n;};
 const action=(label,fn)=>{const b=el('button',label,'wf-button secondary');b.type='button';b.onclick=fn;return b;};
 function inspect(workflow,stage){
  const host=$('workflow-detail');host.replaceChildren(el('h3',stage.kind+' · '+stage.state),el('p',stage.summary));
  for(const ref of stage.evidence){const card=el('section','','wf-flow');card.append(el('h4',ref.label));
   if(ref.artifact){let value;try{value=JSON.parse(ref.excerpt);}catch{}if(value&&typeof value==='object'){const dl=el('dl','','workflow-facts');for(const [key,v] of Object.entries(value)){dl.append(el('dt',key.replace(/([a-z])([A-Z])/g,'$1 $2')),el('dd',Array.isArray(v)?v.join(', '):String(v)));}card.append(dl);}const raw=el('details','','wf-disclosure'),body=el('div','','wf-disclosure-body');raw.append(el('summary','Raw evidence JSON'),body);body.append(el('pre',ref.excerpt,'workflow-excerpt'));card.append(raw);}else card.append(el('pre',ref.excerpt,'workflow-excerpt'));
   if(ref.eventId)card.append(action('Inspect recorded event',()=>{hide();$('chart-panel').hidden=true;window.fogChartInspect?.(ref.eventId);$('workflow-return')?.remove();const back=action('Back to workflow',()=>show($('workflow-canvas-open')));back.id='workflow-return';$('inspector').prepend(back);}),action('Show in timeline',()=>{hide();$('chart-panel').hidden=true;window.fogChartTimeline?.(ref.eventId);}));
   if(ref.artifact)card.append(el('p',ref.artifact+' · '+ref.pointer));host.append(card);
  }
  if(!stage.evidence.length)host.append(el('p','No supporting record supplied. This is unknown, not evidence of failure.'));
  host.append(el('h4','Next step'),el('p',workflow.nextStep),el('h4','Uncertainty'),el('p',workflow.uncertainty));
 }
 function hide(){panel.hidden=true;for(const n of backgrounds())n.inert=false;}
 function show(trigger){opener=trigger;panel.hidden=false;for(const n of backgrounds())n.inert=true;$('workflow-close').focus();}
 $('workflow-close').onclick=()=>{hide();opener?.focus();};panel.addEventListener('keydown',e=>{if(e.key==='Escape')$('workflow-close').click();if(e.key==='Tab'){const nodes=[...panel.querySelectorAll('button,summary,a[href]')].filter(n=>n.getClientRects().length);const first=nodes[0],last=nodes.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}}});
 for(const id of ['workflow-open','workflow-canvas-open'])$(id).onclick=()=>show($(id));
 return {load(value){data=value;const list=$('workflow-list');list.replaceChildren();$('workflow-detail').replaceChildren();
  const rows=data.workflows||[];$('workflow-summary').textContent=rows.length?'Select a stage to inspect its evidence.':'No workflow assessment supplied. Trace activity alone cannot establish completion. Add a workflow manifest with cited requirements and outcomes.';
  for(const workflow of rows){const section=el('section','','wf-flow');section.append(el('h3',workflow.title));const path=el('div','','workflow-path');
   for(const stage of workflow.stages){const b=action('',()=>{inspect(workflow,stage);const heading=$('workflow-detail').querySelector('h3');heading.tabIndex=-1;heading.focus({preventScroll:true});heading.scrollIntoView({block:'start'});for(const other of path.children)other.setAttribute('aria-pressed',String(other===b));});b.classList.add('workflow-stage');b.dataset.state=stage.state;b.setAttribute('aria-pressed','false');b.append(el('strong',stage.kind+(stage.kind==='outcome'?'':' →')),el('span',stage.state),el('span',stage.summary));path.append(b);}
   section.append(path);list.append(section);
  }
  if(rows.length){inspect(rows[0],rows[0].stages[0]);list.querySelector('.workflow-stage').setAttribute('aria-pressed','true');}
  if(location.hash==='#workflow')show($('workflow-open'));
 }};
}
