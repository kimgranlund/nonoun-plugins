#!/usr/bin/env node
// Build the bento page: node scaffold.mjs <spec|source> [more…] --out page.html
//   [--content id] [--specimens dir] [--style file.css] [--mins needs.json] [--areas file.json] [--work dir] [--standalone]
// The page is an Artifact body (no doctype); --standalone adds the doctype and metas for a local file.
// dir/<specimen-id>.html fills a slot; a slot without a file shows its depiction as a placeholder.
// Re-run after every repack: specimens live in their own files, so nothing is lost.
import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { pack } from './lib.mjs'
import { cli } from './pack.mjs'

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c])
const HERE = dirname(fileURLToPath(import.meta.url))

// Selectors for the dark themes, whatever the theme axis sets: a class (ui-colors' .dark) or an attribute.
// When a source's theme axis is not data-theme, the OS preference must not dim the grid on a light theme.
function darkSelectors(spec) {
  const a = spec.axes.find((x) => x.name === 'theme')
  const dark = (a?.values ?? []).filter((v) => spec.chrome.darkThemes.includes(v))
  const sel = dark.map((v) => a.attr === 'class' ? `:root.${v}` : `:root[${a.attr}="${v}"]`)
  return (sel.length ? sel : [':root[data-theme="dark"]']).join(', ')
}

function lightSelectors(spec) {
  const a = spec.axes.find((x) => x.name === 'theme')
  if (!a || a.attr === 'data-theme') return ''
  const light = a.values.filter((v) => !spec.chrome.darkThemes.includes(v))
  return light.length ? `${light.map((v) => a.attr === 'class' ? `:root.${v}` : `:root[${a.attr}="${v}"]`).join(', ')} { --b-grid-minor: ${spec.chrome.gridStrength[0]}%; --b-grid-strong: ${spec.chrome.gridStrength[1]}% }\n` : ''
}

