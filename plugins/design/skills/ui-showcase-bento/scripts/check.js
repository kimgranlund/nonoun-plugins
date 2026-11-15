// In-page checker for a bento showcase. scaffold.mjs inlines it; or evaluate this file in any page built to the contract.
//   uiBentoCheck()               every check, across every axis combination
//   uiBentoCheck({ final: true }) also fails on unfilled placeholders
//   uiBentoRects()               the box of every group, specimen and part, for diffing two renders
// Contract: [data-bento] canvas; [data-group] tiles; [data-specimen] entries; [data-label] for each name;
// optional parts: [data-part], or ui-materials' [data-layer]/[data-relief]/[data-face]; [data-inset] marks content deliberately off the content edge.
// The spec is read from <script type="application/json" id="bento-spec">, or passed as opts.spec.
;(function () {
  const r1 = (v) => Math.round(v * 100) / 100
  const rectOf = (el) => { const r = el.getBoundingClientRect(); return { x: r1(r.x), y: r1(r.y), w: r1(r.width), h: r1(r.height) } }
  const PARTS = '[data-group],[data-specimen],[data-part],[data-plane],[data-relief],[data-layer]'
  const keyOf = (el) => {
    if (el.dataset.group) return 'group:' + el.dataset.group
    if (el.dataset.specimen) return 'specimen:' + el.dataset.specimen
    const sp = el.closest('[data-specimen]')?.dataset.specimen ?? ''
    return 'part:' + sp + '/' + (el.dataset.part ?? el.dataset.plane ?? [el.dataset.layer, el.dataset.relief, el.dataset.face].filter(Boolean).join('.'))
  }
  function rects(root = document) {
    const seen = {}
    return [...root.querySelectorAll(PARTS)].map((el) => {
      let k = keyOf(el); seen[k] = (seen[k] ?? 0) + 1; if (seen[k] > 1) k += '#' + seen[k]
      return [k, rectOf(el)]
    })
  }
  const visible = (el) => { const cs = getComputedStyle(el); return cs.display !== 'none' && cs.visibility !== 'hidden' && +cs.opacity !== 0 }
  const scaleOf = (cs) => {
    if (cs.zoom && +cs.zoom !== 1) return +cs.zoom
    if (cs.scale && cs.scale !== 'none') return parseFloat(cs.scale)
    const m = cs.transform.match(/matrix\(([^)]+)\)/); if (!m) return 1
    const [a, b] = m[1].split(',').map(Number); return Math.hypot(a, b)
  }
  function layoutChecks(canvas, spec, errors, warnings, opts, tag = '') {
    const at = tag ? ` [${tag}]` : ''
    const tiles = [...canvas.querySelectorAll('[data-group]')]
    const needs = {}
    for (const t of tiles) {
      const id = t.dataset.group
      // Measure the content itself: scrollWidth/Height miss content that runs into the end padding, and a flex
      // child may shrink below its own content. Every visible box must sit inside the tile's content box.
      const tcs = getComputedStyle(t), tb = t.getBoundingClientRect()
      const box = { l: tb.left + parseFloat(tcs.paddingLeft), r: tb.right - parseFloat(tcs.paddingRight), t: tb.top + parseFloat(tcs.paddingTop), b: tb.bottom - parseFloat(tcs.paddingBottom) }
      let right = box.l, bottom = box.t, clip = null
      for (const el of t.querySelectorAll('*')) {
        if (!visible(el)) continue
        const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue
        right = Math.max(right, r.right); bottom = Math.max(bottom, r.bottom)
        if (!clip && (r.left < box.l - 0.5 || r.right > box.r + 0.5 || r.top < box.t - 0.5 || r.bottom > box.b + 0.5)) clip = el
      }
      const over = [Math.max(t.scrollWidth - t.clientWidth, right - box.r), Math.max(t.scrollHeight - t.clientHeight, bottom - box.b)]
      if (clip) errors.push(`clipped${at}: ${id} › ${clip.closest('[data-specimen]')?.dataset.specimen ?? clip.tagName.toLowerCase()} leaves the tile's content box`)
      if (over[0] > 1 || over[1] > 1) {
        needs[id] = [Math.ceil(t.getBoundingClientRect().width + Math.max(0, over[0])), Math.ceil(t.getBoundingClientRect().height + Math.max(0, over[1]))]
        errors.push(`overflow${at}: ${id} needs ${over[0] > 1 ? `${Math.ceil(over[0])}px more width ` : ''}${over[1] > 1 ? `${Math.ceil(over[1])}px more height` : ''}`.trim())
      }
    }
    for (let i = 0; i < tiles.length; i++) for (let j = i + 1; j < tiles.length; j++) {
      const a = tiles[i].getBoundingClientRect(), b = tiles[j].getBoundingClientRect()
      const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top)
      if (ox > 0.5 && oy > 0.5) errors.push(`overlap${at}: ${tiles[i].dataset.group} and ${tiles[j].dataset.group}`)
    }
    const cr = canvas.getBoundingClientRect()
    if (canvas.scrollWidth > canvas.clientWidth + 1 || canvas.scrollHeight > canvas.clientHeight + 1) errors.push(`canvas${at}: content scrolls`)
    for (const t of tiles) { const r = t.getBoundingClientRect(); if (r.right > cr.right + 0.5 || r.bottom > cr.bottom + 0.5) errors.push(`canvas${at}: ${t.dataset.group} leaves the canvas`) }
    return needs
  }
  function check(opts = {}) {
    const errors = [], warnings = []
    const specEl = document.getElementById('bento-spec')
    const spec = opts.spec ?? (specEl ? JSON.parse(specEl.textContent) : null)
    const canvas = document.querySelector('[data-bento]')
    if (!canvas) return { ok: false, errors: ['no [data-bento] canvas'], warnings }
    const cr = canvas.getBoundingClientRect()
    if (spec?.canvas && (Math.abs(cr.width - spec.canvas.width) > 0.5 || Math.abs(cr.height - spec.canvas.height) > 0.5))
      errors.push(`canvas is ${r1(cr.width)} × ${r1(cr.height)}, the spec says ${spec.canvas.width} × ${spec.canvas.height}`)

    // labels and counts
    for (const el of canvas.querySelectorAll('[data-group],[data-specimen]')) {
      const own = [...el.querySelectorAll('[data-label]')].find((l) => l.closest('[data-group],[data-specimen]') === el)
      if (!own || !own.textContent.trim()) errors.push(`label: ${keyOf(el)} has no [data-label] text`)
    }
    if (spec?.groups) {
      const count = (sel) => canvas.querySelectorAll(sel).length
      for (const g of spec.groups) {
        if (count(`[data-group="${g.id}"]`) !== 1) errors.push(`count: group ${g.id} appears ${count(`[data-group="${g.id}"]`)} times`)
        for (const s of g.specimens ?? []) {
          const n = count(`[data-specimen="${s.id}"]`)
          if (n !== 1) errors.push(`count: specimen ${s.id} appears ${n} times`)
          else if (!canvas.querySelector(`[data-group="${g.id}"] [data-specimen="${s.id}"]`)) errors.push(`count: specimen ${s.id} is outside group ${g.id}`)
        }
      }
      const known = new Set(spec.groups.flatMap((g) => (g.specimens ?? []).map((s) => s.id)))
      for (const el of canvas.querySelectorAll('[data-specimen]')) if (!known.has(el.dataset.specimen)) errors.push(`count: specimen ${el.dataset.specimen} is not in the spec`)
    }

    // never scaled
    for (const el of canvas.querySelectorAll('*')) {
      const s = scaleOf(getComputedStyle(el))
      if (Math.abs(s - 1) > 1e-3) { errors.push(`scaled: ${el.closest('[data-specimen]')?.dataset.specimen ?? el.tagName.toLowerCase()} is drawn at ${r1(s)}×; give it room instead`); break }
    }

    // placeholders, empty states, truncation
    const ph = canvas.querySelectorAll('[data-placeholder]')
    if (ph.length) (opts.final ? errors : warnings).push(`placeholder: ${ph.length} specimen slots are unfilled (${[...ph].slice(0, 4).map((p) => p.closest('[data-specimen]')?.dataset.specimen).join(', ')}${ph.length > 4 ? ', …' : ''})`)
    for (const el of canvas.querySelectorAll('[data-empty]')) if (!el.textContent.trim()) errors.push(`empty state: ${el.closest('[data-specimen]')?.dataset.specimen} says nothing; name what turns it on`)
    for (const el of canvas.querySelectorAll('*')) {
      const cs = getComputedStyle(el)
      if (cs.textOverflow === 'ellipsis' && el.scrollWidth > el.clientWidth + 1) warnings.push(`truncated: text in ${el.closest('[data-specimen]')?.dataset.specimen ?? '?'} is cut by an ellipsis`)
    }

    // one left edge per specimen: the caption and the first-level content, unless marked [data-inset]
    for (const sp of canvas.querySelectorAll('[data-specimen]')) {
      const cap = [...sp.querySelectorAll('[data-label]')].find((l) => l.closest('[data-specimen]') === sp)
      if (!cap) continue
      const edge = cap.getBoundingClientRect().left
      const slot = sp.querySelector('[data-slot]') ?? sp
      let lineBottom = -Infinity
      for (const el of slot.children) {
        if (el === cap || !visible(el)) continue
        const r = el.getBoundingClientRect()
        const starts = r.top >= lineBottom - 0.5   // only the first item of each line has to sit on the edge
        lineBottom = Math.max(starts ? r.bottom : lineBottom, r.bottom)
        if (!starts || el.hasAttribute('data-inset')) continue
        const l = r.left
        if (Math.abs(l - edge) > 0.5) { warnings.push(`edge: ${sp.dataset.specimen} has content ${r1(l - edge)}px off its caption's left edge (mark it [data-inset] if deliberate)`); break }
      }
    }

    // off the pixel grid: painted boxes only
    let off = 0
    for (const el of canvas.querySelectorAll('*')) {
      if (el.closest('[data-placeholder]')) continue
      const cs = getComputedStyle(el)
      const painted = cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || parseFloat(cs.borderTopWidth) > 0 || el.hasAttribute('data-part')
      if (!painted) continue
      const r = el.getBoundingClientRect()
      if ([r.left - cr.left, r.top - cr.top, r.width, r.height].some((v) => Math.abs(v - Math.round(v)) > 0.01)) off++
    }
    if (off) warnings.push(`grid: ${off} painted boxes sit off whole pixels`)

    // layout, then the same layout under every axis combination
    let needs = layoutChecks(canvas, spec, errors, warnings, opts)
    const axes = (spec?.axes ?? []).filter((a) => a.values?.length > 1)
    if (axes.length && opts.axes !== false) {
      const target = (a) => a.target === 'canvas' ? canvas : document.documentElement
      const saved = axes.map((a) => a.attr === 'class' ? target(a).className : target(a).getAttribute(a.attr))
      const set = (a, v) => {
        const t = target(a)
        if (a.attr === 'class') { for (const x of a.values) t.classList.remove(x); t.classList.add(v) } else t.setAttribute(a.attr, v)
      }
      let combos = [[]]
      for (const a of axes) combos = combos.flatMap((c) => a.values.map((v) => [...c, v]))
      const cap = opts.maxCombos ?? 256   // every combination of a normal sheet; only a very large matrix is sampled
      if (combos.length > cap) warnings.push(`axes: checked ${cap} of ${combos.length} combinations; pass { maxCombos: ${combos.length} } for all`)
      combos = combos.slice(0, cap)
      const baseline = {}, byAxis = new Map()
      for (const combo of combos) {
        combo.forEach((v, i) => set(axes[i], v))
        const tag = combo.map((v, i) => `${axes[i].name}=${v}`).join(' ')
        // report only what this combination adds over the base render, once per message
        const mine = []
        const n2 = layoutChecks(canvas, spec, mine, warnings, opts, tag); for (const k in n2) needs[k] = needs[k] ? needs[k].map((v, i) => Math.max(v, n2[k][i])) : n2[k]
        for (const m of mine) {
          const bare = m.replace(` [${tag}]`, '')
          if (errors.includes(bare)) continue
          const prev = byAxis.get(bare); if (prev) prev.n++; else byAxis.set(bare, { m, n: 0 })
        }
        // boxes must not move along an invariant axis: compare with the combination that differs only there
        const vary = combo.map((v, i) => axes[i].invariant === false ? v : '*').join('|')
        const now = Object.fromEntries(rects(canvas))
        if (!baseline[vary]) { baseline[vary] = { tag, now }; continue }
        const diffs = Object.keys(now).filter((k) => { const a = now[k], b = baseline[vary].now[k]; return !b || ['x', 'y', 'w', 'h'].some((p) => Math.abs(a[p] - b[p]) > 0.5) })
        if (diffs.length) errors.push(`invariance: ${diffs.length} boxes differ between [${baseline[vary].tag}] and [${tag}] (${diffs.slice(0, 3).join(', ')}${diffs.length > 3 ? ', …' : ''})`)
      }
      for (const { m, n } of byAxis.values()) errors.push(n ? `${m} (and ${n} more combinations)` : m)
      axes.forEach((a, i) => { const t = target(a); if (a.attr === 'class') t.className = saved[i]; else if (saved[i] == null) t.removeAttribute(a.attr); else t.setAttribute(a.attr, saved[i]) })
    }
    const dedupe = (xs) => [...new Set(xs)]
    const inv = errors.filter((e) => e.startsWith('invariance'))
    if (inv.length > 2) errors.splice(0, errors.length, ...errors.filter((e) => !e.startsWith('invariance')), inv[0], `invariance: and ${inv.length - 1} more combinations`)
    const out = { ok: !errors.length, errors: dedupe(errors), warnings: dedupe(warnings), needs }
    out.summary = `${out.ok ? 'PASS' : 'FAIL'}: ${out.errors.length} errors, ${out.warnings.length} warnings`
    return out
  }
  window.uiBentoCheck = check
  window.uiBentoRects = () => rects(document.querySelector('[data-bento]') ?? document)
  return 'uiBentoCheck ready'
})()
