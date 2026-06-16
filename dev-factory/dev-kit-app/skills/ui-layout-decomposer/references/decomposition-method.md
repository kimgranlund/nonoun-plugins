# The two-axis decomposition method

A UI layout is correct on **two independent axes that traverse the same spatial/functional hierarchy in opposite
directions**. Decompose (or design, or grade) any UI by walking *both*.

```
            OUTSIDE-IN  (macro → micro · "what the eye parses")
   ┌────────────────────────────────────────────────────────────┐
   │  A1 Frame → A2 Regions → A3 Region order → A4 Groups → A5 Atoms
   │                              ⤫  cross at the CARD / SURFACE  │
   │  B5 Coherence ← B4 Fit ← B3 Feedback ← B2 Binding ← B1 Actions
   └────────────────────────────────────────────────────────────┘
            INSIDE-OUT  (core → whole · "what the hand does")
```

The axes **cross at the region/card/surface**: a panel is simultaneously a *spatial slot* (you see it) and a
*functional home* (you act in it). Two failure shapes follow, and they are opposites:

- **Pretty but dead** — Axis A passes (clean frame, aligned atoms) but Axis B fails (panels host no verbs, or a
  verb has no home). The layout *reads* well and *does* nothing.
- **Functional but unreadable** — Axis B passes (every action works) but Axis A fails (it all stacks in one column,
  no frame). The layout *works* but the eye can't parse it.

Because they are opposites, **score and report the two axes separately. Never average them** — a single middling
number hides which of the two defects you actually have, and they need different fixes.

---

## Axis A — Outside-in (macro-layout → micro-layout)

Zoom in from the viewport to a single atom. **Each level is only measurable once the level above it holds** — so
grade top-down and stop at the first gate that fails.

### A1 · Frame `[gate]`
The viewport is a **fixed, full-bleed shell**, not a scrolling page.
- One layout grid fills the viewport (e.g. `header / body / footer` rows; the body splits into panes/columns).
- The body never page-scrolls; **only inner panes scroll**, independently.
- The frame is **immovable** while content churns (a data update never reflows the chrome).
- *Cascade:* if A1 fails, everything stacks in document order and A2–A5 are unmeasurable. **Fix A1 first.**
- *Common cause of failure:* a CSS grid that never loaded (stale stylesheet cache), a missing height chain
  (`html,body,root → 100%`), or panes that grow the page instead of scrolling internally.

### A2 · Regions `[gate]`
The named regions exist in their slots at the right proportions.
- Each archetype's signature regions are all present and each sits in its grid slot.
- Fixed bars (header/footer/tab-bar) are thin and span their edge; side panes have stable widths; the primary
  surface is elastic.
- Each region is its own surface, separated by a hairline divider — you can point at where one ends and the next
  begins.

### A3 · Region-internal order `[review]`
Each region shares one internal grammar so the eye learns it once.
- Header = identity-left / actions-right with a flexible spacer between.
- A pane = a small **pane-label** + a scrolling body.
- A canvas = `canvas-header` (tools) / `canvas-area` (surface) / `canvas-footer` (status) sub-stack.
- One shared alignment baseline and gutter across regions.

### A4 · Grouping `[review]`
Pane content is chunked into **cards**, not loose text rivers.
- Bordered / rounded / padded groups (analysis cards, inspector sections, form fieldsets) on a consistent rhythm.
- Each card = a label + its content; related atoms live in one card; unrelated ones don't.

### A5 · Atoms `[review]`
Inside a card, atoms align on a grid.
- Label-left / value-right; tabular numerals for numbers; one type scale + spacing scale (tokens only).
- High density but legible; no unaligned run-ons (the `instantiated 2validated 9` smell — missing gutters between
  atoms).

---

## Axis B — Inside-out (feature-actions → feature-surfaces)

Expand out from the atomic verb to whole-shell coherence. Each level presumes the one before it.

### B1 · Action inventory `[gate]`
Enumerate the **verbs** the user performs; every core verb exists and is reachable.
- Generic verb set to probe: **navigate · switch-view · select · inspect · create · edit/modify · act/run ·
  search/command · configure**. Not every UI needs all, but the ones the product promises must be present and not
  buried two clicks deep.

