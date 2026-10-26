// Lexical membership only; not a CSS parser, cascade or semantic-role validator.
export function authoredStyles(html){
 const markup=html.replace(/<!--[\s\S]*?-->/g,'').replace(/<(pre|code|script)\b[^>]*>[\s\S]*?<\/\1\s*>/gi,'');
 return [...[...markup.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style\s*>/gi)].map(m=>m[1]),
  ...[...markup.replace(/<style\b[^>]*>[\s\S]*?<\/style\s*>/gi,'').matchAll(/\bstyle\s*=\s*(["'])([\s\S]*?)\1/gi)].map(m=>m[2])];
}
export function inspectStyles(styles,index){
 const text=styles.join('\n').replace(/\/\*[\s\S]*?\*\//g,'');
 const declared=new Set([...Object.values(index.groups).flatMap(g=>g.names),...[...text.matchAll(/(--[\w-]+)\s*:/g)].map(m=>m[1])]);
 return [...new Set([...text.matchAll(/var\(\s*(--[\w-]+)(?=\s*[,\)])/g)].map(m=>m[1]).filter(name=>!declared.has(name)))].sort();
}
