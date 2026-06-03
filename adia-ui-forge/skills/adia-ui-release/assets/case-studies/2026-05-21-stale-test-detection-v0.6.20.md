# Case study — stale test detection (v0.6.20)

**Cycle:** 2026-05-21 (v0.6.19 → v0.6.20) **Scenario:** `recovery-paths.md` § Scenario 5 (stale test detection) **Source ledger:** `.brain/audit-history/2026-05-21-release-v0.6.20.json` **Outcome:** A v0.6.17 regression guard failed against v0.6.20's deliberate CSS change; assertion updated to match the new contract + a guard for the new behavior added.

---

## §The shape

Operator ran `npm run test:unit` at HEAD as part of v0.6.20 pre-flight. Result: **1 fail / 1078 pass / 1079 total**.

The failing test:

```text
FAIL  packages/web-modules/shell/admin-shell/admin-shell.test.js
  > admin-shell.collapsed.css — vanilla HTML fallback (v0.6.17)
  > contains the vanilla-HTML fallback block

AssertionError: expected '/* ══...' to match /\[slot="heading"\]\s*\{[\s\S]*?display:\s*none/
```

The test was a **v0.6.17 regression guard**: when v0.6.17 added the forgiving-fallback block to `admin-shell.collapsed.css` (clipping vanilla-HTML overflow when the sidebar collapses), the test was added to verify the block stays present. It asserted the rule existed via:

```js
expect(collapsedCSS).toMatch(/\[slot="heading"\]\s*\{[\s\S]*?display:\s*none/);
```

— i.e. `[slot="heading"]` IMMEDIATELY followed by `{ ... display: none`.

---

## §The diagnosis

The v0.6.20 cycle's `[Unreleased]` block included:

> `### Fixed — collapsed sidebar [slot="heading"] hide no longer wipes composed wrappers (FEEDBACK-38 addendum)`

— a deliberate change to the CSS the test was asserting against.

The OLD rule (v0.6.17):

```css
[slot="heading"] {
  display: none;
}
```

The NEW rule (v0.6.20 FB-38 addendum):

```css
:is(span, p, div, h1, h2, h3, h4, h5, h6)[slot="heading"],
[slot="heading"]:not(:has(> [slot])) {
  display: none;
}
```

The new rule **narrows** the hide: plain-text headings (`<span slot="heading">`) are still hidden, but composed wrappers carrying their own slot contract (`<admin-entity-item slot="heading">`) survive collapse via the `:not(:has(> [slot]))` guard.

The test's regex `\[slot="heading"\]\s*\{` requires `[slot="heading"]` to be immediately followed by `{`. In the new CSS, `[slot="heading"]` is followed by `:not(:has(> [slot]))` before `{`. **The test wasn't updated to match the deliberate change.**

This is a **stale test**, not a regression. The peer shipped the CSS change but didn't update the regression guard.

Decision per `recovery-paths.md` § Scenario 5:

> Read the test's assertion + read the CHANGELOG entry that documents the change. Both should describe the same behavior. If they disagree → one of them is stale.
>
> Read the actual production code. If it matches the CHANGELOG entry's description → the test is stale.

Confirmed: CHANGELOG describes the FB-38 addendum behavior; the CSS matches the CHANGELOG; the test is stale.

---

## §The fix

Two assertion changes in `admin-shell.test.js`:

### 1. Update the existing assertion to the new shape

Before:

```js
expect(collapsedCSS).toMatch(/\[slot="heading"\]\s*\{[\s\S]*?display:\s*none/);
```

After:

```js
// v0.6.20 (FEEDBACK-38 addendum): the heading-hide rule narrowed from a
// blanket `[slot="heading"]` to plain-text headings + headings without
// slotted children, so composed wrappers (<admin-entity-item slot="heading">)
// survive collapse. The rule still resolves to `display: none`.
expect(collapsedCSS).toMatch(/\[slot="heading"\][^{]*\{\s*display:\s*none/);
```

Change: `\s*\{` (whitespace then `{`) → `[^{]*\{` (any non-brace chars then `{`). This matches both the old blanket shape AND the new narrowed shape.

### 2. Add a guard assertion for the FB-38-addendum contract

```js
expect(collapsedCSS).toMatch(/\[slot="heading"\]:not\(:has\(>\s*\[slot\]\)\)/);
```

This asserts the `:not(:has(> [slot]))` composed-wrapper guard is present. If a future cycle accidentally reverts the FB-38 addendum, this assertion fires.

### Run the suite

```bash
npx vitest run packages/web-modules/shell/admin-shell/admin-shell.test.js
# Test Files  1 passed (1)
# Tests  6 passed (6)
```

Then ship — `admin-shell.test.js` is part of v0.6.20's release commit allowlist (it's a test update that completes the FB-38-addendum work).

---

## §The lesson

1. **Stale test ≠ regression.** When a test fails against a deliberate CHANGELOG-documented change, the test is stale. Don't "fix the regression" — update the test.
2. **The diagnostic triangle: assertion + CHANGELOG + source code.** Read all three. The two that agree are correct; the one that disagrees is stale.
3. **Update + add — don't just patch.** When the production behavior changes, the test should pin the NEW behavior. Add a guard assertion for the new contract so future regressions fire here.
4. **Inline comment with the cycle ref.** Add a comment in the test naming the cycle (v0.6.20) and the closed feedback (FEEDBACK-38 addendum). Future operators reading the test understand why the assertion has the new shape.
5. **The test update belongs in the release commit.** It's part of the work that ships the CSS change. Stage it explicitly in the release-commit allowlist.

---

## §Ledger fragment

```json
"notes": [
  "STALE TEST FIXED: admin-shell.test.js 'contains the vanilla-HTML fallback block' (a v0.6.17 regression guard) asserted the old blanket [slot=heading] { display: none } shape. The v0.6.20 FEEDBACK-38-addendum fix deliberately narrowed that rule (:is(span,p,div,h1-6)[slot=heading] + [slot=heading]:not(:has(> [slot])) — composed wrappers survive collapse). The peer shipped the CSS change but did not update the test. Deploy session updated the assertion to match the new shape + added a guard assertion for the :not(:has(> [slot])) clause. Not a regression — a stale test."
]
```

`grep -l "STALE TEST" .brain/audit-history/*.json` finds cycles that required this scenario.

---

## §Cross-references

- `../../references/recovery-paths.md` § Scenario 5 — the canonical diagnosis checklist
- `../../references/gates-catalog.md` § Category 8 § `test:unit` — the gate definition + the stale-test-vs-regression triage
- `../../references/cycle-happy-path.md` § Step 5 — staging the test update alongside the release commit
