// Browser collector: measures rendered components and returns lengths.json for fit.mjs.
// Evaluate this file in the page (a browser tool's JavaScript runner, or the DevTools console), then:
//   uiGeometryCollect([
//     { id: 'button', kind: 'control', selector: '.btn-primary' },
//     { id: 'input', kind: 'control', selector: 'input[type=text]' },
//     { id: 'menu', kind: 'frame', selector: '[role=menu]', item: '[role=menuitem]' },
//     { id: 'tabs', kind: 'host', selector: '[role=tablist]', item: '[role=tab]' },
//     { id: 'card', kind: 'card', selector: '.card' },
//     { id: 'page', kind: 'layout', selector: 'main .grid' },
//     { id: 'checkbox', kind: 'mark', selector: 'input[type=checkbox]' },
//   ], { source: 'my-app' })
// Kinds: control, group (a row of controls: its gap), frame (+ item), host (a segmented control or tab list, + item),
// card, layout, mark. List one control per size (sm, default, lg): fit.mjs reads sizes as densities.
// Paddings include the border, because the system measures depth from the outer edge (d − b is inside),
// and each padding records the border it includes, so the fit never has to guess.
// Returns { source, n, lengths, missing }. List the primary control first: ties in fit.mjs go to the first listed.
;(function () {
  const num = (v) => parseFloat(v) || 0
  const round = (v) => Math.round(v * 100) / 100
  function collect(spec, opts = {}) {
    const lengths = [], missing = []
    let n = opts.n
    const put = (comp, role, px, border) => { if (px > 0 || role.endsWith('gap')) lengths.push({ id: `${comp}.${role}`, component: comp, role, px: round(px), ...(border === undefined ? {} : { border: round(border) }) }) }
    for (const s of spec) {
      const el = document.querySelector(s.selector)
      if (!el) { missing.push(s.id); continue }
      const cs = getComputedStyle(el), box = el.getBoundingClientRect()
      const bL = num(cs.borderLeftWidth), bT = num(cs.borderTopWidth)
      const padL = num(cs.paddingLeft) + bL, padT = num(cs.paddingTop) + bT
      const radius = Math.min(num(cs.borderTopLeftRadius), box.height / 2)
      const gap = num(cs.columnGap) || num(cs.rowGap) || num(cs.gap)
      if (s.kind === 'control') {
        if (n === undefined) n = num(cs.fontSize)
        put(s.id, 'height', box.height)
        put(s.id, 'label-inset', padL, bL)
        put(s.id, 'radius', radius)
        const icon = el.querySelector(s.icon || 'svg, img, [class*="icon"]')
        if (icon) put(s.id, 'icon', icon.getBoundingClientRect().height)
      } else if (s.kind === 'group') {
        put(s.id, 'control-gap', gap)
      } else if (s.kind === 'frame') {
        put(s.id, 'frame-depth', padT, bT)
        put(s.id, 'frame-radius', radius)
        const item = s.item ? el.querySelector(s.item) : el.firstElementChild
        if (item) {
          const ics = getComputedStyle(item), ib = item.getBoundingClientRect()
          put(s.id, 'row', ib.height)
          put(s.id, 'row-radius', Math.min(num(ics.borderTopLeftRadius), ib.height / 2))
          put(s.id, 'item-inset', num(ics.paddingLeft))
          const next = item.nextElementSibling
          if (next) put(s.id, 'row-gap', Math.max(0, next.getBoundingClientRect().top - ib.bottom))
        }
      } else if (s.kind === 'host') {
        put(s.id, 'host-height', box.height)
        put(s.id, 'host-depth', padT, bT)
        put(s.id, 'host-radius', radius)
        const item = s.item ? el.querySelector(s.item) : el.firstElementChild
        if (item) {
          const ics = getComputedStyle(item), ib = item.getBoundingClientRect()
          put(s.id, 'segment', ib.height)
          put(s.id, 'segment-radius', Math.min(num(ics.borderTopLeftRadius), ib.height / 2))
        }
      } else if (s.kind === 'card') {
        put(s.id, 'card-depth', padT, bT)
        put(s.id, 'card-radius', radius)
        if (gap) put(s.id, 'card-gap', gap)
      } else if (s.kind === 'layout') {
        put(s.id, 'gutter', gap)
        put(s.id, 'margin', padL)
      } else if (s.kind === 'mark') {
        put(s.id, 'mark', box.height)
      }
    }
    return { source: opts.source ?? location.href, n: n ?? num(getComputedStyle(document.documentElement).fontSize), lengths, missing }
  }
  window.uiGeometryCollect = collect
  return 'uiGeometryCollect ready'
})()
