// Preserve the cascade position and every byte outside the owned glyph block.
export function rewriteIconCSS(css,icons){
 const marker='/* Bundled Phosphor glyphs */\n';
 if(css.split(marker).length!==2)throw Error('Expected exactly one bundled glyph block');
 const start=css.indexOf(marker)+marker.length,tail=css.slice(start);
 const block=tail.match(/^(?:\[data-ph="[a-z-]+"\][^\n]*\{[^\n]+\}\n)+/);
 if(!block)throw Error('Missing or malformed bundled glyph rules');
 const before=css.slice(0,start),after=tail.slice(block[0].length);
 if(/^\[data-ph="[a-z-]+"\].*--ph-source:/m.test(before+after))throw Error('Glyph rule outside owned block');
 const names=Object.keys(icons).sort();if(!names.length||names.some(n=>!/^[-a-z]+\.svg$/.test(n)))throw Error('Invalid icon inventory');
 const rules=names.map(file=>`[data-ph="${file.slice(0,-4)}"]${file==='caret-right.svg'?', :where(details > summary)::before':file==='check.svg'?', .combobox__list [role=option][aria-selected=true]::after':''} { --ph-source:url("data:image/svg+xml,${encodeURIComponent(icons[file])}"); }`).join('\n')+'\n';
 let next=before+rules+after;
 for(const [scheme,icon]of Object.entries({system:'desktop',light:'sun',dark:'moon'})){
  if(!icons[icon+'.svg'])throw Error('Missing scheme icon: '+icon);
  const uri='data:image/svg+xml,'+encodeURIComponent(icons[icon+'.svg']);
  next=next.replace(new RegExp('#color-scheme\\[data-scheme='+scheme+'\\] \\{[^\\n]+\\}'),'#color-scheme[data-scheme='+scheme+'] { --icon: url("'+uri+'"); }');
 }
 return next;
}