export function render(spec, p, { specimens, style } = {}) {
  const ch = spec.chrome, { width: W, height: H } = spec.canvas
  const css = spec.tokens.css.map((f) => {
    if (!existsSync(f)) throw new Error(`tokens: ${f} is missing.${spec.tokens.commands.length ? ' Produce it first: ' + spec.tokens.commands.join(' ; ') : ''}`)
    return `<style data-source="${esc(f.split('/').at(-1))}">\n${readFileSync(f, 'utf8')}\n</style>`
  }).join('\n')
  const colorMap = Object.entries(ch.colors ?? {}).map(([k, v]) => `--b-${k}: ${v};`).join(' ')
  const slot = (s) => {
    const f = specimens && join(specimens, s.id + '.html')
    if (f && existsSync(f)) return `<div class="b-slot" data-slot>${readFileSync(f, 'utf8')}</div>`
    return `<div class="b-slot" data-slot data-placeholder>${esc(s.depiction ?? 'specimen')}</div>`
  }
  const tiles = spec.groups.map((g) => `
  <section class="b-tile" data-group="${esc(g.id)}" aria-labelledby="g-${esc(g.id)}">
    <h2 class="b-title" id="g-${esc(g.id)}" data-label>${esc(g.label)}</h2>
    <div class="b-specimens${g.layout ? ' b-' + esc(g.layout) : ''}">${(g.specimens ?? []).map((s) => `
      <figure class="b-specimen" data-specimen="${esc(s.id)}"${s.grow ? ' data-grow' : ''}>
        <figcaption class="b-caption" data-label>${esc(s.label)}</figcaption>
        ${slot(s)}
      </figure>`).join('')}
    </div>
  </section>`).join('')
  const axes = spec.axes.map((a) => `<label>${esc(a.label ?? a.name)} <select data-axis="${esc(a.name)}">${a.values.map((v) => `<option>${esc(v)}</option>`).join('')}</select></label>`).join('')
  // An axis with captions names its current value in the bar (a material's settings, the anatomy legend).
  const sel = (a, v) => a.attr === 'class' ? `:root.${v}` : `:root[${a.attr}="${v}"]`
  const cssStr = (t) => '"' + String(t).replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"'
  const captionSpans = spec.axes.filter((a) => a.captions).map((a) => `<span class="b-cap" data-cap="${esc(a.name)}"></span>`).join('')
  const captionCss = spec.axes.filter((a) => a.captions).flatMap((a) => Object.entries(a.captions).map(([v, t]) =>
    `${[sel(a, v), ...Object.entries(a.aliases ?? {}).filter(([, to]) => to === v).map(([from]) => sel(a, from))].map((x) => `${x} [data-cap="${a.name}"]::after`).join(', ')} { content: ${cssStr(t)} }`)).join('\n')
  const pub = { id: spec.id, title: spec.title, sources: spec.sources, canvas: spec.canvas, axes: spec.axes,
    groups: spec.groups.map((g) => ({ id: g.id, label: g.label, specimens: (g.specimens ?? []).map(({ id, label }) => ({ id, label })) })) }
  return `<title>${esc(spec.title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="Bento showcase from ${esc(spec.sources.map((s) => s.id).join(', '))}">
${css}
<style>
:root { --b-bg: #f4f4f2; --b-tile: #ffffff; --b-fg: #1d1d1b; --b-muted: #6b6a66; --b-line: #dcdbd6; --b-slot: #ecebe7; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --b-bg: #121211; --b-tile: #1c1c1a; --b-fg: #ecebe7; --b-muted: #9a9993; --b-line: #33332f; --b-slot: #262624; color-scheme: dark } }
:root[data-theme="dark"] { --b-bg: #121211; --b-tile: #1c1c1a; --b-fg: #ecebe7; --b-muted: #9a9993; --b-line: #33332f; --b-slot: #262624; color-scheme: dark }
:root:root:root { ${colorMap} }
body { background: var(--b-bg); color: var(--b-fg); font-family: ${ch.font}; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 16px }
.b-bar { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; max-width: ${W}px; margin: 0 auto 12px; font-size: 12px; color: var(--b-muted) }
.b-bar h1 { font-size: 14px; margin: 0 auto 0 0; color: var(--b-fg); font-weight: 600 }
.b-bar select, .b-bar button { font: inherit }
.b-cap { flex-basis: 100%; order: 9; min-height: 1.4em }   /* the same height with or without a caption, so switching never moves the canvas */
${captionCss}
.b-scroll { overflow-x: auto; max-width: 100% }
[data-bento] { box-sizing: border-box; width: ${W}px; height: ${H}px; margin: 0 auto; padding: ${ch.margin}px; overflow: hidden;
  display: grid; gap: ${ch.gutter}px; grid-template-columns: ${p.columns.map((v) => v + 'px').join(' ')}; grid-template-rows: ${ch.header ? ch.header + 'px ' : ''}${p.rows.map((v) => v + 'px').join(' ')};
  grid-template-areas: ${ch.header ? `"${p.areas[0].split(/\s+/).map(() => 'header').join(' ')}" ` : ''}${p.areas.map((r) => `"${r}"`).join(' ')}; background: var(--b-bg) }
${spec.groups.map((g) => `[data-group="${g.id}"] { grid-area: ${g.id} }`).join('\n')}
.b-tile { box-sizing: border-box; min-width: 0; min-height: 0; overflow: hidden; padding: ${ch.pad}px; border-radius: ${ch.radius}px; background: var(--b-tile); display: flex; flex-direction: column; gap: ${ch.titleGap}px }
${ch.texture === 'grid' ? `/* Grid paper: every tile is ruled from its content edge, minor every ${ch.grid}px, major every ${ch.grid * ch.gridMajor}px.
   It gives overlays and glass something to sit over, so no specimen needs its own backdrop. */
:root { --b-grid-minor: ${ch.gridStrength[0]}%; --b-grid-strong: ${ch.gridStrength[1]}% }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --b-grid-minor: ${ch.gridStrengthDark[0]}%; --b-grid-strong: ${ch.gridStrengthDark[1]}% } }
${lightSelectors(spec)}${darkSelectors(spec)} { --b-grid-minor: ${ch.gridStrengthDark[0]}%; --b-grid-strong: ${ch.gridStrengthDark[1]}% }
.b-tile { --b-grid: color-mix(in oklab, var(--b-line) var(--b-grid-minor), transparent); --b-grid-major: color-mix(in oklab, var(--b-line) var(--b-grid-strong), transparent);
  background-color: var(--b-tile);
  background-image: linear-gradient(var(--b-grid-major) 1px, transparent 1px), linear-gradient(90deg, var(--b-grid-major) 1px, transparent 1px),
                    linear-gradient(var(--b-grid) 1px, transparent 1px), linear-gradient(90deg, var(--b-grid) 1px, transparent 1px);
  background-size: ${ch.grid * ch.gridMajor}px ${ch.grid * ch.gridMajor}px, ${ch.grid * ch.gridMajor}px ${ch.grid * ch.gridMajor}px, ${ch.grid}px ${ch.grid}px, ${ch.grid}px ${ch.grid}px;
  background-position: ${ch.pad}px ${ch.pad}px }
