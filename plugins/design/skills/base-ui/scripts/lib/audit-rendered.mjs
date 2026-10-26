// Serializable browser audit. A temporary invisible length probe is removed immediately; no persistent edits. Pass installed contract metadata.
export function auditRendered({families, retrieved = []}) {
  const issues = [], detected = new Set(), states = [];
  const identify = e => e.id ? `#${e.id}` : `${e.localName}${[...e.classList].map(x => '.' + x).join('')}`;
  const add = (code, e, message) => issues.push({code, element: identify(e), message});
  for (const family of families) {
    if ((family.classes || []).some(c => document.getElementsByClassName(c).length)) detected.add(family.id);
  }
  if (document.querySelector('button')) detected.add('actions');
  if (document.querySelector('input:not([type=checkbox]):not([type=radio]),textarea')) detected.add('fields');
  // Consume the same authoritative anatomy rule as the markup compiler.
  const rule = families.find(f => f.id === 'disclosure').markupRule;
  const disclosures = [...document.querySelectorAll(rule.tag)].filter(e => !e.closest('.' + rule.exemptAncestorClass));
  if (disclosures.length) detected.add('disclosure');
  for (const id of detected) if (!retrieved.includes(id)) issues.push({code:'CONTRACT_NOT_DECLARED', family:id,
    message:`Retrieve component-context.mjs ${id} --record-only (after --shared); rerun with the IDs actually read.`});
  for(const e of document.querySelectorAll('[data-intent]')) {
    const contract=families.map(f=>f.semanticPalettes).find(p=>p?.components.some(c=>e.classList.contains(c.class)));
    const component=contract?.components.find(c=>e.classList.contains(c.class));
    if(!contract||!contract.intents.includes(e.dataset.intent)||!component.appearances.includes(e.dataset.appearance??component.defaultAppearance)||e.classList.contains('secondary'))add('SEMANTIC_VARIANT',e,'Unsupported component/intent/appearance; retrieve semantic palette contract.');
  }
  const ghost=families.find(f=>f.id==='actions')?.implementation?.neutralGhost;
  if(ghost)for(const e of document.querySelectorAll('.button__root.'+ghost.unsupportedClass))if(!e.hasAttribute('data-appearance'))add('ACTION_APPEARANCE',e,ghost.rule);
  const visible = e => e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
  for(const row of document.querySelectorAll('.action-status__root')) {
    if(!visible(row))continue;
    const style=getComputedStyle(row);
    if(style.display!=='flex'||!style.alignItems.includes('baseline'))add('ACTION_STATUS_ALIGNMENT',row,'Action/status composition requires flex first-baseline alignment; inspect actual wrapped text separately.');
  }
  for(const stack of document.querySelectorAll('.disclosure-stack__root')) {
    const children=[...stack.children].filter(e=>e.classList.contains('disclosure__root'));
    for(const [index,e] of children.entries()) {
      if(!visible(e))continue;
      const st=getComputedStyle(e),summary=e.querySelector(':scope > summary');
      if(parseFloat(st.borderBottomWidth)>0 || (index===0&&parseFloat(st.borderTopWidth)>0) || (summary&&getComputedStyle(summary).boxShadow!=='none'))add('DISCLOSURE_STACK_BOUNDARY',e,'Sibling disclosure stack assigns one separator to the following sibling, with no bottom frame or open-summary divider.');
    }
  }
  for(const inner of document.querySelectorAll('.disclosure__root[data-nested-boundary=quiet] .disclosure__root, .reading-flow__root .disclosure__root:not([data-nested-boundary=framed]) .disclosure__root')) {
    if(!visible(inner))continue;
    const style=getComputedStyle(inner),summary=inner.querySelector(':scope > summary');
    const painted=['Top','Right','Bottom','Left'].some(side=>parseFloat(style['border'+side+'Width'])>0 && style['border'+side+'Style']!=='none' && !['transparent','rgba(0, 0, 0, 0)'].includes(style['border'+side+'Color']));
    if(painted||(summary&&getComputedStyle(summary).boxShadow!=='none'))add('NESTED_BOUNDARY_OWNER',inner,'Quiet nested disclosures must not reintroduce frame or summary-divider paint. Outer disclosure owns the boundary.');
  }
  for(const select of document.querySelectorAll('select:not([multiple])')) {
    if(Number(select.getAttribute('size')||1)>1)continue;
    const wrapper=select.parentElement;
    if(!wrapper?.classList.contains('select__root') || wrapper.querySelectorAll(':scope > select').length!==1 || wrapper.querySelectorAll(':scope > [data-slot="indicator"][aria-hidden="true"]').length!==1)
      add('SELECT_ANATOMY',select,'Single-value native select needs one select__root wrapper and one decorative indicator; dynamic markup must consume native-select construction.');
    const indicator=wrapper?.querySelector(':scope > [data-slot="indicator"]');
    if(indicator&&visible(select)&&visible(indicator)){
      const a=select.getBoundingClientRect(),b=indicator.getBoundingClientRect();
      if(b.left<a.left-.75||b.right>a.right+.75||b.top<a.top-.75||b.bottom>a.bottom+.75)
        add('SELECT_INDICATOR_BOUNDS',select,'Native select indicator must stay inside the visible select frame; keep the native control and wrapper widths aligned.');
    }
  }
  for(const group of document.querySelectorAll('.field-action__root')) {
    const field=group.querySelector(':scope > .field__root'),button=group.querySelector(':scope > button'),control=field?.querySelector('input,select,textarea');
    if(!field||!button||!control||group.children.length!==2){add('FIELD_ACTION_ANATOMY',group,'Use one labelled field and one related button; place other commands in a separate action group.');continue;}
    if(!visible(control)||!visible(button))continue;
    const a=control.getBoundingClientRect(),b=button.getBoundingClientRect();
    if(Math.min(a.right,b.right)-Math.max(a.left,b.left)<=0 && Math.abs(a.bottom-b.bottom)>.75)
      add('FIELD_ACTION_ALIGNMENT',group,'Related field and action on the same row must share their control bottom edge.');
  }
  for(const rail of document.querySelectorAll('.control-rail__root')) {
    const button=rail.querySelector(':scope > .actions__root > .button__root.secondary'),summary=rail.querySelector(':scope > .disclosure__root > summary');
    if(!button||!summary||!visible(button)||!visible(summary))continue;
    const textEdge=el=>{const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let n;while(n=walker.nextNode()){if(!n.textContent.trim())continue;const r=document.createRange();r.selectNodeContents(n);const b=r.getBoundingClientRect();return getComputedStyle(el).direction==='rtl'?b.right:b.left;}return null;};
    const a=textEdge(button),b=textEdge(summary);
    if(a!==null&&b!==null&&Math.abs(a-b)>.75)add('CONTROL_TEXT_RAIL',rail,'Related command/disclosure labels must share the actual text start, including the narrow reading-flow treatment.');
  }
  const localUnit = el => {
    const probe=document.createElement('span');
    probe.style.cssText='position:absolute;visibility:hidden;display:block;width:var(--g-margin);min-width:0;max-width:none;height:0;padding:0;border:0;margin:0';
    el.append(probe);const unit=probe.getBoundingClientRect().width;probe.remove();return unit;
  };
  const contentWidth = e => {const s=getComputedStyle(e);return e.clientWidth-parseFloat(s.paddingLeft)-parseFloat(s.paddingRight);};
  const flatReading = e => {
    const owner=e.parentElement?.closest('.reading-flow__root');
    return owner && contentWidth(owner)<=32*parseFloat(getComputedStyle(document.documentElement).fontSize)+.1;
  };
  const checkGaps = parent => {
    const children = [...parent.children].filter(visible);
    for (let i=1;i<children.length;i++) {
      const a=children[i-1].getBoundingClientRect(), b=children[i].getBoundingClientRect();
      // Only vertically stacked siblings; horizontal compositions need their own check.
      if (b.top >= a.top && b.left < a.right && b.right > a.left && b.top-a.bottom < .5)
        add('CONTENT_GAP',parent,'Stacked content touches or overlaps. Use a maintained flow owner or inspect intentional spacing.');
    }
  };
  for (const d of disclosures) {
    const children=[...d.children], summary=children[0], body=children[1];
    const anatomy=d.classList.contains(rule.rootClass) && children.length===rule.children.length && rule.children.every((expected,i)=>children[i]?.localName===expected.tag && (!expected.class||children[i].classList.contains(expected.class))) &&
      (rule.allowDirectText || ![...d.childNodes].some(n=>n.nodeType===3 && n.textContent.trim()));
    states.push({element:identify(d), open:d.open, visible:visible(d)});
    if (!anatomy) {add('DISCLOSURE_ANATOMY',d,'Use details.disclosure__root > summary + div.disclosure__body; place all expanded content inside the body.');continue;}
    if (!d.open || !visible(body)) continue;
    const style=getComputedStyle(body);
    // Resolve the token independently: equal-but-wrong summary/body padding must not validate itself.
    const unit=localUnit(body);
    const pads=['paddingTop','paddingRight','paddingBottom','paddingLeft'].map(k=>parseFloat(style[k]));
    if (!(unit>0) || pads.some((p,i)=>!Number.isFinite(p)||Math.abs(p-((i===1||i===3)&&flatReading(d)?0:2*unit))>.75))
      add('DISCLOSURE_MARGIN',body,'Expanded body must retain the contract margin (2 × local geometry unit).');
    if(Math.abs(parseFloat(style.paddingInlineStart)-parseFloat(getComputedStyle(summary).paddingInlineStart))>.75)add('DISCLOSURE_ALIGNMENT',body,'Summary and body text must share the 2u inline margin.');
    checkGaps(body);
    const bounds=body.getBoundingClientRect();
    for(const child of [...body.children].filter(visible)) {
      const r=child.getBoundingClientRect();
      if(r.left<bounds.left-.75 || r.right>bounds.right+.75) add('CONTENT_OVERFLOW',child,'Expanded content exceeds its body width.');
    }
  }
  for(const el of document.querySelectorAll('.card__root,.notice__root,.page__flow')) {
    if(!visible(el))continue;
    const unit=localUnit(el);
    const style=getComputedStyle(el);
    const factor=el.classList.contains('notice__root')?2:el.classList.contains('card__root')?3:null;
    if(factor&&['paddingTop','paddingRight','paddingBottom','paddingLeft'].some(k=>Math.abs(parseFloat(style[k])-((k==='paddingLeft'||k==='paddingRight')&&flatReading(el)?0:factor*unit-parseFloat(style[k.replace('padding','border')+'Width'])))>.75))add('CONTAINER_MARGIN',el,'Default card margin is 3u; notice margin is 2u. Verify intentional custom geometry separately.');
    if(el.classList.contains('page__flow')&&Math.abs(parseFloat(style.rowGap)-3*unit)>.75)add('PAGE_GUTTER',el,'Page sections use a 3u gutter.');
  }
  for(const e of document.querySelectorAll('.interval__option')) {
    if(!visible(e))continue;
    const owner=e.closest('.intervals__root'),track=e.querySelector('.interval__track'),fill=e.querySelector('.interval__fill');
    const lo=Number(owner?.dataset.domainStart),hi=Number(owner?.dataset.domainEnd),start=Number(e.dataset.intervalStart),end=Number(e.dataset.intervalEnd);
    if(!track||!fill||![lo,hi,start,end].every(Number.isFinite)||hi<=lo||end<=start||start<lo||end>hi){add('INTERVAL_DOMAIN',e,'Require finite ordered endpoints inside the declared domain.');continue;}
    const t=track.getBoundingClientRect(),f=fill.getBoundingClientRect(),offset=getComputedStyle(e).direction==='rtl'?t.right-f.right:f.left-t.left;
    if(t.width<=0||Math.abs(f.width-t.width*(end-start)/(hi-lo))>1||Math.abs(offset-t.width*(start-lo)/(hi-lo))>1)add('INTERVAL_GEOMETRY',e,'Track span/offset must encode the declared interval independently of label/control width.');
  }
  for(const cell of document.querySelectorAll('.table__root [data-selection]')) {
    if(!visible(cell))continue;
    const bounds=cell.getBoundingClientRect(),walker=document.createTreeWalker(cell,NodeFilter.SHOW_TEXT);let node;
    while(node=walker.nextNode()){
      if(!node.textContent.trim()||node.parentElement.closest('.sr-only,[hidden]')||!visible(node.parentElement))continue;
      const range=document.createRange();range.selectNodeContents(node);
      if([...range.getClientRects()].some(r=>r.right>bounds.right+.75||r.left<bounds.left-.75||r.bottom>bounds.bottom+.75)){
        add('SELECTION_COLUMN_OVERFLOW',cell,'Compact selection cells require an accessible name without overflowing visible label text; use aria-label or sr-only per collections.selectionColumn.');break;
      }
    }
  }
  for(const li of document.querySelectorAll('li')) {
    if(!li.querySelector('details') || !visible(li)) continue;
    const owner=li.children.length===1?li.firstElementChild:li;
    // Summary and body share a border; body content gaps are audited above.
    if(!owner.matches("details.disclosure__root"))checkGaps(owner);
  }
  // A minimum reading measure is an outcome check, independent of margin correctness.
  // 24ch is a kit floor for prose, not a universal readability/accessibility claim.
  for(const e of document.querySelectorAll('.card__root p,.disclosure__body p,[data-prose]')) {
    if(!visible(e)||e.textContent.trim().length<80)continue;
    const probe=document.createElement('span');probe.style.cssText='position:absolute;visibility:hidden;display:block;width:24ch;height:0;padding:0;border:0';e.append(probe);
    const floor=probe.getBoundingClientRect().width;probe.remove();
    let outerCard=null;for(let parent=e.parentElement;parent&&!parent.classList.contains('page__root');parent=parent.parentElement)if(parent.classList.contains('card__root'))outerCard=parent;
    const owner=e.closest('.reading-flow__root')||outerCard||e.closest('.page__root')||document.documentElement;
    const minimum=Math.min(floor,contentWidth(owner));
    if(contentWidth(e)+.75<minimum)add('PROSE_MEASURE',e,`Long text has ${contentWidth(e).toFixed(1)}px; requires at least ${minimum.toFixed(1)}px. Use one outer reading-flow__root region or recompose narrow columns.`);
  }
  // Fixed-width selects budget every choice. Content-sized selects budget the observed selection;
  // callers must visit other selections because each has a different rendered width.
  const measure=document.createElement('canvas').getContext('2d');
  for(const select of document.querySelectorAll('select:not([multiple])')){
    if(!visible(select)||select.size>1)continue;
    const st=getComputedStyle(select);measure.font=st.font;
    const available=select.clientWidth-parseFloat(st.paddingLeft)-parseFloat(st.paddingRight);
    const spacing=parseFloat(st.letterSpacing)||0;
    for(const option of (st.fieldSizing==='content'?select.selectedOptions:select.options)){if(option.hidden)continue;const label=option.label;const width=measure.measureText(label).width+Math.max(0,[...label].length-1)*spacing;
      if(width>available+1){add('SELECT_TEXT_FIT',select,`Option "${label}" needs ${width.toFixed(1)}px; available ${available.toFixed(1)}px. Use distinct concise labels with wrapping full detail, or a wrapping chooser.`);break;}
    }
  }
  return {detectedFamilies:[...detected].sort(), issues, disclosureStates:states,
    scope:'Observed DOM only. Closed disclosure anatomy is checked; geometry requires open, visible bodies. Retrieval IDs are author declarations, not proof of reads. Other components and unvisited application states remain unverified.'};
}
