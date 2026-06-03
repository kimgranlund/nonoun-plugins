---
name: rubric-score
description: >
  Phase 3 rubric — A-vs-B gap scoring. Compares the ideal spec (Phase 1)
  against the actual canvas decomposition (Phase 2) across five structural
  dimensions plus one mechanical intent check. Max score: 105.
  (v2.0.0: D6 replaced with mechanical root-component match check;
  rubric-spec.md deleted — Phase 1 no longer scored.)
---

# Rubric — A-vs-B Gap Score (Fidelity)

**Used in**: Phase 3 of loop-protocol.md. **Input**: `spec.*` fields from Phase 1 + the decomposed trust-boundary file from Phase 2. **Output**: Score 0–105, delta vs prior cycle, per-dimension breakdown.

> The input is ALWAYS the sanitized decomposed file — never the raw DOM. See §TrustBoundary in loop-protocol.md.

---

## §Thresholds

Max score is 105 (D1–D5 at 20 each = 100; D6 mechanical = 0 or +5).

| Level | Score | Meaning |
| --- | --- | --- |
| **Excellence** | 92–105 | Generated output matches the ideal spec with only cosmetic gaps |
| **Acceptable** | 70–91 | Structural intent met; minor primitive substitutions or missing secondary elements |
| **Failing** | 0–69 | Wrong root container, wrong layout strategy, or primary intent not represented |

**Exit condition gate**: every prompt at Excellence (92+) AND no prompt has `overflowElements.length > 0` in its decomposed file.

---

## §VisualGate (independent of structural score)

**The visual gate is evaluated from `decomposed.overflowElements` before Phase 3 scoring. It cannot be compensated by a high structural score.**

A prompt with `rubricScore.score ≥ 92` is still **FAILING** if:

- `overflowElements.length > 0` — mechanically detected text/layout clipping

Each overflow entry auto-promotes to a **P1 cosmetic finding** in Phase 4:

- `p1Count += 1` per overflow element
- Issue text: `"[tag] content clipped — overflow:hidden with scrollWidth > clientWidth"`

This enforces the independence of visual and structural review lanes:

- **Structural lane** (Phase 3): correct component types, nesting, attributes
- **Visual lane** (Phase 2→4 overflow gate): legible, unclipped, visible render

A prompt must clear both lanes independently. The analytics-chart case (score 93, all stat labels clipped to "T.." and "$..", chart invisible) is the canonical example of structural pass / visual fail.

---

## §Dimensions

Score each dimension 0–20 except D6 (0–10 modifier). Apply D6 as a bonus or penalty on top of D1–D5.

### D1 — Root container fidelity (0–20)

Does the actual root container match the spec?

| Score | Condition |
| --- | --- |
| 20 | Exact match: same tag + same key attrs |
| 15 | Same tag, minor attr difference (missing `size` or `variant`) |
| 10 | Same category (both are card-like, or both are layout-only) |
| 5 | Wrong category but not catastrophically wrong |
| 0 | Completely wrong (e.g. bare div where card-ui expected; form stamped as table) |

### D2 — Layout strategy fidelity (0–20)

Does the actual layout direction / primitive match the spec?

| Score | Condition |
| --- | --- |
| 20 | Exact: same layout primitive, same gap, same direction |
| 15 | Same direction (vertical/horizontal) but wrong primitive or missing gap attr |
| 10 | Layout direction correct; gap incorrect or missing |
| 5 | Wrong direction but content still readable |
| 0 | Horizontal where vertical required (or vice versa), or no layout applied |

### D3 — Slot vocabulary fidelity (0–20)

For slotted components (card-ui, drawer-ui, modal-ui, etc.): do the slot placements match?

Key slot contracts to check:

- card-ui: header → `slot=icon`, `slot=heading`, `slot=description`, `slot=action`; body → `<section>` child; footer → `slot="footer"` on footer element
- list-item-ui: `slot=icon`, `slot=text`, `slot=description`, `slot=action`
- field-ui: no slots — content is the control child

