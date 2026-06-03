---
name: rubric-cosmetic
description: >
  Phase 4 rubric — visual and cosmetic quality audit of the canvas screenshot.
  Covers geometry, spacing, optical alignment, visual balance, and token usage.
  Separate from structural correctness (rubric-score.md).
---

# Rubric — Cosmetic & Visual Quality

**Used in**: Phase 4 of loop-protocol.md. **Input**: The canvas screenshot from Phase 2. **Output**: P1/P2/P3 issue count and issue list. P1 blocks prompt from PASSING.

---

## §Thresholds

A prompt is considered **cosmetically PASSING** when:

- P1 count = 0
- P2 count ≤ 2
- P3 count ≤ 4

A prompt has a **cosmetic BLOCK** (cannot be marked PASSING overall) when:

- P1 count ≥ 1

---

## §Severity Definitions

| Severity | Meaning | Example |
| --- | --- | --- |
| **P1** | User-visible layout failure; something looks broken or unusable | Content overflows canvas, zero-height element, overlapping text, invisible text on background |
| **P2** | Noticeably wrong; degrades quality but doesn't break functionality | Wrong padding on form fields, badge sitting outside its container, inconsistent gap scale |
| **P3** | Minor cosmetic; acceptable but suboptimal | Slightly off optical alignment, minor spacing inconsistency, icon size mismatch |

---

## §Cosmetic Dimensions

### COS-1 — Container geometry (P1/P2/P3)

Does each container use its space correctly?

Questions:

- Does any container have zero height or width when it should be non-zero? → P1
- Does any container overflow its parent visibly? → P1
- Is the aspect ratio of cards or images distorted? → P2
- Are containers expanding beyond their content without reason? → P2
- Is whitespace inside containers balanced (not all padding on one side)? → P3

### COS-2 — Spacing scale (P1/P2/P3)

Is the spacing system applied consistently?

Questions:

- Are there any elements with 0 visible gap when there should be clear separation? → P1
- Are any spacing values visually inconsistent within the same region (e.g. 3px between some fields, 20px between others)? → P2
- Is the spacing scale consistent with the AdiaUI token scale (multiples of 4px)? → P3
- Are margins and paddings balanced optically (left margin ≈ right margin in a centred block)? → P3

### COS-3 — Optical alignment (P2/P3)

Are elements optically aligned?

Questions:

- Are text baselines misaligned across a horizontal row? → P2
- Are icons vertically centred against their companion text? → P2 or P3
- Are action buttons aligned to the trailing edge of their container? → P3
- Are labels flush-left consistently within their group? → P3

### COS-4 — Visual balance (P2/P3)

Does the composition feel balanced?

Questions:

- Is there a single element that dominates the canvas with no visual counterweight? → P2
- Are left/right or top/bottom regions visually balanced relative to their importance? → P3
- Are font weight / size contrast ratios appropriate (heading vs body vs label)? → P2 if heading and body are same weight

### COS-5 — Token usage signals (P2/P3)

Can we infer any token misuse from the visual output?

Questions:

- Does any text appear at very low contrast against its background? → P2 (potential fg-subtle on bg-subtle)
- Does any background appear black/white when it should be a subtle tint? → P2
- Does any border appear too thick or too thin for its context? → P3
- Does any component appear unstyled (default browser styles bleeding through)? → P1

### COS-6 — Empty state quality (P2/P3)

For prompts where the canvas generates an empty or skeleton state:

Questions:

- Is the empty state visually communicative (not just a blank box)? → P2 if blank
- Does the empty state have appropriate height (not collapsed to near-zero)? → P2 if collapsed
- Is placeholder text readable and appropriately styled? → P3

---

## §Issue Format

Record each issue as a severity + location + observation:

```json
[
  { "severity": "P1", "location": "card-ui root", "issue": "Card height is zero — canvas-ui likely returned empty components array" },
  { "severity": "P2", "location": "field-ui email label", "issue": "Label appears right-aligned instead of left-aligned; field-ui inline mode applied incorrectly" },
  { "severity": "P2", "location": "action button", "issue": "button-ui primary appears clipped — container max-width cutting off trailing padding" },
  { "severity": "P3", "location": "col-ui body gap", "issue": "Gap between form fields inconsistent — some 8px, some 16px" }
]
```

---

## §Screenshot Reading Protocol

When reading the screenshot:

1. First scan for P1 issues (broken layout, overflow, invisible content).
2. Then scan each region top-to-bottom for P2 issues.
3. Finally note P3 issues.
4. Do not infer issues beyond what is visible — if you cannot see the spacing value, note "spacing appears inconsistent" not "gap is 7px".
5. Use the prompt context to evaluate intent: a loading skeleton that looks sparse is correct; a completed form that looks sparse may be a COS-6 finding.

---

## §Connection to Root Causes

Cosmetic findings often trace to one of:

- **Canvas CSS** — the gallery's `gallery-canvas-wrap` or canvas-ui CSS.
- **Component CSS** — the a2ui-root rendering inside canvas-ui picks up component token overrides.
- **Template attrs missing** — `gap=` not in the component node; default renders without spacing.
- **Wrong primitive** — a structurally wrong primitive that doesn't support the expected layout.

Record the suspected connection in the finding when it's obvious. Phase 5 (root cause) confirms it.
