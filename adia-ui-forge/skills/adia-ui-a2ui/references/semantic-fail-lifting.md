# Reference: Semantic fail lifting — sub-60 fail triage procedure

**Source:** Absorbed from the former `zettel-internals` skill (§Semantic Fail Lifting) — Phase 3 rollup. **Used by:** mode 5 of `adia-ui-a2ui` (lift semantic fails). **Companion:** `strategy-engines.md`, `zettel-calibration.md`, `eval-diagnostics.md`.

---

## Semantic Fail Lifting

Use when `npm run eval:diff -- --engine zettel --semantic` reports any intent with `semanticScore < 60` or `< 70`. These are rows where the judge says the UI emitted for an intent doesn't actually match what was asked for.

## What a sem fail looks like

The judge scores on 3 axes:

- **dominantPattern** (weight 0.5) — does the root/primary component match the intent type? (chat, form, calendar, data-display, nav…)
- **requiredCapabilities** (weight 0.35) — are the specific controls the intent requires actually present?
- **forbiddenNoise** (weight 0.15) — are off-topic components prominent?

A sub-60 score almost always means dominantPattern scored < 40.

## Triage procedure

1. Read the latest eval run's `zettel.json` — find rows with `semanticScore < 70`, sorted ascending.
2. For each row, read `row.semanticAxes.dominantPattern.{expected, observed}` and `row.semanticAxes.requiredCapabilities.missing`.
3. Group failures into three buckets:
   - **Thin composition** — retrieved comp exists but is too sparse (e.g., calendar-month-view had nav + weekday labels only, no grid).
   - **Wrong composition winning** — retrieval collision; a different comp steals the intent via keyword overlap (e.g., empty-state won "error state with retry" because its keywords included both).
   - **No matching composition exists** — need to author a new one (e.g., no accordion-settings composition existed; drawer-panel won instead).

## Fix strategies (in order of preference)

### Strategy A — Use a domain-specific primitive as the root

The judge weights root component identity and component counts heavily. A Card wrapping 38 Badges

- 43 Texts reads as "data-display" even if a 7-column Grid is inside. Swapping to a semantically-correct primitive fixes this instantly.

Examples that worked:

- calendar: `CalendarPicker` (not Grid of Text) → 32→65
- chat: `Chat` > `Text[role=user|assistant]` (not Row+Text bubbles) → 52→70+
- command palette: `Command` > `ActionItem` (not Command > Text) → 42→70+

Check the registry (75+ components) before authoring children. **These do NOT exist**: `ChatMessage`, `CommandItem`, `TimelineItem`. Use:

- Chat children → `Text` with `role="user"|"assistant"`
- Command children → `ActionItem`
- Timeline children → freeform (e.g., Row + Icon + Text + Badge)

Inspect `packages/web-components/components/<name>/<name>.a2ui.json` for the component's props/slots/examples before writing the composition.

### Strategy B — Resolve retrieval collisions by keyword surgery

When an unrelated comp wins retrieval, don't just enrich the correct comp — also **strip overlapping keywords from the losing comp**.

Worked example: `empty-state.json` had keywords `["empty", "empty state", "no results", "illustration", "error state", "retry", "nothing"]`. Added new `error-state-retry` composition BUT empty-state still won for "error state with retry" (sem=32) until its keywords dropped `"error state"` and `"retry"`. Then error-state-retry won at sem=91.

### Strategy C — Author a new composition when none exists

Indicators:

- Multiple intents fail pointing at the same wrong candidate
- Candidate's `dominantPattern.expected` ≠ any existing comp's purpose

When authoring:

- Use `card-header-with-description` fragment for the top (top-leverage fragment at 36+ uses)
- Use `labeled-toggle` / `labeled-input` fragments for form controls — boosts reuse ratio
- Put the pattern's signature affordance as the dominant child (Timeline[mode=steps] for a wizard, Textarea+Richtext for an editor, Accordion for settings, etc.)
- Rich keyword set (15-20 terms) with exact intent phrases and domain synonyms ("import wizard", "csv import", "multi-step form")

## Build + verify loop

After each change:

    node scripts/build/components.mjs           # rebuild
    node scripts/build/components.mjs --verify  # confirm clean

Then run the semantic eval (cached, so only changed intents re-judge):

    node packages/a2ui/mcp/scripts/eval-diff.mjs --engine zettel --semantic

Compare `avgSem` and the sub-60 list row by row. Cache is content-hashed on (rubricVersion, intent, a2ui-messages) — only changed generations re-judge.

## Don't regress reuse ratio

Adding new compositions without fragments lowers corpus reuse. Threshold is 29.9% (`fragment_refs / composition_nodes`). Watch the post-build line:

    fragment refs: 197 across 664 composition nodes (reuse 29.7%)

Fixes that lift reuse while keeping sem gains:

- Use existing fragments (card-header-with-description, labeled-toggle, labeled-input, footer-cancel-save, icon-title-description) in every new composition
- Extract an intra-composition fragment if a subtree repeats 10+ times (see `fragment-graph.md` — leverage rule exception #2)

## Verification before done

Full gate sweep:

    node scripts/build/components.mjs --verify \
      && npm run smoke:engines \
      && npm run smoke:register-engine \
      && npm run test:a2ui \
      && node packages/a2ui/mcp/scripts/eval-diff.mjs --engine zettel --semantic

Thresholds to hold:

- coverage = 100
- avgScore ≥ 88 (structural)
- avgSem > baseline
- reuse ratio ≥ 29.9%
- test:a2ui green (+ 1 skipped OK)

## Session outcomes cheat sheet

A representative lift cycle — all lifts came from Strategy A + B + C combinations:

calendar-month-view 32 → 65 (A: CalendarPicker root) event-calendar-details 32 → 72 (A: same comp rewrite) error-state-retry 32 → 91 (C: new comp + B: strip empty-state kwds) accordion-settings 32 → 92 (C: new comp, Accordion root) chat-interface 52 → 70+ (A: Chat > Text[role]) command-palette 42 → 70+ (A: Command > ActionItem + shortcuts) data-import-wizard 38 → 70+ (C: new, Timeline[mode=steps] + Upload) markdown-editor-preview 42 → 70+ (C: new, Textarea + Richtext split) notification-preferences 62 → 70+ (C: new, labeled-toggle fragments)

avgSem 83 → 87. Reuse 26.4 → 33.5 (peak) → 29.7 (final).
