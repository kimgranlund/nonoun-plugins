/* Concatenate components.js before this adapter and register the actual leaf ID.
   One coherent workflow per leaf; native editing values and stage survive remounts. */
function registerWorkflowExample(unitId){
 registerPrototype({unitId,initialState:{values:{},step:0,saved:null,focusStep:false},
  reduce:(state,action)=>action.type==='workflow-change'?action.snapshot:state,
  render(root,state){
   root.querySelectorAll('[name]').forEach(e=>{if(Object.hasOwn(state.values,e.name)&&e.value!==state.values[e.name]){e.value=state.values[e.name];e.closest('[data-workflow-combobox]')?.workflowRestore?.();}});
   const form=root.querySelector('[data-workflow-stepper]');if(form){form.dataset.restoreStep=String(state.step);form.workflowSavedDraft=state.saved;if(Number(form.dataset.currentStep)!==state.step)form.workflowShow?.(state.step);if(state.saved){const same=state.saved.contact===form.elements.contact.value&&state.saved.email===form.elements.email.value;form.querySelector('[data-step-status]').textContent=same?'Draft saved in this page. Nothing was sent.':'Unsaved changes. Nothing is sent.';}}
  },
  bind({root,on,dispatch,signal}){
   const cleanup=globalThis.mountWorkflowPatterns(root);
   let priorStep=Number(root.querySelector('[data-workflow-stepper]')?.dataset.currentStep||0);
   const capture=()=>queueMicrotask(()=>{if(signal.aborted)return;const form=root.querySelector('[data-workflow-stepper]');const currentStep=Number(form?.dataset.currentStep||0),focusStep=currentStep!==priorStep;priorStep=currentStep;dispatch({type:'workflow-change',snapshot:{values:Object.fromEntries([...root.querySelectorAll('[name]')].map(e=>[e.name,e.value])),step:Number(form?.dataset.currentStep||0),saved:form?.workflowSavedDraft||null,focusStep}});if(focusStep&&!signal.aborted)focusWorkflowStep(form,currentStep);});
   on('input','input',capture);on('change','select',capture);on('click','button',capture);on('submit','form',capture);
   return cleanup;
  }
 });
}
