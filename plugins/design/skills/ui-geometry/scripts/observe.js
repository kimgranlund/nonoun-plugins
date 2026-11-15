// Page observer: measures a rendered page and returns the observables of references/archetypes.json.
// Evaluate this file in the page (a browser tool's JavaScript runner, the DevTools console, or scripts/observe.mjs), then:
//   uiGeometryObserve()                  → { viewport, observables, notMeasured }
// It reads the first three viewports at the current width. Set a 1440 × 900 viewport and a light colour-scheme
// preference to compare with the profiles, which were measured that way.
// Three kinds of observable need more than one evaluation and are left to scripts/observe.mjs:
//   pixels (uiGeometryObserve.pixelStats on a screenshot), followsScheme (a second load preferring dark) and
//   bodyRatio (a second load at 390px).
// Colour is read in HCT (uiGeometryObserve.math.hct); contrast as APCA Lc and WCAG 2 ratio.
// The APCA constants are those published for APCA-W3 0.0.98G-4g and are used here to measure web content.
;(function () {
  const math = (() => {
  const lin = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4 }
  const xyz = ([r, g, b]) => { r = lin(r) * 100; g = lin(g) * 100; b = lin(b) * 100; return [0.41233895 * r + 0.35762064 * g + 0.18051042 * b, 0.2126 * r + 0.7152 * g + 0.0722 * b, 0.01932141 * r + 0.11916382 * g + 0.95034478 * b] }
  const lstar = (y) => { y /= 100; return y > 216 / 24389 ? 116 * Math.cbrt(y) - 16 : (24389 / 27) * y }
  const yFromL = (L) => 100 * (L > 8 ? ((L + 16) / 116) ** 3 : L / (24389 / 27))
  const cone = ([x, y, z]) => [0.401288 * x + 0.650173 * y - 0.051461 * z, -0.250268 * x + 1.204414 * y + 0.045854 * z, -0.002079 * x + 0.048952 * y + 0.953127 * z]
  // viewing conditions: D65 white, adapting luminance (200/π)·Y(L*50)/100, background L* 50, average surround
  const W = [95.047, 100, 108.883], La = (200 / Math.PI) * yFromL(50) / 100, n = yFromL(50) / W[1], c = 0.69, Nc = 1
  const k = 1 / (5 * La + 1), FL = 0.2 * k ** 4 * (5 * La) + 0.1 * (1 - k ** 4) ** 2 * Math.cbrt(5 * La)
  const D = Math.min(1, Math.max(0, 1 - (1 / 3.6) * Math.exp((-La - 42) / 92))), rgbW = cone(W), rgbD = rgbW.map((v) => D * (100 / v) + 1 - D)
  const Nbb = 0.725 / n ** 0.2, z = 1.48 + Math.sqrt(n)
  const adapt = (v) => { const f = (FL * Math.abs(v) / 100) ** 0.42; return Math.sign(v) * 400 * f / (f + 27.13) }
  const Aw = (() => { const [r, g, b] = rgbW.map((v, i) => adapt(v * rgbD[i])); return (2 * r + g + 0.05 * b) * Nbb })()
  /** HCT of an sRGB colour: { h: hue in degrees, c: chroma, t: tone }. */
  const hct = (rgb) => {
    const X = xyz(rgb), [rA, gA, bA] = cone(X).map((v, i) => adapt(v * rgbD[i]))
    const a = (11 * rA - 12 * gA + bA) / 11, b = (rA + gA - 2 * bA) / 9, u = (20 * rA + 20 * gA + 21 * bA) / 20, p2 = (40 * rA + 20 * gA + bA) / 20
    const hue = ((Math.atan2(b, a) * 180) / Math.PI + 360) % 360, J = 100 * (p2 * Nbb / Aw) ** (c * z)
    const hp = hue < 20.14 ? hue + 360 : hue, e = 0.25 * (Math.cos((hp * Math.PI) / 180 + 2) + 3.8)
    const t = ((50000 / 13) * e * Nc * Nbb * Math.hypot(a, b)) / (u + 0.305), alpha = t ** 0.9 * (1.64 - 0.29 ** n) ** 0.73
    return { h: hue, c: alpha * Math.sqrt(J / 100), t: lstar(X[1]) }
  }
  const relL = ([r, g, b]) => 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
  /** WCAG 2 contrast ratio, 1 to 21. */
  const wcag = (a, b) => { const x = relL(a), y = relL(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05) }
  const sY = ([r, g, b]) => 0.2126729 * (r / 255) ** 2.4 + 0.7151522 * (g / 255) ** 2.4 + 0.0721750 * (b / 255) ** 2.4
  /** APCA Lc, signed: positive for dark text on a light ground. Constants as published for 0.0.98G-4g; for measuring web content. */
  const apca = (txt, bg) => {
    const clamp = (y) => (y > 0.022 ? y : y + (0.022 - y) ** 1.414), T = clamp(sY(txt)), B = clamp(sY(bg))
    if (Math.abs(B - T) < 0.0005) return 0
    if (B > T) { const s = (B ** 0.56 - T ** 0.57) * 1.14; return s < 0.1 ? 0 : (s - 0.027) * 100 }
    const s = (B ** 0.65 - T ** 0.62) * 1.14; return s > -0.1 ? 0 : (s + 0.027) * 100
  }
  return { hct, wcag, apca }
})()
  const PART = {
    base: (() => {
  const W = innerWidth, H = innerHeight, maxY = 3 * H
  const num = (v) => parseFloat(v) || 0, r2 = (v) => v == null ? null : Math.round(v * 100) / 100
  const q = (a, p) => { if (!a.length) return null; a = [...a].sort((x, y) => x - y); return a[Math.min(a.length - 1, Math.floor(a.length * p))] }
  const med = (a) => q(a, 0.5)
  const banner = (e) => e.closest('[id*="cookie" i],[class*="cookie" i],[id*="consent" i],[class*="consent" i],[id*="onetrust" i]')
  const clear = (c) => !c || c === 'transparent' || /rgba\(.*,\s*0\)$/.test(c)
  // text
  const sizes = {}, lefts = [], rights = [], longs = []
  let total = 0, upper = 0, cov1 = 0, cov3 = 0, n0 = 0
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT), range = document.createRange()
  let nd
  while ((nd = tw.nextNode()) && n0 < 8000) {
    const t = nd.nodeValue.trim(); if (!t) continue
    const p = nd.parentElement; if (!p || /^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA|OPTION)$/.test(p.tagName) || banner(p)) continue
    const c = getComputedStyle(p); if (c.visibility === 'hidden' || c.display === 'none' || +c.opacity === 0) continue
    range.selectNodeContents(nd); const rs = [...range.getClientRects()].filter((r) => r.width > 1 && r.height > 1)
    if (!rs.length || rs[0].top + scrollY > maxY || rs[0].right < 0 || rs[0].left > W) continue
    n0++
    const fs = r2(num(c.fontSize)); sizes[fs] = (sizes[fs] || 0) + t.length; total += t.length
    if (c.textTransform === 'uppercase' || (t.length > 2 && t === t.toUpperCase() && /[A-Z]/.test(t))) upper += t.length
    for (const r of rs) { const y = r.top + scrollY, a = r.width * r.height; if (y < maxY) cov3 += a; if (y < H) cov1 += a; lefts.push(r.left); rights.push(r.right) }
    if (t.length > 150) longs.push({ fs, cpl: t.length / rs.length, w: Math.max(...rs.map((r) => r.width)), left: Math.min(...rs.map((r) => r.left)), lh: num(c.lineHeight) / fs, wt: +c.fontWeight })
  }
  const ranked = Object.entries(sizes).map(([s, n]) => [+s, n]).sort((a, b) => b[1] - a[1])
  const body = ranked[0]?.[0] || 16
  const used = ranked.filter(([, n]) => n / total >= 0.01).map(([s]) => s).sort((a, b) => a - b)
  const display = Math.max(...ranked.filter(([, n]) => n >= 6).map(([s]) => s), body)
  const bl = longs.filter((l) => l.fs === body)
  // controls
  const ctl = []
  for (const e of document.querySelectorAll('button,[role=button],input:not([type=hidden]):not([type=checkbox]):not([type=radio]),select,a')) {
    if (banner(e)) continue
    const b = e.getBoundingClientRect(); if (b.height < 10 || b.height > 160 || b.width < 10 || b.top + scrollY > maxY) continue
    const c = getComputedStyle(e); if (c.visibility === 'hidden' || c.display === 'none') continue
    const bw = num(c.borderTopWidth), boxed = !clear(c.backgroundColor) || (bw > 0 && c.borderTopStyle !== 'none' && !clear(c.borderTopColor))
    if (e.tagName === 'A' && !boxed) continue
    const txt = (e.innerText || e.value || e.placeholder || '').trim()
    ctl.push({ h: b.height, w: b.width, fs: num(c.fontSize), pad: num(c.paddingLeft) + bw, r: Math.min(num(c.borderTopLeftRadius), b.height / 2), bw, boxed, txt: txt.length > 0, up: c.textTransform === 'uppercase', ls: num(c.letterSpacing) / num(c.fontSize), wt: +c.fontWeight })
  }
  const tc = ctl.filter((x) => x.txt && x.boxed), ic = ctl.filter((x) => !x.txt)
  // icons
  const icons = []
  for (const e of document.querySelectorAll('svg')) {
    const b = e.getBoundingClientRect(); if (b.width < 8 || b.width > 72 || b.width / b.height < 0.7 || b.width / b.height > 1.4 || b.top + scrollY > maxY || banner(e)) continue
    const vb = e.viewBox?.baseVal?.width || b.width; let sw = 0
    const sh = e.querySelector('path,line,circle,rect,polyline'); if (sh) { const sc = getComputedStyle(sh); if (sc.stroke !== 'none') sw = num(sc.strokeWidth) }
    icons.push({ s: b.width, sr: sw ? sw / vb : 0 })
  }
  // surfaces: shadows, borders, radii, media
  let shadows = 0, hard = [], bordered = 0, bws = [], radii = [], surf = 0, img1 = 0, img3 = 0, seen = 0
  for (const e of document.body.querySelectorAll('*')) {
    if (seen > 6000) break
    const b = e.getBoundingClientRect(); if (b.width < 8 || b.height < 8 || b.top + scrollY > maxY || b.bottom + scrollY < 0) continue
    seen++
    const c = getComputedStyle(e); if (c.visibility === 'hidden' || c.display === 'none') continue
    if (/^(IMG|VIDEO|PICTURE|CANVAS)$/.test(e.tagName) || (c.backgroundImage.includes('url(') && b.width > 60)) {
      if (e.tagName === 'PICTURE') continue
      const x0 = Math.max(0, b.left), x1 = Math.min(W, b.right), y0 = b.top + scrollY, y1 = b.bottom + scrollY
      if (x1 > x0) { img3 += (x1 - x0) * Math.max(0, Math.min(maxY, y1) - Math.max(0, y0)); img1 += (x1 - x0) * Math.max(0, Math.min(H, y1) - Math.max(0, y0)) }
    }
    if (c.boxShadow !== 'none') {
      const layers = c.boxShadow.split(/,(?![^(]*\))/).filter((l) => !/inset/.test(l)).map((l) => l.replace(/rgba?\([^)]*\)|#\w+|[a-z]+\([^)]*\)/g, '').trim().split(/\s+/).map(num))
      const real = layers.filter((l) => Math.abs(l[0]) + Math.abs(l[1]) + (l[2] || 0) > 1 || (l[3] || 0) > 1.5)
      if (real.length) { shadows++; const big = real.sort((a, b2) => (Math.abs(b2[1]) + (b2[2] || 0)) - (Math.abs(a[1]) + (a[2] || 0)))[0]; const off = Math.abs(big[0]) + Math.abs(big[1]); hard.push(off > 0 ? (big[2] || 0) / off : 99) }
    }
    const bw = Math.max(num(c.borderTopWidth), num(c.borderBottomWidth), num(c.borderLeftWidth))
    const hasB = bw > 0 && [c.borderTopStyle, c.borderBottomStyle, c.borderLeftStyle].some((s) => s !== 'none') && ![c.borderTopColor, c.borderBottomColor, c.borderLeftColor].every(clear)
    if (hasB) { bordered++; bws.push(bw) }
    if ((hasB || !clear(c.backgroundColor)) && b.width > 40 && b.height > 24 && b.width < W * 0.98) { surf++; radii.push(Math.min(num(c.borderTopLeftRadius), b.height / 2, b.width / 2) / Math.min(b.height, b.width) * 2) }
  }
  const L = q(lefts, 0.03), R = q(rights, 0.97)
  return JSON.stringify({
    url: location.host + location.pathname.slice(0, 40), W, H, pages: r2(document.documentElement.scrollHeight / H),
    type: { body, display, contrast: r2(display / body), min: used[0], sizes: used, nSizes: used.length, upperShare: r2(upper / total), bodyLH: r2(med(bl.map((l) => l.lh))), bodyWt: med(bl.map((l) => l.wt)) },
    layout: { margin: r2(L), marginEm: r2(L / body), occupancy: r2((R - L) / W), measureCPL: r2(med(bl.map((l) => l.cpl))), colW: r2(med(bl.map((l) => l.w))), colLeft: r2(med(bl.map((l) => l.left))), textCov1: r2(cov1 / (W * H)), textCov3: r2(cov3 / (W * maxY)), imgCov1: r2(img1 / (W * H)), imgCov3: r2(img3 / (W * maxY)) },
    controls: { n: ctl.length, boxedText: tc.length, iconOnly: ic.length, h: r2(med(tc.map((x) => x.h))), fs: r2(med(tc.map((x) => x.fs))), loft: r2(med(tc.map((x) => x.h / x.fs))), loftLo: r2(q(tc.map((x) => x.h / x.fs), 0.1)), loftHi: r2(q(tc.map((x) => x.h / x.fs), 0.9)), padEm: r2(med(tc.map((x) => x.pad / x.fs))), kappa: r2(med(tc.map((x) => x.r / (x.h / 2)))), bw: r2(med(tc.map((x) => x.bw))), labelToBody: r2(med(tc.map((x) => x.fs)) / body), upShare: r2(tc.filter((x) => x.up).length / (tc.length || 1)), track: r2(med(tc.map((x) => x.ls))), wt: med(tc.map((x) => x.wt)), iconBtnH: r2(med(ic.map((x) => x.h))) },
    icons: { n: icons.length, size: r2(med(icons.map((i) => i.s))), toBody: r2(med(icons.map((i) => i.s)) / body), strokeShare: r2(icons.filter((i) => i.sr).length / (icons.length || 1)), strokeRatio: r2(med(icons.filter((i) => i.sr).map((i) => i.sr)) * 1000) / 1000 },
    body3: { els: seen, shadows, shadowBlurPerOffset: r2(med(hard)), bordered, borderShare: r2(bordered / seen), bw: med(bws), bwMax: q(bws, 0.95), surfaces: surf, kappaMed: r2(med(radii)), squareShare: r2(radii.filter((r) => r < 0.02).length / (radii.length || 1)), pillShare: r2(radii.filter((r) => r > 0.9).length / (radii.length || 1)) },
  })
}),
    extra: (() => {
  const W = innerWidth, H = innerHeight, maxY = 3 * H
  const num = (v) => parseFloat(v) || 0, r2 = (v) => v == null || Number.isNaN(v) ? null : Math.round(v * 100) / 100
  const med = (a) => { a = a.filter((v) => v != null && !Number.isNaN(v)).sort((x, y) => x - y); return a.length ? a[a.length >> 1] : null }
  const clear = (c) => !c || c === 'transparent' || /rgba\(.*,\s*0\)$/.test(c)
  const banner = (e) => e.closest('[id*="cookie" i],[class*="cookie" i],[id*="consent" i],[class*="consent" i],[id*="onetrust" i]')
  let total = 0, mono = 0, heavy = 0, wsum = 0, n0 = 0; const sizes = {}
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let nd
  while ((nd = tw.nextNode()) && n0 < 8000) {
    const t = nd.nodeValue.trim(); if (!t) continue
    const p = nd.parentElement; if (!p || /^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA|OPTION)$/.test(p.tagName) || banner(p)) continue
    const c = getComputedStyle(p); if (c.visibility === 'hidden' || c.display === 'none' || +c.opacity === 0) continue
    const b = p.getBoundingClientRect(); if (b.width < 1 || b.top + scrollY > maxY) continue
    n0++; total += t.length; const fs = num(c.fontSize); sizes[fs] = (sizes[fs] || 0) + t.length
    if (/mono|courier|consolas|menlo|fixed|terminal/i.test(c.fontFamily)) mono += t.length
    const w = +c.fontWeight || 400; wsum += w * t.length; if (w >= 700) heavy += t.length
  }
  const ranked = Object.entries(sizes).sort((a, b) => b[1] - a[1]), body = +(ranked[0]?.[0] || 16)
  const display = Math.max(...ranked.filter(([, n]) => n >= 6).map(([s]) => +s), body)
  // buttons: the painted face may be the element, a near descendant or a pseudo-element
  const painted = (c) => !clear(c.backgroundColor) || c.backgroundImage !== 'none' || (num(c.borderTopWidth) > 0 && c.borderTopStyle !== 'none' && !clear(c.borderTopColor))
  const face = (e) => {
    const c = getComputedStyle(e); if (painted(c)) return { c, b: e.getBoundingClientRect() }
    for (const ps of ['::before', '::after']) { const pc = getComputedStyle(e, ps); if (pc.content !== 'none' && painted(pc)) return { c: pc, b: e.getBoundingClientRect() } }
    for (const k of e.querySelectorAll(':scope > *, :scope > * > *')) { const kc = getComputedStyle(k), kb = k.getBoundingClientRect(); if (kb.height >= 16 && kb.width >= 24 && painted(kc)) return { c: kc, b: kb } }
    return null
  }
  const btn = []
  for (const e of document.querySelectorAll('button,[role=button],a,input[type=submit],input[type=button]')) {
    if (banner(e)) continue
    const eb = e.getBoundingClientRect(); if (eb.height < 12 || eb.height > 240 || eb.width < 24 || eb.top + scrollY > maxY) continue
    const ec = getComputedStyle(e); if (ec.visibility === 'hidden' || ec.display === 'none') continue
    const txt = (e.innerText || e.value || '').trim(); if (!txt || txt.length > 40 || txt.includes('\n')) continue
    const f = face(e); if (!f || f.b.height > 240 || f.b.width > W * 0.9) continue
    let fs = num(ec.fontSize); const leaf = [...e.querySelectorAll('*')].find((k) => k.childElementCount === 0 && k.textContent.trim()); if (leaf) fs = num(getComputedStyle(leaf).fontSize)
    const sh = f.c.boxShadow !== 'none' ? f.c.boxShadow.split(/,(?![^(]*\))/).filter((l) => !/inset/.test(l)).map((l) => l.replace(/rgba?\([^)]*\)|#\w+|[a-z]+\([^)]*\)/g, '').trim().split(/\s+/).map(num)) : []
    const hard = sh.some((l) => Math.abs(l[1]) >= 2 && (l[2] || 0) <= 1) || num(f.c.borderBottomWidth) >= num(f.c.borderTopWidth) + 2
    btn.push({ h: f.b.height, fs, k: Math.min(num(f.c.borderTopLeftRadius), f.b.height / 2) / (f.b.height / 2), hard, w: +(leaf ? getComputedStyle(leaf).fontWeight : ec.fontWeight) || 400 })
  }
  return JSON.stringify({ monoShare: r2(mono / (total || 1)), heavyShare: r2(heavy / (total || 1)), meanWeight: Math.round(wsum / (total || 1)), bodyVh: r2(body / H * 100), displayVh: r2(display / H * 100),
    buttons: btn.length, loft2: r2(med(btn.map((x) => x.h / x.fs))), btnToBody: r2(med(btn.map((x) => x.h)) / body), kappa2: r2(med(btn.map((x) => x.k))), hardShare: r2(btn.filter((x) => x.hard).length / (btn.length || 1)), btnWeight: med(btn.map((x) => x.w)) })
}),
    fontMetrics: (family, weight = 400, raw = false) => {
  const SZ = 400, W = SZ * 3, H = SZ * 2, BASE = Math.round(SZ * 1.4), X0 = Math.round(SZ * 0.5)
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H
  const cx = cv.getContext('2d', { willReadFrequently: true })
  const font = (fam) => `${weight} ${SZ}px ${fam}`
  const adv = (s, fam) => { cx.font = font(fam); return cx.measureText(s).width }
  // availability: the family must change the advance of a test string against two different fallbacks
  const probe = 'mmmmmmmmmmlliWQ@g', q = `"${family}"`, generic = /^(system-ui|ui-serif|ui-sans-serif|ui-monospace|ui-rounded|serif|sans-serif|monospace)$/.test(family)
  if (!raw && !generic && adv(probe, `${q}, monospace`) === adv(probe, 'monospace') && adv(probe, `${q}, serif`) === adv(probe, 'serif')) return null
  const fam = raw || generic ? family : q
  const ink = (ch) => {
    cx.fillStyle = '#fff'; cx.fillRect(0, 0, W, H); cx.fillStyle = '#000'; cx.font = font(fam); cx.textBaseline = 'alphabetic'; cx.fillText(ch, X0, BASE)
    const d = cx.getImageData(0, 0, W, H).data, on = (x, y) => x >= 0 && y >= 0 && x < W && y < H && d[(y * W + x) * 4] < 128
    let x0 = W, x1 = -1, y0 = H, y1 = -1
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (d[(y * W + x) * 4] < 128) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y }
    return { on, x0, x1, y0, y1, w: x1 - x0 + 1, h: y1 - y0 + 1 }
  }
  const r3 = (v) => Math.round(v * 1000) / 1000
  const Hh = ink('H'), xx = ink('x'), capH = BASE - Hh.y0, xH = BASE - xx.y0
  const asc = BASE - ink('d').y0, desc = ink('p').y1 - BASE
  // stem and serif from the left leg of 'H': the first run of ink on a row. (Capital I carries bars in some sans faces, so it cannot be used.)
  const I = Hh, runRow = (g, y) => { let run = 0; for (let x = g.x0; x <= g.x1 + 1; x++) { if (g.on(x, y)) run++; else if (run) break } return run }
  const midI = Math.round(I.y0 + I.h * 0.72), stem = runRow(I, midI), foot = runRow(I, I.y1 - 2), head = runRow(I, I.y0 + 2)
  const serif = foot > stem * 1.35
  let serifH = 0; if (serif) { serifH = 2; for (let y = I.y1 - 2; y > midI; y--) { if (runRow(I, y) > stem * 1.35) serifH++; else break } }
  // bracket: how gradually the foot narrows into the stem. `flat` counts the rows that keep the foot's full width.
  // Both counts start two rows above the lowest ink, because a cupped serif is narrower on its very last row.
  let flat = 0; if (serif) { flat = 2; for (let y = I.y1 - 2; y > midI; y--) { if (runRow(I, y) >= foot * 0.92) flat++; else break } }
  // stroke contrast and stress axis from 'o': thickness of the ring along rays from its centre
  const o = ink('o'), ocx = (o.x0 + o.x1) / 2, ocy = (o.y0 + o.y1) / 2, th = []
  for (let a = 0; a < 180; a += 5) {
    const t = a * Math.PI / 180; let total = 0
    for (const sgn of [1, -1]) { let run = 0, seen = false; for (let r = 0; r < SZ; r++) { const x = Math.round(ocx + sgn * Math.cos(t) * r), y = Math.round(ocy - sgn * Math.sin(t) * r); if (o.on(x, y)) { run++; seen = true } else if (seen) break } total += run }
    th.push([a, total / 2])
  }
  const ring = th.filter(([, v]) => v > 0), thick = Math.max(...ring.map(([, v]) => v)), thin = Math.min(...ring.map(([, v]) => v))
  // thin points sit on the stress axis. 90° = thin at top and bottom = vertical stress; above 90° = axis leaning back to the left (old-style).
  const thinAt = ring.filter(([, v]) => v <= thin + Math.max(1.5, thin * 0.08)).map(([a]) => a), thinAngle = thinAt.reduce((s, a) => s + a, 0) / thinAt.length
  const lower = 'abcdefghijklmnopqrstuvwxyz', avg = adv(lower, fam) / 26
  const mono = Math.abs(adv('i', fam) - adv('m', fam)) < 0.5 && Math.abs(adv('l', fam) - adv('W', fam)) < 0.5
  return {
    family, weight, capHeight: r3(capH / SZ), xHeight: r3(xH / SZ), xToCap: r3(xH / capH), ascender: r3(asc / SZ), descender: r3(desc / SZ),
    capToStem: r3(capH / stem), contrast: r3(thin / thick), stressAxis: thin / thick < 0.7 ? Math.round(thinAngle - 90) : null,
    serif, serifRatio: r3(foot / stem), serifThickness: serif ? r3(serifH / stem) : 0, bracket: serif && serifH ? r3(1 - flat / serifH) : 0,
    avgAdvance: r3(avg / SZ), nWidth: r3(ink('n').w / xH), oWidth: r3(o.w / o.h), mono,
  }
},
    type: (FM) => {
  const H = innerHeight, maxY = 3 * H, num = (v) => parseFloat(v) || 0, r3 = (v) => v == null || Number.isNaN(v) ? null : Math.round(v * 1000) / 1000
  const med = (a) => { a = a.filter((v) => v != null && !Number.isNaN(v)).sort((x, y) => x - y); return a.length ? a[a.length >> 1] : null }
  const banner = (e) => e.closest('[id*="cookie" i],[class*="cookie" i],[id*="consent" i],[class*="consent" i],[id*="onetrust" i]')
  const faces = {}, sizes = {}, bySize = {}; let total = 0, n0 = 0
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let nd
  while ((nd = tw.nextNode()) && n0 < 8000) {
    const t = nd.nodeValue.trim(); if (!t) continue
    const p = nd.parentElement; if (!p || /^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA|OPTION)$/.test(p.tagName) || banner(p)) continue
    const c = getComputedStyle(p); if (c.visibility === 'hidden' || c.display === 'none' || +c.opacity === 0) continue
    const b = p.getBoundingClientRect(); if (b.width < 1 || b.top + scrollY > maxY) continue
    n0++; total += t.length
    const fs = Math.round(num(c.fontSize) * 100) / 100, w = Math.round((+c.fontWeight || 400) / 100) * 100, key = c.fontFamily + '|' + w
    faces[key] = (faces[key] || 0) + t.length; sizes[fs] = (sizes[fs] || 0) + t.length
    const s = (bySize[fs] ??= { faces: {}, lh: [] }); s.faces[key] = (s.faces[key] || 0) + t.length
    const lh = num(c.lineHeight); if (lh && t.length > 20) s.lh.push(lh / fs)
  }
  if (!total) return null
  const ranked = Object.entries(sizes).map(([s, n]) => [+s, n]).sort((a, b) => b[1] - a[1]), body = ranked[0][0]
  const used = ranked.filter(([, n]) => n / total >= 0.01).map(([s]) => s).sort((a, b) => a - b)
  const display = Math.max(...ranked.filter(([, n]) => n >= 6).map(([s]) => s), body)
  const top = (o) => Object.entries(o).sort((a, b) => b[1] - a[1])[0][0]
  const cache = {}, metric = (key) => { if (!(key in cache)) { const [fam, w] = key.split('|'); try { cache[key] = FM(fam, +w, true) } catch (e) { cache[key] = null } } return cache[key] }
  const cls = (m) => !m ? null : (m.contrast < 0.1 || m.xToCap < 0.52) ? 'script' : m.mono ? 'monospaced' : m.serif ? (m.serifThickness >= 0.7 && m.contrast >= 0.6 ? 'slab' : m.contrast <= 0.2 && m.bracket <= 0.25 ? 'didone' : 'bracketed serif') : m.contrast < 0.5 ? 'modulated sans' : 'sans'
  const main = Object.entries(faces).filter(([, n]) => n / total >= 0.01).sort((a, b) => b[1] - a[1]).slice(0, 8)
  let serifChars = 0, measuredChars = 0
  for (const [key, n] of main) { const m = metric(key); if (m) { measuredChars += n; if (m.serif) serifChars += n } }
  const bodyKey = top(bySize[body].faces), dispKey = top(bySize[display].faces), B = metric(bodyKey), D = metric(dispKey)
  const steps = used.slice(1).map((s, i) => s / used[i])
  const face = (key, m) => m && { family: key.split('|')[0].slice(0, 60), weight: +key.split('|')[1], faceClass: cls(m), serif: m.serif, xToCap: m.xToCap, xHeightEm: m.xHeight, faceWeight: m.capToStem, strokeContrast: m.contrast, faceWidth: m.avgAdvance, mono: m.mono }
  return {
    body, display, sizes: used, scaleStep: r3(med(steps)), stepMin: r3(Math.min(...steps, Infinity) === Infinity ? null : Math.min(...steps)), stepMax: r3(steps.length ? Math.max(...steps) : null),
    lineRatio: r3(med(bySize[body].lh)), lineRatioDisplay: r3(med(bySize[display].lh)),
    nFaces: new Set(main.map(([k]) => k.split('|')[0])).size, nFaceWeights: main.length, serifShare: measuredChars ? r3(serifChars / measuredChars) : null,
    bodyFace: face(bodyKey, B), displayFace: face(dispKey, D), sameFace: bodyKey.split('|')[0] === dispKey.split('|')[0],
    xHeightPx: B ? r3(body * B.xHeight) : null,
  }
},
    colour: () => {
  const W = innerWidth, H = innerHeight, maxY = 3 * H, num = (v) => parseFloat(v) || 0
  const cv = document.createElement('canvas'); cv.width = cv.height = 1
  const cx = cv.getContext('2d', { willReadFrequently: true }), memo = {}
  const rgba = (c) => { if (c in memo) return memo[c]; cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = c; cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data; return (memo[c] = [d[0], d[1], d[2], d[3] / 255]) }
  const over = (top, under) => { const a = top[3]; return [0, 1, 2].map((i) => Math.round(top[i] * a + under[i] * (1 - a))) }
  const banner = (e) => e.closest('[id*="cookie" i],[class*="cookie" i],[id*="consent" i],[class*="consent" i],[id*="onetrust" i]')
  // effective background: composite the ancestors' fills down to the canvas; note when an image sits behind
  const bgMemo = new WeakMap()
  const bgOf = (el) => {
    if (!el) return { c: [255, 255, 255], img: false }
    if (bgMemo.has(el)) return bgMemo.get(el)
    const cs = getComputedStyle(el), own = rgba(cs.backgroundColor), hasImg = cs.backgroundImage !== 'none' || /^(IMG|VIDEO|CANVAS|PICTURE)$/.test(el.tagName)
    let r
    if (own[3] >= 0.999) r = { c: own.slice(0, 3), img: hasImg }
    else { const p = bgOf(el.parentElement); r = { c: own[3] > 0 ? over(own, p.c) : p.c, img: hasImg || p.img } }
    bgMemo.set(el, r); return r
  }
  const key = (c) => c.join(',')
  const text = {}, fills = {}; let chars = 0, n0 = 0
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let nd
  while ((nd = tw.nextNode()) && n0 < 8000) {
    const t = nd.nodeValue.trim(); if (!t) continue
    const p = nd.parentElement; if (!p || /^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA|OPTION)$/.test(p.tagName) || banner(p)) continue
    const cs = getComputedStyle(p); if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue
    const b = p.getBoundingClientRect(); if (b.width < 1 || b.top + scrollY > maxY) continue
    n0++; chars += t.length
    const bg = bgOf(p), fgc = rgba(cs.color), fg = fgc[3] >= 0.999 ? fgc.slice(0, 3) : over(fgc, bg.c)
    const size = Math.round(num(cs.fontSize)), bold = (+cs.fontWeight || 400) >= 700, link = !!p.closest('a')
    const k = [key(fg), key(bg.c), size, bold ? 1 : 0, link ? 1 : 0, bg.img ? 1 : 0].join('|')
    text[k] = (text[k] || 0) + t.length
  }
  let seen = 0
  for (const el of document.body.querySelectorAll('*')) {
    if (seen > 6000) break
    const b = el.getBoundingClientRect(); if (b.width < 8 || b.height < 8 || b.top + scrollY > maxY || b.bottom + scrollY < 0 || banner(el)) continue
    seen++
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue
    const own = rgba(cs.backgroundColor); if (own[3] < 0.05) continue
    const c = own[3] >= 0.999 ? own.slice(0, 3) : over(own, bgOf(el.parentElement).c)
    const area = Math.max(0, Math.min(W, b.right) - Math.max(0, b.left)) * Math.max(0, Math.min(maxY, b.bottom + scrollY) - Math.max(0, b.top + scrollY))
    if (!area) continue
    const ctl = el.matches('button,[role=button],a,input[type=submit],input[type=button]') ? 1 : 0
    const k = key(c) + '|' + ctl; fills[k] = (fills[k] || 0) + area
  }
  const page = bgOf(document.body)
  return { W, H, chars, pageBg: key(page.c), pageImg: page.img, text, fills }
},
    shape: () => {
  const W = innerWidth, H = innerHeight, maxY = 3 * H, num = (v) => parseFloat(v) || 0
  const r2 = (v) => v == null || Number.isNaN(v) ? null : Math.round(v * 100) / 100
  const med = (a) => { a = a.filter((v) => v != null && !Number.isNaN(v)).sort((x, y) => x - y); return a.length ? a[a.length >> 1] : null }
  const banner = (e) => e.closest('[id*="cookie" i],[class*="cookie" i],[id*="consent" i],[class*="consent" i],[id*="onetrust" i]')
  const clear = (c) => !c || c === 'transparent' || /rgba\(.*,\s*0\)$/.test(c)
  const info = new Map()
  const box = (e) => {
    if (info.has(e)) return info.get(e)
    const b = e.getBoundingClientRect(), cs = getComputedStyle(e)
    const ok = b.width >= 4 && b.height >= 4 && cs.display !== 'none' && cs.visibility !== 'hidden' && +cs.opacity > 0 && b.top + scrollY < maxY && b.bottom + scrollY > 0 && b.right > 0 && b.left < W
    const v = { b, cs, ok, flow: ok && cs.position !== 'absolute' && cs.position !== 'fixed' }
    info.set(e, v); return v
  }
  // body size, for gaps in em
  const sizes = {}; let chars = 0, centred = 0; const edges = {}
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let nd, n0 = 0
  while ((nd = tw.nextNode()) && n0 < 8000) {
    const t = nd.nodeValue.trim(); if (!t) continue
    const p = nd.parentElement; if (!p || /^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA|OPTION)$/.test(p.tagName) || banner(p)) continue
    const v = box(p); if (!v.ok) continue
    n0++; chars += t.length; const fs = Math.round(num(v.cs.fontSize)); sizes[fs] = (sizes[fs] || 0) + t.length
    if (v.cs.textAlign === 'center') centred += t.length
    const range = document.createRange(); range.selectNodeContents(nd); const r = range.getClientRects()[0]; if (r) { const x = Math.round(r.left); edges[x] = (edges[x] || 0) + t.length }
  }
  const body = +(Object.entries(sizes).sort((a, b) => b[1] - a[1])[0]?.[0] || 16)
  // groups: containers whose flow children sit in one column or one row
  const groups = new Map(), gaps = [], uniform = []; let seen = 0
  for (const e of document.body.querySelectorAll('*')) {
    if (seen > 5000) break
    const v = box(e); if (!v.ok || banner(e)) continue
    const kids = [...e.children].filter((k) => box(k).flow); if (kids.length < 2) continue
    seen++
    const bs = kids.map((k) => box(k).b)
    const col = bs.every((b, i) => i === 0 || b.top >= bs[i - 1].bottom - 1), row = !col && bs.every((b, i) => i === 0 || b.left >= bs[i - 1].right - 1)
    if (!col && !row) continue
    const gs = bs.slice(1).map((b, i) => Math.round((col ? b.top - bs[i].bottom : b.left - bs[i].right) * 2) / 2)
    const g = med(gs), cs = v.cs
    const region = (!clear(cs.backgroundColor) || ['Top', 'Bottom', 'Left', 'Right'].some((s) => num(cs[`border${s}Width`]) > 0 && cs[`border${s}Style`] !== 'none' && !clear(cs[`border${s}Color`])) || cs.boxShadow !== 'none') && v.b.width * v.b.height >= 2000 && v.b.width < W * 0.99
    groups.set(e, { g, col, region, kids: kids.length, pad: col ? [num(cs.paddingTop), num(cs.paddingBottom)] : [num(cs.paddingLeft), num(cs.paddingRight)], padAll: { t: num(cs.paddingTop), b: num(cs.paddingBottom), l: num(cs.paddingLeft), r: num(cs.paddingRight) } })
    for (const x of gs) if (x > 0 && x <= 240) gaps.push(x)
    if (kids.length >= 3) uniform.push(bs.every((b) => Math.abs(b.width - bs[0].width) <= 1 && Math.abs(b.height - bs[0].height) <= 1) ? 1 : 0)
  }
  // proximity: separation between a group and its neighbours (the parent's gap plus the group's own padding on that axis) over the gap between its members
  const ratios = []
  for (const [e, G] of groups) {
    const P = groups.get(e.parentElement); if (!P || !(G.g > 0) || G.region) continue
    const pad = P.col ? (G.padAll.t + G.padAll.b) / 2 : (G.padAll.l + G.padAll.r) / 2, outer = P.g + 2 * pad
    if (outer > 0) ratios.push(outer / G.g)
  }
  const multi = [...groups.values()].filter((G) => G.kids >= 2)
  // surfaces: shape of every painted box
  const surf = []; let cornerShape = 0, clipped = 0, s2 = 0
  for (const e of document.body.querySelectorAll('*')) {
    if (s2 > 6000) break
    const v = box(e); if (!v.ok || v.b.width < 16 || v.b.height < 16 || banner(e)) continue
    const cs = v.cs, painted = !clear(cs.backgroundColor) || (num(cs.borderTopWidth) > 0 && cs.borderTopStyle !== 'none' && !clear(cs.borderTopColor))
    if (cs.clipPath && cs.clipPath !== 'none') clipped++
    if (!painted || v.b.width >= W * 0.98) continue
    s2++
    const short = Math.min(v.b.width, v.b.height), r = Math.min(num(cs.borderTopLeftRadius), short / 2)
    if (cs.cornerShape && !/^round/.test(cs.cornerShape)) cornerShape++
    surf.push({ r, short, aspect: Math.max(v.b.width, v.b.height) / short, full: r >= short / 2 - 0.5 })
  }
  const rounded = surf.filter((s) => s.r > 0 && !s.full), rad = {}
  for (const s of rounded) { const k = Math.round(s.r); rad[k] = (rad[k] || 0) + 1 }
  const radii = Object.entries(rad).filter(([, n]) => n / (rounded.length || 1) >= 0.02).map(([k]) => +k).sort((a, b) => a - b)
  const gapCount = {}; for (const g of gaps) gapCount[g] = (gapCount[g] || 0) + 1
  const gapRank = Object.entries(gapCount).sort((a, b) => b[1] - a[1]); let acc = 0, nGaps = 0; for (const [, n] of gapRank) { acc += n; nGaps++; if (acc >= gaps.length * 0.9) break }
  const edgeRank = Object.values(edges).sort((a, b) => b - a)
  return {
    body, groups: multi.length, proximityRatio: r2(med(ratios)), proxN: ratios.length, proxAbove1: ratios.length ? r2(ratios.filter((x) => x > 1).length / ratios.length) : null, prox15to3: ratios.length ? r2(ratios.filter((x) => x >= 1.5 && x <= 3).length / ratios.length) : null,
    regionShare: multi.length ? r2(multi.filter((G) => G.region).length / multi.length) : null, uniformShare: uniform.length ? r2(uniform.reduce((s, x) => s + x, 0) / uniform.length) : null,
    gaps: gaps.length, gapMedian: med(gaps), gapEm: r2(med(gaps) / body), gridShare4: gaps.length ? r2(gaps.filter((g) => g % 4 === 0).length / gaps.length) : null, gridShare8: gaps.length ? r2(gaps.filter((g) => g % 8 === 0).length / gaps.length) : null, nGaps: gaps.length ? nGaps : null, topGaps: gapRank.slice(0, 6).map(([g]) => +g),
    surfaces: surf.length, circleShare: surf.length ? r2(surf.filter((s) => s.full && s.aspect <= 1.1).length / surf.length) : null, pillShare2: surf.length ? r2(surf.filter((s) => s.full && s.aspect > 1.1).length / surf.length) : null, squareShare2: surf.length ? r2(surf.filter((s) => s.r === 0).length / surf.length) : null,
    nRadii: radii.length, radii, cornerShape, clipped,
    centeredShare: chars ? r2(centred / chars) : null, edgeTop3Share: chars ? r2(edgeRank.slice(0, 3).reduce((s, x) => s + x, 0) / chars) : null, nEdges: (() => { let a = 0, n = 0; for (const x of edgeRank) { a += x; n++; if (a >= chars * 0.8) break } return n })(),
  }
},
    layout: () => {
  const W = innerWidth, H = innerHeight, maxY = 3 * H, num = (v) => parseFloat(v) || 0
  const r2 = (v) => v == null || Number.isNaN(v) ? null : Math.round(v * 100) / 100
  const q = (a, p) => { a = a.filter((v) => v != null && !Number.isNaN(v)).sort((x, y) => x - y); return a.length ? a[Math.min(a.length - 1, Math.floor(a.length * p))] : null }
  const banner = (e) => e.closest('[id*="cookie" i],[class*="cookie" i],[id*="consent" i],[class*="consent" i],[id*="onetrust" i]')
  const vis = (e) => { const b = e.getBoundingClientRect(), cs = getComputedStyle(e); return b.width >= 4 && b.height >= 4 && cs.display !== 'none' && cs.visibility !== 'hidden' && +cs.opacity > 0 && b.top + scrollY < maxY && b.bottom + scrollY > 0 && b.right > 0 && b.left < W ? { b, cs } : null }
  // text: body size, extents, alignment points in the first viewport
  const sizes = {}, lefts = [], rights = [], xs = new Set(), ys = new Set(); let items = 0, chars = 0, n0 = 0
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT), range = document.createRange(); let nd
  while ((nd = tw.nextNode()) && n0 < 8000) {
    const t = nd.nodeValue.trim(); if (t.length < 2) continue
    const p = nd.parentElement; if (!p || /^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA|OPTION)$/.test(p.tagName) || banner(p)) continue
    const v = vis(p); if (!v) continue
    range.selectNodeContents(nd); const rs = [...range.getClientRects()].filter((r) => r.width > 1 && r.height > 1); if (!rs.length) continue
    n0++; chars += t.length; const fs = Math.round(num(v.cs.fontSize) * 100) / 100; sizes[fs] = (sizes[fs] || 0) + t.length
    for (const r of rs) { lefts.push(r.left); rights.push(r.right) }
    if (rs[0].top < H && rs[0].top >= 0) { items++; xs.add(Math.round(rs[0].left / 2)); ys.add(Math.round(rs[0].top / 2)) }
  }
  for (const im of document.querySelectorAll('img,video,canvas,svg')) { const v = vis(im); if (v && v.b.top < H && v.b.top >= 0 && v.b.width >= 16) { items++; xs.add(Math.round(v.b.left / 2)); ys.add(Math.round(v.b.top / 2)) } }
  const body = +(Object.entries(sizes).sort((a, b) => b[1] - a[1])[0]?.[0] || 0)
  const L = q(lefts, 0.03), R = q(rights, 0.97)
  // equal columns: children of one container with equal widths, counted along their first row
  const cols = []; let seen = 0
  for (const e of document.body.querySelectorAll('*')) {
    if (seen > 5000) break
    const v = vis(e); if (!v || banner(e) || e.children.length < 2) continue
    seen++
    const kids = [...e.children].map(vis).filter((k) => k && k.cs.position !== 'absolute' && k.cs.position !== 'fixed'); if (kids.length < 2) continue
    const w0 = kids[0].b.width; if (w0 < Math.max(60, W * 0.05) || !kids.every((k) => Math.abs(k.b.width - w0) <= 2)) continue
    const top = Math.min(...kids.map((k) => k.b.top)), row = kids.filter((k) => Math.abs(k.b.top - top) <= 2).sort((a, b) => a.b.left - b.b.left)
    if (row.length < 2 || row[1].b.left < row[0].b.right - 1) continue
    cols.push({ n: row.length, w: w0, gutter: row[1].b.left - row[0].b.right, area: v.b.width * v.b.height })
  }
  const byN = {}; for (const c of cols) byN[c.n] = (byN[c.n] || 0) + c.area
  const el1 = [...document.body.querySelectorAll('*')].filter((e) => { const b = e.getBoundingClientRect(); return b.width >= 4 && b.height >= 4 && b.top < H && b.bottom > 0 }).length
  return {
    W, H, body, chars, margin: r2(L), marginShare: L == null ? null : r2(Math.max(0, L) / W), contentShare: L == null ? null : r2(Math.min(1, (R - L) / W)), contentWidth: L == null ? null : Math.round(R - L),
    maxCols: cols.length ? Math.max(...cols.map((c) => c.n)) : 1, colMode: cols.length ? +Object.entries(byN).sort((a, b) => b[1] - a[1])[0][0] : 1, colSets: cols.length,
    gutter: r2(q(cols.map((c) => c.gutter), 0.5)), gutterRatio: r2(q(cols.map((c) => c.gutter / c.w), 0.5)), colWidth: r2(q(cols.map((c) => c.w), 0.5)),
    items, nX: xs.size, nY: ys.size, regularity: items ? r2(1 - (xs.size + ys.size) / (2 * items)) : null, elements1: el1, pages: r2(document.documentElement.scrollHeight / H),
  }
},
  }
  const r2 = (v) => (v == null || Number.isNaN(v) ? null : Math.round(v * 100) / 100)
  const wmed = (pairs, p = 0.5) => { pairs = pairs.filter(([v]) => v != null).sort((a, b) => a[0] - b[0]); const tot = pairs.reduce((s, [, w]) => s + w, 0); let acc = 0; for (const [v, w] of pairs) { acc += w; if (acc >= tot * p) return v } return null }
  /** Colour observables from the weights PART.colour collects. */
  function colourObservables(t) {
    const memo = {}, hct = (k) => memo[k] ??= (() => { const rgb = k.split(',').map(Number), h = math.hct(rgb); return { h: h.h, c: h.c, t: h.t, rgb } })()
    const txt = Object.entries(t.text).map(([k, n]) => { const [fg, bg, size, bold, link, img] = k.split('|'); return { fg: hct(fg), bg: hct(bg), size: +size, bold: bold === '1', link: link === '1', img: img === '1', n } })
    const fills = Object.entries(t.fills).map(([k, a]) => { const [c, ctl] = k.split('|'); return { key: c, c: hct(c), ctl: ctl === '1', a } })
    const chars = txt.reduce((s, x) => s + x.n, 0), area = t.W * t.H * 3
    if (!chars) return {}
    for (const x of txt) { x.lc = math.apca(x.fg.rgb, x.bg.rgb); x.ratio = math.wcag(x.fg.rgb, x.bg.rgb); x.large = x.size >= 24 || (x.size >= 19 && x.bold) }
    const sizes = {}; for (const x of txt) sizes[x.size] = (sizes[x.size] || 0) + x.n
    const body = +Object.entries(sizes).sort((a, b) => b[1] - a[1])[0][0]
    const pairs = {}; for (const x of txt.filter((x) => x.size === body && !x.link)) { const k = x.fg.rgb + '|' + x.bg.rgb; (pairs[k] ??= { x, n: 0 }).n += x.n }
    const bp = Object.values(pairs).sort((a, b) => b.n - a.n)[0]?.x ?? [...txt].sort((a, b) => b.n - a.n)[0]
    const solid = txt.filter((x) => !x.img), share = (f, xs = txt) => xs.filter(f).reduce((s, x) => s + x.n, 0) / (xs.reduce((s, x) => s + x.n, 0) || 1)
    const own = fills.filter((f) => f.key !== t.pageBg), chromatic = [...txt.filter((x) => x.fg.c >= 16 && x.n / chars >= 0.005).map((x) => x.fg), ...own.filter((f) => f.c.c >= 16 && f.a / area >= 0.002).map((f) => f.c)]
    const ctl = fills.filter((f) => f.ctl && f.key !== t.pageBg)
    return {
      pageTone: r2(hct(t.pageBg).t), textTone: r2(bp.fg.t), bodyLcAbs: r2(Math.abs(bp.lc)), lowLcShare: r2(share((x) => Math.abs(x.lc) < 60, solid)), wcagFailShare: r2(share((x) => x.ratio < (x.large ? 3 : 4.5), solid)),
      darkShare: r2(share((x) => x.bg.t < 50)), textChromaShare: r2(share((x) => x.fg.c >= 16)), fillShare: r2(Math.min(1, own.reduce((s, f) => s + f.a, 0) / area)), chromaFillShare: r2(Math.min(1, own.filter((f) => f.c.c >= 16).reduce((s, f) => s + f.a, 0) / area)),
      maxChroma: r2(Math.max(0, ...chromatic.map((c) => c.c))), nHues: new Set(chromatic.map((c) => Math.floor(c.h / 30))).size, ctlChroma: r2(wmed(ctl.map((f) => [f.c.c, f.a]))),
    }
  }
  /** Every observable one evaluation can give, named as in references/archetypes.json. A null was looked for and not found. */
  function observe() {
    const m = JSON.parse(PART.base()), x = JSON.parse(PART.extra()), t = PART.type(PART.fontMetrics), c = PART.colour(), s = PART.shape(), l = PART.layout()
    const b = t?.bodyFace, d = t?.displayFace
    const o = {
      body: m.type.body, contrast: m.type.contrast, nSizes: m.type.nSizes, upperShare: m.type.upperShare,
      textCov: m.layout.textCov3, imgCov: r2(Math.min(1, m.layout.imgCov3)), occupancy: r2(Math.min(1, m.layout.occupancy)), measure: r2(m.layout.measureCPL),
      loft: m.controls.loft, labelToBody: m.controls.boxedText ? m.controls.labelToBody : null, ctlTracking: m.controls.boxedText ? m.controls.track : null, ctlUpperShare: m.controls.boxedText ? m.controls.upShare : null, iconOnlyShare: m.controls.n >= 5 ? r2(m.controls.iconOnly / m.controls.n) : null, iconToBody: m.icons.n ? m.icons.toBody : null,
      borderShare: m.body3.borderShare, bwMax: m.body3.bwMax ?? null, kappaSurface: m.body3.kappaMed, squareShare: m.body3.squareShare, pillShare: m.body3.pillShare,
      monoShare: x.monoShare, heavyShare: x.heavyShare, meanWeight: x.meanWeight, displayVh: x.displayVh, kappa2: x.buttons >= 2 ? x.kappa2 : null,
      serifShare: t?.serifShare ?? null, strokeContrast: b?.strokeContrast ?? null, dispContrast: d?.strokeContrast ?? null, faceWeight: b?.faceWeight ?? null, dispWeight: d?.faceWeight ?? null, faceWidth: b?.faceWidth ?? null,
      nFaces: t?.nFaces ?? null, scaleStep: t?.scaleStep ?? null, lineRatio: t?.lineRatio ?? null, lineRatioDisplay: t?.lineRatioDisplay ?? null, xHeightPx: t?.xHeightPx ?? null,
      ...colourObservables(c),
      proximityRatio: s.proxN >= 3 ? s.proximityRatio : null, regionShare: s.regionShare, uniformShare: s.uniformShare, gapEm: s.gapEm, gridShare4: s.gaps >= 10 ? s.gridShare4 : null, nGaps: s.nGaps,
      circleShare: s.circleShare, nRadii: s.nRadii, centeredShare: s.centeredShare, edgeTop3Share: s.edgeTop3Share,
      maxCols: l.maxCols, marginShare: l.marginShare, gutterRatio: l.colSets ? l.gutterRatio : null, regularity: l.items >= 8 ? l.regularity : null, elements1: l.elements1, pagesLong: l.pages,
    }
    for (const k of observe.KEYS) if (!(k in o)) o[k] = null
    return { viewport: [innerWidth, innerHeight], observables: o, notMeasured: observe.RUNNER_KEYS, detail: { bodyFace: b ?? null, displayFace: d ?? null, radii: s.radii, topGaps: s.topGaps, sizes: t?.sizes ?? null, pageBg: c.pageBg } }
  }
  /** Observables one evaluation gives. */
  observe.KEYS = ['body', 'contrast', 'nSizes', 'upperShare', 'ctlTracking', 'ctlUpperShare', 'textCov', 'imgCov', 'occupancy', 'measure', 'loft', 'labelToBody', 'iconOnlyShare', 'iconToBody', 'borderShare', 'bwMax', 'kappaSurface', 'squareShare', 'pillShare', 'monoShare', 'heavyShare', 'meanWeight', 'displayVh', 'kappa2',
    'serifShare', 'strokeContrast', 'dispContrast', 'faceWeight', 'dispWeight', 'faceWidth', 'nFaces', 'scaleStep', 'lineRatio', 'lineRatioDisplay', 'xHeightPx',
    'pageTone', 'textTone', 'bodyLcAbs', 'lowLcShare', 'wcagFailShare', 'darkShare', 'textChromaShare', 'fillShare', 'chromaFillShare', 'maxChroma', 'nHues', 'ctlChroma',
    'proximityRatio', 'regionShare', 'uniformShare', 'gapEm', 'gridShare4', 'nGaps', 'circleShare', 'nRadii', 'centeredShare', 'edgeTop3Share',
    'maxCols', 'marginShare', 'gutterRatio', 'regularity', 'elements1', 'pagesLong']
  /** Observables that need a screenshot or a second load: scripts/observe.mjs adds them. */
  observe.RUNNER_KEYS = ['bgShare', 'edgeDensity', 'jpegKb', 'colourCount', 'colourfulness', 'mirrorLR', 'balanceLR', 'followsScheme', 'bodyRatio']
  observe.math = math
  /** async (base64 PNG of the first viewport) → pixel observables. Run it in any page. */
  observe.pixelStats = async (b64) => {
  const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode()
  const w = Math.round(img.width / 2), h = Math.round(img.height / 2), cv = document.createElement('canvas'); cv.width = w; cv.height = h
  const cx = cv.getContext('2d', { willReadFrequently: true }); cx.drawImage(img, 0, 0, w, h)
  const d = cx.getImageData(0, 0, w, h).data, n = w * h, bins = new Map(), lum = new Float32Array(n)
  for (let i = 0; i < n; i++) { const r = d[i * 4], g = d[i * 4 + 1], b = d[i * 4 + 2]; lum[i] = 0.2126 * r + 0.7152 * g + 0.0722 * b; const k = (r >> 4) << 8 | (g >> 4) << 4 | (b >> 4); bins.set(k, (bins.get(k) || 0) + 1) }
  const mode = [...bins.entries()].sort((a, b) => b[1] - a[1])[0][0]
  // the ground: mean colour of the most common bin; a pixel is ground when within 14 of it in each channel
  let sr = 0, sg = 0, sb = 0, c = 0
  for (let i = 0; i < n; i++) { const r = d[i * 4], g = d[i * 4 + 1], b = d[i * 4 + 2]; if (((r >> 4) << 8 | (g >> 4) << 4 | (b >> 4)) === mode) { sr += r; sg += g; sb += b; c++ } }
  const gr = sr / c, gg = sg / c, gb = sb / c, ink = new Uint8Array(n); let bg = 0
  for (let i = 0; i < n; i++) { const isBg = Math.abs(d[i * 4] - gr) <= 14 && Math.abs(d[i * 4 + 1] - gg) <= 14 && Math.abs(d[i * 4 + 2] - gb) <= 14; if (isBg) bg++; else ink[i] = 1 }
  let edge = 0, ec = 0; for (let y = 0; y < h - 1; y++) for (let x = 0; x < w - 1; x++) { const i = y * w + x; edge += Math.abs(lum[i + 1] - lum[i]) + Math.abs(lum[i + w] - lum[i]); ec += 2 }
  let inkL = 0, inkR = 0, inkT = 0, inkB = 0, both = 0, either = 0
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const a = ink[y * w + x]; if (a) { x < w / 2 ? inkL++ : inkR++; y < h / 2 ? inkT++ : inkB++ } if (x < w / 2) { const m = ink[y * w + (w - 1 - x)]; if (a || m) either++; if (a && m) both++ } }
  // colourfulness, Hasler and Süsstrunk 2003
  let srg = 0, syb = 0, srg2 = 0, syb2 = 0
  for (let i = 0; i < n; i++) { const r = d[i * 4], g = d[i * 4 + 1], b = d[i * 4 + 2], rg = r - g, yb = 0.5 * (r + g) - b; srg += rg; syb += yb; srg2 += rg * rg; syb2 += yb * yb }
  const mrg = srg / n, myb = syb / n, colourfulness = Math.sqrt(Math.max(0, srg2 / n - mrg * mrg) + Math.max(0, syb2 / n - myb * myb)) + 0.3 * Math.sqrt(mrg * mrg + myb * myb)
  const r3 = (v) => Math.round(v * 1000) / 1000
  return { bgShare: r3(bg / n), groundLum: Math.round(0.2126 * gr + 0.7152 * gg + 0.0722 * gb), edgeDensity: r3(edge / ec / 255), colourCount: [...bins.values()].filter((v) => v / n >= 0.001).length, colourfulness: r3(colourfulness),
    balanceLR: inkL + inkR ? r3(1 - Math.abs(inkL - inkR) / (inkL + inkR)) : null, balanceTB: inkT + inkB ? r3(1 - Math.abs(inkT - inkB) / (inkT + inkB)) : null, mirrorLR: either ? r3(both / either) : null }
}
  /** Body size and page ground alone, for the second loads. */
  observe.quick = () => { const l = PART.layout(), c = PART.colour(); return { body: l.body, pageTone: r2(math.hct(c.pageBg.split(',').map(Number)).t) } }
  ;(typeof window !== 'undefined' ? window : globalThis).uiGeometryObserve = observe
})()
