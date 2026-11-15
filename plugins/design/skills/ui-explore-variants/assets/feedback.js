// Feedback capture for an exploration page. Vanilla, no dependencies.
// Finds every `section[data-variant]`, adds a verdict, "works" and "does not work" choices and a note to each, adds an
// overall block after the last section of `[data-explore]`, and copies one JSON object the reader pastes back in chat.
// Reads from `[data-explore]`: data-question, data-round, data-aspects (comma list; a section or a wrapper around a
// moment's sections may carry its own, and the nearest wins). Controls marked `data-fb-control`
// (a width slider, a time scrubber) are recorded with their current values, so the feedback says what was on screen.
// Compare: each section may carry data-moment (the component or UI moment it answers) and, when kept from an earlier
// round, its own data-round. A corner button, the key C and a "Compare all" button in each variant open a modal dialog
// that holds every variant of one moment side by side, live: the variant's `.stage` is moved into its card and put back
// on close, with a placeholder of the same height left in the page. Compare is a view; the JSON gains nothing.
(function () {
  const root = document.querySelector('[data-explore]');
  if (!root) return;
  const sections = [...root.querySelectorAll('section[data-variant]')];
  if (!sections.length) return;
  const KEY = 'ui-explore-variants:' + document.title + ':' + (root.dataset.round || '1');
  const VERDICTS = [['pursue', 'Pursue'], ['parts', 'Keep parts'], ['drop', 'Drop']];
  const NEXT = [['refine', 'Refine the picks'], ['combine', 'Combine the picks'], ['more', 'Explore further'], ['build', 'Build it']];
  const DEFAULT_ASPECTS = 'Layout,Density,Readability,Interaction,Fits the system';
  // the nearest data-aspects wins: the variant's own, a wrapper around one moment's variants, then the container's
  const aspectsOf = (s) => {
    const host = s.closest('[data-aspects]');
    return ((host && root.contains(host) ? host : root).dataset.aspects || DEFAULT_ASPECTS).split(',').map((a) => a.trim()).filter(Boolean);
  };
  const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  let state = { variants: {}, overall: {} };
  try { state = JSON.parse(localStorage.getItem(KEY)) || state; } catch (e) { /* no storage: start empty */ }
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* draft not kept */ } refresh(); };
  const nameOf = (s) => s.dataset.name || (s.querySelector('h2') || {}).textContent || s.dataset.variant;

  const pill = (type, name, value, label, checked) =>
    `<label class="fb-pill"><input type="${type}" name="${name}" value="${value}" id="${name}-${slug(value)}"${checked ? ' checked' : ''}><span>${label}</span></label>`;

  for (const s of sections) {
    const id = s.dataset.variant, v = (state.variants[id] = state.variants[id] || { verdict: null, works: [], doesnt: [], note: '' });
    const ASPECTS = aspectsOf(s);
    const f = document.createElement('form');
    f.className = 'fb'; f.setAttribute('aria-label', 'Feedback on ' + nameOf(s));
    f.innerHTML =
      `<div class="fb-row"><span class="fb-l">Verdict</span><div class="fb-set">${VERDICTS.map(([k, l]) => pill('radio', `fb-${id}-verdict`, k, l, v.verdict === k)).join('')}</div></div>` +
      `<div class="fb-row"><span class="fb-l">Works</span><div class="fb-set">${ASPECTS.map((a) => pill('checkbox', `fb-${id}-works`, a, a, v.works.includes(a))).join('')}</div></div>` +
      `<div class="fb-row"><span class="fb-l">Does not</span><div class="fb-set">${ASPECTS.map((a) => pill('checkbox', `fb-${id}-doesnt`, a, a, v.doesnt.includes(a))).join('')}</div></div>` +
      `<div class="fb-row"><label class="fb-l" for="fb-${id}-note">Note</label><textarea id="fb-${id}-note" rows="2" placeholder="What to change, keep or try">${(v.note || '').replace(/</g, '&lt;')}</textarea></div>`;
    f.addEventListener('submit', (e) => e.preventDefault());
    f.addEventListener('input', () => {
      v.verdict = (f.querySelector(`[name="fb-${id}-verdict"]:checked`) || {}).value || null;
      v.works = [...f.querySelectorAll(`[name="fb-${id}-works"]:checked`)].map((i) => i.value);
      v.doesnt = [...f.querySelectorAll(`[name="fb-${id}-doesnt"]:checked`)].map((i) => i.value);
      v.note = f.querySelector('textarea').value;
      save();
    });
    s.appendChild(f);
  }

  const o = state.overall = Object.assign({ next: null, note: '' }, state.overall);
  const box = document.createElement('section');
  box.className = 'fb-overall'; box.id = 'feedback';
  box.innerHTML =
    `<h2>Send feedback</h2>` +
    `<p class="fb-sum" aria-live="polite"></p>` +
    `<form class="fb" aria-label="Overall feedback">` +
    `<div class="fb-row"><span class="fb-l">Next</span><div class="fb-set">${NEXT.map(([k, l]) => pill('radio', 'fb-next', k, l, o.next === k)).join('')}</div></div>` +
    `<div class="fb-row"><label class="fb-l" for="fb-overall-note">Overall</label><textarea id="fb-overall-note" rows="3" placeholder="How the picks should combine, what is missing, questions">${(o.note || '').replace(/</g, '&lt;')}</textarea></div>` +
    `</form>` +
    `<div class="fb-actions"><button type="button" class="fb-copy">Copy feedback JSON</button><button type="button" class="fb-clear">Clear</button><span class="fb-status" role="status"></span></div>` +
    `<details class="fb-json"><summary>Preview the JSON</summary><textarea readonly rows="10" aria-label="Feedback JSON"></textarea></details>`;
  sections[sections.length - 1].parentNode.appendChild(box);
  const of = box.querySelector('form'), out = box.querySelector('.fb-json textarea'), status = box.querySelector('.fb-status'), sum = box.querySelector('.fb-sum');
  of.addEventListener('submit', (e) => e.preventDefault());
  of.addEventListener('input', () => { o.next = (of.querySelector('[name="fb-next"]:checked') || {}).value || null; o.note = of.querySelector('textarea').value; save(); });

  function payload() {
    const controls = {};
    document.querySelectorAll('[data-fb-control]').forEach((c) => { controls[c.dataset.fbControl || c.id] = c.type === 'checkbox' ? c.checked : c.value; });
    document.querySelectorAll('[data-fb-control-group] [aria-pressed="true"]').forEach((b) => { controls[b.closest('[data-fb-control-group]').dataset.fbControlGroup] = b.textContent.trim(); });
    return {
      skill: 'ui-explore-variants', schema: 1,
      exploration: document.title, question: root.dataset.question || null, round: Number(root.dataset.round || 1),
      controls,
      variants: sections.map((s) => Object.assign({ id: s.dataset.variant, name: nameOf(s).trim() }, state.variants[s.dataset.variant])),
      overall: { next: o.next, note: o.note },
      capturedAt: new Date().toISOString(),
    };
  }
  function refresh() {
    const p = payload(); out.value = JSON.stringify(p, null, 2);
    const by = (k) => p.variants.filter((v) => v.verdict === k).map((v) => v.name);
    const judged = p.variants.filter((v) => v.verdict).length;
    sum.textContent = judged
      ? `${judged} of ${p.variants.length} judged. Pursue: ${by('pursue').join(', ') || 'none'}. Keep parts: ${by('parts').join(', ') || 'none'}. Drop: ${by('drop').join(', ') || 'none'}.`
      : `Give each variant a verdict above, then copy the JSON and paste it in the chat.`;
  }
  box.querySelector('.fb-copy').addEventListener('click', () => {
    refresh();
    const done = () => { status.textContent = 'Copied. Paste it in the chat.'; };
    const fallback = () => { box.querySelector('.fb-json').open = true; out.focus(); out.select(); status.textContent = 'Copy was refused here. The JSON is selected: copy it by hand.'; };
    try { navigator.clipboard.writeText(out.value).then(done, fallback); } catch (e) { fallback(); }
  });
  let armed = false;
  box.querySelector('.fb-clear').addEventListener('click', (e) => {
    if (!armed) { armed = true; e.target.textContent = 'Clear everything?'; setTimeout(() => { armed = false; e.target.textContent = 'Clear'; }, 3000); return; }
    try { localStorage.removeItem(KEY); } catch (err) { /* nothing stored */ }
    root.querySelectorAll('.fb input').forEach((i) => { i.checked = false; }); root.querySelectorAll('.fb textarea').forEach((t) => { t.value = ''; });
    for (const k of Object.keys(state.variants)) state.variants[k] = { verdict: null, works: [], doesnt: [], note: '' };
    o.next = null; o.note = ''; armed = false; e.target.textContent = 'Clear'; status.textContent = 'Cleared.'; refresh();
  });
  document.addEventListener('input', (e) => { if (e.target.matches && e.target.matches('[data-fb-control]')) refresh(); });
  document.addEventListener('click', (e) => { if (e.target.closest && e.target.closest('[data-fb-control-group]')) setTimeout(refresh, 0); });
  refresh();

  // ---- Compare ----
  if (sections.length < 2 || !window.HTMLDialogElement) return;
  const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
  const momentOf = (s) => s.dataset.moment || '';
  const roundOf = (s) => s.dataset.round || root.dataset.round || '1';
  const momentName = (m) => (m ? m.replace(/[-_]+/g, ' ') : 'All variants');
  const moments = [...new Set(sections.map(momentOf))];
  const rounds = [...new Set(sections.map(roundOf))].sort((a, b) => a - b);
  const VIRTUAL = 24; // beyond this many cards, only those near the view hold their stage
  const KEYPREF = 'ui-explore-variants:compare-key';
  const opt = (v, l) => `<option value="${esc(v)}">${esc(l)}</option>`;

  const dlg = document.createElement('dialog');
  dlg.className = 'fb-cmp'; dlg.setAttribute('aria-labelledby', 'fb-cmp-title');
  dlg.innerHTML =
    `<header class="fb-cmp-head"><h2 id="fb-cmp-title">Compare</h2>` +
    `<label${moments.length > 1 ? '' : ' hidden'}>Moment <select class="fb-cmp-moment">${moments.map((m) => opt(m, momentName(m))).join('')}</select></label>` +
    `<label${rounds.length > 1 ? '' : ' hidden'}>Round <select class="fb-cmp-round">${opt('', 'All')}${rounds.map((r) => opt(r, r)).join('')}</select></label>` +
    `<label>Verdict <select class="fb-cmp-verdict">${opt('', 'All')}${VERDICTS.map(([k, l]) => opt(k, l)).join('')}${opt('none', 'Not judged')}</select></label>` +
    `<button type="button" class="fb-cmp-fit" aria-pressed="false">Fit to width</button>` +
    `<span class="fb-cmp-controls"></span>` +
    `<label class="fb-cmp-key"><input type="checkbox"> Key C opens Compare</label>` +
    `<button type="button" class="fb-cmp-close">Close</button></header>` +
    `<p class="fb-cmp-count" role="status"></p>` +
    `<div class="fb-cmp-track" tabindex="0" role="group" aria-label="Variants side by side"></div>`;
  document.body.appendChild(dlg);
  const q = (c) => dlg.querySelector(c);
  const mSel = q('.fb-cmp-moment'), rSel = q('.fb-cmp-round'), vSel = q('.fb-cmp-verdict'), fitBtn = q('.fb-cmp-fit');
  const track = q('.fb-cmp-track'), count = q('.fb-cmp-count'), keyBox = q('.fb-cmp-key input'), mirror = q('.fb-cmp-controls');

  // One card per variant, built once. A verdict chosen on a card is written through the variant's own form.
  const cards = sections.map((s) => {
    const id = s.dataset.variant, el = document.createElement('article');
    el.className = 'fb-cmp-card'; el.setAttribute('aria-label', nameOf(s).trim());
    el.innerHTML = `<header><b>${esc(nameOf(s).trim())}</b><span class="fb-cmp-meta"></span>` +
      `<div class="fb-set" role="group" aria-label="Verdict">${VERDICTS.map(([k, l]) => pill('radio', `cmp-${id}-verdict`, k, l, false)).join('')}</div></header><div class="fb-cmp-body"></div>`;
    el.addEventListener('input', (e) => {
      if (!e.target.matches('[type=radio]')) return;
      const i = [...s.querySelectorAll('.fb [type=radio]')].find((r) => r.name === `fb-${id}-verdict` && r.value === e.target.value);
      if (i) { i.checked = true; i.dispatchEvent(new Event('input', { bubbles: true })); }
    });
    track.appendChild(el);
    return { s, id, el, body: el.querySelector('.fb-cmp-body'), meta: el.querySelector('.fb-cmp-meta'), stage: s.querySelector('.stage'), hold: null };
  });
  const mount = (c) => {
    if (c.hold || !c.stage) return;
    c.hold = document.createElement('div'); c.hold.className = 'fb-cmp-hold'; c.hold.setAttribute('aria-hidden', 'true');
    c.hold.style.height = c.stage.getBoundingClientRect().height + 'px';
    c.stage.replaceWith(c.hold); c.body.style.minWidth = c.body.style.minHeight = ''; c.body.appendChild(c.stage);
  };
  const unmount = (c) => {
    if (!c.hold) return;
    const r = c.body.getBoundingClientRect(); c.body.style.minWidth = r.width + 'px'; c.body.style.minHeight = r.height + 'px';
    c.body.style.zoom = ''; c.hold.replaceWith(c.stage); c.hold = null;
  };
  const fitOn = () => fitBtn.getAttribute('aria-pressed') === 'true';
  function fit() {
    const live = cards.filter((c) => !c.el.hidden && c.hold);
    for (const c of live) c.body.style.zoom = '';
    const w = live.length ? Math.max(200, (track.clientWidth - 32 - 16 * (live.length - 1)) / live.length) : 0;
    for (const c of live) {
      const z = fitOn() ? Math.min(1, w / c.el.offsetWidth) : 1;
      c.body.style.zoom = z < 1 ? z : '';
      c.meta.textContent = `Round ${roundOf(c.s)}` + (z < 1 ? ` · scaled to ${Math.round(z * 100)}%` : '');
    }
  }
  let io = null;
  function show() {
    const m = mSel.value, r = rSel.value, v = vSel.value;
    if (io) { io.disconnect(); io = null; }
    for (const c of cards) {
      const verdict = (state.variants[c.id] || {}).verdict || null;
      c.el.hidden = !(momentOf(c.s) === m && (!r || roundOf(c.s) === r) && (!v || (v === 'none' ? !verdict : verdict === v)));
      c.el.querySelectorAll('header [type=radio]').forEach((i) => { i.checked = i.value === verdict; });
      c.meta.textContent = `Round ${roundOf(c.s)}`;
      if (c.el.hidden) { unmount(c); c.body.style.minWidth = c.body.style.minHeight = ''; }
    }
    const live = cards.filter((c) => !c.el.hidden);
    if (live.length > VIRTUAL && window.IntersectionObserver) {
      io = new IntersectionObserver((es) => { for (const e of es) { const c = cards.find((x) => x.el === e.target); if (e.isIntersecting) mount(c); else unmount(c); } fit(); }, { root: track, rootMargin: '50%' });
      live.slice(0, VIRTUAL).forEach(mount); live.slice(VIRTUAL).forEach((c) => io.observe(c.el));
    } else live.forEach(mount);
    const all = cards.filter((c) => momentOf(c.s) === m).length;
    count.textContent = live.length ? `${live.length} of ${all} variants${moments.length > 1 ? ' of ' + momentName(m) : ''}, at ${fitOn() ? 'fitted' : 'natural'} size.` : 'No variant matches these filters.';
    fit();
  }

  // A copy of each shared control, bound to the page's own, so the stress applies in the dialog too.
  const pulls = [];
  document.querySelectorAll('[data-fb-control]').forEach((c) => {
    if (!/^(INPUT|SELECT)$/.test(c.tagName) || c.type === 'radio') return;
    const k = c.cloneNode(true), lab = c.id && document.querySelector(`label[for="${c.id}"]`), wrap = document.createElement('label');
    k.removeAttribute('id'); k.removeAttribute('data-fb-control');
    wrap.append((lab ? lab.textContent.trim() : c.dataset.fbControl || c.id) + ' ', k); mirror.appendChild(wrap);
    const pull = () => { if (c.type === 'checkbox') k.checked = c.checked; else k.value = c.value; };
    k.addEventListener('input', () => {
      if (c.type === 'checkbox') c.checked = k.checked; else c.value = k.value;
      c.dispatchEvent(new Event('input', { bubbles: true })); c.dispatchEvent(new Event('change', { bubbles: true }));
      requestAnimationFrame(fit);
    });
    c.addEventListener('input', pull); pulls.push(pull);
  });
  document.querySelectorAll('[data-fb-control-group]').forEach((g) => {
    const wrap = document.createElement('span'); wrap.className = 'fb-cmp-group'; wrap.setAttribute('role', 'group'); wrap.setAttribute('aria-label', g.dataset.fbControlGroup);
    g.querySelectorAll('button').forEach((b) => {
      const k = document.createElement('button'); k.type = 'button'; k.textContent = b.textContent.trim();
      k.addEventListener('click', () => { b.click(); setTimeout(() => { pulls.forEach((p) => p()); fit(); }, 0); });
      pulls.push(() => k.setAttribute('aria-pressed', b.getAttribute('aria-pressed') || 'false')); wrap.appendChild(k);
    });
    mirror.appendChild(wrap);
  });

  let opener = null;
  function openCompare(moment, id) {
    if (dlg.open) return;
    opener = document.activeElement;
    if (moment != null) mSel.value = moment;
    pulls.forEach((p) => p()); dlg.showModal(); show();
    const c = id && cards.find((x) => x.id === id);
    if (c && !c.el.hidden) c.el.scrollIntoView({ inline: 'start', block: 'nearest' });
  }
  // Escape is the dialog's own (a layer open inside a variant that takes Escape first must cancel the keydown).
  dlg.addEventListener('close', () => {
    if (io) { io.disconnect(); io = null; }
    for (const c of cards) { unmount(c); c.body.style.minWidth = c.body.style.minHeight = ''; }
    if (opener && opener.focus) opener.focus();
    refresh();
  });
  q('.fb-cmp-close').addEventListener('click', () => dlg.close());
  fitBtn.addEventListener('click', () => { fitBtn.setAttribute('aria-pressed', String(!fitOn())); show(); });
  for (const sel of [mSel, rSel, vSel]) sel.addEventListener('change', show);

  const fab = document.createElement('button');
  fab.type = 'button'; fab.className = 'fb-cmp-open'; fab.textContent = 'Compare';
  fab.addEventListener('click', () => openCompare());
  document.body.appendChild(fab);
  for (const s of sections) {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'fb-cmp-all'; b.textContent = 'Compare all';
    b.setAttribute('aria-label', `Compare all variants${momentOf(s) ? ' of ' + momentName(momentOf(s)) : ''}, from ${nameOf(s).trim()}`);
    b.addEventListener('click', () => openCompare(momentOf(s), s.dataset.variant));
    (s.querySelector('.opt-head') || s).appendChild(b);
  }
  // A one-key shortcut can be turned off (WCAG 2.1.4); the choice is kept in the reader's browser.
  let keyOn = true;
  try { keyOn = localStorage.getItem(KEYPREF) !== 'off'; } catch (e) { /* no storage: on */ }
  const tellKey = () => { keyBox.checked = keyOn; if (keyOn) fab.setAttribute('aria-keyshortcuts', 'C'); else fab.removeAttribute('aria-keyshortcuts'); fab.title = keyOn ? 'Compare variants side by side (C)' : 'Compare variants side by side'; };
  keyBox.addEventListener('change', () => { keyOn = keyBox.checked; try { localStorage.setItem(KEYPREF, keyOn ? 'on' : 'off'); } catch (e) { /* not kept */ } tellKey(); });
  tellKey();
  document.addEventListener('keydown', (e) => {
    if (!keyOn || dlg.open || e.defaultPrevented || e.ctrlKey || e.metaKey || e.altKey || (e.key || '').toLowerCase() !== 'c') return;
    if (e.target.closest && e.target.closest('input, textarea, select, [contenteditable], [role="textbox"]')) return;
    e.preventDefault(); openCompare();
  });
})();
