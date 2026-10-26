import fs from 'node:fs';
const d=JSON.parse(fs.readFileSync(new URL('../references/review/concepts.json',import.meta.url)));const id=process.argv[2];
if(!id||id==='--list')console.log(d.concepts.map(c=>c.id).join('\n'));else{const c=d.concepts.find(c=>c.id===id);if(!c)throw Error('Unknown design concept: '+id);console.log(JSON.stringify(c,null,2));}
