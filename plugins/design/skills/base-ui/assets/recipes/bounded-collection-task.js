// Application state only. Geometry, scroll ownership and control decoration are authored HTML/CSS.
(()=>{
 const root=document.querySelector('[data-bounded-task]');if(!root)return;
 const contact=root.querySelector('#bounded-contact'),choices=[...root.querySelectorAll('[name=supplies]')],status=root.querySelector('#bounded-status');let saved=null;
 const draft=()=>({contact:contact.value,selected:choices.filter(e=>e.checked&&!e.disabled).map(e=>e.value)});
 const paint=()=>{const value=draft();root.querySelector('#bounded-restore').disabled=!saved;root.querySelector('#bounded-total').textContent=`${value.selected.length} items selected · ${choices.filter(e=>value.selected.includes(e.value)).reduce((n,e)=>n+Number(e.dataset.minutes),0)} min preparation`;status.textContent=saved?(JSON.stringify(value)===JSON.stringify(saved)?'Saved':'Unsaved changes'):'No saved draft';};
 root.addEventListener('input',paint);
 root.addEventListener('submit',event=>{event.preventDefault();if(!root.reportValidity())return;saved=draft();paint();});
 root.querySelector('#bounded-restore').addEventListener('click',()=>{if(!saved)return;contact.value=saved.contact;choices.forEach(e=>e.checked=saved.selected.includes(e.value));paint();});
 root.querySelector('#bounded-save').disabled=false;root.dataset.ready='';paint();
})();
