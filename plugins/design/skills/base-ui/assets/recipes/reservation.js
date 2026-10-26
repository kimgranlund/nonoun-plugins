const catalog={recorder:{label:'Portable recorder',minutes:20},shotgun:{label:'Shotgun microphone',minutes:15},lighting:{label:'Compact lighting kit',minutes:25}};
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const values=s=>({items:s.items,name:s.name,email:s.email,note:s.items.includes('lighting')?s.note:''});
const statusFor=s=>s.saved?(same(values(s),s.saved)?'Saved snapshot matches current values.':'Current values differ from the saved snapshot.'):'No saved snapshot yet. Save a valid reservation to create one.';
const fieldBindings=[['contact-name','name','name-help','name-error'],['contact-email','email','email-help','email-error'],['delivery-note','note','delivery-note-help','delivery-note-error']];
const selectionMessage='Choose no more than two available items. Remove a choice before selecting another.';
const reservationDefinition={initialState:{items:[],name:'',email:'',note:'',errors:{},saved:null,notice:'',noticeKind:''},reduce(state,a){
  if(a.type==='edit-items'){
    if(a.items.length>2)return {...state,errors:{...state.errors,items:selectionMessage},notice:'',noticeKind:''};
    const errors={...state.errors};delete errors.items;if(!a.items.includes('lighting'))delete errors.note;
    return {...state,items:a.items,errors,notice:'',noticeKind:''};
  }
  if(a.type==='edit-name'){const errors={...state.errors};if(a.name.trim())delete errors.name;return {...state,name:a.name,errors,notice:'',noticeKind:''};}
  if(a.type==='edit-email'){const errors={...state.errors};if(a.valid)delete errors.email;return {...state,email:a.email,errors,notice:'',noticeKind:''};}
  if(a.type==='edit-note'){const errors={...state.errors};if(a.note.trim())delete errors.note;return {...state,note:a.note,errors,notice:'',noticeKind:''};}
  if(a.type==='save'){
    const errors={...a.errors};
    if(Object.keys(errors).length)return {...state,errors,notice:'Please correct the highlighted fields before saving.',noticeKind:'error'};
    const saved={...values(state),items:[...state.items]};return {...state,saved,errors:{},notice:'Reservation saved in this page session.',noticeKind:'saved'};
  }
  if(a.type==='restore'){
    if(!state.saved)return {...state,notice:'No saved snapshot exists yet. Save a valid reservation first.',noticeKind:'error'};
    return {...state,items:[...state.saved.items],name:state.saved.name,email:state.saved.email,note:state.saved.note||'',errors:{},notice:'Restored the saved snapshot.',noticeKind:'saved'};
  }
  return state;
},render(root,s){
  const count=root.querySelector('[data-review-id="selected-count"]'),total=root.querySelector('[data-review-id="prep-total"]'),list=root.querySelector('[data-review-id="selected-items"]');
  const minutes=s.items.reduce((n,id)=>n+(catalog[id]?.minutes||0),0);
  if(count)count.textContent=`${s.items.length} ${s.items.length===1?'item':'items'} selected`;
  if(total)total.textContent=`${minutes} preparation ${minutes===1?'minute':'minutes'}`;
  if(list)list.innerHTML=s.items.length?s.items.map(id=>`<li>${catalog[id].label} · ${catalog[id].minutes} min</li>`).join(''):'<li>No equipment selected</li>';
  for(const [id,key,helpId,errorId] of fieldBindings){
    const input=root.querySelector('#'+id);if(input&&document.activeElement!==input&&input.value!==s[key])input.value=s[key];
    const err=root.querySelector('#'+errorId);if(err){err.textContent=s.errors[key]||'';err.hidden=!s.errors[key];}
    if(input){input.setAttribute('aria-invalid',s.errors[key]?'true':'false');input.setAttribute('aria-describedby',s.errors[key]?helpId+' '+errorId:helpId);}
  }
  root.querySelectorAll('input[type=checkbox][value]').forEach(input=>{input.checked=s.items.includes(input.value);});
  const group=root.querySelector('[data-review-id="equipment-group"]'),ee=root.querySelector('#equipment-error');if(group){group.setAttribute('aria-invalid',s.errors.items?'true':'false');group.setAttribute('aria-describedby',s.errors.items?'equipment-help equipment-error':'equipment-help');}if(ee){ee.textContent=s.errors.items||'';ee.hidden=!s.errors.items;}
  const lighting=s.items.includes('lighting'),noteGroup=root.querySelector('[data-review-id="delivery-note-group"]');if(noteGroup)noteGroup.hidden=!lighting;
  const status=root.querySelector('[data-review-id="reservation-status"]');if(status){status.textContent=s.notice||statusFor(s);status.dataset.state=s.noticeKind||((s.saved&&same(values(s),s.saved))?'saved':'');}
},bind({root,on,dispatch}){
  on('change','input[type=checkbox][value]',(e)=>{const selected=[...root.querySelectorAll('input[type=checkbox][value]:checked')].map(x=>x.value);if(selected.length>2){dispatch({type:'edit-items',items:selected});return;}dispatch({type:'edit-items',items:selected});});
  on('input','#contact-name',(e,node)=>dispatch({type:'edit-name',name:node.value}));
  on('input','#contact-email',(e,node)=>dispatch({type:'edit-email',email:node.value,valid:node.validity.valid}));
  on('input','#delivery-note',(e,node)=>dispatch({type:'edit-note',note:node.value}));
  on('click','[data-review-id="save-reservation"]',()=>{const name=root.querySelector('#contact-name'),email=root.querySelector('#contact-email'),note=root.querySelector('#delivery-note'),items=[...root.querySelectorAll('input[type=checkbox][value]:checked')].map(x=>x.value);const errors={};if(items.length<1)errors.items='Choose at least one available item.';else if(items.length>2)errors.items=selectionMessage;if(!name.value.trim())errors.name='Enter a contact name.';if(!email.value||!email.validity.valid)errors.email='Enter a valid email address.';if(items.includes('lighting')&&!note.value.trim())errors.note='Enter a delivery note for the lighting kit.';dispatch({type:'save',errors});const first=errors.items?root.querySelector('input[type=checkbox][value]'):errors.name?name:errors.email?email:errors.note?note:null;if(first)first.focus();});
  on('click','[data-review-id="restore-reservation"]',()=>dispatch({type:'restore'}));
}};