### B2 · Action → surface binding `[gate]`
Each verb has **one obvious surface, co-located with its object**.
- The surface for acting on X lives where X lives (inspect-a-cell → the pane showing the cell; switch-view → the
  header above the view).
- **No orphan verb** (an action the product needs with no surface to perform it) and **no orphan surface** (a panel
  that hosts no verb and shows nothing live).

### B3 · State + feedback `[review]`
Surfaces reflect state and confirm results.
- The selected object highlights; the active view/tab/mode is marked; in-flight work animates; an action confirms
  (optimistic update, toast, or the gate/validation refusal *with its reason*). The surface tells you what it did.

### B4 · Surface → pane fit `[review]`
Surfaces cluster by the **job** they serve.
- Telemetry / analysis → one pane; the artifact under work → the primary surface; properties / inspection / edit →
  another pane; global status + warnings → the footer; navigation → the nav region. A surface lives in the pane
  whose job it serves, nowhere else.

### B5 · Cross-surface coherence `[review]`
One model, many agreeing projections.
- A single selection updates every surface that should reflect it (pick a record → its detail, its chart, its
  breadcrumb all change). No surface contradicts another; nothing is entered twice. One source of truth, projected.

---

## Scoring

- A `[gate]` failure on **A1 · A2 · B1 · B2** ⇒ **BLOCKED**: fix it before grading any `[review]` (a collapsed
  frame or an orphaned action makes the finer judgments meaningless).
- `[review]` dimensions score **1–5**; a shippable layout is **≥4 on every review with zero gate failures**.
- **Report Axis A and Axis B scores separately**, gate failures first, each with the single corrective it implies.

---

## Workflows

### DECOMPOSE (read an existing UI → region map + grade)
1. **A1 first** — is there a fixed frame, or does it stack? If it stacks, that's the headline; name the cause and
   stop the outside-in walk there.
2. **Name the regions (A2)** against the closest archetype's vocabulary — use the *pattern names*, not prose.
3. **Walk A3 → A5** only while the gates hold.
4. **Inventory the verbs (B1)**, bind each to a surface (B2), then judge feedback / fit / coherence (B3–B5).
5. **Match the archetype** (`archetype-*.md`) and present its wireframe with the live UI's regions mapped onto it.
6. **Two-axis verdict** — separate A and B scores, gate failures first, one fix each.

### DESIGN (intent → wireframe)
1. **Pick the archetype** from the intent: *work in one artifact* → productivity-shell; *navigate many records* →
   saas-dashboard; *read to convert* → marketing-site; *thumb-first* → mobile-app.
2. **Inside-out first** — list the verbs the product must afford (B1), then assign each a surface and a home pane
   (B2/B4). This decides which regions you actually need.
3. **Outside-in second** — lay the chosen regions into the archetype's frame (A1/A2), then specify each region's
   internal order, cards, and atoms (A3–A5).
4. **Emit the ASCII wireframe** with every region named and every required verb placed. Verify: no orphan verb, no
   orphan surface.

### GRADE (score a layout against the rubric)
Run the rubric top-down per axis, gates before reviews, and produce the two separate axis scores with evidence
cited from the artifact (not impressions). One Critical (a gate failure) plus the corrective beats a page of prose.

---

## Reading the cross (worked shape)

```
                         OUTSIDE-IN
        A1 frame  ─ A2 regions ─ A3 order ─ A4 cards ─ A5 atoms
                                    │
   a REGION  ───────────────────────┼──────────────  the same region is…
                                    │
        B1 verbs  ─ B2 binding ─ B3 feedback ─ B4 fit ─ B5 coherence
                         INSIDE-OUT
```
The right-hand pane of a productivity-shell is, on Axis A, *region → label + scrolling card stack → aligned
property rows*; on Axis B it is *the home of the edit/inspect verbs → reflecting the current selection → agreeing
with the canvas*. Grade it on both; a beautiful inspector that edits nothing fails B even as it aces A.
