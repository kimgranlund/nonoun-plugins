// The recipe lint: checks every kit/components/<id>/<id>.css against docs/specs/css-contract.md.
//
//   node scripts/lint-recipes.mjs    exit 1 if a recipe breaks a rule
//
// Each problem names the rule it breaks (C1, C5, D59 ...). kit/components/recipes.test.js runs this on the
// real recipes and, as the negative control, on copies with one rule broken at a time.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LAYERS = '@layer reset, base, tokens, recipes, utilities;';
const PREFIX = 'ui';
const WORDS = ['face', 'ink', 'line', 'height', 'inset', 'gap', 'radius'];
/** The order of condition rules in a recipe (D55). hidden and ready are not ordered. */
const ORDER = ['hover', 'focus-visible', 'active', 'checked', 'indeterminate', 'pressed', 'selected', 'current', 'expanded', 'open', 'invalid', 'loading', 'read-only', 'disabled'];
/** The states whose token falls back to the base public token (D54, C7). The token of any other state does not (C30). */
const FOLLOWS_BASE = ['hover', 'active'];
/** A property that paints. A recipe that sets one needs a forced-colours block (C19). */
const PAINTS = /^(background|color$|box-shadow|border(?!-radius)|outline|fill$|stroke)/;
/** What a hover rule may set (D63). An outline takes no room, so the forced-colours hover ring (D124) is paint too. */
const PAINT_ONLY = ['background-color', 'color', 'box-shadow', 'border-color', 'outline-color', 'outline', 'outline-width', 'outline-style', 'outline-offset', 'fill', 'stroke', 'opacity'];
const SYSTEM_COLOURS = ['Canvas', 'CanvasText', 'ButtonFace', 'ButtonText', 'ButtonBorder', 'Highlight', 'HighlightText', 'GrayText', 'Mark', 'MarkText', 'LinkText', 'VisitedText', 'Field', 'FieldText', 'AccentColor', 'AccentColorText', 'SelectedItem', 'SelectedItemText'];
const NAMED_COLOURS = ['black', 'white', 'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink', 'gray', 'grey', 'silver', 'navy', 'teal', 'aqua', 'lime', 'maroon', 'olive', 'fuchsia', 'transparent'];
const LENGTH = /(?<![\w.-])-?\d*\.?\d+(px|rem|em|ch|ex|vh|vw|vmin|vmax|cm|mm|in|pt|pc|lh|rlh|cqw|cqh|cqi|cqb)\b/;
const RAW_STATE = /:(invalid|valid|required|optional|read-only|read-write|user-valid|user-invalid|checked|indeterminate|hover|active|focus-visible|focus-within|focus|disabled|enabled|popover-open)\b|\[(aria-[a-z]+|disabled|checked|selected|open|pressed|expanded|current|invalid|loading|readonly|required|indeterminate|hidden|data-(hover|active|focus|focus-visible|highlighted|ready))\b/;

/** Parses CSS into nested nodes: { prelude, children } for a block, { prop, value } for a declaration, { statement } otherwise. */
export function parse(css) {
  const text = css.replace(/\/\*[\s\S]*?\*\//g, '');
  let i = 0;
  const block = () => {
    const nodes = []; let buffer = ''; let quote = ''; let depth = 0;
    for (; i < text.length; i++) {
      const ch = text[i];
      if (quote) { buffer += ch; if (ch === quote) quote = ''; continue; }
      if (ch === '"' || ch === "'") { quote = ch; buffer += ch; continue; }
      if (ch === '(') depth++; else if (ch === ')') depth--;
      if (depth === 0 && ch === '{') { i++; nodes.push({ prelude: buffer.trim().replace(/\s+/g, ' '), children: block() }); buffer = ''; continue; }
      if (depth === 0 && ch === '}') return nodes;
      if (depth === 0 && ch === ';') {
        const line = buffer.trim(); buffer = '';
        if (!line) continue;
        const colon = line.indexOf(':');
        if (line.startsWith('@') || colon === -1) nodes.push({ statement: line });
        else nodes.push({ prop: line.slice(0, colon).trim(), value: line.slice(colon + 1).trim() });
        continue;
      }
      buffer += ch;
    }
    return nodes;
  };
  return block();
}

/** The text inside each `:where(` of a selector, with nested parentheses kept. */
function whereParts(selector) {
  const parts = []; const open = ':where(';
  for (let at = selector.indexOf(open); at !== -1; at = selector.indexOf(open, at + 1)) {
    let depth = 1, end = at + open.length;
    while (depth > 0 && end < selector.length) { const ch = selector[end++]; if (ch === '(') depth++; else if (ch === ')') depth--; }
    parts.push({ inner: selector.slice(at + open.length, end - 1), start: at, end });
  }
  return parts.filter((p, n, all) => !all.some((q, m) => m !== n && q.start < p.start && q.end >= p.end));
}
const splitSelectors = (prelude) => { const out = []; let depth = 0, buffer = ''; for (const ch of prelude) { if (ch === '(') depth++; if (ch === ')') depth--; if (ch === ',' && depth === 0) { out.push(buffer.trim()); buffer = ''; } else buffer += ch; } if (buffer.trim()) out.push(buffer.trim()); return out; };
const stripUrls = (value) => value.replace(/url\((?:"[^"]*"|'[^']*'|[^)]*)\)/g, 'url()');
const reads = (value) => [...value.matchAll(/var\(\s*(--[A-Za-z0-9_-]+)/g)].map((m) => m[1]);

/**
 * @param {string} id  The component id.
 * @param {string} css  The recipe's text.
 * @param {{ conditions: Record<string, string>, declared: Set<string>, manifestTokens?: string[], focusable?: boolean, parts?: string[] }} context
 *   `parts` are the names of the manifest's parts other than the root; a public token may name one (D92).
 *   `styleOnly` is true for a style-only recipe, whose scope is the root attribute of a native element.
 *   `focusable` is false for a root that never takes focus; such a recipe needs no focus ring (C20).
 * @returns {{ rule: string, message: string }[]}
 */
export function lint(id, css, context) {
  const problems = [];
  const fail = (rule, message) => problems.push({ rule, message });
  // A component's recipe is scoped to its tag; a style-only recipe to the attribute its native element carries.
  const tag = context.styleOnly ? `[data-${PREFIX}="${id}"]` : `${PREFIX}-${id}`;
  const stateOf = Object.fromEntries(Object.entries(context.conditions).map(([state, condition]) => [condition, state]));
  // --<id>-[<part>-]<word>[-<state or variant>]. Groups: 1 the part with its hyphen, 2 the word, 3 the suffix.
  const partNames = (context.parts ?? []).map((p) => p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
  const publicName = new RegExp(`^--${id}-(${partNames ? `(?:${partNames})-` : '(?!)'})?(${WORDS.join('|')})(-[a-z0-9-]+)?$`);
  // The base public tokens of this recipe: a public token with no state or variant, which some private token reads first.
  const bases = new Set([...css.replace(/\/\*[\s\S]*?\*\//g, '').matchAll(/:\s*var\(\s*(--[A-Za-z0-9_-]+)/g)].map((m) => m[1]).filter((name) => { const m = publicName.exec(name); return m && !m[3]; }));

  if (!css.trimStart().startsWith(LAYERS)) fail('C1', 'the file does not begin with the cascade layer order statement');
  if (/:defined/.test(css)) fail('D43', 'the recipe mentions :defined; the kit does not hide a component that is not yet defined');
  const top = parse(css);
  const blocks = top.filter((n) => n.children);
  if (blocks.length !== 1 || blocks[0].prelude !== '@layer recipes') { fail('C2', 'everything after the order statement must sit in one "@layer recipes" block'); return problems; }
  if (top.some((n) => n.prop || (n.statement && n.statement + ';' !== LAYERS))) fail('C1', 'a rule sits outside the recipes cascade layer');
  // D108: after the scope the layer may hold keyframes, each named for the recipe: @keyframes <id>-<word>.
  const frames = blocks[0].children.filter((n) => n.prelude?.startsWith('@keyframes'));
  for (const f of frames) if (!new RegExp(`^@keyframes ${id}-[a-z]+(?:-[a-z]+)*$`).test(f.prelude)) fail('D108', `"${f.prelude}" is not named ${id}-<word>`);
  const scopes = blocks[0].children.filter((n) => !frames.includes(n));
  if (scopes.length !== 1 || scopes[0].prelude !== `@scope (${tag})`) { fail('D53', `the recipes layer must hold exactly one "@scope (${tag})" block`); return problems; }
  if (frames.length && blocks[0].children[0] !== scopes[0]) fail('D108', 'keyframes come after the scope');

  const declaredPrivate = new Set();
  const publicRead = new Set();
  let hasBoxSizing = false;
  let rootSetsDisplay = false, restatesHidden = false, hasForcedColours = false, hasFocusRing = false, paints = false;
  /** @type {Record<string, string[]>} */ const sequences = {};

  const walk = (nodes, media) => {
    for (const node of nodes) {
      if (node.statement) { fail('D53', `unexpected statement "${node.statement}"`); continue; }
      if (node.prop) { fail('D53', `the declaration "${node.prop}" is not inside a rule`); continue; }
      if (node.prelude.startsWith('@media')) {
        if (node.prelude === '@media (forced-colors: active)') hasForcedColours = true;
        walk(node.children, [...media, node.prelude]);
        continue;
      }
      if (node.prelude.startsWith('@')) { fail('D53', `unexpected at-rule "${node.prelude}"`); continue; }
      // C31: the one rule that is not a token block, a root rule or a part rule. It makes the recipe's boxes border boxes.
      const box = /^:where\(:scope, \[data-part\](?:, [a-z]+)*\)$/.test(node.prelude);
      if (box) {
        if (media.length || node.children.length !== 1 || node.children[0].prop !== 'box-sizing' || node.children[0].value !== 'border-box') fail('C31', 'the box-sizing rule declares only "box-sizing: border-box", outside any media query');
        hasBoxSizing = true;
        continue;
      }
      const forced = media.includes('@media (forced-colors: active)');
      const declarations = node.children.filter((n) => n.prop);
      if (node.children.some((n) => n.children)) fail('D53', `"${node.prelude}" nests another rule`);
      const isTokenBlock = node.prelude === ':where(:scope)';
      const isVariantBlock = /^:where\(:scope\[[a-z-]+="[^"]+"\]\)$/.test(node.prelude);
      // C5 as amended: the two rules other than the token and variant blocks that may set a private token.
      // A coordinator hands its items its disabled state: a rule on the root whose only condition is disabled
      // sets a token its token block declares to empty. A part rule with no condition stops a token the root
      // hands down at that part: it sets a token its token block declares to `initial`.
      const ruleSelectors = isTokenBlock || isVariantBlock ? [] : splitSelectors(node.prelude);
      const handsDisabled = !media.length && ruleSelectors.length > 0 && ruleSelectors.every((s) => s === `:scope:where(${context.conditions.disabled})`);
      const stopsAtPart = !media.length && ruleSelectors.length > 0 && ruleSelectors.every((s) => /^:scope > \[data-part="[a-z-]+"\]$/.test(s));
      const mayDeclare = (d) => d.prop.startsWith('--_') && declaredPrivate.has(d.prop) && ((handsDisabled && d.value === '') || (stopsAtPart && d.value === 'initial'));

      for (const d of declarations) {
        const bare = stripUrls(d.value);
        // D59: no literal colour, no literal length other than 0.
        if (/#[0-9a-fA-F]{3,8}\b/.test(bare) || /\b(rgba?|hsla?|oklch|oklab|lab|lch|hwb|color|color-mix)\(/.test(bare)) fail('D59', `${d.prop}: a literal or computed colour in "${d.value.slice(0, 60)}"`);
        for (const word of bare.split(/[^A-Za-z-]+/)) {
          if (NAMED_COLOURS.includes(word.toLowerCase())) fail('D59', `${d.prop}: the colour keyword "${word}"`);
          if (SYSTEM_COLOURS.includes(word) && !forced) fail('D59', `${d.prop}: the system colour "${word}" outside the forced-colors block`);
        }
        if (LENGTH.test(bare)) fail('D59', `${d.prop}: a literal length in "${d.value.slice(0, 60)}"`);
        // C22: logical properties only.
        if (/(^|-)(left|right)(-|$)/.test(d.prop)) fail('C22', `the physical property "${d.prop}"`);
        // D61: motion only for a ready root, and only when motion is allowed.
        if (/^(transition|animation)/.test(d.prop) && !(media.includes('@media (prefers-reduced-motion: no-preference)') && (context.styleOnly || node.prelude.includes(`:where(${context.conditions.ready})`)))) fail('D61', `"${d.prop}" outside a ready root or outside the motion query`);

        if (isTokenBlock || isVariantBlock) {
          if (!d.prop.startsWith('--_')) fail(isVariantBlock ? 'D58' : 'C5', `"${d.prop}" is declared in a ${isVariantBlock ? 'variant' : 'token'} block; only private tokens may be`);
          if (isTokenBlock && !forced) declaredPrivate.add(d.prop);
          // C33: nothing fades. A disabled part is painted with colour tokens, so no recipe has a token for a fade.
          if (/^--_fade(-|$)/.test(d.prop)) fail('C33', `"${d.prop}" is a token for a fade; a disabled part is painted with colour tokens, never faded`);
          const names = reads(d.value);
          for (const name of names.filter((n) => n.startsWith(`--${id}-`))) {
            publicRead.add(name);
            if (!publicName.test(name)) fail('D60', `the public token "${name}" does not use the words ${WORDS.join(', ')}`);
          }
          const first = names[0];
          const m = first && publicName.exec(first);
          if (m && m[3]) {
            const suffix = m[3].slice(1);
            // A suffix that is no state of the matrix is a variant. A suffix of several states, such as checked-disabled,
            // is the token of a state too (C30).
            const states = (rest) => rest === '' || Object.keys(context.conditions).some((s) => (rest === s || rest.startsWith(`${s}-`)) && states(rest.slice(s.length + 1)));
            if (states(suffix) && !FOLLOWS_BASE.includes(suffix)) {
              const other = names.slice(1).find((n) => n.startsWith(`--${id}-`) || n.startsWith('--_'));
              if (other) fail('D54', `"${d.prop}": ${first} is the token of a state other than ${FOLLOWS_BASE.join(' and ')}; it falls back to the kit's value, not to ${other}`);
            } else {
              // hover, active or a variant: the base public token comes next, when the recipe has one (C7).
              const base = `--${id}-${m[1] ?? ''}${m[2]}`;
              const other = names.slice(1).find((n) => n.startsWith(`--${id}-`));
              if (bases.has(base) ? names[1] !== base : other) fail('D54', bases.has(base) ? `"${d.prop}": after ${first} the fallback must be ${base}` : `"${d.prop}": ${first} falls back to ${other}, but the recipe has no base token ${base}`);
            }
          }
        } else {
          if (!forced && PAINTS.test(d.prop)) paints = true;
          if (d.prop.startsWith('--') && !mayDeclare(d)) fail('C5', `the custom property "${d.prop}" is declared outside the token block`);
          for (const name of reads(d.value)) if (!name.startsWith('--_')) fail('C6', `"${d.prop}" reads ${name}; a rule may read private tokens only`);
        }
        for (const name of reads(d.value)) {
          if (!name.startsWith('--_') && !name.startsWith(`--${id}-`) && !context.declared.has(name)) fail('T4', `${name} is read but tokens.css does not declare it`);
        }
      }
      if (isTokenBlock || isVariantBlock) continue;

      for (const selector of splitSelectors(node.prelude)) {
        if (!selector.startsWith(':scope')) fail('D53', `the selector "${selector.slice(0, 50)}" does not start at the root`);
        if (/\[data-part/.test(selector) && /(^|[^>]\s)\[data-part|\S\[data-part/.test(selector.replace(/> \[data-part/g, ''))) fail('D56', `a part in "${selector.slice(0, 50)}" is not selected with the child combinator`);
        let rest = selector;
        const states = [];
        for (const part of whereParts(selector)) {
          const state = stateOf[part.inner];
          if (!state) fail('D55', `":where(${part.inner.slice(0, 40)}…)" is not a condition of the state matrix`);
          else states.push(state);
          rest = rest.replace(`:where(${part.inner})`, '');
        }
        const raw = RAW_STATE.exec(rest);
        if (raw) fail('S12', `"${raw[0]}" in "${selector.slice(0, 50)}" selects a state without its condition`);
        // A variant is an attribute with a value on the root, in either kind of quotes. An attribute on an element
        // inside the root, such as a part's data-part (C14) or a row's data-level, is the author's own data.
        const onRoot = rest.split(/\s*[>+~]\s*|\s+/)[0];
        if (/\[[a-z-]+=(?:"[^"]*"|'[^']*')\]/.test(onRoot)) fail('D58', `"${selector.slice(0, 50)}" selects a variant outside a variant block`);

        if (states.includes('hover')) {
          if (!media.includes('@media (hover: hover)')) fail('D64', 'a hover rule sits outside @media (hover: hover)');
          for (const d of declarations) if (!PAINT_ONLY.includes(d.prop)) fail('D63', `a hover rule sets "${d.prop}", which is not paint`);
        }
        // C33: a rule whose selector holds the disabled condition declares no opacity, in any media block.
        if (states.includes('disabled') && declarations.some((d) => d.prop === 'opacity')) fail('C33', `"${selector.slice(0, 50)}" fades a disabled part with opacity; paint it with colour tokens`);
        if (states.includes('hidden') && declarations.some((d) => d.prop === 'display' && d.value === 'none')) restatesHidden = true;
        if (states.includes('focus-visible') && rest === ':scope' && declarations.some((d) => d.prop === 'outline')) hasFocusRing = true;
        // A root whose operable mark is its own pseudo-element may draw the ring on that mark, with the kit's ring tokens.
        if (states.includes('focus-visible') && /^:scope::(before|after)$/.test(rest)
          && declarations.some((d) => d.prop === 'outline' && /var\(--_ring-width\)/.test(d.value) && /var\(--_ring\)/.test(d.value))
          && declarations.some((d) => d.prop === 'outline-offset' && /var\(--_ring-offset\)/.test(d.value))) hasFocusRing = true;
        if (selector === ':scope' && !media.length && declarations.some((d) => d.prop === 'display')) rootSetsDisplay = true;
        const ordered = states.filter((s) => ORDER.includes(s));
        if (ordered.length) (sequences[forced ? 'forced' : 'main'] ??= []).push(ordered[0]);
      }
    }
  };
  walk(scopes[0].children, []);
  forcedPaint(scopes[0].children, context, fail);

  for (const [where, sequence] of Object.entries(sequences)) {
    for (let n = 1; n < sequence.length; n++) {
      if (ORDER.indexOf(sequence[n]) < ORDER.indexOf(sequence[n - 1])) fail('D55', `in the ${where} rules, ${sequence[n]} comes after ${sequence[n - 1]}; the order is ${ORDER.join(', ')}`);
    }
  }
  for (const m of css.replace(/\/\*[\s\S]*?\*\//g, '').matchAll(/var\(\s*(--_[A-Za-z0-9_-]+)/g)) {
    if (!declaredPrivate.has(m[1])) { fail('C8', `${m[1]} is read but not declared in the token block`); declaredPrivate.add(m[1]); }
  }
  if (!hasBoxSizing) fail('C31', 'no rule makes the root and the parts border boxes: ":where(:scope, [data-part]) { box-sizing: border-box; }"');
  if (rootSetsDisplay && !restatesHidden) fail('C16', 'the root sets display, but no rule keeps a hidden root from showing');
  if (paints && !hasForcedColours) fail('D15', 'the recipe paints, but there is no @media (forced-colors: active) block');
  if (context.focusable !== false && !hasFocusRing) fail('C20', 'no rule draws an outline on the focus-visible condition, on the root or, with the ring tokens, on its ::before or ::after');
  if (context.manifestTokens) {
    const listed = new Set(context.manifestTokens);
    for (const name of publicRead) if (!listed.has(name)) fail('D13', `the recipe reads ${name}, which the manifest does not list`);
    for (const name of listed) if (!publicRead.has(name)) fail('D13', `the manifest lists ${name}, which the recipe does not read`);
  }
  return problems;
}

/**
 * C19 as amended (D124), two checks on what a recipe paints under forced colours.
 *  - GrayText means disabled: it appears in a forced-colours block only in a rule that holds the disabled condition or
 *    selects a placeholder (`[data-placeholder]`, `::placeholder`), or in a private token that is named for disabled,
 *    is guarded by the inherited `--_group-disabled`, or is read only by such rules.
 *  - A label in HighlightText sits on a Highlight face, and Chromium's backplate (Firefox's, over a thumb) hides that face
 *    behind its glyphs unless the element opts out of forcing. So every rule whose `color` resolves to HighlightText under
 *    forced colours, in any variant and with any inherited switch on or off, needs a forced-colours rule for the same
 *    selector, or for its part with no condition, whose `forced-color-adjust` resolves to none there.
 */
function forcedPaint(nodes, context, fail) {
  const rules = [];
  const collect = (list, media) => { for (const n of list) { if (!n.children) continue; if (n.prelude.startsWith('@')) collect(n.children, [...media, n.prelude]); else rules.push({ prelude: n.prelude, media, decls: n.children.filter((d) => d.prop) }); } };
  collect(nodes, []);
  const forced = (r) => r.media.includes('@media (forced-colors: active)');
  const isToken = (r) => r.prelude === ':where(:scope)' || /^:where\(:scope\[[a-z-]+="[^"]+"\]\)$/.test(r.prelude);
  const disabled = `:where(${context.conditions.disabled})`;
  const placeholder = (sel) => /\[data-placeholder\]|::placeholder/.test(sel);
  const allowed = (prelude) => splitSelectors(prelude).every((sel) => sel.includes(disabled) || placeholder(sel));
  // Which rules read a private token, directly or through other tokens.
  const tokenReads = new Map();
  for (const r of rules.filter(isToken)) for (const d of r.decls) for (const name of reads(d.value)) { if (!tokenReads.has(name)) tokenReads.set(name, new Set()); tokenReads.get(name).add(d.prop); }
  const readers = (name, seen = new Set()) => {
    if (seen.has(name)) return []; seen.add(name);
    const direct = rules.filter((r) => !isToken(r) && r.decls.some((d) => reads(d.value).includes(name)));
    return [...direct, ...[...(tokenReads.get(name) ?? [])].flatMap((t) => readers(t, seen))];
  };
  for (const r of rules.filter(forced)) for (const d of r.decls) {
    if (!/\bGrayText\b/.test(d.value)) continue;
    if (isToken(r)) {
      if (/disabled/.test(d.prop) || /^var\(--_group-disabled\)/.test(d.value)) continue;
      const by = readers(d.prop);
      if (by.length && by.every((x) => allowed(x.prelude))) continue;
      fail('C19', `${d.prop} is GrayText under forced colours, but is read by a rule that is neither disabled nor a placeholder; GrayText means disabled`);
    } else if (!allowed(r.prelude)) fail('C19', `"${r.prelude.slice(0, 60)}" paints GrayText under forced colours without the disabled condition; GrayText means disabled`);
  }
  // Token values per scenario: each variant, each inherited switch on (empty) or off (invalid).
  const INVALID = Symbol('invalid');
  const variants = [null, ...new Set(rules.filter(isToken).map((r) => r.prelude.match(/\[([a-z-]+="[^"]+")\]/)?.[1]).filter(Boolean))];
  const switches = rules.filter((r) => r.prelude === ':where(:scope)' && !forced(r)).flatMap((r) => r.decls.filter((d) => d.prop.startsWith('--_') && d.value === 'inherit').map((d) => d.prop));
  const combos = switches.reduce((all, s) => all.flatMap((c) => [{ ...c, [s]: INVALID }, { ...c, [s]: '' }]), [{}]);
  for (const variant of variants) for (const combo of combos) {
    const tokens = {};
    for (const f of [false, true]) for (const r of rules.filter((x) => isToken(x) && forced(x) === f)) {
      const v = r.prelude.match(/\[([a-z-]+="[^"]+")\]/)?.[1] ?? null;
      if (v === null || v === variant) for (const d of r.decls) if (d.prop.startsWith('--_')) tokens[d.prop] = d.value;
    }
    Object.assign(tokens, combo);
    const resolve = (value, seen = new Set()) => {
      let out = '', at = 0;
      for (;;) {
        const k = value.indexOf('var(', at);
        if (k < 0) { out += value.slice(at); break; }
        out += value.slice(at, k);
        let depth = 0, j = k + 3;
        for (; j < value.length; j++) { if (value[j] === '(') depth++; if (value[j] === ')' && --depth === 0) break; }
        const inner = value.slice(k + 4, j); at = j + 1;
        const comma = inner.indexOf(','), name = (comma < 0 ? inner : inner.slice(0, comma)).trim(), fallback = comma < 0 ? null : inner.slice(comma + 1).trim();
        let got = !name.startsWith('--_') || seen.has(name) ? INVALID : tokens[name] ?? INVALID;
        if (got !== INVALID && typeof got === 'string') got = ['initial', 'inherit'].includes(got) ? INVALID : resolve(got, new Set([...seen, name]));
        if (got === INVALID) got = fallback === null ? INVALID : resolve(fallback, seen);
        if (got === INVALID) return INVALID;
        out += got;
      }
      return out.trim();
    };
    const optOuts = rules.filter((r) => forced(r) && !isToken(r) && r.decls.some((d) => d.prop === 'forced-color-adjust' && resolve(d.value) === 'none')).flatMap((r) => splitSelectors(r.prelude));
    const bare = (sel) => whereParts(sel).reduceRight((s, p) => s.slice(0, p.start) + s.slice(p.end), sel);
    for (const r of rules.filter((x) => !isToken(x))) {
      const color = r.decls.filter((d) => d.prop === 'color').pop();
      if (!color || resolve(color.value) !== 'HighlightText') continue;
      for (const sel of splitSelectors(r.prelude)) {
        if (optOuts.includes(sel) || optOuts.includes(bare(sel))) continue;
        fail('C19', `"${sel.slice(0, 60)}" paints its label HighlightText under forced colours${variant ? ` (${variant})` : ''} with no forced-color-adjust: none for it; the engine's backplate hides the Highlight face behind the glyphs`);
      }
    }
  }
}

/** Whether a component's root ever takes focus: it has a tabindex of its own, or its tab list or menu gives it one. @param {any} manifest */
export const takesFocus = (manifest) => manifest.focus !== 'none';

/** The names of a manifest's parts other than the root: a public token may name one. @param {any} manifest */
export const partsOf = (manifest) => Object.keys(manifest.parts).filter((name) => name !== 'root');

/** What the lint needs from the rest of the kit. */
export function context() {
  const states = JSON.parse(fs.readFileSync(path.join(root, 'references/states.json'), 'utf8')).states;
  // What the kit's two generated stylesheets declare: tokens.css, and icons.css once the kit has icons.
  const tokens = ['tokens.css', 'icons.css'].map((f) => path.join(root, 'kit/styles', f)).filter((f) => fs.existsSync(f)).map((f) => fs.readFileSync(f, 'utf8')).join('\n');
  return {
    conditions: Object.fromEntries(states.map((s) => [s.id, s.condition])),
    declared: new Set([...tokens.matchAll(/(--[A-Za-z0-9_-]+)\s*:/g)].map((m) => m[1])),
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const components = path.join(root, 'kit/components');
  const shared = context();
  let count = 0, files = 0;
  for (const id of fs.readdirSync(components)) {
    const file = path.join(components, id, `${id}.css`);
    if (!fs.existsSync(file)) continue;
    files++;
    const manifest = JSON.parse(fs.readFileSync(path.join(components, id, `${id}.manifest.json`), 'utf8'));
    for (const p of lint(id, fs.readFileSync(file, 'utf8'), { ...shared, manifestTokens: manifest.tokens, focusable: takesFocus(manifest), parts: partsOf(manifest), styleOnly: manifest.kind === 'recipe' })) { count++; console.log(`ERROR kit/components/${id}/${id}.css ${p.rule}: ${p.message}`); }
  }
  console.log(count ? `${count} problem(s) in ${files} recipe(s)` : `${files} recipe(s) follow the CSS contract`);
  process.exit(count ? 1 : 0);
}
