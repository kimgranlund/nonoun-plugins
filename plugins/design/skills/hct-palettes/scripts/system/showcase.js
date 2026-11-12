// showcase.js — a static 1280 × 960 specimen sheet of one generated colour system (brief: ../../references/showcase.md).
// 24 specimens in 8 groups. Every colour is a variable of the run's system.css (inlined) or a value read from its
// system.json; the sheet adds only neutral chrome (layout, system type) and no colour of its own. Mode panels carry the
// forced selector of their mode (classes or attributes, scope included), so each takes that mode's variables.
// Machine-readable marks for scripts/check.mjs: data-group, data-specimen, data-mode-panel, data-annot, data-flag.
import { clampChroma } from './anchors.js';

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const okCss = ([L, C, H]) => 'oklch(' + +L.toFixed(4) + ' ' + +C.toFixed(4) + ' ' + +(((H % 360) + 360) % 360).toFixed(2) + ')';
const lab = ([L, C, H]) => [L, C * Math.cos(H * Math.PI / 180), C * Math.sin(H * Math.PI / 180)];
const dE = (p, q) => { const a = lab(p), b = lab(q); return 100 * Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]); };
const r1 = (x) => Math.round(x * 10) / 10;
const KINDS = ['normal', 'protan', 'deutan', 'tritan'];
const BANDS = [['bg', 1, 2], ['fill', 3, 5], ['border', 6, 8], ['solid', 9, 10], ['text', 11, 12]];
const STATUS = ['critical', 'warning', 'success', 'info'];

