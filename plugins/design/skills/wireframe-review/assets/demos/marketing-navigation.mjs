const h=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const labels={product:'Product','use-cases':'Use cases',pricing:'Pricing',story:'Customer story'};
const route=(id,label=labels[id])=>`<a href="#${id}" data-page-id="${id}" data-review-id="route-${id}">${h(label)}</a>`;
export function marketingNavigation(pattern,brand='Relay'){
 const enterprise=pattern==='enterprise',minimal=pattern==='minimal';
 const identity=`<a class="mh-brand" href="#home" data-page-id="home" data-review-id="brand">${h(brand)}</a>`;
 const primary=enterprise?`<details class="mh-group"><summary data-review-id="product-menu">Product <i class="ph-icon" data-ph="caret-down" aria-hidden="true"></i></summary><div>${route('product')}${route('use-cases')}</div></details><details class="mh-group"><summary data-review-id="resources-menu">Resources <i class="ph-icon" data-ph="caret-down" aria-hidden="true"></i></summary><div>${route('story')}</div></details>${route('pricing')}`:Object.keys(labels).filter(id=>!minimal||id!=='pricing').map(id=>route(id)).join('');
 return `<nav class="marketing-header mh-${pattern}" aria-label="${h(brand)} destinations"><div class="mh-inner">${identity}<details class="mh-destinations"${minimal?'':' open'}><summary data-review-id="menu-trigger">${minimal?'Explore':'Menu'} <i class="ph-icon" data-ph="list" aria-hidden="true"></i></summary><div class="mh-links">${primary}</div></details><div class="mh-actions">${minimal?route('pricing'):''}<a class="button__root" href="#contact" data-page-id="contact" data-review-id="route-contact"><span data-slot="label">Plan a pilot</span><i class="ph-icon" data-ph="arrow-up-right" aria-hidden="true"></i></a></div></div></nav>`;
}
