/** Pure token relationship renderer. excerpts contains full source strings by path. */
export function renderTokens({ tokens, index, contract, excerpts, helpers }) {
  const { esc, code, sourceLink, inspector, tokenCard, sourceIdentity } = helpers;
  const paths = {
    type: 'assets/foundation/ultimate-tokens/typography.css',
    geometry: 'assets/foundation/maison/geometry.css',
    contract: 'references/style/contract.json',
    context: 'references/style/product-foundation.md',
    profile: 'assets/wireframe.css',
    spacing: 'assets/recipes/spacing.html',
    choices: 'references/style/components/contract.json'
  };
  const gap = text => `<p data-status="gap">Gap: ${esc(text)}</p>`;
  // Break opportunities preserve textContent, link targets and full source identity.
  const breakText = text => Array.from(String(text), char => esc(char)).join('<wbr>');
  const breakLink = html => html.replace(/>([^<]+)</g, (_, text) =>
    `>${(text.match(/&(?:#\d+|#x[\da-f]+|[a-z]+);|./giu) ?? []).join('<wbr>')}<`);
  function source(path, start = 1, end) {
    const text = excerpts[path];
    if (typeof text !== 'string' || !text.trim()) return gap(`Missing authoritative excerpt: ${path}`);
    const lines = text.trimEnd().split('\n');
    const last = Math.min(end ?? lines.length, lines.length);
    const selectionKey = `lines:${start}-${last}`;
    const identity = sourceIdentity(path, selectionKey);
    if (!identity || identity.path !== path || identity.selectionKey !== selectionKey || !identity.sha256) {
      return gap(`Missing or misrouted source identity: ${path} ${selectionKey}`);
    }
    return `<div class="flow__root" data-source-path="${esc(path)}" data-selection-key="${esc(selectionKey)}"><p>${breakLink(sourceLink(path))} · SHA-256 ${breakText(identity.sha256)} · ${breakText(selectionKey)}</p>${code(lines.slice(start - 1, last).join('\n'))}</div>`;
  }
  function choicesContext(){const record=JSON.parse(excerpts[paths.choices]??'null')?.families?.find(f=>f.id==='choices');if(!record?.geometry)return gap('Missing authoritative choices geometry');const identity=sourceIdentity(paths.choices,'family:choices.geometry');return '<p>Authoritative choice mark/body relationship: '+sourceLink(paths.choices)+'</p>'+code(JSON.stringify({source:identity,geometry:record.geometry},null,2));}
  function localContext(id) {
    const rules = {
      'tokens-typography-product': [[paths.context, 46, 46], [paths.context, 48, 50]],
      'tokens-typography-content': [[paths.context, 48, 48], [paths.context, 46, 46], [paths.context, 50, 50]],
      'tokens-geometry': [[paths.context, 23, 25], [paths.context, 50, 50]]
    };
    return '<p>Applicable authored rules, followed by inherited context and dependencies. No recorded evaluation context payload was supplied.</p>' +
      rules[id].map(([path, start, end]) => source(path, start, end)).join('') + (id==='tokens-geometry'?choicesContext():'') +
      '<p>Inherited foundation styles and default geometry context (authoritative contract excerpt):</p>' + source(paths.contract, 3, 17) +
      '<p><a href="#tokens-shared-context">Supplemental shared source guidance</a>.</p>';
  }
  function unit(id, title, specimen, manifest, notes) {
    return `<section id="${id}" class="section__flow" data-token-unit="${id}"><header class="heading-group__root"><h2>${title}</h2><p>${notes}</p></header><div class="flow__root">${specimen}${inspector('Implementation', code(specimen) + `<p>Dependencies: shared foundation typography, geometry, layout and wireframe profile CSS; shared inspector/Phosphor caret styling. Native form controls need no initializer. No application actions are implemented.</p>` + source(paths.profile, 1, 170))}${inspector('Manifest', manifest)}${inspector('Context', localContext(id))}${inspector('Verification', `<p data-status="unverified">Unverified. Declared relationships and illustrative specimens only. No compatible report, browser/version, viewport, scheme, density, loaded-font observation or measured layout evidence is supplied.</p><p>Check narrow and wide widths, keyboard focus, both schemes and inherited densities. At 200% zoom and text enlargement, inspect wrapping, reachable controls and clipping. Record actual boxes separately from resolved custom properties and declared expressions.</p>`)}</div></section>`;
  }
  const field = prefix => `<div class="field__root"><label class="field__label" for="${prefix}-name">Collection title with a deliberately long field label for narrow wrapping</label><input id="${prefix}-name" value="A long collection title" aria-describedby="${prefix}-help"><p class="field__help" id="${prefix}-help">Help text explains the field without replacing its label.</p></div>`;
  const typeSpecimen = context => `<div data-type-context="${context}" class="flow__root" data-tier="product" data-scale="md" data-size="md"><h3>${context === 'product' ? 'Product UI' : 'Editorial content'} heading</h3><p>A paragraph with enough words to reveal wrapping when the review surface narrows. Semantic h3 rank stays the same across contexts.</p>${field(`type-${context}`)}<button type="button">Control label with a long description that may wrap</button><p class="type-tiny-md">Caption · illustrative tiny role; semantic caption placement has no exact slot manifest.</p>${context === 'content' ? '<div class="card__root flow__root" data-type-context="product"><h4>Nested product heading</h4><p>A product card resets editorial heading context.</p></div>' : '<section class="flow__root" data-type-context="content"><h4>Nested editorial heading</h4><p>An explicit content boundary restores editorial scale.</p></section>'}</div>`;
  const geometrySpecimen = `<section class="product__root card__root flow__root" data-spacing="loose" data-tier="product" data-scale="md" data-size="md" data-radius="default" aria-labelledby="geometry-title"><h3 id="geometry-title">Local product / md / md context</h3><div class="flow__root">${field('geometry')}<fieldset class="field-group__root" data-surface="plain"><legend>Related choices</legend><div class="options__root"><label class="choice__root"><input class="checkbox__control" type="checkbox"><span class="choice__body">A long choice label demonstrates the fixed mark slot beside a wrapping text body.</span></label></div></fieldset></div><div class="flow__root" data-size="sm"><h4>Nested small control density</h4>${field('geometry-small')}<button type="button">Small local control</button></div><footer class="stack__root" data-spacing="tight"><p>Card margin = 3u; major groups = 3u; fields = 2u; related label/control/help = 1u.</p><p>Choice mark/body gap uses one full gutter. Button icon/label gaps use the same full gutter.</p></footer></section>`;
  const nonColor = tokens.filter(t => !['color', 'colors'].includes(t.group));
  const typeDeclarations = source(paths.type);
  const geometryDeclarations = source(paths.geometry) + source(paths.contract);
  const other = ['motion', 'elevation', 'layering', 'responsive'].map(domain => {
    const declared = nonColor.filter(t => t.group === domain && t.declarations?.length);
    return `<section id="tokens-${domain}" class="section__flow"><h2>${domain}</h2>${declared.length ? declared.map(tokenCard).join('') + gap('Declaration-only coverage; no domain behavior contract or compatible verification supplied.') : gap(`No authoritative ${domain} domain declarations/contract supplied. Profile responsive CSS does not establish a complete responsive token system.`)}</section>`;
  }).join('');
  return `<div class="page__flow"><header class="heading-group__root"><h1>Design tokens</h1><p>Typography and geometry relationships. Declared expressions, resolved properties and observed layout are separate evidence.</p></header><section id="tokens-shared-context" class="section__flow"><h2>Shared source context</h2>${inspector('Context', source(paths.context, 1, 50) + '<p>Current guidance uses 4u/3u/2u/1u. Discovery identifies earlier one/two-margin report prose as superseded; historical reports are not current browser passes.</p>')}</section>${unit('tokens-typography-product', 'Product typography', typeSpecimen('product'), typeDeclarations + source(paths.contract), 'Declared stacks and size/weight/line-height/tracking/casing are preserved in the source inspector. Font loading and resolved font metrics are unknown.')}${unit('tokens-typography-content', 'Content typography', typeSpecimen('content'), gap('No exact manifest maps every heading/body/label/help/control/caption slot; the specimen is illustrative.') + typeDeclarations, 'Inter Tight, Inter and JetBrains Mono declarations include generic fallbacks; declaration does not prove loading. Compare semantic ranks independently from visual scale.')}${unit('tokens-geometry', 'Geometry and rhythm', geometrySpecimen, geometryDeclarations, 'u = local --g-margin. Product/md/md declarations resolve to 9px margin and a 36px minimum control frame; 4u/3u/2u is the 36/27/18 reference, not a fixed override. Density, text/icon slots, borders and radii follow local source roles; actual edge/gap/wrapping measurements remain unverified.')}${other}<section id="token-declaration-index" class="section__flow"><h2>Complete non-color declaration index</h2><p>Subordinate declaration reference. Search requires the coordinator’s shared filtering runtime; without JavaScript all entries remain available. Resolved and scoped defaults are coordinator observations, not layout measurements.</p><label for="token-search">Search declarations<input id="token-search" type="search" data-token-search aria-controls="token-list"></label><div id="token-list" class="flow__root" data-token-list>${nonColor.map(tokenCard).join('')}</div>${!index?.groups ? gap('Token index groups unavailable; membership cannot be checked here.') : ''}${!contract?.defaults ? gap('Style contract defaults unavailable.') : ''}</section></div>`;
}
