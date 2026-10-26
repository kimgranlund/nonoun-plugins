// Inspector-owned selects: fixed jig geometry, independent of specimen settings.
export function createJig(root){
 const selects=[];let dispatch,opened=null;
 for(const select of root.querySelectorAll('select')){
  const id=select.id,options=[...select.options].map(o=>({value:o.value,label:o.textContent}));
  const label=root.querySelector(`label[for="${id}"]`),field=select.closest('.field__root');
  field.classList.add('jig-select-field');label.id=id+'-label';label.htmlFor=id+'-trigger';
  const holder=document.createElement('div');holder.className='jig-select';
  holder.innerHTML=`<input type="hidden" id="${id}"><button type="button" id="${id}-trigger" class="jig-select-trigger" role="combobox" aria-haspopup="listbox" aria-expanded="false" aria-controls="${id}-popup" aria-labelledby="${label.id} ${id}-value"><span id="${id}-value"></span><i class="ph ph-caret-down" aria-hidden="true"></i></button><div id="${id}-popup" class="listbox__root jig-popup" role="listbox" aria-labelledby="${label.id}" popover="auto">${options.map((o,i)=>`<div id="${id}-option-${i}" class="listbox__option" role="option" aria-selected="false" data-index="${i}"><span data-slot="label">${o.label}</span><i class="ph ph-check" aria-hidden="true"></i></div>`).join('')}</div>`;
  holder.querySelector('input').value=select.value;select.closest('.select__root').replaceWith(holder);
  const trigger=holder.querySelector('button'),popup=holder.querySelector('[role=listbox]'),rows=[...popup.children];
  let active=0,typed='',lastType=0;
  const position=()=>{const r=trigger.getBoundingClientRect(),w=Math.min(Math.max(r.width,160),innerWidth-16);popup.style.width=w+'px';popup.style.left=Math.max(8,Math.min(r.left,innerWidth-w-8))+'px';popup.style.maxHeight=Math.max(80,Math.min(240,innerHeight-16))+'px';const h=popup.getBoundingClientRect().height;popup.style.top=Math.max(8,Math.min(r.bottom+4,innerHeight-h-8))+'px';};
  const highlight=i=>{active=(i+rows.length)%rows.length;rows.forEach((r,j)=>r.dataset.active=String(j===active));trigger.setAttribute('aria-activedescendant',rows[active].id);const r=rows[active].getBoundingClientRect(),p=popup.getBoundingClientRect();if(r.top<p.top+4)popup.scrollTop-=p.top+4-r.top;else if(r.bottom>p.bottom-4)popup.scrollTop+=r.bottom-p.bottom+4;};
  const close=()=>{if(popup.matches(':popover-open'))popup.hidePopover();trigger.setAttribute('aria-expanded','false');trigger.removeAttribute('aria-activedescendant');if(opened===entry)opened=null;};
  const open=()=>{if(opened&&opened!==entry)opened.close();active=Math.max(0,options.findIndex(o=>o.value===holder.querySelector('input').value));popup.showPopover();opened=entry;position();trigger.setAttribute('aria-expanded','true');highlight(active);};
  const commit=()=>{const value=options[active].value;close();dispatch({type:'axis',key:id,value});trigger.focus();};
  trigger.addEventListener('click',()=>popup.matches(':popover-open')?close():open());
  trigger.addEventListener('keydown',e=>{
   if(e.isComposing)return;
   const isOpen=popup.matches(':popover-open');
   if(['ArrowDown','ArrowUp','Home','End','Enter',' '].includes(e.key)){
    e.preventDefault();if(!isOpen){open();if(e.key==='Home')highlight(0);if(e.key==='End')highlight(rows.length-1);return;}
    if(e.key==='Enter'||e.key===' '){commit();return;}
    highlight(e.key==='Home'?0:e.key==='End'?rows.length-1:active+(e.key==='ArrowDown'?1:-1));
   }else if(e.key==='Escape'){e.preventDefault();close();}else if(e.key==='Tab'){close();}
   else if(e.key.length===1&&!e.ctrlKey&&!e.metaKey&&!e.altKey){e.preventDefault();if(!isOpen)open();const now=Date.now();typed=now-lastType>700?e.key:typed+e.key;lastType=now;const i=options.findIndex(o=>o.label.toLowerCase().startsWith(typed.toLowerCase()));if(i>=0)highlight(i);}
  });
  popup.addEventListener('pointerdown',e=>e.preventDefault());
  popup.addEventListener('click',e=>{const row=e.target.closest('[data-index]');if(row){highlight(Number(row.dataset.index));commit();}});
  popup.addEventListener('toggle',()=>{if(!popup.matches(':popover-open'))close();});
  trigger.addEventListener('blur',close);
  const entry={close,position,sync(s){const value=s[id],index=options.findIndex(o=>o.value===String(value));holder.querySelector('input').value=value;holder.querySelector('#'+id+'-value').textContent=options[index]?.label??value;rows.forEach((row,i)=>row.setAttribute('aria-selected',String(i===index)));}};
  selects.push(entry);
 }
 // Keep values in the same horizontal rail as label and native accessible slider.
 for(const range of root.querySelectorAll('.controls input[type=range]')){
  const field=range.closest('.field__root'),label=field.querySelector('label'),output=label.querySelector('output');
  field.classList.add('jig-range-field');field.append(output);
  const number=document.createElement('input');number.type='number';number.className='jig-number';number.min=range.min;number.max=range.max;number.step=range.step;const context=range.id.endsWith('Gutter')?label.textContent.trim()+' gutter':range.id.startsWith('container')?'Container radius '+label.textContent.trim():'Control radius '+label.textContent.trim();number.setAttribute('aria-label',context+' percentage');range.setAttribute('aria-label',context+' percentage');field.append(number);output.hidden=true;
  range.addEventListener('input',()=>{number.removeAttribute('aria-invalid');number.value=range.value;});
  root.addEventListener('click',e=>{const action=e.target.closest('[data-action]');if(action&&(action.dataset.action==='reset'||action.dataset.command==='reset'||(action.dataset.action==='radius-preset'&&range.id.startsWith(action.dataset.family)))){number.removeAttribute('aria-invalid');number.value=range.value;}},true);
  const set=()=>{if(number.value===''||!number.validity.valid){number.setAttribute('aria-invalid','true');return;}number.removeAttribute('aria-invalid');dispatch({type:'dial',key:range.id,value:number.value});};
  number.addEventListener('input',()=>{if(number.value===''||!number.validity.valid)number.setAttribute('aria-invalid','true');else number.removeAttribute('aria-invalid');});number.addEventListener('change',set);number.addEventListener('keydown',e=>{if(e.key==='Enter'){set();number.blur();}});
  selects.push({sync(){if(document.activeElement!==number&&!number.hasAttribute('aria-invalid'))number.value=range.value;}});
 }
 addEventListener('resize',()=>opened?.position());
 document.addEventListener('scroll',e=>{if(!e.target.closest?.('.jig-popup'))opened?.close();},true);
 return {bind(fn){dispatch=fn;},sync(s){selects.forEach(e=>e.sync(s));}};
}
