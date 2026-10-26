/* Optional caret enhancement. Native dialog commands retain opening/focus ownership. */
(()=>{
  document.querySelectorAll('dialog').forEach(dialog=>{
    dialog.addEventListener('toggle',event=>{
      if(event.newState!=='open')return;
      const field=dialog.querySelector('input[autofocus],textarea[autofocus]');
      if(!field||document.activeElement!==field||typeof field.setSelectionRange!=='function')return;
      if(field instanceof HTMLInputElement&&!['text','search','tel','url','password'].includes(field.type))return;
      field.setSelectionRange(field.value.length,field.value.length);
    });
  });
})();