/** The classes and attributes an element needs to match a compound selector of classes and attributes (`.a.b[x=y]`). */
export function mountOf(selector) {
  const classes = [...selector.matchAll(/\.([\w-]+)/g)].map((m) => m[1]);
  const attrs = [...selector.matchAll(/\[([\w-]+)(?:=("?)([\w-]+)\2)?\]/g)].map((m) => [m[1], m[3] ?? '']);
  return { classes, attrs };
}
/** True when a selector is only classes and attributes, so an element can be made to match it. */
export const mountable = (selector) => selector.replace(/\.[\w-]+/g, '').replace(/\[[\w-]+(?:=("?)[\w-]+\1)?\]/g, '') === '';

/**
 * @param {object} ctx
 * @param {object} ctx.json      system.json as written
 * @param {string} ctx.css       system.css as written (inlined)
 * @param {(id: string) => string} ctx.forced  the forced selector of a mode, scope included
 * @param {boolean} ctx.p3       true when system.css carries a Display P3 upgrade
 */
export function showcaseHtml({ json, css, forced, p3 }) {
  const ids = Object.keys(json.modes), L = json.modes.light, D = json.modes.dark;
  const extraId = ids.find((id) => id !== 'light' && id !== 'dark') || null;
  const accents = json.families.accents, all = json.families.all;
  const v = (name) => `var(${name})`, c = (role) => `var(--colors-${role})`, step = (f, s) => `var(--colors-${f}-${s})`;
  const pf = L.roles.primary === 'neutral' ? 'gray' : L.roles.primary;
  const attrsOf = (id, cls = '') => { const m = mountOf(forced(id)); return `class="${esc([...cls.split(/\s+/), ...m.classes].filter(Boolean).join(' '))}"${m.attrs.map(([k, x]) => ` ${k}="${esc(x)}"`).join('')}`; };
  const panel = (id, inner, cls = '') => `<div ${attrsOf(id, 'sc-panel ' + cls)} data-mode-panel="${esc(id)}">${inner}</div>`;
  const spec = (id, title, desc, body, cls = '') => `<figure class="sc-spec ${cls}" data-specimen="${esc(id)}" aria-label="${esc(title)}"><figcaption><b>${esc(title)}</b> · ${desc}</figcaption>${body}</figure>`;
  const group = (id, title, body) => `<section class="sc-group sc-g-${id}" data-group="${esc(id)}" aria-label="${esc(title)}"><h2>${esc(title)}</h2>${body}</section>`;
  const note = (text, state) => `<p class="sc-note"${state ? ` data-state="${esc(state)}"` : ''}>${text}</p>`;
  const flag = (kind, attrs, text) => `<span class="sc-flag" data-flag="${kind}"${Object.entries(attrs).map(([k, x]) => ` data-${k}="${esc(x)}"`).join('')}>✗ ${text}</span>`;
  const pairOf = (M, fg, bg) => M.contrast?.pairs.find((p) => p.fg === fg && p.bg === bg);
  const has = (M, name) => name in M.variables;

  // ── 1. Ramps ────────────────────────────────────────────────────────────────────────────────────────────
  // More than 16 families (the Radix hue set) can't stay legible in the ramp tiles: show the families the roles use.
  const roleFams = new Set(Object.values(L.roles).map((f) => (f === 'neutral' ? 'gray' : f)).concat('gray'));
  // Neutrals split: ground and surface have their own strips under Neutral & surfaces; the tiles keep the accents and the ink (gray).
  const tileFams = json.neutrals ? all.filter((f) => f !== 'ground' && f !== 'surface') : all;
  const shownFams = tileFams.length > 16 ? tileFams.filter((f) => roleFams.has(f)).slice(0, 16) : tileFams;
  const famNote = shownFams.length < tileFams.length ? ` · ${shownFams.length} of ${tileFams.length} (role families)` : json.neutrals ? ', gray = ink' : '';
  // Step 9 carries an "A" in the label its family's solid takes in that mode (light or dark, system.json › solidLabels).
  const labelCss = (id, f) => { const e = json.modes[id].solidLabels?.[f]; return e ? json.labelColors[e.label].css : null; };
  const rampTable = (id) => panel(id, `<div class="sc-ramp" style="--rows:${shownFams.length}"><span></span>${[...Array(12)].map((_, i) => `<span class="sc-num">${i + 1}</span>`).join('')}${shownFams.map((f) => `<code>${esc(f)}</code>${[...Array(12)].map((_, i) => { const lc = i === 8 && labelCss(id, f); return `<span class="sw${lc ? ' sc-lbl' : ''}" title="${esc(f)} ${i + 1}${lc ? ' · ' + json.modes[id].solidLabels[f].label + ' label' : ''}" style="background:${step(f, i + 1)}${lc ? ';color:' + lc : ''}"${lc ? ` data-label="${json.modes[id].solidLabels[f].label}"` : ''}>${lc ? 'A' : ''}</span>`; }).join('')}`).join('')}</div>`);
  const byLabel = (id, which) => shownFams.filter((f) => json.modes[id].solidLabels?.[f]?.label === which);
  const t = L.settings.targetsLight, pr = L.ramps[pf], solidStep = L.solidSteps?.primary ?? 9, anchoredStep = L.anchorReport.find((a) => a.role === 'primary')?.step;
  const solidPair = pairOf(L, 'primary-on-solid', 'primary-solid'), pLabel = L.solidLabels?.[pf]?.label ?? 'light', kr = L.keyRun?.[pf];
  // Key-run deviations from even spacing (anchors, floors), every mode and family: each one flagged.
  const short = (r) => r.replace(/-floor$/, '').replace(/^hover-floor-unreachable$/, 'hover unreachable');
  const krFlags = ids.map((id) => { const fl = Object.entries(json.modes[id].keyRun || {}).flatMap(([f, r]) => r.deviations.map((d) => flag('keyrun', { mode: id, family: f, step: d.step, reason: d.reason }, `${f} ${d.step} ${short(d.reason)}`))); return fl.length ? `<span class="sc-nw">${esc(id)}:</span> ${fl.join(' ')}` : ''; }).filter(Boolean);
  const cuspFams = (id) => shownFams.filter((f) => json.modes[id].solidLabels?.[f]?.cusp);
  const annot = pr.map((s, i) => { const n = i + 1, tg = n === 1 ? null : t[n - 2], off = tg != null && Math.abs(s.apcaOnPage - tg) > 1.5;
    const why = n === anchoredStep ? ' ◆' : off ? ' *' : '';
    return `<div class="sc-step${n === solidStep ? ' is-solid' : ''}"><span class="sw sc-big" style="background:${step(pf, n)}"></span><span class="sc-lc" data-annot="lc" data-step="${n}" data-lc="${s.apcaOnPage}"${tg != null ? ` data-target="${tg}"` : ''}>Lc ${s.apcaOnPage}${why}</span><span class="sc-tg">${tg != null ? 'target ' + tg : 'page'}</span></div>`; }).join('');
  const legend = panel('light', `<div class="sc-legend">${BANDS.map(([name, a, b]) => `<span class="sc-band" style="grid-column:${a}/${b + 1}">${name} ${a}–${b}</span>`).join('')}${annot}</div>
    <p class="sc-solid" data-annot="solid-lc" data-step="${solidStep}" data-value="${solidPair?.lc ?? ''}" data-floor="${L.apca.solid}"><span class="sc-chip" style="background:${c('primary-solid')};color:${c('primary-on-solid')}">Label</span> primary solid (${esc(pf)} ${solidStep}) vs its ${pLabel} label: <b>Lc ${solidPair?.lc ?? '–'}</b> ${solidPair && solidPair.lc >= L.apca.solid ? `≥ ${L.apca.solid} ✓` : `✗ under ${L.apca.solid}`} · <span data-annot="keyrun" data-lc="${kr ? kr.lc.join(' ') : ''}">9–12 on the page: Lc ${kr ? kr.lc.join(' → ') : '–'}</span> (even thirds) · * moved by a solve${anchoredStep ? ', ◆ anchored' : ''}</p>
    <p class="sc-meta" data-annot="labels">A on step 9 = its label · dark label, light / dark: ${esc(byLabel('light', 'dark').join(', ') || 'none')} / ${byLabel('dark', 'dark').join() === byLabel('light', 'dark').join() ? 'same' : esc(byLabel('dark', 'dark').join(', ') || 'none')}${json.brightHues ? ` · bright hues ${json.brightHues[0]}–${json.brightHues[1]}° at the cusp: ${esc(shownFams.filter((f) => json.modes.light.solidLabels?.[f]?.brightHue).join(', ') || 'none')}` : ' · bright hues off'} · key-run deviations: ${krFlags.length ? krFlags.join(' · ') : 'none ✓'}</p>`);
  const g1 = group('ramps', 'Ramps', spec('ramps-light', 'Light ramps', `steps 1–12 per family${famNote || ', light page'}`, rampTable('light'))
    + spec('ramps-dark', 'Dark ramps', `generated for the dark page`, rampTable('dark'))
    + spec('step-use', 'Step use', `the step bands on the primary ramp (${esc(pf)}), each step's APCA Lc on the page vs its target`, legend, 'sc-wide'));

  // ── 2. Neutral & surfaces ───────────────────────────────────────────────────────────────────────────────
  const surfAnchor = L.anchorReport.find((a) => a.role === 'ground' || a.role === 'ink' || a.role === 'neutral');
  const tintFam = accents[L.settings.neutralFrom] ?? accents[0];
  const tintText = L.settings.mat === 'none' ? 'untinted (mat none)' : surfAnchor ? `hue from the ${esc(surfAnchor.role)} anchor (${esc(surfAnchor.value)})` : `tint source <b>${esc(tintFam)}</b> <span class="sw sc-inline" style="background:${step(tintFam, 9)}"></span> ${esc(tintFam)} 9 · tint ${L.settings.tint}%`;
  const neutralRamp = panel('light', `<div class="sc-row12"><code>gray</code>${[...Array(12)].map((_, i) => `<span class="sw sc-cell" style="background:${step('gray', i + 1)}"><i>${i + 1}</i></span>`).join('')}</div><p class="sc-meta">${tintText}</p>`);
  const ladder = (id) => panel(id, `<div class="sc-ladder" style="background:${c('bg')}"><span>${esc(id)}<br>bg</span><div style="background:${c('bg-subtle')}"><span>bg-<br>subtle</span><div style="background:${c('bg-muted')}"><span>bg-<br>muted</span></div></div></div>`, 'sc-half');
  const fills = (id) => panel(id, `<div class="sc-fills">${['', '-hover', '-active'].map((s) => `<span class="sc-ctl" style="background:${c('bg-control' + s)};border-color:${c('control-border')}">${s ? s.slice(1) : 'rest'}</span>`).join('')}</div>`, 'sc-half');
  // Neutrals split: the three families (ground, surface, ink), a card on the page per shown mode with its separation.
  const NS = json.neutrals, shownModes = ['light', 'dark', extraId].filter(Boolean);
  const famRows = () => { const src = (f) => esc(L.neutralSources[f].source.replace(/^Radix /, '').replace(/^the run's neutral$/, 'run neutral').replace(/ \(neutralFrom \d+\)$/, ''));
    return panel('light', `<div class="sc-fams">${['ground', 'surface', 'ink'].map((f, k) => `<code>${f}</code>${[...Array(12)].map((_, i) => `<span class="sw sc-cell" style="background:${step(f, i + 1)}">${k === 2 ? `<i>${i + 1}</i>` : ''}</span>`).join('')}`).join('')}</div><p class="sc-meta">${src('ground')} · ${src('surface')} (+${NS.surfaceLift.light} L*) · ${src('ink')}${NS.cross ? ' · dark: crossed' : ''} · gray = ink</p>`); };
  const sepFlags = ids.filter((id) => json.modes[id].separation && !json.modes[id].separation.pass).map((id) => flag('separation', { mode: id, value: json.modes[id].separation.dE }, `${id} ΔE ${json.modes[id].separation.dE}`));
  const cardOn = (id) => { const S = json.modes[id].separation; return panel(id, `<div class="sc-page" style="background:${c('bg')}"><div class="sc-card2" style="background:${c('surface')};border-color:${c('border')}"><b>Card</b><span class="sc-well" style="background:${c('bg-muted')};color:${c('fg-muted')}">muted</span></div></div><p class="sc-meta" title="APCA Lc ${S.lc}">${esc(id)}<br>ΔE ${S.dE}${S.pass ? ' ✓' : ' ✗'}</p>`, 'sc-half'); };
  const fillsOn = (id) => NS ? panel(id, `<div class="sc-fills sc-onsurf" style="background:${c('surface')}">${['', '-hover', '-active'].map((s) => `<span class="sc-ctl" style="background:${c('bg-control' + s)};border-color:${c('control-border')}">${s ? s.slice(1) : 'rest'}</span>`).join('')}</div>`, 'sc-half') : fills(id);
  const g2 = NS ? group('neutral', 'Neutral & surfaces', spec('neutral-ramp', 'Neutral families', 'ground · surface · ink, light', famRows())
    + spec('surface-ladder', 'Card on page', `surface on bg, separation ≥ ${NS.separationMin}${sepFlags.length ? ' ' + sepFlags.join(' ') : ''}`, `<div class="sc-pair">${shownModes.map(cardOn).join('')}</div>`)
    + spec('control-fills', 'Control fills', 'bg-control on surface, control-border', `<div class="sc-pair">${fillsOn('light')}${fillsOn('dark')}</div>`))
    : group('neutral', 'Neutral & surfaces', spec('neutral-ramp', 'Neutral ramp', 'gray 1–12 and its tint source', neutralRamp)
    + spec('surface-ladder', 'Surface ladder', 'bg → bg-subtle → bg-muted', `<div class="sc-pair">${ladder('light')}${ladder('dark')}</div>`)
    + spec('control-fills', 'Control fills', 'bg-control, control-border', `<div class="sc-pair">${fills('light')}${fills('dark')}</div>`));

  // ── 3. Roles ────────────────────────────────────────────────────────────────────────────────────────────
  const famOf = (r) => (L.roles[r] === 'neutral' ? 'gray' : L.roles[r]);
  // Per shown mode: primary and secondary solid + hover on their own label, then each one's family, label and APCA Lc.
  const SOLID_ROLES = ['primary', 'secondary'];
  const solidMeta = (M, r) => { const f = M.roles[r] === 'neutral' ? 'gray' : M.roles[r], p = pairOf(M, r + '-on-solid', r + '-solid'), h = pairOf(M, r + '-on-solid', r + '-solid-hover');
    return `${esc(f)} <b>${esc(M.solidLabels?.[f]?.label ?? '–')}</b> ${p?.lc ?? '–'}/${h?.lc ?? '–'}`; };
  const solids = ['light', 'dark'].map((id) => { const M = json.modes[id];
    return panel(id, `<div class="sc-solids"><div>${SOLID_ROLES.map((r) => `<span class="sc-btn" style="background:${c(r + '-solid')};color:${c(r + '-on-solid')}">${r}</span><span class="sc-btn" style="background:${c(r + '-solid-hover')};color:${c(r + '-on-solid')}">hover</span>`).join('')}</div><span class="sc-meta">${esc(id)} · ${SOLID_ROLES.map((r) => solidMeta(M, r)).join(' · ')}</span></div>`); }).join('');
  const status = panel('light', `<div class="sc-status"><span></span><span class="sc-num">solid</span><span class="sc-num">subtle + border + fg</span><span class="sc-num">fg on bg</span>${STATUS.map((r) => `<code>${r}</code><span class="sc-chip" style="background:${c(r + '-solid')};color:${c(r + '-on-solid')}" title="${esc(L.solidLabels?.[famOf(r)]?.label ?? '')} label">${esc(L.roles[r])}</span><span class="sc-chip" style="background:${c(r + '-subtle')};color:${c(r + '-fg')};box-shadow:inset 0 0 0 1px ${c(r + '-border')}">${r} message</span><span style="color:${c(r + '-fg')}">Lc ${pairOf(L, r + '-fg', 'bg')?.lc ?? '–'}</span>`).join('')}</div>`);
  const focus = panel('light', `<div class="sc-focus"><span class="sc-btn sc-ring" style="background:${c('primary-solid')};color:${c('primary-on-solid')};outline-color:${c('focus-ring')}">on a solid</span><span class="sc-card sc-ring" style="background:${c(json.neutrals ? 'surface' : 'bg-subtle')};border-color:${c('border')};outline-color:${c('focus-ring')}">on a surface</span><span class="sc-meta">2px, offset 2px</span></div>`);
  const g3 = group('roles', 'Roles', spec('solids', 'Solids', 'solid / hover on own label, APCA Lc, light · dark', solids)
    + spec('status', 'Status roles', 'solid (own label) · subtle + border + fg', status)
    + spec('focus', 'Focus ring', 'on a solid and on a surface', focus));

  // ── 4. Transparency ────────────────────────────────────────────────────────────────────────────────────
  const alphaRows = (fams) => `<div class="sc-alpha"><span></span>${[...Array(12)].map((_, i) => `<span class="sc-num">a${i + 1}</span>`).join('')}${fams.map((f) => `<code>${esc(f)}</code>${[...Array(12)].map((_, i) => `<span class="sw" style="background:${step(f, 'a' + (i + 1))}"></span>`).join('')}`).join('')}</div>`;
  const aFams = [...new Set([pf, 'gray'])], hasAlpha = !!L.alpha;
  const alphaOff = note('Alpha steps are off in this run (<code>alpha: false</code>).', 'alpha-off');
  const scrim = panel('light', `<div class="sc-scrim"><div class="sc-content"><b>Page content</b><span style="background:${c('bg-muted')}"></span><span style="background:${c('bg-muted')}"></span><span class="sc-chip" style="background:${c('primary-solid')};color:${c('primary-on-solid')}">Action</span></div><div class="sc-backdrop" style="background:${c('bg-backdrop')}"></div><div class="sc-dialog" style="background:${c('bg')};border-color:${c('border')}">Dialog over bg-backdrop</div></div>`);
  const g4 = group('transparency', 'Transparency', spec('alpha-page', 'Alpha over the page', `reproduces steps 1–12`, hasAlpha ? panel('light', alphaRows(aFams)) : alphaOff)
    + spec('alpha-surface', 'Over a contrasting surface', 'bg-inverse: the tint shows', hasAlpha ? panel('light', `<div class="sc-inv" style="background:${c('bg-inverse')};color:${c('fg-inverse')}">${alphaRows(aFams)}</div>`) : alphaOff)
    + spec('scrim', 'Backdrop', 'bg-backdrop over content', scrim));

  // ── 5. Modes ────────────────────────────────────────────────────────────────────────────────────────────
  const card = () => `<div class="sc-ui" style="background:${c(json.neutrals ? 'surface' : 'bg-subtle')};border-color:${c('border')}">
    <div class="sc-ui-h"><b>Deploys</b><span class="sc-chip" style="background:${c('success-subtle')};color:${c('success-fg')}">● Live</span></div>
    <p style="color:${c('fg-muted')}">3 services updated in the last hour.</p>
    <span class="sc-ui-l" style="color:${c('fg-muted')}">Branch</span><span class="sc-field" style="background:${c('bg')};border-color:${c('control-border')}">main</span>
    <div class="sc-list"><span>api</span><span style="background:${c('bg-selected')};color:${c('fg-selected')}">▸ web</span><span>worker</span></div>
    <span class="sc-chip sc-alert" style="background:${c('critical-subtle')};color:${c('critical-fg')};box-shadow:inset 0 0 0 1px ${c('critical-border')}">✗ 1 check failed</span>
    <div class="sc-mini">${[52, 70, 38, 84, 60, 46].map((h, i) => `<span style="height:${h}%;background:${c('data-' + (i + 1))}"></span>`).join('')}</div>
    <div class="sc-ui-f"><span class="sc-btn" style="background:${c('primary-solid')};color:${c('primary-on-solid')}">Deploy</span><span class="sc-btn" style="background:${c('bg-control')};color:${c('fg')};box-shadow:inset 0 0 0 1px ${c('control-border')}">Cancel</span></div>
    <span class="sc-ui-l" style="color:${c('fg-subtle')}">Updated 12:04</span></div>`;
  const modeSpec = (id, slot) => id ? spec('mode-' + slot, id, `${esc(json.modes[id].scheme)} scheme${json.modes[id].contrastMode ? ' · contrast' : ''}`, panel(id, card(), 'sc-mode'))
    : spec('mode-' + slot, 'Extra mode', 'none in this run', note('This run has light and dark only (<code>extraModes: false</code>).', 'no-extra-mode'), 'sc-modecol');
  const g5 = group('modes', 'Modes', modeSpec('light', 'light') + modeSpec('dark', 'dark') + modeSpec(extraId, 'extra'));

  // ── 6. Brand ────────────────────────────────────────────────────────────────────────────────────────────
  const anchors = L.anchorReport;
  const failsFor = (role, key) => ids.filter((id) => json.modes[id].anchorReport.find((a) => a.role === role)?.[key] === false);
  const clippedIn = (role) => ids.filter((id) => json.modes[id].anchorReport.find((a) => a.role === role)?.gamut?.inTarget === false);
  const srcText = (a) => esc(typeof a.source?.value === 'object' ? JSON.stringify(a.source.value) : (a.source?.value ?? a.value));
  // One flag per anchor and condition; data-modes lists every mode where it holds (all of them, when it holds everywhere).
  const modesText = (list) => (list.length === ids.length && ids.length > 1 ? `all ${ids.length} modes` : list.join(', '));
  const marksOf = (label, kind, role, list, extra = '') => (list.length ? flag(kind, { role, modes: list.join(' ') }, `${label}${extra}: ${modesText(list)}`) : '');
  const anchorTable = anchors.length ? `<div class="sc-anchors">${anchors.map((a) => { const d = D.anchorReport.find((x) => x.role === a.role);
    const clip = clippedIn(a.role), clipDE = [...new Set(clip.map((id) => json.modes[id].anchorReport.find((x) => x.role === a.role).gamut.clipDE))].join(' / ');
    const marks = [marksOf('out of order', 'anchor-order', a.role, failsFor(a.role, 'inOrder')), marksOf('out of range', 'anchor-range', a.role, failsFor(a.role, 'inRange')), marksOf('clipped', 'anchor-clip', a.role, clip, ` ΔE ${clipDE}`)].filter(Boolean).join(' ');
    const surface = a.role === 'ground' || a.role === 'ink' || a.role === 'surface';
    return `<div class="sc-anchor"><span class="sw sc-inline" style="background:${esc(a.value)}"></span><code>${esc(a.role)}</code> ${srcText(a)} → <b>${esc(a.family === 'neutral' ? 'gray' : a.family)} ${a.step}</b>${d && d.step !== a.step ? ` (dark ${d.step})` : ''} · Lc ${a.lc}${surface ? '' : ` (target ${a.target})`} · ΔE ${a.dE} ${marks || '<span class="sc-ok">✓ in order, range, gamut</span>'}</div>`; }).join('')}</div>`
    : note('No anchors in this run: every ramp comes from the settings alone (add <code>anchors</code> to pin brand colours).', 'no-anchors');
  const ground = anchors.find((a) => a.role === 'ground'), ink = anchors.find((a) => a.role === 'ink');
  const ends = (id) => { const M = json.modes[id], g = M.ramps.gray, pg = json.neutrals ? M.ramps.ground : g; return panel(id, `<div class="sc-ends"><span class="sc-big2" style="background:${c('bg')};color:${c('fg')};border-color:${c('border')}">Aa</span><span><b>${esc(id)}</b><br>page ${esc(pg[0].hex)}<br>ink ${esc(g[11].hex)}</span></div>`, 'sc-half'); };
  const endsDesc = ground || ink ? `ground ${ground ? srcText(ground) : '–'} · ink ${ink ? srcText(ink) : '–'}` : `no ground/ink anchors${json.request.endpoints ? ' · endpoints ' + esc(JSON.stringify(json.request.endpoints)) : ''}`;
  let gamutBody;
  if (json.target !== 'display-p3') gamutBody = note('sRGB-only run (<code>target: srgb</code>): no Display P3 upgrade.', 'srgb-only');
  else {
    const cand = []; for (const f of all) L.ramps[f].forEach((s) => { const [l, ch, h] = s.oklch, cs = clampChroma(l, ch, h, 'srgb'); cand.push({ f, step: s.step, p3: s.css, srgb: okCss([l, cs, h]), d: dE(s.oklch, [l, cs, h]) }); });
    cand.sort((a, b) => b.d - a.d); const pick = []; for (const x of cand) if (x.d > 0.5 && pick.length < 6 && !pick.some((y) => y.f === x.f)) pick.push(x);
    gamutBody = pick.length ? `<div class="sc-p3">${pick.map((x) => `<div><span class="sc-split"><span style="background:${x.srgb}"></span><span style="background:${x.p3}"></span></span><span class="sc-meta"><code>${esc(x.f)} ${x.step}</code><br>ΔE ${r1(x.d)}</span></div>`).join('')}</div><p class="sc-meta">left sRGB fallback · right P3 (light)${p3 ? '' : '; p3Fallback off: CSS has P3 only'}</p>`
      : note('Every step fits sRGB: the P3 upgrade changes nothing.', 'p3-none');
  }
  const g6 = group('brand', 'Brand', spec('anchors', 'Anchor report', 'requested → pinned step, Lc, ΔE', anchors.length ? panel('light', anchorTable) : anchorTable)
    + spec('ground-ink', ground || ink ? 'Ground and ink' : 'Page and ink', endsDesc, `<div class="sc-pair">${ends('light')}${ends('dark')}</div>`)
    + spec('gamut', 'P3 vs sRGB', 'widest-gamut steps', gamutBody));

  // ── 7. Data ─────────────────────────────────────────────────────────────────────────────────────────────
  const HEIGHTS = [62, 84, 48, 72, 38, 56];
  const barChart = (colors, labels) => `<div class="sc-bars">${colors.map((col, i) => `<div><span class="sc-bar" style="height:${HEIGHTS[i]}%;background:${col}"></span><i>${labels[i]}</i></div>`).join('')}</div>`;
  let dataBars, cvdBars, ramps;
  if (L.series) {
    dataBars = panel('light', `<p class="sc-meta"><b>normal vision</b> min ΔE ${L.seriesCvd.normal.minDE}</p><div class="sc-chart" style="background:${c('bg-subtle')}">${barChart(L.series.map((_, i) => c('data-' + (i + 1))), L.series.map((_, i) => String(i + 1)))}</div><p class="sc-meta">${L.series.map((s, i) => `${i + 1} ${esc(s.family)} ${s.step}`).join(' · ')}</p>`);
    const weak = ids.flatMap((id) => KINDS.filter((k) => json.modes[id].seriesCvd[k].minDE < json.modes[id].seriesCvd.threshold).map((k) => flag('series-weak', { mode: id, kind: k, value: json.modes[id].seriesCvd[k].minDE }, `${id} ${k} ${json.modes[id].seriesCvd[k].minDE}`)));
    const sim = (k) => { const s = L.seriesCvd[k]; return panel('light', `<p class="sc-meta"><b>${k}</b> min ΔE ${s.minDE} (${s.pair.join(' & ')})${s.minDE < L.seriesCvd.threshold ? ' ✗' : ''}</p><div class="sc-chart" style="background:${c('bg-subtle')}">${barChart(s.hex, s.hex.map((_, i) => String(i + 1)))}</div>`); };
    cvdBars = `<div class="sc-cvds">${sim('deutan')}${sim('protan')}</div><p class="sc-meta">Under ΔE ${L.seriesCvd.threshold} in any mode: ${weak.length ? weak.join(' ') : 'none ✓'}</p>`;
    const strip = (pre, list) => `<div class="sc-seq">${list.map((s, i) => `<span class="sw sc-cell" style="background:${c(pre + (i + 1))}"><i>${s.step}</i></span>`).join('')}</div>`;
    ramps = `<div class="sc-pair">${panel('light', `<p class="sc-meta">sequential · ${esc(L.sequential[0].family)} steps</p>${strip('data-seq-', L.sequential)}`, 'sc-half')}${L.diverging ? panel('light', `<p class="sc-meta">diverging · ${esc(L.diverging[0].family)} → gray → ${esc(L.diverging.at(-1).family)}</p>${strip('data-div-', L.diverging)}`, 'sc-half') : note('Diverging is off in this run (<code>diverging: true</code> adds it): sequential only.', 'no-diverging')}</div>`;
  } else { const off = note('Data series are off in this run (<code>series: false</code>).', 'series-off'); dataBars = cvdBars = ramps = off; }
  const g7 = group('data', 'Data', spec('series', 'Series', 'data-1…6 on bg-subtle', dataBars)
    + spec('series-cvd', 'Series under CVD', 'the same bars, simulated (light)', cvdBars)
    + spec('data-ramps', 'Sequential & diverging', 'labelled by step', ramps, 'sc-wide'));

  // ── 8. Scales & checks ──────────────────────────────────────────────────────────────────────────────────
  const tonal = json.tonal;
  const tonalBody = tonal ? `<div class="sc-tonal">${[...new Set([pf, 'gray'])].map((f) => { const tt = tonal[f]; if (!tt) return ''; return `<code>${esc(f)}</code><div class="sc-stops" style="--n:${tt.stops.length}">${tt.stops.map((x) => `<span class="sw sc-cell" title="${esc(f)} ${x.stop}" style="background:${v('--palette-' + f + '-' + x.stop)}"><i>${+x.stop / 10}</i></span>`).join('')}</div>${tt.primes ? `<code>primes</code><div class="sc-primes">${tt.primes.map((x) => `<span class="sc-dot" style="background:${v('--palette-' + f + '-' + x.name)}"></span><i>${esc(x.name)}</i>`).join('')}</div>` : ''}`; }).join('')}</div><p class="sc-meta">stop ÷ 10 (5 = 050); mode-independent${tonal[pf]?.primes ? '' : '; no Primes (<code>primes: true</code>)'}</p>`
    : note('The tonal layer is off in this run (<code>tonal: false</code>).', 'tonal-off');
  const shown = ['light', 'dark', extraId].filter(Boolean);
  // Weakest first: the smallest margin of |Lc| over the pair's APCA threshold.
  const matrix = (id) => { const M = json.modes[id], ps = [...M.contrast.pairs].sort((a, b) => (a.lc - a.threshold) - (b.lc - b.threshold)), miss = ps.filter((p) => !p.pass), rows = ps.slice(0, Math.max(5, Math.min(miss.length, 8)));
    return panel(id, `<table class="sc-t"><tr><th>${esc(id)}</th><th></th><th>Lc</th><th>needs</th><th>APCA</th></tr>${rows.map((p) => `<tr><td>${esc(p.fg)} on ${esc(p.bg)}</td><td><span class="sc-aa" style="background:${c(p.bg)};color:${c(p.fg)}">Aa</span></td><td>${p.lc}</td><td>${p.threshold}</td><td>${p.pass ? '✓' : '✗ miss'}</td></tr>`).join('')}</table>${miss.length > rows.length ? `<p class="sc-meta">+${miss.length - rows.length} more APCA misses in system.json</p>` : ''}`); };
  const aaLine = `<p class="sc-meta">APCA misses per mode: ${ids.map((id) => { const n = json.modes[id].contrast.summary.fail; return n ? flag('lc-miss', { mode: id, count: n }, `${id} ${n}`) : `<span class="sc-nw">${esc(id)} 0 ✓</span>`; }).join(' ')}</p>`;
  const tm = L.tonalMap?.primary;
  const mapBody = tm ? panel('light', `<div class="sc-map">${tm.steps.map((x) => `<div><span class="sw" style="background:${step(pf, x.step)}"></span><i>${x.step}</i><span class="sw" style="background:${v('--palette-' + tm.family + '-' + x.stop)}"></span><i>${x.stop}</i><i class="sc-de">${x.dE}</i></div>`).join('')}</div><p class="sc-meta">step (top) → nearest stop (bottom), ΔE; solid → ${esc(tm.solid)}</p>`)
    : note('No tonal map without the tonal layer.', 'tonal-off');
  const g8 = group('scales', 'Scales & checks', spec('tonal', 'Tonal 050–950', `${esc(pf)} and gray${tonal?.[pf]?.primes ? ' with Primes' : ''}`, tonalBody)
    + spec('contrast', 'Contrast excerpt', `five weakest pairs per shown mode, APCA Lc`, shown.map(matrix).join('') + aaLine)
    + spec('tonal-map', 'Tonal ↔ role map', 'primary steps → nearest stop', mapBody));

  const summary = `${ids.length} modes (${ids.join(', ')}) · ${esc(L.settings.generator)} · hue set ${esc(L.settings.hueSet)} · target ${esc(json.target)} · selectors ${esc(json.selectors)}${json.request.scope ? ' · scope ' + esc(json.request.scope) : ''}${json.request.lightDark ? ' · light-dark()' : ''}`;
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1280"><title>Colour system showcase</title><style>${css}</style><style>${SHEET}</style></head>
<body><main ${attrsOf('light', 'sc-sheet')} data-showcase="1"><header class="sc-head"><h1>Colour system showcase</h1><span>${summary}</span></header>
<div class="sc-grid">${g1}${g5}${g2}${g3}${g4}${g8}${g6}${g7}</div></main></body></html>\n`;
}

// Neutral chrome: layout and system type only. Every colour below is a variable of the run.
const SHEET = `
html,body{margin:0;padding:0}
.sc-sheet{box-sizing:border-box;width:1280px;height:960px;padding:12px;overflow:hidden;display:flex;flex-direction:column;gap:8px;background:var(--colors-bg);color:var(--colors-fg);font:11px/1.3 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.sc-sheet *{box-sizing:border-box}
.sc-head{display:flex;align-items:baseline;gap:12px;height:16px;white-space:nowrap}.sc-head h1{margin:0;font-size:13px}.sc-head span{color:var(--colors-fg-muted)}
.sc-grid{flex:1;min-height:0;display:grid;grid-template-columns:296px 296px 296px 1fr;grid-template-rows:318px 296px 1fr;gap:8px;grid-template-areas:"ramps ramps modes modes" "neutral roles transparency scales" "brand data data scales"}
.sc-group{min-width:0;min-height:0;overflow:hidden;border:1px solid var(--colors-border);border-radius:8px;padding:6px 8px 8px;display:flex;flex-direction:column;gap:5px}
.sc-group h2{margin:0;font-size:11px;line-height:14px;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.sc-g-ramps{grid-area:ramps;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:auto 1fr auto;column-gap:8px}.sc-g-ramps h2,.sc-wide{grid-column:1/-1}
.sc-g-modes{grid-area:modes;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:auto 1fr;column-gap:8px}.sc-g-modes h2{grid-column:1/4}
.sc-g-neutral{grid-area:neutral}.sc-g-roles{grid-area:roles}.sc-g-transparency{grid-area:transparency}.sc-g-scales{grid-area:scales}.sc-g-brand{grid-area:brand}
.sc-g-data{grid-area:data;display:grid;grid-template-columns:1fr 2fr;grid-template-rows:auto auto auto;align-content:start;column-gap:8px}.sc-g-data h2{grid-column:1/-1}
.sc-spec{margin:0;min-width:0;flex:none;display:flex;flex-direction:column;gap:3px}
.sc-spec figcaption{font-size:10px;line-height:13px;color:var(--colors-fg-muted);white-space:nowrap}.sc-spec figcaption b{color:var(--colors-fg)}
.sc-panel{background:var(--colors-bg);color:var(--colors-fg);border:1px solid var(--colors-border);border-radius:6px;padding:4px 6px;min-width:0}
.sc-pair{display:flex;gap:6px}.sc-half{flex:1;min-width:0}
.sw{display:block;border-radius:2px;min-height:6px}.sw.sc-lbl{font-size:8px;line-height:1;font-weight:700;display:flex;align-items:center;justify-content:center;overflow:hidden}.sw.sc-inline{display:inline-block;width:10px;height:10px;min-height:0;vertical-align:-1px;margin-right:3px;box-shadow:inset 0 0 0 1px var(--colors-border-strong)}
.sc-num{font-size:8.5px;line-height:10px;color:var(--colors-fg-muted);text-align:center}
code{font:9.5px ui-monospace,SFMono-Regular,Menlo,monospace}
.sc-meta{margin:0;font-size:9.5px;line-height:12px;color:var(--colors-fg-muted)}
.sc-note{margin:0;padding:6px 8px;border:1px dashed var(--colors-border-strong);border-radius:6px;color:var(--colors-fg-muted);font-size:10px}
.sc-flag{display:inline-block;padding:0 3px;border-radius:3px;font-size:9px;line-height:12px;font-weight:600;color:var(--colors-critical-fg);background:var(--colors-critical-subtle);box-shadow:inset 0 0 0 1px var(--colors-critical-border);margin:1px 0}
.sc-g-ramps .sc-spec:not(.sc-wide){flex:1;min-height:0}.sc-g-ramps .sc-spec:not(.sc-wide) .sc-panel{flex:1;min-height:0}
.sc-ramp{display:grid;grid-template-columns:44px repeat(12,1fr);grid-template-rows:10px repeat(var(--rows),1fr);gap:1px;height:100%}
.sc-ramp code{font-size:8.5px;line-height:1;align-self:center;overflow:hidden}
.sc-legend{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:2px 3px}
.sc-band{text-align:center;font-size:9px;line-height:11px;color:var(--colors-fg-muted);border-bottom:1px solid var(--colors-border-strong)}
.sc-step{display:flex;flex-direction:column;align-items:center;font-size:8.5px;line-height:10px}.sc-big{width:100%;height:18px;margin-bottom:1px}
.sc-step.is-solid .sc-big{outline:2px solid var(--colors-fg);outline-offset:1px}.sc-lc{font-weight:600;white-space:nowrap}.sc-tg{color:var(--colors-fg-muted);white-space:nowrap}
.sc-solid{margin:4px 0 0;font-size:9.5px;line-height:12px}.sc-chip{display:inline-block;padding:0 5px;border-radius:4px;font-size:9.5px;line-height:15px;white-space:nowrap}
.sc-row12{display:grid;grid-template-columns:30px repeat(12,1fr);gap:1px;align-items:center}
.sw.sc-cell{height:16px;position:relative}.sw.sc-cell i{position:absolute;left:0;right:0;top:100%;text-align:center;font-style:normal;font-size:8px;line-height:10px;color:var(--colors-fg-muted)}
.sc-row12{margin-bottom:10px}
.sc-ladder{display:flex;align-items:stretch;gap:4px;padding:3px;border-radius:4px;font-size:9px;line-height:10px}.sc-ladder div{flex:1;display:flex;gap:4px;padding:3px;border-radius:4px}.sc-ladder span{flex:none}
.sc-fills{display:flex;gap:3px}.sc-onsurf{padding:3px;border-radius:4px}
.sc-fams{display:grid;grid-template-columns:40px repeat(12,1fr);gap:2px 1px;align-items:center;margin-bottom:10px}.sc-fams code{font-size:8.5px;line-height:1}.sc-fams .sw.sc-cell{height:12px}
.sc-page{padding:5px;border-radius:4px;margin-bottom:2px}.sc-card2{display:flex;align-items:center;justify-content:space-between;gap:3px;padding:3px 5px;border:1px solid;border-radius:5px;font-size:9.5px;line-height:12px}.sc-well{border-radius:3px;padding:0 3px;font-size:8.5px}.sc-ctl{flex:1;text-align:center;line-height:16px;border:1px solid;border-radius:4px;font-size:9.5px}
.sc-solids{display:flex;flex-direction:column;gap:2px}.sc-solids div{display:flex;align-items:center;gap:4px}.sc-solids b{font-weight:600}
.sc-btn{display:inline-block;padding:0 8px;border-radius:4px;font-size:10px;line-height:17px;font-weight:600}
.sc-status{display:grid;grid-template-columns:auto auto 1fr auto;gap:1px 6px;align-items:center}.sc-status .sc-num{text-align:left}.sc-status code{line-height:15px}
.sc-focus{display:flex;align-items:center;gap:12px;padding:2px 3px}.sc-ring{outline:2px solid;outline-offset:2px}.sc-card{padding:0 8px;line-height:17px;border:1px solid;border-radius:5px;font-size:10px}
.sc-alpha{display:grid;grid-template-columns:36px repeat(12,1fr);grid-template-rows:10px 13px 13px;gap:1px}.sc-alpha code{font-size:8.5px;line-height:1;align-self:center}
.sc-inv{padding:2px 4px;border-radius:4px}.sc-inv .sc-num,.sc-inv code{color:inherit}
.sc-scrim{position:relative;height:56px;border-radius:4px;overflow:hidden}.sc-content{display:flex;flex-direction:column;gap:3px;padding:3px 4px}.sc-content>span:not(.sc-chip){height:5px;border-radius:2px;width:70%}.sc-content .sc-chip{align-self:flex-start}
.sc-backdrop{position:absolute;inset:0}.sc-dialog{position:absolute;left:34%;top:12px;right:6%;padding:5px 8px;border:1px solid;border-radius:6px;font-size:10px}
.sc-g-modes .sc-spec{min-height:0}.sc-mode{flex:1;display:flex;padding:8px}.sc-g-modes .sc-note{flex:1}
.sc-ui{flex:1;border:1px solid;border-radius:8px;padding:8px;display:flex;flex-direction:column;gap:4px}
.sc-ui p{margin:0;font-size:10px}.sc-ui-h{display:flex;justify-content:space-between;align-items:center;font-size:12px}.sc-ui-l{font-size:9.5px}
.sc-field{display:block;padding:2px 6px;border:1px solid;border-radius:4px}
.sc-list{display:flex;flex-direction:column}.sc-list span{padding:1px 6px;border-radius:4px}
.sc-alert{align-self:flex-start}.sc-mini{flex:1;min-height:24px;display:flex;align-items:flex-end;gap:4px}.sc-mini span{flex:1;border-radius:2px 2px 0 0}
.sc-ui-f{display:flex;gap:6px}
.sc-t{border-collapse:collapse;width:100%;font-size:9px;line-height:11px}.sc-t th{text-align:left;font-weight:600;color:var(--colors-fg-muted)}.sc-t td,.sc-t th{padding:0 4px 1px 0;border-bottom:1px solid var(--colors-border);white-space:nowrap}
.sc-anchors{display:flex;flex-direction:column;gap:3px;font-size:9.5px;line-height:12px}.sc-anchor{display:block}.sc-ok{color:var(--colors-fg-muted)}.sc-nw,.sc-flag{white-space:nowrap}.sc-marks{color:var(--colors-critical-fg)}
.sc-ends{display:flex;align-items:center;gap:6px;font-size:9px;line-height:11px}.sc-big2{display:inline-block;padding:2px 6px;border:1px solid;border-radius:4px;font-size:14px;font-weight:600}
.sc-p3{display:grid;grid-template-columns:repeat(3,1fr);gap:3px 6px}.sc-p3 div{display:flex;align-items:center;gap:4px;white-space:nowrap;min-width:0}.sc-p3 .sc-meta{line-height:10px}.sc-p3 code{font-size:8.5px}
.sc-split{display:inline-flex;flex:none;width:28px;height:16px;border-radius:3px;overflow:hidden}.sc-split span{flex:1}
.sc-chart{border-radius:4px;padding:4px 4px 0}
.sc-bars{display:flex;gap:4px;height:84px;align-items:stretch}.sc-bars div{flex:1;display:flex;flex-direction:column;justify-content:flex-end;min-width:0}
.sc-bar{display:block;border-radius:2px 2px 0 0}.sc-bars i{font-style:normal;font-size:8px;text-align:center;color:var(--colors-fg-muted);height:11px;line-height:11px}
.sc-cvds{display:flex;gap:8px}.sc-cvds>.sc-panel{flex:1}
.sc-seq{display:flex;gap:1px;margin-bottom:10px}.sc-seq .sw{flex:1;height:14px}
.sc-tonal{display:grid;grid-template-columns:40px 1fr;gap:0 4px;align-items:center}.sc-tonal code{align-self:start;line-height:16px}
.sc-stops{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:1px;margin-bottom:10px}
.sc-primes{display:flex;flex-wrap:wrap;align-items:center;gap:1px 2px}.sc-dot{width:9px;height:9px;border-radius:50%}.sc-primes i{font-style:normal;font-size:7.5px;line-height:10px;color:var(--colors-fg-muted);margin-right:2px}
.sc-g-scales .sc-spec .sc-panel+.sc-panel{margin-top:2px}.sc-aa{display:inline-block;padding:0 3px;border-radius:3px;box-shadow:inset 0 0 0 1px var(--colors-border)}
.sc-map{display:grid;grid-template-columns:repeat(12,1fr);gap:2px}.sc-map div{display:flex;flex-direction:column;align-items:center;gap:1px}.sc-map .sw{width:100%;height:12px}.sc-map i{font-style:normal;font-size:8px;line-height:9px}.sc-de{color:var(--colors-fg-muted)}
`;
