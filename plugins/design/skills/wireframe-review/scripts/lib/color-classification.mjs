// Classification follows the installed export's explicit section labels.
// Equal light/dark values do not make a semantic role a primitive.
export function classifyExportColors(css) {
 const entries=new Map();let family=null,kind='shared';
 for(const line of css.split('\n')) {
  const section=line.match(/\/\*\s*([^,]+),\s*(flat mode-independent primitives|semantic roles)\s*\*\//);
  if(section){family=section[1].trim().toLowerCase();kind=section[2]==='semantic roles'?'semantic':'primitive';continue;}
  const declaration=line.match(/^\s*(--md-color-[\w-]+)\s*:/);
  if(!declaration)continue;
  const name=declaration[1];
  entries.set(name,{kind,family});
 }
 return entries;
}
