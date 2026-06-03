# adia-ui-dogfood

Six-mode static + visual QA sweep for the adia-ui framework substrate. The agent-facing skill body — all six modes, triage rules, fix recipes, and verify targets — is in `SKILL.md`. This README covers the one bundled script.

## The component visual probe (`scripts/analyze.mjs`)

Walks every `site/components/*` demo page in headless Chromium and runs visual-correctness probes that type-checks and tests don't catch:

| # | Probe | Bug class it detects |
| --- | --- | --- |
| 1 | Zero-area | Element collapsed (parent `display:none`, toolbar overflow spilled it, layout glitch) |
| 2 | Transparent fill | `[data-swatch]` / variant pill / button / chart indicator whose computed bg is `rgba(0,0,0,0)` — fallback token doesn't resolve (the chart-legend `--chart-N` class) |
| 3 | Empty control | `input-ui` / `search-ui` whose `connected()` should have stamped internals but didn't |
| 4 | Synonym-attr / synonym-slot drift | Markers from the attribute-api-migration convention (`avatar-ui[name]`, `grid-ui[cols]`, `card-ui [slot=meta]`, etc.) |
| 5 | Alert flex-row | `alert-ui` with multiple bare `<text-ui>` children (need `<col-ui slot="content">` wrap) |
| 6 | Missing component CSS / unstyled popover | a `*-ui` tag on the page with no matching stylesheet loaded; an open popover with transparent bg + zero padding |
| 7 | Console | Every `console.error` + `console.warn` during page load + 800ms settling |

Output: a severity-ranked markdown report at `docs/reports/dogfooding-YYYY-MM-DD.md` under the repo root.

## Run locally

Run from the framework monorepo checkout (the script resolves the repo root from `$ADIA_REPO_ROOT` if set, else the current working directory):

```bash
# Terminal 1
npm run dev

# Terminal 2 (S = ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-dogfood/scripts/analyze.mjs)
node "$S"                       # full sweep
node "$S" --filter chart-legend # one page
node "$S" --port 5174           # custom port
node "$S" --out /tmp/r.md       # custom path
```

Exit code: **1** if any **critical** finding, **0** otherwise. CI-friendly.

## Schedule as a remote agent

The script is the data gatherer. A scheduled agent wraps it with git orchestration: check out the repo, start the dev server, run the script, triage findings, commit/PR. The full agent procedure — env setup, the 3-question triage gate, the ≤5-fix-per-PR blast-radius cap, the verify gate, and the PR shape — is documented in `SKILL.md` (§ Component Dogfood + §Plan-Execute-Verify). Weekly cadence is a reasonable default; pages drift slowly.

Hard rules carried from the source skill:

- Never touch a component's deprecation-handler string when sweeping the attribute it deprecates.
- Never edit historic MIGRATION GUIDE sections; only the active version section.
- Don't fix more than 5 critical findings in one PR — leave the rest for follow-up so humans can review fix shape before scaling.

## False positives + tuning

The probes are intentionally narrow. Known places where "transparent fill" is by design (and shouldn't be added to `COLORED_SELECTORS`):

- `tag-ui` without a variant (`muted` / default) — bg is correctly `--a-bg-muted`, not transparent.
- `button-ui[variant=ghost]` — transparent by design.
- `[data-swatch]` for `chart-legend-ui[shape=dashed]` — intentionally transparent bg + colored `border-top`. The probe handles this case.

If a finding is a known false positive, add the parent component or selector to the skip-list rather than removing it from `COLORED_SELECTORS` (preserves coverage on the canonical case).

## When to revisit the probe set

- New component ships → add to `STAMP_CONTRACTS` if it has internal stamping logic.
- New synonym-attribute drift class documented in the attribute-api-migration convention → add to `DRIFT_MARKERS`.
- A class of bugs slips past the analyzer in a real PR → add a probe for that bug class first, _then_ fix it. Test for the test.
