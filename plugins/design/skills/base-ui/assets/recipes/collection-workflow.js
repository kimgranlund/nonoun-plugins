// Standalone example. Adapt to the prototype controller lifecycle inside a review shell.
(()=>{
 const root=document.querySelector('[data-collection-workflow]'),form=root.querySelector('form'),contact=root.querySelector('#loan-contact'),choices=[...root.querySelectorAll('[name=equipment]')],status=root.querySelector('#loan-status');let saved=null;
 const draft=()=>({contact:contact.value,selected:choices.filter(e=>e.checked&&!e.disabled).map(e=>e.value)});
 const paint=()=>{const value=draft(),count=value.selected.length,minutes=choices.filter(e=>value.selected.includes(e.value)).reduce((n,e)=>n+Number(e.dataset.minutes),0);root.querySelector('#loan-total').textContent=`${count} ${count===1?'item':'items'} selected · ${minutes} min preparation`;status.textContent=saved?(JSON.stringify(value)===JSON.stringify(saved)?'Saved in this page.':'Unsaved changes. The last saved draft is retained.'):'Draft has not been saved.';};
 form.addEventListener('input',paint);
 form.addEventListener('submit',event=>{event.preventDefault();saved=draft();const snapshot=root.querySelector('#loan-snapshot');snapshot.hidden=false;snapshot.querySelector('p').textContent=`${saved.contact}: ${saved.selected.join(', ')||'No equipment selected'}`;paint();});
 root.querySelector('#loan-restore').addEventListener('click',()=>{contact.value=saved?.contact||'';choices.forEach(e=>e.checked=!!saved?.selected.includes(e.value));paint();});
})();
