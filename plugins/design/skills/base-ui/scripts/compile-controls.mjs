import {normalizeClassNames} from './class-names.mjs';
// Build-time markup compilation. No browser scanner or runtime decoration.
import {SELECT_INDICATOR} from '../assets/control-markup.mjs';
import {existsSync,readFileSync} from 'node:fs';
const paletteContract=JSON.parse(readFileSync(new URL('../references/semantic-palettes.json',import.meta.url)));
const markupFamilies=JSON.parse(readFileSync(new URL('../references/style/components/contract.json',import.meta.url))).families.filter(f=>f.markupRule);
function checkMarkup(item){
 if(!item?.rule)return;
 const {family,rule}=item;
 if(!item.classes.includes(rule.rootClass)||item.children.length!==rule.children.length||(!rule.allowDirectText&&item.directText)||rule.children.some((expected,i)=>{const child=item.children[i];return child?.tag!==expected.tag||(expected.class&&!child.classes.includes(expected.class));}))
  throw Error('Component anatomy mismatch: '+family+'. Expected '+rule.tag+'.'+rule.rootClass+' > '+rule.children.map(c=>c.tag+(c.class?'.'+c.class:'')).join(' + ')+'. Retrieve: component-context.mjs '+family+' --record-only.');
}
import {fileURLToPath} from 'node:url';
const iconRoot=new URL('../assets/icons/',import.meta.url);
const attrs=tag=>Object.fromEntries([...tag.matchAll(/([\w:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/g)].map(m=>[m[1].toLowerCase(),m[2]??m[3]??m[4]]));
const voids=new Set('area base br col embed hr img input link meta param source track wbr'.split(' '));
export function compileControls(html){
 const tokens=html.match(/<!--[\s\S]*?-->|<(script|style|textarea)\b(?:[^>"']|"[^"]*"|'[^']*')*>[\s\S]*?<\/\1\s*>|<(?:[^>"']|"[^"]*"|'[^']*')*>|[^<]+|</gi)||[];
 const stack=[];let out='';
 for(let token of tokens){
  if(!/^<\/?[a-z]/i.test(token)||/^<(script|style|textarea)\b/i.test(token)){if(stack.at(-1)?.rule&&!/^<!--/.test(token)&&token.trim())stack.at(-1).directText=true;out+=token;continue;}
  const close=/^<\//.test(token),tag=token.match(/^<\/?([\w-]+)/)[1].toLowerCase();
  if(close){const index=stack.findLastIndex(item=>item.tag===tag);const item=index<0?null:stack[index];if(index>=0){for(const closed of stack.slice(index))checkMarkup(closed);stack.splice(index);}out+=token;if(tag==='select'&&item?.wrapped)out+=SELECT_INDICATOR+'</span>';continue;}
  token=token.replace(/\sclass\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i,(_,double,single,bare)=>' class="'+normalizeClassNames(double??single??bare)+'"');
  const a=attrs(token),classes=(a.class||'').split(/\s+/);
  if(a['data-intent']!==undefined){
   const component=paletteContract.components.find(c=>classes.includes(c.class));
   if(!component||!Object.hasOwn(paletteContract.intents,a['data-intent'])||!component.appearances.includes(a['data-appearance']??component.defaultAppearance)||classes.includes('secondary'))throw Error('Unsupported semantic palette component/intent/appearance; retrieve references/semantic-palettes.json');
  }
  if(stack.at(-1)?.rule)stack.at(-1).children.push({tag,classes});
  const family=markupFamilies.find(f=>f.markupRule.tag===tag&&!stack.some(p=>p.classes.includes(f.markupRule.exemptAncestorClass)));
  const validation=family?{family:family.id,rule:family.markupRule,children:[],directText:false}:{};
  for(const icon of [a['data-ph'],a['data-select-icon']].filter(Boolean))if(!/^[a-z][a-z0-9-]*$/.test(icon)||!existsSync(fileURLToPath(new URL(icon+'.svg',iconRoot))))throw Error('Unbundled Phosphor icon: '+icon);
  if(a['data-select-icon']==='caret-down')throw Error('data-select-icon is a leading semantic icon; omit caret-down because compileControls owns the trailing indicator');
  if(a['data-leading-icon'])throw Error('Removed runtime data-leading-icon; use build-time data-select-icon or authored icon anatomy');
  if((a.class||'').split(/\s+/).some(c=>['menu__root','menu__content','menu__indicator'].includes(c)))throw Error('Removed legacy menu markup; use native-patterns recipe');
  const wrapped=tag==='select'&&!stack.at(-1)?.classes?.includes('select__root');
  if(wrapped){const icon=a['data-select-icon'],prefix=a['data-prefix'];out+='<span class="select__root'+(icon?' has-leading-icon':'')+(prefix?' has-prefix':'')+'">';if(icon)out+=`<span data-slot="icon" aria-hidden="true"><i class="ph-icon" data-ph="${icon}" aria-hidden="true"></i></span>`;if(prefix)out+='<span class="select__prefix" aria-hidden="true">'+prefix.replace(/</g,'&lt;').replace(/>/g,'&gt;')+'</span>';}
  token=token.replace(/\sdata-select-icon\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)/gi,'');out+=token;
  if(!voids.has(tag)&&!token.endsWith('/>'))stack.push({tag,wrapped,classes,...validation});
 }
 if(stack.some(item=>item.rule))throw Error('Unclosed component markup: '+stack.filter(item=>item.rule).map(item=>item.family).join(', '));
 return out;
}
