---
id: T-0241
title: "Schema format: ## Kinds registry table, ## Decide and ## Legacy in the layout parser"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2
depends: []   # T-NNNN, file:<path>, cap:<name>
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The docs/layout.md parser in plugins/sdlc-lite/scripts/onboard.py reads two new optional sections, `## Kinds` and `## Legacy`, and `Layout` exposes them, without changing how `## Homes` and `## Frozen paths` parse.

## Intent
- Do: add `kinds` (home to one of the nine fixed kinds: specs, planning, decisions, references, guides, reports, assets, archive, other) and `legacy` (a list of backticked globs, same form as `## Frozen paths`) to `Layout`; parse `## Kinds` as the 11-column registry table (id, kind, holds, not, why, writer, form, life, entry, read, owner; one row per home, header must name all columns) in place of the earlier `is <kind>` line form, parse `## Decide` as numbered `N. <question>? yes -> `id`` lines ending in one `otherwise -> `id`` line, and the same parser for a `.sdlc/layout.md`; parse the legacy lines and one-glob lines; an unknown kind, a line outside the forms, a kind line for a home missing from `## Homes`, and a duplicate heading each raise LayoutError naming the file and line; the current parser behavior for files without the new sections is unchanged. Selftest cases: positive for both sections, an older-style file still parses, and one negative control per error; keep `onboard.py check` and `setup` output unchanged for existing repos.
- Non-goals: any checks (ticket after this one), any file moves, a version bump, tag, push, or publish.
- Done when: selftest passes with the new cases, `python3 plugins/sdlc-lite/scripts/onboard.py check` output on this repository is unchanged, the full check.sh passes, and an independent verifier passed.

## Context
Part of the docs schema design (docs/docs-schema/design.md v0.4 with the user's decisions of 2026-10-05 under Resolved decisions, ticket T-0240), reviewed once (v0.1) by an independent architect (docs/reports/docs-schema-design-review.md). Build as ONE handwritten solo step under the burn-down rules (lane solo; philosophy: "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction."); one independent verifier; merge main in first; check.py guard numbers stay unique (guard 23); a new check needs a positive case and an observed negative control.

## Constraints
The parser only: no `render_registry`, no drift check (they wait for the placement proof T-0248). The existing parser must still ignore the new sections when unchanged callers read a file with them.
One authoritative location per fact. No em dashes. Do not touch other agents' worktrees.

## Closed

2026-10-05: Layout parser reads Kinds, Decide, Legacy; selftest gates with negative controls; verifier L3 pass
