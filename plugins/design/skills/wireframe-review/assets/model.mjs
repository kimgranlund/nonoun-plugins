export const IDS = ['A', 'B', 'C'];
const own = (obj, key) => Object.prototype.hasOwnProperty.call(obj, key);
const fail = message => { throw new Error(message); };
export const clone = value => JSON.parse(JSON.stringify(value));
export const now = () => new Date().toISOString();

// Implements exactly the JSON Schema vocabulary used by the bundled schemas.
export function validateShape(value, schema, root = schema, path = '$') {
  if (schema.$ref) return validateShape(value, root.$defs[schema.$ref.split('/').pop()], root, path);
  if (own(schema, 'const') && value !== schema.const) fail(`${path}: wrong schema version/value`);
  if (schema.enum && !schema.enum.includes(value)) fail(`${path}: unsupported value`);
  const type = value === null ? 'null' : Array.isArray(value) ? 'array' : typeof value;
  if (schema.type && ![].concat(schema.type).includes(type)) fail(`${path}: expected ${schema.type}`);
  if (type === 'string') {
    if (schema.minLength !== undefined && value.length < schema.minLength) fail(`${path}: too short`);
    if (schema.maxLength !== undefined && value.length > schema.maxLength) fail(`${path}: too long`);
    if (schema.pattern && !new RegExp(schema.pattern).test(value)) fail(`${path}: invalid format`);
  }
  if (type === 'number' && (!Number.isFinite(value) || value < (schema.minimum ?? -Infinity) || value > (schema.maximum ?? Infinity))) fail(`${path}: out of range`);
  if (type === 'array') {
    if (value.length < (schema.minItems ?? 0) || value.length > (schema.maxItems ?? Infinity)) fail(`${path}: wrong item count`);
    value.forEach((item, i) => validateShape(item, schema.items, root, `${path}[${i}]`));
  }
  if (type === 'object') {
    for (const key of schema.required || []) if (!own(value, key)) fail(`${path}.${key}: required`);
    for (const [key, item] of Object.entries(value)) {
      if (['__proto__', 'prototype', 'constructor'].includes(key)) fail(`${path}: unsafe object key`);
      if (own(schema.properties || {}, key)) validateShape(item, schema.properties[key], root, `${path}.${key}`);
      else if (schema.additionalProperties === false) fail(`${path}.${key}: unexpected field`);
      else if (schema.additionalProperties && typeof schema.additionalProperties === 'object') validateShape(item, schema.additionalProperties, root, `${path}.${key}`);
    }
  }
  return value;
}
export function findUnit(manifest, id) { return manifest.units.find(u => u.id === id); }
export function findVariant(unit, id) { return unit?.variants.find(v => v.id === id); }
// Read real opening-tag attributes; CSS selectors, comments and raw text are not DOM targets.
function reviewAttributes(html) {
  const attrs=[];let i=0;
  while(i<html.length){
    const start=html.indexOf('<',i);if(start<0)break;
    if(html.startsWith('<!--',start)){const end=html.indexOf('-->',start+4);i=end<0?html.length:end+3;continue;}
    const tag=html.slice(start).match(/^<([a-z][a-z0-9:-]*)(?=[\s/>])/i);
    if(!tag){i=start+1;continue;}
    let j=start+tag[0].length;
    while(j<html.length){
      while(/\s/.test(html[j]||'')&&j<html.length)j++;
      if(html[j]==='>'||html[j]==='/'){const end=html.indexOf('>',j);j=end<0?html.length:end+1;break;}
      const keyStart=j;while(j<html.length&&!/[\s=/>]/.test(html[j]))j++;
      const key=html.slice(keyStart,j).toLowerCase();if(!key){j++;continue;}
      while(j<html.length&&/\s/.test(html[j]))j++;
      let value='',quoted=false;
      if(html[j]==='='){
        j++;while(j<html.length&&/\s/.test(html[j]))j++;
        const quote=html[j];quoted=quote==='"'||quote==="'";
        if(quoted){j++;const end=html.indexOf(quote,j);value=html.slice(j,end<0?html.length:end);j=end<0?html.length:end+1;}
        else{const valueStart=j;while(j<html.length&&!/[\s>]/.test(html[j]))j++;value=html.slice(valueStart,j);}
      }
      if(key==='data-review-id')attrs.push({value,quoted});
    }
    i=j;
    if(['style','script','textarea','title'].includes(tag[1].toLowerCase())){
      const close=new RegExp('</'+tag[1]+'\\s*>','ig');close.lastIndex=i;const end=close.exec(html);i=end?close.lastIndex:html.length;
    }
  }
  return attrs;
}
export function elementIds(html) {
  return reviewAttributes(html).filter(a=>a.quoted&&/^[a-z][a-z0-9-]*$/.test(a.value)).map(a=>a.value);
}
export function validateManifest(manifest, schema) {
  validateShape(manifest, schema);
  const seen = new Set();
  for (const unit of manifest.units) {
    if (seen.has(unit.id) || ['constructor', 'prototype'].includes(unit.id)) fail(`Duplicate/reserved unit: ${unit.id}`);
    seen.add(unit.id);
    if (unit.variants.some((v,i)=>v.id!==IDS[i])) fail(`${unit.id}: expected ordered contiguous proposal IDs starting at A`);
    for (const v of unit.variants) {
      if (unit.kind === 'page') {
        if (v.html.trim() || !v.composition.length) fail(`${unit.id}/${v.id}: page needs a composition and empty HTML`);
        const refs = new Set();
        for (const part of v.composition) {
          const child = findUnit(manifest, part.unitId);
          if (!child || child.kind === 'page' || refs.has(child.id)) fail(`${unit.id}/${v.id}: missing, nested, or repeated composition unit`);
          if(!findVariant(child,part.variantId)) fail(`${unit.id}/${v.id}: missing composition proposal`);
          refs.add(child.id);
        }
      } else {
        if (!v.html.trim() || v.composition.length) fail(`${unit.id}/${v.id}: leaf needs HTML and empty composition`);
        const ids = elementIds(v.html);
        if (!ids.length || new Set(ids).size !== ids.length) fail(`${unit.id}/${v.id}: missing/duplicate data-review-id`);
        if (reviewAttributes(v.html).length !== ids.length) fail(`${unit.id}/${v.id}: review IDs must be quoted lowercase semantic slugs`);
        if (new Set(unit.variants.map(x => x.html.trim())).size !== unit.variants.length) fail(`${unit.id}: proposal HTML must differ`);
      }
    }
    if (unit.kind === 'page' && new Set(unit.variants.map(v => JSON.stringify(v.composition))).size !== unit.variants.length) fail(`${unit.id}: page compositions must differ`);
  }
  const interactionIds = new Set();
  for (const interaction of manifest.interactions || []) {
    if (interactionIds.has(interaction.id)) fail(`Duplicate interaction: ${interaction.id}`);
    interactionIds.add(interaction.id);
    const variant = findVariant(findUnit(manifest, interaction.unitId), interaction.variantId);
    if (!variant || !elementIds(variant.html).includes(interaction.elementId)) fail(`Missing interaction target: ${interaction.id}`);
    if (interaction.status !== 'implemented' && !interaction.limitations.length) fail(`Static/unavailable interaction needs limitations: ${interaction.id}`);
  }
  return manifest;
}
export function newChoice(ids=IDS) { return {selectedVariant:null, states:Object.fromEntries(ids.map(id=>[id,'unreviewed'])), note:''}; }
export function reviewContext(manifest) {
  return {...(manifest.intent ? {intent:clone(manifest.intent)} : {}),units:manifest.units.map(u=>({id:u.id,title:u.title,...(u.intent?{intent:clone(u.intent)}:{}),variants:u.variants.map(({id,title,rationale,tradeoff})=>({id,title,rationale,tradeoff}))}))};
}
const canonical=value=>JSON.stringify(value, function(key,item){return item && !Array.isArray(item) && typeof item==='object' ? Object.fromEntries(Object.keys(item).sort().map(k=>[k,item[k]])) : item;});
export function newReview(manifest) {
  return {schemaVersion:'1.1',context:reviewContext(manifest),projectId:manifest.projectId,revision:manifest.revision,reviewer:'',summary:'',updatedAt:now(),choices:Object.fromEntries(manifest.units.map(u=>[u.id,newChoice(u.variants.map(v=>v.id))])),pageOverrides:{},comments:[]};
}
export function selectVariant(review, unitId, variantId) {
  const c=review.choices[unitId];
  if(variantId!==null&&!own(c.states,variantId)) fail('Unknown proposal');
  for (const id of Object.keys(c.states)) if (c.states[id]==='selected') c.states[id]='considered';
  c.selectedVariant=variantId;
  if (variantId) c.states[variantId]='selected';
  review.updatedAt=now();
}
export function setVariantState(review, unitId, variantId, state) {
  if(state==='selected') return selectVariant(review,unitId,variantId);
  const c=review.choices[unitId]; if(!own(c.states,variantId)) fail('Unknown proposal'); c.states[variantId]=state;
  if(c.selectedVariant===variantId) c.selectedVariant=null;
  review.updatedAt=now();
}
export function resolveParts(manifest, review, pageId, pageVariantId, assembled=true) {
  const page=findUnit(manifest,pageId);
  const variant=findVariant(page,pageVariantId || review.choices[pageId]?.selectedVariant || 'A');
  return variant.composition.map(part=>({unitId:part.unitId,variantId:assembled ? (review.pageOverrides[pageId]?.[part.unitId] || review.choices[part.unitId]?.selectedVariant || part.variantId) : part.variantId}));
}
export function validateReview(review, schema, manifest) {
  validateShape(review,schema);
  if(review.schemaVersion==='1.1' && !review.context) fail('Review context is required for version 1.1');
  if(!manifest) return review;
  if(review.context && canonical(review.context)!==canonical(reviewContext(manifest))) fail('Review context does not match this revision');
  if(review.projectId!==manifest.projectId) fail('Different project. Current review was not changed.');
  if(review.revision!==manifest.revision) fail('Different revision. Ask your agent to map the old review explicitly. Current review was not changed.');
  if(Object.keys(review.choices).length!==manifest.units.length) fail('Choice records do not match the manifest');
  for(const unit of manifest.units) {
    const c=review.choices[unit.id]; if(!c) fail(`Missing choice: ${unit.id}`);
    if(Object.keys(c.states).sort().join()!==unit.variants.map(v=>v.id).sort().join()) fail(`${unit.id}: proposal states do not match manifest`);
    const selected=Object.keys(c.states).filter(id=>c.states[id]==='selected');
    if((c.selectedVariant===null && selected.length) || (c.selectedVariant!==null && (selected.length!==1 || selected[0]!==c.selectedVariant))) fail(`${unit.id}: inconsistent selected state`);
  }
  for(const [pageId, overrides] of Object.entries(review.pageOverrides)) {
    const page=findUnit(manifest,pageId); if(page?.kind!=='page') fail(`Invalid override page: ${pageId}`);
    for(const [unitId,variantId] of Object.entries(overrides)) {if(!page.variants.some(v=>v.composition.some(p=>p.unitId===unitId))) fail(`Unit ${unitId} is not on page ${pageId}`);if(!findVariant(findUnit(manifest,unitId),variantId)) fail(`Missing override proposal ${unitId}/${variantId}`);}
  }
  const seen=new Set();
  for(const comment of review.comments) {
    if(seen.has(comment.id)) fail(`Duplicate comment ID: ${comment.id}`); seen.add(comment.id);
    const t=comment.target, unit=findUnit(manifest,t.unitId), page=findUnit(manifest,t.pageId);
    if(t.pageId!==null && page?.kind!=='page') fail(`${comment.id}: unknown page`);
    if(t.scope==='site' && [t.pageId,t.unitId,t.variantId,t.elementId,t.position].some(x=>x!==null)) fail(`${comment.id}: site scope has a target`);
    if(t.scope==='page' && (!page || [t.unitId,t.variantId,t.elementId,t.position].some(x=>x!==null))) fail(`${comment.id}: invalid page note`);
    if(['unit','element','decision'].includes(t.scope)) {
      if(!unit || (t.scope!=='decision' && !t.variantId)) fail(`${comment.id}: unknown unit/variant`);
      if(page && page.id!==unit.id && !page.variants.some(v=>v.composition.some(p=>p.unitId===unit.id))) fail(`${comment.id}: unit is not on this page`);
      if(t.scope==='decision' && [t.variantId,t.elementId,t.position].some(x=>x!==null)) fail(`${comment.id}: invalid decision note`);
      if(t.scope==='element' && (!t.elementId || !elementIds(findVariant(unit,t.variantId).html).includes(t.elementId))) fail(`${comment.id}: unknown element`);
      if(t.scope==='unit' && (t.elementId!==null || t.position!==null)) fail(`${comment.id}: invalid unit note`);
    }
    if(comment.revision!==review.revision && !comment.migration) fail(`${comment.id}: older comment needs an explicit migration record`);
    if(comment.migration?.fromRevision===review.revision) fail(`${comment.id}: migration source must be an earlier revision`);
  }
  return review;
}