:root[data-bento-grid="off"] .b-tile { background-image: none }` : ''}
.b-title { flex: none; margin: 0; font-size: ${ch.title}px; font-weight: 600; line-height: 1.3 }
.b-specimens { display: flex; flex-wrap: wrap; align-content: flex-start; gap: ${ch.specimenGap}px; min-height: 0 }
.b-specimens.b-column { flex-direction: column; flex-wrap: nowrap }
/* Specimens and their parts never shrink: content that does not fit overflows its tile and the check reports it. */
.b-specimen { margin: 0; display: flex; flex-direction: column; gap: ${ch.captionGap}px; flex: 0 0 auto }
.b-specimen[data-grow] { flex: 1 1 100% }
.b-caption { font-size: ${ch.caption}px; line-height: 1.3; color: var(--b-muted) }
.b-slot { display: flex; flex-wrap: wrap; gap: ${ch.specimenGap / 2}px; align-items: flex-start }
.b-slot > * { flex-shrink: 0 }
/* A placeholder takes what the row leaves, so an unfilled sheet never overflows. */
.b-specimen:has(> [data-placeholder]) { flex: 1 1 140px; min-width: 0 }
.b-slot[data-placeholder] { box-sizing: border-box; padding: 8px; border-radius: 6px; background: var(--b-slot); font-size: 11px; color: var(--b-muted) }
.b-out { font-family: ui-monospace, monospace }
</style>
${style ? `<style data-source="specimens">\n${readFileSync(style, 'utf8')}\n</style>` : ''}
<header class="b-bar"><h1>${esc(spec.title)}</h1>${axes}<button type="button" data-run-check>Check</button><span class="b-out" data-check-out></span>${captionSpans}</header>
<div class="b-scroll"><main data-bento aria-label="${esc(spec.title)}">${ch.header ? `\n  <div style="grid-area:header" data-header></div>` : ''}${tiles}
</main></div>
<script type="application/json" id="bento-spec">${JSON.stringify(pub).replace(/</g, '\\u003c')}</script>
<script>
${readFileSync(join(HERE, 'check.js'), 'utf8')}
;(function () {
  const spec = JSON.parse(document.getElementById('bento-spec').textContent)
  const key = 'ui-bento:' + spec.id
  let saved = {}; try { saved = JSON.parse(localStorage.getItem(key) || '{}') } catch {}
  const target = (a) => a.target === 'canvas' ? document.querySelector('[data-bento]') : document.documentElement
  const apply = (a, v) => { const t = target(a); if (a.attr === 'class') { a.values.forEach((x) => t.classList.remove(x)); t.classList.add(v) } else t.setAttribute(a.attr, v) }
  for (const a of spec.axes) {
    const sel = document.querySelector('[data-axis="' + a.name + '"]')
    const prefer = a.name === 'theme' && matchMedia('(prefers-color-scheme: dark)').matches && a.values.includes('dark') ? 'dark' : a.values[0]
    const was = (a.aliases ?? {})[saved[a.name]] ?? saved[a.name]   // a retired value maps to its replacement
    const v = a.values.includes(was) ? was : prefer
    sel.value = v; apply(a, v)
    sel.addEventListener('change', () => { apply(a, sel.value); saved[a.name] = sel.value; try { localStorage.setItem(key, JSON.stringify(saved)) } catch {} })
  }
  document.querySelector('[data-run-check]').addEventListener('click', () => {
    const r = uiBentoCheck(); document.querySelector('[data-check-out]').textContent = r.summary + (r.errors[0] ? ' · ' + r.errors[0] : '')
  })
})()
</script>
`
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    const { spec, o } = cli(process.argv.slice(2))
    if (!o.out) throw new Error('--out page.html is required')
    const p = pack(spec)
    const head = o.standalone ? '<!doctype html>\n<html lang="en"><meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<style>body{margin:0}</style>\n' : ''
    writeFileSync(o.out, head + render(spec, p, { specimens: o.specimens, style: o.style }))
    const n = spec.groups.reduce((s, g) => s + (g.specimens?.length ?? 0), 0)
    const filled = o.specimens ? spec.groups.flatMap((g) => g.specimens ?? []).filter((s) => existsSync(join(o.specimens, s.id + '.html'))).length : 0
    console.log(`wrote ${o.out}: ${spec.groups.length} groups, ${n} specimens (${filled} filled), columns ${p.columns.join('/')}, rows ${p.rows.join('/')}; axes ${spec.axes.map((a) => a.name).join(', ')}`)
  } catch (e) { console.error(e.message); process.exit(e.code === 'NOFIT' ? 1 : 2) }
}
