// Mount with createUIRuntime().mount; query only the supplied root.
const titleRequestDefinition={initialState:{title:'',step:0,attempted:false,confirmed:false},
 reduce(state,action){
  if(action.type==='edit')return {...state,title:action.title,confirmed:false};
  if(action.type==='next')return {...state,attempted:true,step:state.title.trim()?1:0};
  if(action.type==='back')return {...state,step:0};
  if(action.type==='confirm')return state.title.trim()&&state.step===1?{...state,confirmed:true}:state;
  return state;
 },
 render(root,state){
  const input=root.querySelector('[name=title]');if(input.value!==state.title)input.value=state.title;
  root.querySelectorAll('[data-step]').forEach((panel,index)=>panel.hidden=index!==state.step);
  input.setAttribute('aria-invalid',String(state.attempted&&!state.title.trim()));
  root.querySelector('#title-error').hidden=!state.attempted||!!state.title.trim();
  root.querySelector('[data-title-summary]').textContent=state.title;
  root.querySelector('[data-confirmation]').hidden=!state.confirmed;
  root.querySelector('[data-confirm]').disabled=state.confirmed;
  root.querySelectorAll('[data-progress]').forEach((item,index)=>{const status=index===state.step?'current':index<state.step?'completed':'upcoming';item.dataset.stepState=status;item.querySelector('[data-step-state-label]').textContent=status[0].toUpperCase()+status.slice(1);if(index===state.step)item.setAttribute('aria-current','step');else item.removeAttribute('aria-current');});
 },
 bind({root,on,dispatch}){
  on('input','[name=title]',(event,input)=>dispatch({type:'edit',title:input.value}));
  on('click','[data-next]',()=>{const input=root.querySelector('[name=title]');dispatch({type:'edit',title:input.value});dispatch({type:'next'});if(!input.value.trim()){input.focus();return;}if(!focusWorkflowStep(root.querySelector('form'),1))throw Error('Missing review-step heading');});
  on('click','[data-back]',()=>{dispatch({type:'back'});if(!focusWorkflowStep(root.querySelector('form'),0))throw Error('Missing title-step heading');});
  on('click','[data-confirm]',()=>dispatch({type:'confirm'}));
 }
};
