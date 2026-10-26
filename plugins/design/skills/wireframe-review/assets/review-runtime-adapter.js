/* Review identity and read-only policy; lifecycle is supplied by base-ui. */
const prototypeDefinitions=new Map(),prototypeRuntime=createUIRuntime();
function registerPrototype(definition){
 if(!definition?.unitId||prototypeDefinitions.has(definition.unitId)||typeof definition.reduce!=='function'||typeof definition.render!=='function')throw Error('Invalid or duplicate prototype definition');
 if(definition.bind&&(typeof definition.bind!=='function'||definition.bind.length>1))throw Error('Prototype bind expects bind({root,on,dispatch,signal}); positional bind(root,dispatch) is unsupported');
 prototypeDefinitions.set(definition.unitId,definition);
}
function prototypeUnmountAll(){prototypeRuntime.unmountAll();}
function prototypeMount(doc,readOnly){for(const root of doc.querySelectorAll('[data-unit-id]')){const definition=prototypeDefinitions.get(root.dataset.unitId);if(definition)prototypeRuntime.mount({root,definition,stateKey:JSON.stringify([root.dataset.unitId,root.dataset.variantId]),readOnly});}}
function revisePrototypePlan(state,patch){return {...state,...patch,planRevision:(state.planRevision??0)+1,approvedRevision:null};}
function approvePrototypePlan(state){return {...state,approvedRevision:state.planRevision??0};}
function prototypePlanApproved(state){return state.approvedRevision!=null&&state.approvedRevision===(state.planRevision??0);}

// Call only after a committed Next/Back render; mounting and typing do not request focus.
