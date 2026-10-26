/* Explicit concise labels; never truncate titles or mutate record identity. */
function renderCompactOptions(records,selected){
 const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 if(!records.length||records.some(r=>typeof r.id!=='string'||!r.id.trim()||typeof r.optionLabel!=='string'||!r.optionLabel.trim())||new Set(records.map(r=>r.id)).size!==records.length||new Set(records.map(r=>r.optionLabel.trim().toLocaleLowerCase())).size!==records.length)throw Error('Unique IDs and distinct nonempty option labels required');
 if(!records.some(r=>r.id===selected))throw Error('Selected record must exist');
 return records.map(r=>`<option value="${esc(r.id)}"${r.id===selected?' selected':''}>${esc(r.optionLabel)}</option>`).join('');
}
