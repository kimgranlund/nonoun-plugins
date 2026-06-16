# Roadmap — ui-layout-decomposer

## Now (0.1.0)
The method + the four archetype wireframe libraries, usable for DECOMPOSE / DESIGN / GRADE.

## Next
- **More archetypes:** `docs-site` (left-nav + reading column + on-this-page TOC), `chat/agent` (thread + composer +
  context rail), `data-grid/spreadsheet`, `kanban/board`, `email/三-pane client`, `media-player`.
- **A routing-eval corpus** (`evals/routing-corpus.json`) — trigger + adversarial phrases scored before the
  description is locked (the skills-studio D5 gate), so routing accuracy is measured, not assumed.
- **A grading worked-example per archetype** — a real screenshot decomposed end-to-end on both axes, as a
  calibration reference for the rubric.
- **Responsive/adaptive notes** — how each archetype reflows across breakpoints (the master-detail ⇄ stacked graft),
  promoted from scattered "variants" notes into a first-class dimension.

## Someday
- A tiny `bin/` linter that checks an emitted ASCII wireframe for the gate invariants (every named region present;
  no orphan verb/surface) — mechanizing the Verify Target the way the catalog's other skills mechanize theirs.
- Cross-link to brand-forge (visual/color) + product-forge (UX strategy) so a full review hands structure here and
  skin/taste there.
