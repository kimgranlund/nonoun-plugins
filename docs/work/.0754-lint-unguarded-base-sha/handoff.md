---
id: T-0754
title: "steps.py lint flags a criterion that names SDLC_BASE_SHA without a guard"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A plan or handoff criterion that names `$SDLC_BASE_SHA` cannot pass vacuously when the variable is unset: `steps.py lint` refuses a criterion that names it without a `${SDLC_BASE_SHA:?}` guard or an `export SDLC_BASE_SHA=` in the same criterion.

## Intent
- Do: add the lint rule in `plugins/sdlc-lite/scripts/steps.py` next to the existing `SDLC_BASE_SHA` case (about line 6084), with a message that shows the guarded form. Update the planner's criterion guidance in `plugins/sdlc-lite/agents/planner.md` and `skills/handoff-format/SKILL.md` only if they show an unguarded example (keep the merge-step block identical in both; `check.py` compares them), then regenerate agents.
- Non-goals: rewriting existing closed handoffs.
- Done when: the criteria pass.

## Context
T-0735 verifier (2026-10-24): with the variable unset, `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- plugins 2>/dev/null)"` exits 0 (vacuous pass) while the bare `git diff` exits 128 `bad revision ''`. Roles launched by `dispatch.py prepare` have no SDLC_BASE_SHA; T-0735 added only a brief line telling them to export it.

## Acceptance criteria
1. A `steps.py` selftest case: lint refuses a criterion with an unguarded `$SDLC_BASE_SHA` and accepts the `: "${SDLC_BASE_SHA:?}" &&` and `export SDLC_BASE_SHA=<sha> &&` prefix forms; with the rule removed the refusal case fails (state the FAIL line).
2. `steps.py lint` passes on every task dir under `docs/work/` that holds a `planner-*.md` and is open (fix any open one it flags).
3. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`steps.py lint`, `split`, `swap`, and `widen` refuse a criterion span that reads `$SDLC_BASE_SHA` without a top-level guard prefix: `: "${SDLC_BASE_SHA:?}" &&`, or `export SDLC_BASE_SHA=<value> &&` / `SDLC_BASE_SHA=<value> &&` with a non-empty value that does not read the variable. An inline `${SDLC_BASE_SHA:?}` inside `$(...)` or before a pipe no longer counts: with the variable unset it aborts only that subshell and the outer test still passes (the selftest runs both and shows rc 0 for the inline form, rc != 0 for the prefix). The refusal message shows the prefix fix. Detector: `unguarded_base_sha`, beside `pins_sha`.
- `:` added to `BUILTINS`: without it a `: "..." && ...` span was not a command span, so no consumer (lint, widen, guards, t0475/k8/rt cases) saw it. With `:` removed the selftest failed on those cases.
- `split` skips this one rule for a step whose newest verifier result passes (`passed_steps`), so a replan keeps passed text verbatim (planner rule 9). Reverting that exemption turns the case `split --only does not refuse an unguarded span in a step that already passed` red; disabling the rule turns the five refusal cases and `split --only refuses the same unguarded span in a step with no verifier pass` red.
- Guidance: `agents/planner.md` rules 6 and 13 teach the prefix form; generated planner agents and Codex TOMLs regenerated; `docs/references/sdlc-internals.md` lists the refusal; the `requires_clean_diff` message shows the prefix form. About 14 selftest fixtures take the prefix.
- Criterion 2 reworded from "every open handoff" to "every task dir under `docs/work/` that holds a `planner-*.md` and is open", because `steps.py lint` needs a plan and exits 1 ("no Step blocks") on a ticket handoff by design. The only task dir holding a `planner-*.md` is `docs/work/plan-reliability-docs`, stopped since 2026-10-19 with no ticket pointing at it, so it is not open; my earlier edit to its `planner-L3.md` is reverted (the file equals the base). No open plan needed a fix.
- Open ticket handoffs hold no `## Step` blocks, so their criteria are not linted by `steps.py lint`; the detector finds nothing in their criteria.

## Outcome

2026-10-24 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 969df8b649b3
- Changed: see commits
- Commits: d9e002c T-0754: require a top-level guard prefix for $SDLC_BASE_SHA, exempt passed steps in split; 59089a0 T-0754: steps.py lint refuses an unguarded $SDLC_BASE_SHA in a criterion
- Check: 1 A `steps.py` selftest case: lint refuses a criterion with an unguarded `$SDLC_BASE_SHA` and accep...: pass
- Check: 2 `steps.py lint` passes on every task dir under `docs/work/` that holds a `planner-*.md` and is op...: pass
- Check: 3 selftest through gate_lock exits 0, `check.py` exits 0, `check-packaging.py` passes, `git diff --...: pass
- Follow-up: note: plugins/sdlc-lite/scripts/steps.py:1517 the guard accepts export... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/steps.py:544 with : in BUILTINS, prose... -> notes.md
