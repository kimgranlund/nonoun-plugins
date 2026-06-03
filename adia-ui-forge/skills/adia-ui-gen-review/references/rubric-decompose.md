---
name: rubric-decompose
description: >
  Phase 2 rubric — evaluates the structured decomposition of the actual
  canvas output. Measures the quality and completeness of the analysis,
  not the quality of the generated output (that's rubric-score.md).
---

# Rubric — Canvas Decomposition

**Used in**: Phase 2 of loop-protocol.md. **Input**: Screenshot + DOM tree from the canvas-ui render. **Output**: A score 0–100 and a list of findings (not yet compared to Spec).

---

## §Thresholds

| Level | Score | Meaning |
| --- | --- | --- |
| **Excellence** | 85–100 | Complete outside-in decomposition; every element identified with correct primitive name |
| **Acceptable** | 65–84 | Minor gaps in decomposition — one level missed, or one element misidentified |
| **Failing** | 0–64 | Decomposition incomplete; root container or major child missed |

**Gate score to pass this phase**: ≥ 65. Failing decomposition invalidates the score in Phase 3.

---

## §Decomposition Protocol

The agent must walk the DOM from **outside-in**, exactly in this order:

1. **Root container** — What is the outermost element tag? (`canvas-ui` renders to a2ui-root, then the component tree. The "root" is the first rendered component node.)
2. **Layout strategy** — flex? grid? col-ui? row-ui? raw block?
3. **Primary regions** — Header / body / footer? Named card slots? Left/right panes?
4. **Content regions** — For each primary region, what primitives fill it?
5. **Leaf nodes** — What are the text nodes, icon nodes, button nodes at the leaves?
6. **Data binding** — What attributes carry content? (`text=`, `label=`, `value=`, `icon=`, etc.)

For each level, the agent must name:

- The element tag (e.g. `card-ui`, `col-ui`, `field-ui`)
- Key attributes observed (e.g. `variant="primary"`, `icon="email"`)
- Slot placement if a slotted child (e.g. `slot="action"`)

---

## §Dimensions

Score each dimension 0–20. Total = sum of 5 dimensions.

### D1 — Root container identification (0–20)

| Score | Description                                      |
| ----- | ------------------------------------------------ |
| 18–20 | Correct tag + key attrs recorded                 |
| 13–17 | Tag correct, attrs incomplete                    |
| 8–12  | Tag partially correct (e.g. "some card element") |
| 0–7   | Root not identified or wrong                     |

### D2 — Layout strategy accuracy (0–20)

| Score | Description                                                         |
| ----- | ------------------------------------------------------------------- |
| 18–20 | Layout primitive named correctly with direction + gap if applicable |
| 13–17 | Layout type correct but gap or direction missing                    |
| 8–12  | "stacked" or "column" without naming the primitive                  |
| 0–7   | Layout not described or incorrect                                   |

### D3 — Primary and secondary region completeness (0–20)

Score based on how many key regions were identified vs missed.

- If the canvas has a card header, body section, and footer: all three must be named.
- Partial credit proportional to regions identified.

### D4 — Primitive identification accuracy (0–20)

For each named element, is the primitive correctly identified?

- `button-ui` not `button` or "a button"
- `field-ui` not `div with label`
- `badge-ui` not "small colored text"

Deduct 3 per misidentified primitive. Floor 0.

### D5 — Data binding capture (0–20)

Were the key attrs recorded?

- Content-carrying attrs: `text=`, `label=`, `value=`, `icon=`, `heading=`
- Structural attrs: `variant=`, `size=`, `gap=`, `columns=`
- Missing attrs that were visible: deduct 4 each. Floor 0.

---

## §Screenshot Requirements

The agent must confirm:

- [ ] Screenshot taken AFTER `canvas-ui.processAll()` settles (≥2s wait).
- [ ] Clip is the `.gallery-canvas-wrap` bounding box exactly.
- [ ] Screenshot is saved to the cycle's `screenshots/<slug>.png`.
- [ ] If canvas height is < 50px, flag as RENDER_FAILURE and skip Phase 3.

---

## §Findings Format

Record findings as descriptive strings (observations, not judgments):

```json
[
  "Root: card-ui (no size or variant attrs visible)",
  "Layout: col-ui gap=3 inside section slot",
  "Missing: no footer slot populated; actions appear inline in body",
  "D5: button-ui text attr absent — label rendered via ::after pseudo, not captured"
]
```
