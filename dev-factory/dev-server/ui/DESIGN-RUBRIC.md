# App-Shell Design Rubric — two crossing axes

The cockpit (`ui/`) is graded against the reference app-shell (the `ui-app` HCT tool) on **two independent axes that
traverse the same hierarchy in opposite directions** — the UI analogue of the dev-factory's own PRD↔SPEC seam:

- **Outside-in · macro→micro layout** grades the **space the eye parses** — the whole frame down to one aligned atom.
  (The *outside* view: what it looks like.)
- **Inside-out · actions→surfaces** grades the **behavior the hand performs** — the atomic verb out to whole-shell
  coherence. (The *inside* view: what it does.)

They **cross at the region / card / surface**: every panel is simultaneously a *spatial slot* (Axis A) and a
*functional home* (Axis B). A shell can be spatially perfect yet functionally orphaned (panels no one acts in), or
functionally complete yet spatially collapsed (every surface stacked in one column). **Both axes must pass** — and a
failure on each is a *different defect with a different fix*, so the two scores are reported separately.

**Severity.** `[gate]` = a binary structural invariant; one failure **cascades** (a collapsed frame voids every finer
judgment beneath it, so grade gates first). `[review]` = a graded judgment, 1–5.

---

## Axis A · Outside-in (macro-layout → micro-layout)

Zoom in from the viewport to the atom. Each level is only measurable once the level above it holds.

| # | Level | Intent | Criteria |
|---|---|---|---|
| **A1** | **Frame** (macro) | The viewport is a fixed, full-bleed shell — not a scrolling page. | `[gate]` ONE 3-col × 3-row grid (`header / left·center·right / footer`) fills 100vh; the body never scrolls; only panes scroll internally; the frame is immovable while content churns. |
| **A2** | **Regions** | The five regions occupy their slots at the right proportions. | `[gate]` header (~48px) + footer (~30px) span full width; left (~290px) · center (elastic) · right (~300–330px) sit between; each on its own surface, separated by a 1px divider. |
| **A3** | **Region-internal order** (meso) | Each region shares one internal grammar. | `[review]` header = brand-left / actions-right with a flex spacer; each pane = `pane-label` + a scroll body; the canvas = `canvas-header / canvas-area / canvas-footer` sub-grid; one shared alignment baseline + gutter. |
| **A4** | **Grouping** | Pane content is chunked into cards, not loose text. | `[review]` bordered, rounded, padded cards (analysis cards, inspector sections) on a consistent vertical rhythm; each = a label + its content; no naked text rivers. |
| **A5** | **Atoms** (micro) | Inside a card, atoms align on a grid. | `[review]` label-left / value-right; tabular numerals; one type + spacing scale (tokens only); dense but legible; no unaligned run-ons (`instantiated 2validated 9`). |

---

## Axis B · Inside-out (feature-actions → feature-surfaces)

Expand out from the atomic verb to whole-shell coherence. Each level presumes the one before it.

| # | Level | Intent | Criteria |
|---|---|---|---|
| **B1** | **Action inventory** (core) | Every core verb exists and is reachable. | `[gate]` switch-canvas · select (cell/ticket) · inspect (detail / asset / signals) · steer · create (ticket/brief) · transition (advance/block) · zoom · theme — each present, none buried two clicks deep. |
| **B2** | **Action → surface binding** | Each verb has ONE obvious surface, co-located with its object. | `[gate]` switching in the canvas-header; inspecting in the right pane; steering a tab *where you inspect*; creating a header button → modal. **No orphan verb** (an action with no surface) and **no orphan surface** (a panel with no verb). |
| **B3** | **State + feedback** | Surfaces reflect state and confirm results. | `[review]` selected object highlights; active mode/tab is marked; a running worker pulses; every action confirms (optimistic update / toast / the gate's refusal reason) — the surface tells you what it did. |
| **B4** | **Surface → pane fit** | Surfaces cluster by the job they serve. | `[review]` telemetry/analysis → left; the artifact under work → center; properties/inspection/steering → right; global status + warnings → footer. A surface lives in the pane whose *job* it serves, nowhere else. |
| **B5** | **Cross-surface coherence** (whole) | One model, many agreeing projections. | `[review]` one selection updates the left analysis AND the right inspector; the milestone strip, footer counts, rail, and canvas never disagree; a single source of truth, projected — never re-entered. |

---

## Scoring

- A `[gate]` failure on **A1 · A2 · B1 · B2** ⇒ the shell is **BLOCKED**: fix it before grading any `[review]`
  dimension (a collapsed frame makes A3–A5 literally unmeasurable).
- `[review]` dimensions score 1–5; a shippable shell is **≥ 4 on every review dim with zero gate failures**.
- Report **Axis A and Axis B scores separately.** "Pretty but dead" (A passes, B fails) and "functional but
  unreadable" (B passes, A fails) are opposite failures and must not average into a misleading middle.

---

## Applied — current cockpit vs the reference (HCT)

| Dim | Reference | Current cockpit | Verdict |
|---|---|---|---|
| **A1 Frame** | fixed 3×3, panes scroll | **collapsed to one column** — the stale `styles.css` cache never loaded the grid rules | **GATE FAIL → fixed** (`styles.css?v=10`); re-shoot to confirm |
| **A2 Regions** | 5 divided regions | present in the DOM; unstyled until the CSS loads | pending re-grade |
| **A3–A5** | rich cards, aligned atoms | rules authored against tokens; verify after refresh | pending |
| **B1 Actions** | full | switch · select · inspect · steer · create · zoom · theme present | **pass** |
| **B2 Binding** | tight | switcher→canvas-header, inspect→right, steer→tab, create→header | pass, **except `transition` has no surface yet** (no advance/block buttons in the Cell tab) |
| **B3 Feedback** | selection ring · ⚠/✓ · unsaved dot | selection + pulse + toast wired; **no pinned preview card** like the reference's bottom swatch | partial |
| **B4 Fit** | clean | correct | **pass** |
| **B5 Coherence** | one model | `selectInspector` fans one selection to both panes | **pass** |

**Headline:** the current shell is **functionally sound (Axis B largely passes) but spatially collapsed (Axis A1
gate-fails)** — a pure macro-frame failure from a stale stylesheet cache, *not* a design error. Once `styles.css` is
versioned and reloaded, re-grade A2–A5 against the reference. The two known **Axis-B** gaps to close next, in order:

1. **B2 — the `transition` surface.** The Cell tab shows detail but offers no *advance / block* action; the verb
   exists (the board DnD) but has no home in the inspector where its object lives.
2. **B3 — a pinned preview card.** The reference pins a live preview at the bottom of the right pane (its
   `surface · onSurface` swatch); the cockpit's inspector should pin the selected cell's latest signal / verify
   result / live worker tail so the inspector always *shows a result*, not just metadata.