Score: 18–20 = all key slots correct. Deduct 5 per incorrect or missing slot placement. Floor 0.

### D4 — Primitive accuracy (0–20)

For each key element, does the actual primitive match what the spec required?

Compare `spec.keyComponents` (A) against `decomposed.components` (B):

- 20 = all key elements match
- Deduct 5 per wrong primitive (component in B not matching corresponding component in A)
- Deduct 3 per missing element (in A but absent from B)
- Deduct 2 per unexpected element (in B but absent from A)
- Floor 0

Use the lookup table in loop-protocol.md §Phase 2 for tag-to-name mapping. Do NOT use rubric-spec.md D3 (that file was deleted in v2.0.0).

### D5 — Content and data binding fidelity (0–20)

Are the key attrs populated with meaningful content?

| Attr                    | Expected                 | Deduct if missing |
| ----------------------- | ------------------------ | ----------------- |
| `text=` on button-ui    | Non-empty action label   | –4                |
| `label=` on field-ui    | Describes the field      | –3                |
| `value=` on stat-ui     | Shows a realistic number | –4                |
| `change=` on stat-ui    | Shows trend delta        | –2                |
| `icon=` on button/nav   | Correct semantic icon    | –3                |
| `variant=` on badge/tag | Correct semantic variant | –2                |

Score: Start at 20. Apply deductions. Floor 0.

### D6 — Root component match (mechanical, 0 or +5)

Does `decomposed.rootComponent` (from Phase 2 lookup) match `spec.rootComponent` (from Phase 1 spec output)?

| Score | Condition                                                     |
| ----- | ------------------------------------------------------------- |
| +5    | Exact tag match (both are "Card", or both are "Column", etc.) |
| 0     | Different root component                                      |

This is a single mechanical lookup comparison — no agent judgment required. It replaced the former ±10 subjective "intent satisfaction modifier" (v2.0.0). The human QA gate in §Cycle Close covers intent verification for the cycle.

---

## §Delta Calculation

For each prompt:

```text
delta = rubricScore.score(cycle N) - rubricScore.score(cycle N-1)
```

- Positive delta = improvement.
- Zero delta = no change (investigate if this persists two cycles).
- Negative delta = regression (must be explained in root-cause analysis before cycle N+1).

If no prior cycle exists, delta = null.

---

## §Root-Cause Classification

For each gap found in D1–D5, classify the cause:

| Code | Cause |
| --- | --- |
| `WRONG_CHUNK` | Retrieval returned the wrong corpus chunk (wrong content for intent) |
| `EMPTY_CHUNK` | Chunk exists but template has no useful attrs (props not transpiled) |
| `WRONG_COMPONENT` | Chunk has the right structure but wrong primitive (e.g. select-ui children are Text nodes) |
| `MISSING_PROPS` | Component present but key attrs not set (label, text, value) |
| `WRONG_NESTING` | Component used correctly but placed at wrong DOM depth |
| `TRANSPILER_GAP` | Prop not in catalog; transpiler cannot extract it |
| `RETRIEVAL_SCORE` | Correct chunk exists but scored lower than wrong chunk |
| `FREE_FORM_HALLUC` | Free-form LLM chose a non-existent or wrong primitive |
| `COSMETIC_ONLY` | Structure correct; only visual/spacing issue |

Record cause codes in `scores.json` per gap entry.

---

## §DomainMismatchCheck

Before Phase 3 scoring, verify the retrieved chunk's domain matches the gallery prompt's group. This is a pre-scoring gate, not a rubric dimension:

```text
prompt group  → expected domains
auth/         → auth, forms
billing/      → billing, settings, forms
dashboard/    → dashboard, data
data-tables/  → data, settings
forms/        → forms, data
content/      → content, layout, marketing
navigation/   → navigation, layout
settings/     → settings, forms
notifications/→ agent, data
team-access/  → settings, data
onboarding/   → onboarding, forms, auth
```

