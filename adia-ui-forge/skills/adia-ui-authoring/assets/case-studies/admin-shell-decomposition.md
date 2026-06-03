# Case study — Mode 3: admin-shell decomposition

**Scenario:** [shell-patterns.md](../../references/shell-patterns.md) — decompose a ~305-LOC monolith into a family of bespoke cluster-namespaced children **Source:** the canonical ADR-0023 instance — first bespoke shell cluster **Outcome:** 3 JS-bearing children + 7 CSS-only stubs = 10 bespoke elements. Pattern then mechanically replicated to chat, editor, and simple clusters.

---

## §The shape

`<app-shell-ui>` had grown to ~305 LOC — sidebar resize + collapse + persistence + ResizeObserver breakpoints + Cmd+K palette + toggle binding + 6 distinct `data-*` region selectors + a 4-way `||` chain in `connected()` reading legacy and new shapes in priority order. Author markup was `<app-shell-ui>` with `<aside data-sidebar="leading">` regions, `<dialog data-command>` palette, and `[data-app-shell-toggle]` action buttons. CSS had layered files with `:is(legacy, bespoke)` lifts spread across 6 stylesheets.

The host coordinated everything. Adding a 4th cluster (chat) meant duplicating the entire mechanism behind a `<chat-shell-ui>` wrapper or generalizing the host — both bad. State queries went through threshold-math inference (compute width → infer collapsed) rather than reading reflected attributes.

---

## §The diagnosis

Per [shell-patterns.md](../../references/shell-patterns.md) § Architectural principles, every shell-specific concern should earn its own custom element with a documented attribute API. State should live as reflected attributes. Parent shells should coordinate via `querySelector` + slot routing without centralizing child behavior.

The 4-concern decomposition heuristic identified:

| Concern | What was in the host | Becomes |
| --- | --- | --- |
| 1. **Side-region behavior** (resize + collapse + persist + narrow-mode RO) | ~150 LOC of leading/trailing sidebar coordination | `<admin-sidebar>` (JS-bearing) |
| 2. **Keyboard-driven overlay** (Cmd+K palette) | ~80 LOC of dialog binding + global keydown + focus trap | `<admin-command>` (JS-bearing) |
| 3. **Cluster-specific orchestration** (mode reflection, attribute-forwarding to children) | ~75 LOC that legitimately belongs in the host | stays in `<admin-shell>` (slimmed coordinator) |
| 4. **Structural composition** (content / topbar / statusbar / scroll / page / page-header / page-body) | implicit via CSS rules matching `data-*` selectors | 7 CSS-only stubs |

Default split for a 5-concern shell predicts 2-3 JS-bearing + 5-7 CSS-only = 7-10. Admin landed at 3 + 7 = 10.

---

## §The fix

### Phase 1 (introduce)

Authored 10 bespoke children under `packages/web-modules/shell/` with the cluster-namespace convention (`admin-*`, no `-ui` suffix per ADR-0015). Each JS-bearing child got the 6-file scaffold (yaml + js + css? + html + examples.html + test.js + generated a2ui.json); each CSS-only stub got the 4-file scaffold (yaml + html + examples.html + generated a2ui.json).

Reflected attributes from the start:

- `<admin-sidebar>` — `[collapsed]` (boolean), `[name]` (string), `[min-width]` / `[max-width]` (string)
- `<admin-command>` — `[open]` (boolean), `[shortcut]` (enum)

Host (`<admin-shell>`) read BOTH shapes via `:is()` selectors during the compat window:

```js
static SIDEBAR_SEL =
  ':is(admin-sidebar[slot="leading"], admin-sidebar[slot="trailing"], ' +
  '[data-admin-sidebar], aside-ui[slot="leading"], aside-ui[slot="trailing"])';

btn.addEventListener('click', () => {
  const sidebar = this.querySelector(`:is(admin-sidebar[slot="${name}"], [data-admin-sidebar="${name}"])`);
  if (typeof sidebar.toggle === 'function') sidebar.toggle();
  else this.legacyToggle(sidebar, name);
});
```

CSS bridge `admin-shell.bespoke.css` (~240 LOC) imported last — isolating bespoke rules from legacy CSS so Phase 3 deprecation could be a single regex pass.

### Phase 3 (deprecate — ~9 days later)

ADR-0024 closed the arc. Host dropped priority-chain reads. CSS lifts collapsed `:is(legacy, bespoke)` to bespoke-only. `admin-shell.js`: **~305 → ~87 LOC (−71%)** — the shrinkage was the architectural signal that the abstraction was correct.

---

## §The verification

- `admin-sidebar.test.js` — 10/10 specs (registration, default reflected values, property-attribute round-trip, public API, events, persistence, disconnect cleanup)
- `admin-command.test.js` — 9/9 specs (Cmd+K toggle, focus trap, esc close, dialog polyfill workaround)
- `node scripts/build/components.mjs --verify` — clean
- `npm run verify:traits` — 100%
- `npm run smoke:engines` — green
- `smoke:consumers` — 6/6 (legacy markup still worked through compat window)
- at deprecation: bespoke-children tests 78/78 + a clean release verification cut

---

## §The lesson

Three things graduated from the admin cluster:

1. **The 4-concern heuristic generalizes.** Chat (3+3=6 children), editor (4+2=6, with delegation to `<pane-ui>`), simple (1+2=3 — thinnest cluster) all decomposed cleanly with the same heuristic.
2. **Compat window must be SHORT.** ~9 days was enough to migrate 6 consumers; the host bloated to ~305 LOC during compat and shrank back to ~87 at deprecation. Longer would have let the dual-shape reads rot the host.
3. **Test the BEHAVIOR, not the mechanism.** Several attempts to `vi.spyOn(document, 'addEventListener')` failed in happy-dom's customElements lifecycle quirks; testing "does Cmd+K toggle?" instead always worked.

Pattern compounds — each successive cluster built faster:

- admin (1st): ~4 hours (inventing the pattern)
- chat (2nd): ~2 hours (mechanical replication)
- editor (3rd): ~2 hours (introduces delegation pitfall #11)
- simple (4th): **~30 minutes** (mechanical follow-template)

Skills compound when they're maintained.

## §Cross-references

- [shell-patterns.md](../../references/shell-patterns.md) § Examples — 4 canonical clusters
- ADR-0023 — bespoke shell-tier children architectural rationale
- ADR-0024 — legacy shell shapes retired (canonical deprecation playbook)
- ADR-0015 — `<cluster-thing>` naming convention (no `-ui` suffix for bespoke children)
- `packages/web-modules/shell/admin-shell/` — canonical implementation
- `packages/web-modules/shell/admin-shell/css/admin-shell.bespoke.css` — the CSS bridge pattern in production
