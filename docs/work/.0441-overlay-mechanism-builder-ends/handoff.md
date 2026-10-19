---
id: T-0441
title: "Per-level prompt overlays: generator mechanism plus builder L1 and L5 overlays"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Role prompts can differ by level at generation time, with `overlays/builder.md` carrying `## L1` and `## L5` only; every other generated agent stays byte-identical.

## Intent
- Do: build the mechanism and first overlays exactly as the architect design says (Approach, Interfaces, Constraints and assumptions, the first-build file list and checks): `plugins/sdlc-lite/overlays/<role>.md` with `## L<n>` sections inserted before `## Output` as a `## At this level` block with the fixed first line, in `claude_roles.py definitions()` and `codex_roles.py instructions()`; the generator refuses an overlay with an H2 inside, a `results.SCHEMA` heading, over 20 lines, a role with no `levels.json` row, an unknown level, or a denylist word; `check.py` item for it with negative controls; `overlays/builder.md` with `## L1` (ordered procedure and gap defaults) and `## L5` (goal, KPI, budget, judgment rules).
- Non-goals: any model or effort row; overlays for other roles or levels (T-0443); the A/B (T-0442).
- Done when: the design's red-first criteria and first-build checks pass, `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/agents/builder-L3.md` holds, only builder-L1, builder-L5 and their two Codex TOMLs change, `check.sh` exits 0, one live builder L1 dispatch on a throwaway step runs with the overlay.

## Context
Design: `.sdlc/.0440-per-tier-agent-prompts/architect-L1.md` (read all of it). Hypothesis and evidence: same file and `docs/reports/2026-10-11-plan-doc-live-run.md`. Generators: `plugins/sdlc-lite/scripts/claude_roles.py`, `codex_roles.py`; checks `check.py` items 18, 21, 25, 43.

## Constraints
Model and effort rows unchanged. Hard invariants never vary by tier. Never hand-edit a generated file; run both `generate` commands.

## Plan review
- plan defect: step 2: dispatch.py prepare refused the step handoff (steps.py lint): cited path does not exist: .sdlc/0441-overlay-mechanism-builder-ends/live-builder-L1.md and .sdlc/0441-overlay-mechanism-builder-ends/live-builder-L1.cmd. These are outputs the step creates; name them so lint does not read them as cited inputs (for example put them in the step dir, not as backticked paths that must exist). Step 1 passed verification (step-1/verifier-L2.md); replan step 2 only and keep step 1 unchanged.

## Closed

2026-10-11: warnings acknowledged: red controls recorded after the first edit in step 2; every step verifier passed, check.sh exit 0 on the integration branch; the live run shows the overlay in the definition, not changed behavior, which T-0442 measures

> - process deviation: red-checkpoint: retrospective: attempt 7814d8e5fd81416c80aa2e7b16a4fe9f, handoff sha256 6888c4b7a99c, 4 of 4 (red) criteria in step 2 had no pre-edit red control. These are the live-run file checks (`test -s` and `test -f` on the live-run files). The builder says `redck.py record` ran before any edit in step 2 but logged the controls as retrospective, because step 1's files already differed from base. The step 2 verifier passed, and a passing verdict does not clear this deviation. The verifier did run its own red checks: the AGENTS.md grep counts 0 at base, and the live-run files do not exist at base.
> - Both steps passed: step 1 (verifier L2) and step 2 (verifier L1). Step 1 has no `process-deviations.md`.
> - The handoff's Plan review records one plan defect: step 2's first handoff cited output paths that did not exist yet. The planner replanned step 2 only, and step 1 stayed unchanged.
> - The step 2 live run proves less than the "Done when" line suggests. It shows that `claude -p --agent sdlc-lite:builder-L1` exited 0 and that its report has `## Status` and no `## At this level`. That the generated builder-L1 definition carries the overlay block rests on a grep of `agents/builder-L1.md`. Nothing in the artifacts shows the live agent acting on the overlay's content.