If the decomposed rootComponent + components clearly indicate a **different domain** (e.g. email inbox for a contact form prompt, social media post for a blog post prompt), classify as `RETRIEVAL_SCORE` and flag for human QA review. **Do not score these prompts as PASSING without human verification.** DOM scoring will see valid component types regardless of whether the content answers the prompt.

---

## §KnownGaps — failures the scoring system cannot detect

These failure classes pass Phase 3 and Phase 4 mechanically but are visually wrong. Human QA (§Cycle Close) is the only gate that catches them unless a computed-style probe is added to Phase 2.

### Layout-axis collapse (validated analytics-chart C14)

**What it is**: Two or more elements that should be on separate lines render on the same line because the wrong CSS display mode is active.

**Why it passes**: Phase 3 scores component presence — both Text nodes are in the tree, so D4 is satisfied. The overflow visual gate (Phase 4) only detects `scrollWidth > clientWidth`, not wrong-axis layout.

**Canonical case**: `text-ui` has `display:inline` by default. In a card header where the grid layout didn't activate (because `slot` attribute was dropped during transpilation), an inline `text-ui` collapses next to the block `<h3>` on the same line.

**Detection**: Only via human QA or a computed-style probe that checks `getComputedStyle(el).display` and `getBoundingClientRect().top` to confirm each Text node occupies a distinct vertical position.

**Prevention**: In corpus HTML, use native block elements (`h3`, `p`) for card headers with subtitles — see loop-protocol.md §CorpusHTMLPatterns.

### Empty chart (no data)

**What it is**: `chart-ui` renders at 0px height when no data is provided, but the component IS in the DOM tree.

**Why it passes**: Phase 3 sees `Chart` in the component list — D4 satisfied. The visual gate doesn't flag 0px chart within a card that has other content (the card itself is non-zero height).

**Detection**: Overflow gate catches 0px chart only if it causes the card to collapse below 50px. Otherwise only human QA.

**Prevention**: Always provide `data='[…]'` inline on `chart-ui` elements in corpus HTML — see loop-protocol.md §CorpusHTMLPatterns.

### Viewport clipping (canvas boundary)

**What it is**: Content is visually cut off by the canvas viewport edge, not by a CSS `overflow: hidden` boundary.

**Why it passes**: The overflow detector (the Phase 2 decompose script) only fires on elements where `scrollWidth > clientWidth` AND `overflow: hidden` is computed. If the element is simply wider than the canvas viewport, no CSS overflow rule fires — the content is cut by the browser paint boundary instead.

**Canonical case**: magic-link-sent alert content "Didn't get th..." — the alert renders fully but the canvas viewport clips the trailing text.

**Detection**: Only via human visual inspection of the screenshot. The overflow gate misses this class entirely.

**Prevention**: Keep canvas-bound content narrow (avoid long inline text without wrapping). Use `text-ui align="center"` for centered auth cards.

### RETRIEVAL_SCORE failures (wrong content, correct-looking DOM)

**What it is**: The retrieval engine returns a completely different chunk (email inbox, social media post, etc.) that happens to share component types (Card + List + Avatar) with the expected content.

**Why it passes**: Phase 3 scores component presence — `Card + List + Avatar = valid structure` regardless of whether those components are showing the right content for the prompt. The visual gate catches clipping, not semantic mismatch.

**Canonical cases**:

- contact-form → email inbox (both have Card + Field/List)
- team-members → email inbox (both have List + Avatar + Text)
- blog-post-card → social media post card (both have Card + Avatar + Image)
- invoice-table → invoice detail line-items (both have Card + Table)

**Detection**: Human QA gate — this IS why §Cycle Close requires human review of 5 sampled prompts. RETRIEVAL_SCORE failures will fool automated scoring every time. See §DomainMismatchCheck for a pre-screening heuristic.

**Prevention**: Ensure each gallery prompt has a dedicated chunk with highly specific keywords that outscores any generic competitor. The HTML→harvest fix workflow ensures chunks are grounded.
