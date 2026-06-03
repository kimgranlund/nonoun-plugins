# Common gotchas — composite authoring traps

Five concrete failure modes encountered across a billing-overview rebuild + multi-demo grandfather-elimination cycle. Each is the kind of bug that:

- Renders visually broken without console errors
- Passes existing audits silently
- Is fixed in one place but recurs in others until pattern-corrected

Read this BEFORE Phase 3 sketch. Each entry includes the pattern, the detector (if any), and the fix.

---

## 1. Component used without reading its CSS — and especially without reading its composition grammar

**Pattern**: Stamping `<X-ui>` and relying on attributes/slots without opening `X-ui.css`. The primitive's `@scope` rules ARE part of its API contract, not implementation details. Particularly load-bearing: composition grammars (which children the primitive expects + how it lays them out).

**Example**: `payment-method-list-ui` stamped three sibling `<div data-brand>/<div data-meta>/<div data-actions>` inside `<card-ui>` and re-implemented the 3-column grid via custom `@scope` rules. Bypassed card-ui's canonical `<header>` + `[slot=icon|heading|description|action]` grammar entirely. Result: visual debt downstream (50% icon-to-frame ratio, off-rhythm tag placement, fragile chrome).

**Detector**: [§Phase 2.5a Component Literacy](composite-demo-protocol.md) suggests `composition_grammar` extraction from each used primitive's `.css`. `audit:card-structure` catches the specific card-ui bypass; analogous audits don't exist yet for avatar-ui / drawer-ui / aside-ui (forward work).

**Fix**: Read the primitive's `.css` end-to-end. Identify its expected child structure (slot grammar). USE it; never invent a parallel layer.

---

## 2. Parent CSS overriding child component's intrinsic display

**Pattern**: A parent composite hides/shows an embedded child via `display: none` ↔ `display: block` toggling. The `display: block` override beats the child's `:scope { display: flex }` from its own `@scope` (specificity 0,2,0 vs 0,1,0). Child's intrinsic layout silently collapses.

**Example**: 4 billing composites all had:

```css
/* WRONG — clobbers empty-state-ui's flex column */
:scope > [data-empty] { display: none; }
:scope[empty] > [data-empty] { display: block; }
```

`empty-state-ui` declares its own `:scope { display: flex; flex-direction: column; align-items: center }`. The parent's `display: block` removed that, making icon + heading + description flow inline: **`⊡ No payment methodsAdd a method to get started.`**

**Detector**: None today. Caught by user visual review.

**Fix** — invert visibility toggle so no display value is set when shown:

```css
/* RIGHT — child's :scope display remains intact */
:scope:not([empty]) > [data-empty] { display: none; }
```

---

## 3. Mixed sizes across form/control groups

**Pattern**: A composite stamps multiple form/control primitives in the same visual row (toolbar, button cluster, filter strip) without coordinating `size` attributes. Defaults differ — buttons might default `sm`, inputs default to a larger size, search-ui doesn't forward `size` to its inner input.

**Example**: an invoice-history toolbar had buttons at `size='sm'` (24px), filter chips at `size='sm'` (24px), search input at default (~36px). Same row, mismatched baseline.

**Detector**: None today. Caught by user visual review.

**Fix**:

- When stamping a control group, set the SAME `size` attribute on every control explicitly.
- Wrapper primitives (search-ui wraps input-ui; select-ui wraps native select) MUST forward `[size]` to their inner control. If a wrapper doesn't forward, file a fix in the wrapper rather than working around it in the consumer.

---

## 4. minmax(min, 1fr) inside repeat() fighting container queries

**Pattern**: A grid uses `repeat(N, minmax(<min>, 1fr))` with a hardcoded minimum, BUT the container also has `@container` queries that collapse columns at breakpoints. The minmax fights the breakpoints — when the container narrows, columns hit the floor and overflow before the breakpoint reduces column count.

**Example**: a dashboard-layout KPI grid was `repeat(4, minmax(16em, 1fr))` plus `@container ≤48em → 2 cols` and `≤32em → 1 col`. Redundant + conflicted. Removed the minmax; container queries own the responsive collapse cleanly.

**Detector**: None today.

**Fix**: When a grid has container-query breakpoints, use plain `repeat(N, 1fr)`. The breakpoints handle responsive behavior; minmax is for grids WITHOUT container queries.

---

## 5. Nested `<!-- ... -->` inside design-plan canonical-sketch fenced blocks

**Pattern**: The `<!-- design-plan: ... -->` block contains a fenced ` ```canonical-sketch ... ``` ` body. Authors sometimes paste HTML examples with inner `<!-- ... -->` comments into the sketch. HTML comments DON'T NEST — the inner `-->` closes the OUTER `<!-- design-plan: -->`. Trailing ` ``` --> ` then leaks as visible text on the page.

**Example**: a billing-overview.examples.html had two inner comments inside its canonical-sketch (annotations + a drawer composition example). Stray ` ``` --> ` rendered above the page header.

**Detector**: ✓ caught by `check:demo-pattern-source` — emits `phase_3_sketch contains an inner <!-- ... --> comment` finding.

**Fix**: Remove inner HTML comments from the canonical-sketch. Use plain text annotations or remove the doc-noise entirely.

---

## Meta-pattern across all 5

**Composites and primitives have layered contracts. The parent's CSS shouldn't reach into the child's layout territory. The child's CSS shouldn't fight its parent's container queries. The audit should detect the rendering hazard, not just the parsing structure.**

The structural defense for #1 (composition-grammar bypass) is `npm run audit:card-structure[:strict]` / `npm run audit:avatar-structure` / `npm run audit:alert-structure` (HTML + JS `createElement` scan) plus `npm run audit:sketch-grammar` at Phase 3. Phase 2.5a Component Literacy is a literacy hint, not a gate — the mechanical defenses above are the proximate fix; pre-flight is optional enrichment. See [composite-demo-protocol.md](composite-demo-protocol.md) §Phase 2.5a for the reframing. The other four gotchas are caught only by visual review until corresponding audits are added.
