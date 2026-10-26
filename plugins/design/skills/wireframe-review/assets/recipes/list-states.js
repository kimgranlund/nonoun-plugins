/* Standalone example. Adapt into the review controller lifecycle with proposal-scoped queries. */
(()=>{
 const host=document.querySelector('[data-list-example]');if(!host)return;
 const list=host.querySelector('.list__root'),rows=[...list.children],filter=host.querySelector('#directory-filter'),sort=host.querySelector('#directory-sort'),empty=host.querySelector('.empty__root'),status=host.querySelector('[role=status]');let order='source';
 const render=()=>{const query=filter.value.trim().toLocaleLowerCase();rows.forEach(row=>{row.hidden=!(row.dataset.name+' '+row.dataset.team).toLocaleLowerCase().includes(query);row.dataset.selected=String(row.querySelector('input').checked);});const visible=rows.filter(row=>!row.hidden).length,selected=rows.filter(row=>row.querySelector('input').checked).length;empty.hidden=visible>0;list.hidden=visible===0;host.dataset.state=visible?'populated':'empty';status.textContent=`${selected} selected · ${visible} visible. ${order==='source'?'Names as supplied.':order==='asc'?'Names sorted A to Z.':'Names sorted Z to A.'}`;};
 filter.addEventListener('input',render);rows.forEach(row=>row.querySelector('input').addEventListener('change',render));
 sort.addEventListener('click',()=>{order=order==='asc'?'desc':'asc';const sorted=[...rows].sort((a,b)=>a.dataset.name.localeCompare(b.dataset.name,'en')*(order==='asc'?1:-1));sorted.forEach(row=>list.append(row));sort.textContent=order==='asc'?'Sort names Z to A':'Sort names A to Z';render();});
 host.querySelector('#directory-clear').addEventListener('click',()=>{filter.value='';render();filter.focus();});render();
})();
