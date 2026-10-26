// Standalone controller passed to build.mjs; root-local hooks are separate from payload/cache.
const actionRoutingRuntime=createUIRuntime();
actionRoutingRuntime.mount({root:document.getElementById('action-routing'),stateKey:'action-routing',definition:{
 initialState:{selected:'A',inspected:false},
 reduce(state,action){if(action.type==='select')return {selected:action.id,inspected:false};if(action.type==='inspect')return {...state,inspected:true};return state;},
 render(root,state){
  root.querySelector('[data-record-choices]').innerHTML=['A','B'].map(id=>`<button type="button" class="record-choice__root" data-action="select-record" data-record="${id}" aria-pressed="${state.selected===id}">Record ${id}</button>`).join('');
  const detail=root.querySelector('[data-record-detail]');detail.dataset.renderedRecord=state.selected;
  detail.innerHTML=`<p>Evidence for record ${state.selected}</p><button type="button" class="button__root" data-action="inspect-record">Inspect evidence</button>`;
  root.querySelector('[data-record-status]').textContent=state.inspected?'Inspecting '+state.selected:'No event selected';
 },
 bind({onAction}){
  onAction('select-record',(event,button,dispatch)=>dispatch({type:'select',id:button.dataset.record}));
  onAction('inspect-record',(event,button,dispatch)=>dispatch({type:'inspect'}));
 }
}});
