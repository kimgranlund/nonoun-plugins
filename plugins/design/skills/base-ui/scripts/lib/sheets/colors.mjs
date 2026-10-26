// Pure renderer. Source acquisition, chrome, styles and verification belong to the coordinator.
const COLOR = 'assets/foundation/ultimate-tokens/colors.css';
const INDEX = 'references/style/token-index.json';
const CONTRACT = 'references/style/contract.json';
const WORKFLOW = 'references/workflows/reference-sheets.md';
const PROFILE = 'assets/wireframe.css';
const SEED = 'assets/foundation/ultimate-tokens/source-state.json';
const RECIPE = 'assets/recipes/semantic-colors.html';
const RUNTIME = 'assets/recipes/semantic-colors.js';
const COMPONENTS = 'references/style/components/contract.json';
const FOUNDATION = 'references/style/product-foundation.md';
const id = name => name.replace(/^--/, '');

export function renderColors({tokens, colorKinds, pairs = [], seedState, excerpts = {}, helpers}) {
  const {esc, code, sourceLink, inspector, sourceIdentity} = helpers;
  const gap = message => `<p data-gap>${esc(message)}</p>`;
  const wrap = text => [...String(text)].map(c => esc(c)).join('<wbr>');
  const identity = (path, key) => {
    const value = sourceIdentity(path, key);
    return `<p class="source-identity">${sourceLink(path)}<br>Selection: <code>${wrap(key)}</code><br>SHA-256: <code>${wrap(value?.sha256 || 'unknown')}</code></p>`;
  };
  const source = (path, key, text) => identity(path, key) + (typeof text === 'string' ? code(text) : gap(`Missing source excerpt: ${path}#${key}`));
  const json = path => {
    if (typeof excerpts[path] !== 'string') return null;
    try { return JSON.parse(excerpts[path]); } catch { return null; }
  };
  // Select exact JSON member bytes rather than reserialize authoritative prose.
  const member = (path, key) => {
    const text = excerpts[path];
    if (typeof text !== 'string') return undefined;
    const start = text.indexOf(`"${key}"`);
    if (start < 0) return undefined;
    const open = text.indexOf('{', start); let depth = 0, quoted = false, escaped = false;
    for (let i = open; i < text.length; i++) {
      const c = text[i];
      if (quoted) { if (escaped) escaped = false; else if (c === '\\') escaped = true; else if (c === '"') quoted = false; }
      else if (c === '"') quoted = true;
      else if (c === '{') depth++;
      else if (c === '}' && --depth === 0) return text.slice(start, i + 1);
    }
  };
  const paragraphs = (path, match) => excerpts[path]?.split('\n\n').filter(p => match.test(p)).join('\n\n') || undefined;
  const local = () => source(CONTRACT, 'tokenUsage.color', member(CONTRACT, 'color')) +
    source(WORKFLOW, 'color swatch / primitive classification / popover body rules', paragraphs(WORKFLOW, /Each light\/dark|Use `button.swatch__root|Classify primitive|Content popovers/)) +
    '<p><a href="#colors-shared-context">Shared context</a></p>' + gap('Per-role intent manifest and recorded evaluation context payload unavailable. Names do not establish usage or contrast.');
  const inspect = (title, body) => inspector(title, `<div class="disclosure__body flow__root">${body}</div>`);
  const four = (markup, manifest, context, verification) => inspect('Implementation', code(markup) + identity(PROFILE, 'swatch__root / popover__root / details; native behavior, no initializer') + '<p>Styles: indexed foundations and assets/wireframe.css. Native auto popover; no opener JavaScript.</p>') + inspect('Manifest', manifest) + inspect('Context', context) + inspect('Verification', verification);
  const unverified = gap('Unverified: no artifact-bound browser, keyboard, focus, dismissal, anchor, scrolling, enlarged-text or cross-browser evidence supplied. Build time and discovery findings are not passes.');
  const colors = tokens.filter(t => t.group === 'color');
  const index = json(INDEX)?.groups?.color;
  if (index && (colors.length !== index.names.length || new Set(colors.map(t => t.name)).size !== colors.length || index.names.some(n => !colors.some(t => t.name === n)))) throw Error('Color inventory membership mismatch');
  const authoritative = new Map(); let family = null, kind = 'shared';
  for (const line of (excerpts[COLOR] || '').split('\n')) {
    const section = line.match(/\/\*\s*([^,]+),\s*(flat mode-independent primitives|semantic roles)\s*\*\//);
    if (section) { family = section[1].trim().toLowerCase(); kind = section[2] === 'semantic roles' ? 'semantic' : 'primitive'; }
    const decl = line.match(/^\s*(--md-color-[\w-]+)\s*:/);
    if (decl) authoritative.set(decl[1], {kind, family, line});
  }
  const groups = new Map();
  for (const t of colors) {
    const classified = colorKinds.get(t.name), actual = authoritative.get(t.name);
    if (actual && (!classified || actual.kind !== classified.kind || actual.family !== classified.family)) throw Error('Source classification mismatch: ' + t.name);
    const c = actual || classified;
    // Subdivide only source-classified primitives; equal paints never affect membership.
    const group = !c ? 'Unclassified — source gap' : c.kind === 'shared' ? 'Shared colors' : c.kind === 'semantic' ? `${c.family} semantic` : /-scrim-\d{3}$/.test(t.name) ? `${c.family} scrims` : /-\d{3}$/.test(t.name) ? `${c.family} palette` : `${c.family} primes`;
    if (!groups.has(group)) groups.set(group, []);
    groups.get(group).push(t);
  }
  const cell = t => {
    const tokenId = id(t.name), popId = 'values-' + tokenId, anchor = '--anchor-' + tokenId;
    const light = t.resolved?.light?.oklch, dark = t.resolved?.dark?.oklch;
    const swatch = light && dark ? `<button type="button" class="swatch__root color-values-trigger" popovertarget="${popId}" style="anchor-name:${anchor}" aria-label="Values and sources for ${esc(t.name)}"><span aria-hidden="true" style="background:${esc(light)}"></span><span aria-hidden="true" style="background:${esc(dark)}"></span></button>` : gap('Missing precise resolved OKLCH: ' + t.name);
    const declared = authoritative.get(t.name)?.line;
    const manifest = source(COLOR, t.name, declared) + identity(INDEX, 'groups.color.names[' + t.name + ']') + (!index ? gap('Authoritative membership manifest unavailable.') : '');
    const values = `<dl><dt>Light</dt><dd>${esc(light || 'unknown')}</dd><dt>Dark</dt><dd>${esc(dark || 'unknown')}</dd></dl>`;
    const panel = `<section class="popover__root color-popover" popover="auto" id="${popId}" style="position-anchor:${anchor}" aria-labelledby="title-${tokenId}"><header class="popover__header heading-group__root"><h3 id="title-${tokenId}">${esc(t.name)}</h3><button type="button" popovertarget="${popId}" popovertargetaction="hide">Close</button></header><div class="popover__body flow__root">${values}${four(swatch, manifest, local(), identity(COLOR, t.name) + unverified + (/-scrim|backdrop/.test(t.name) ? gap('Alpha compositing and contrast unmeasured; no compositing background/state supplied.') : ''))}</div></section>`;
    return `<div class="color-entry" id="${tokenId}" data-item="${esc(t.name)}" data-search="${esc(t.name)}"><h3>${esc(t.name.replace('--md-color-', ''))}</h3>${swatch}${panel}</div>`;
  };
  const palettes = [...groups].map(([name, entries]) => `<article class="sheet-item card__root palette-group flow__root" data-palette="${esc(name)}" data-search="${esc(name + ' ' + entries.map(t => t.name).join(' '))}"><header class="heading-group__root"><h2>${esc(name)}</h2><p>${entries.length} declarations · light left / dark right</p></header><div class="palette-grid${name.endsWith('palette') || name.endsWith('scrims') || name.endsWith('primes') ? ' palette-ramp' : ''}">${entries.map(cell).join('')}</div></article>`).join('');
  const allowed = new Map([['Profile surface', ['--ui-surface', '--ui-ink']], ['Profile action', ['--ui-action', '--ui-on-action']]]);
  const examples = pairs.map(p => {
    const def = allowed.get(p.title);
    if (!def || p.bg !== def[0] || p.fg !== def[1] || !['light', 'dark'].includes(p.scheme)) throw Error('Unsupported profile pair');
    const markup = `<div class="pair card__root flow__root" style="color-scheme:${p.scheme};background:var(${p.bg});color:var(${p.fg})"><strong>${esc(p.title)} · ${p.scheme}</strong><span>Surface text</span></div>`;
    return `<section class="section__flow">${markup}${four(markup, source(PROFILE, ':root profile pair aliases', excerpts[PROFILE]?.split('\n').filter(l => l.includes(p.bg + ':') || l.includes(p.fg + ':')).join('\n')), local(), identity(PROFILE, p.bg + '/' + p.fg) + identity(COLOR, 'paired token declarations') + code(JSON.stringify({backgroundToken:p.bg, foregroundToken:p.fg, state:'default', scheme:p.scheme, background:p.background, foreground:p.foreground, ratio:p.ratio ?? 'unmeasured', method:'Coordinator-supplied Chromium-resolved opaque sRGB; WCAG relative luminance'}, null, 2)) + '<p>Scoped supplied pair measurement; excludes other roles, states, alpha compositing and a global accessibility pass.</p>' + unverified)}</section>`;
  }).join('');
  const interfaceMarkup = excerpts[RECIPE];
  if (typeof interfaceMarkup !== 'string' || !interfaceMarkup.trim()) throw Error('Missing maintained semantic color recipe: ' + RECIPE);
  const runtime = excerpts[RUNTIME];
  if (typeof runtime !== 'string' || !runtime.trim()) throw Error('Missing maintained semantic color runtime: ' + RUNTIME);
  const profileRules = excerpts[PROFILE]?.split('\n').filter(l => /--ui-(surface|ink|muted|label|border|focus|action|action-hover|on-action|media-base):|^body |^p |:where\(\.button__root|:where\(input|^label |:focus-visible|^\.field__root|^\.card__root |^\.product__root |^\.actions__root /.test(l)).join('\n');
  if (!profileRules) throw Error('Missing semantic color profile declarations');
  const componentMembers = ['fields', 'actions'].map(name => {
    const text = excerpts[COMPONENTS];
    if (typeof text !== 'string') throw Error('Missing component context');
    // The source object starts immediately before its exact id declaration.
    const start = text.lastIndexOf('{', text.indexOf('"id": "' + name + '"'));
    if (start < 0) throw Error('Missing component context: ' + name);
    let depth = 0, quoted = false, escaped = false;
    for (let i = start; i < text.length; i++) {
      const c = text[i];
      if (quoted) { if (escaped) escaped = false; else if (c === '\\') escaped = true; else if (c === '"') quoted = false; }
      else if (c === '"') quoted = true;
      else if (c === '{') depth++;
      else if (c === '}' && --depth === 0) return source(COMPONENTS, 'families.' + name, text.slice(start, i + 1));
    }
    throw Error('Invalid component context: ' + name);
  }).join('');
  const additional = `<section id="colors-profile-roles" data-unit-id="colors-profile-roles" class="section__flow">${interfaceMarkup}<script src="semantic-colors.js" defer></script>${inspect('Implementation', source(RECIPE, 'entire maintained recipe; exact displayed markup', interfaceMarkup) + source(RUNTIME, 'entire maintained local runtime', runtime) + '<p>Dependencies: indexed foundations, assets/wireframe.css and semantic-colors.js (deferred script). Native probes require no JavaScript. The complete busy fixture and field require JavaScript; without it the busy button stays disabled with a noscript explanation. Work is page-local and timed; no external operation or persistence.</p>' + source(PROFILE, 'applicable profile declarations', profileRules))}${inspect('Manifest', '<p>CSS source declarations and aliases; this is a declaration selection, not a semantic-role contract.</p>' + source(PROFILE, 'applicable profile declarations', profileRules))}${inspect('Context', source(CONTRACT, 'tokenUsage.color', member(CONTRACT, 'color')) + source(CONTRACT, 'families.surface', member(CONTRACT, 'surface')) + source(FOUNDATION, 'product heading context', paragraphs(FOUNDATION, /Cards, dialogs, popovers|Within \x60.surface__inverse\x60/)) + componentMembers)}${inspect('Verification', unverified + gap('Unverified until artifact-bound attachment: surface text, field label/help/border, primary/secondary/ghost rest, hover, pointer-held active, real keyboard focus outline, disabled and disabled-hover stability across schemes and engines; local busy running, guarded reentry and completion with status. Native probes and JS lifecycle are verified separately; disabled alpha/group-opacity paint is observed, exempt from enabled thresholds. Disabled contrast is recorded as exempt. Excludes whole accessibility, installed Safari and generative reliability.'))}</section>`;
  return `<section class="section__flow"><h2>Source palettes and roles</h2><div class="flow__root">${palettes}</div></section><section class="section__flow"><h2>Seed inputs</h2>${inspect('Seed values and provenance', source(SEED, 'entire source-state.json', excerpts[SEED]) + (seedState ? code(JSON.stringify(seedState, null, 2)) : gap('Seed state unavailable.')))}</section><section class="section__flow" id="colors-shared-context"><h2>Shared color context</h2>${inspect('Context', source(WORKFLOW, 'source-derived sheet authority and color rules', excerpts[WORKFLOW]) + source(CONTRACT, 'tokenUsage.color', member(CONTRACT, 'color')))}${!index ? gap('Membership manifest unavailable; completeness is unknown.') : `<p>${colors.length} source color tokens.</p>`}</section><section class="section__flow"><h2>Profile pairings</h2><p>Only the two supplied source-defined pair definitions are measured. Resolved swatches preserve supplied OKLCH and alpha.</p>${examples || gap('Profile pair measurement evidence unavailable.')}${additional}</section>`;
}
