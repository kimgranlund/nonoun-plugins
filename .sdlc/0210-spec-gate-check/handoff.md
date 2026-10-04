---
id: T-0210
title: "Spec gate A1: specgate.py check, run.sh plan-reviewer refusal, plan guard-timeout line"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M
priority: P2         # P1 | P2 | P3
depends: []
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add the free half of the spec gate: `scripts/specgate.py check`, the `run.sh` plan-reviewer refusal, and a plan-level `guard timeout:` line that `steps.py split --only` honors.

## Intent
- Do: Section A (A1) of the addendum. `specgate.py` imports `steps` (no second criterion parser) and has `check <plan | task dir>`: flags a `(guard)` span running check.sh (or a command the planner rule names as slow) when the plan has no `guard timeout: <seconds>` line, a criterion span repeated verbatim across steps, and a `(red)` tag beside `(guard)` on one line; read-only, exit 0 or 1. `steps.py split --only` reads the plan's `guard timeout:` as the default for `--guard-timeout`. `run.sh`, before `exec run_lifecycle.py` and only for role plan-reviewer, runs `specgate.py check "$dir"`; findings on stderr, exit 2, no runs.jsonl line and no .running file; `SDLC_SPECGATE=off` skips it and writes `specgate: "off"` on the run line. One rule line each in `agents/planner.md` and `skills/handoff-format/SKILL.md` (measure a whole-suite guard once and write the timeout line). Selftest plus check.py guards; regenerate Codex agents.
- Non-goals: changing any model or effort default; conductor wording beyond a pointer line; a version bump, tag, push, or publish.
- Done when: the changes are built, an independent verifier passed each step, and a positive plan passes; negative controls fail first: a check.sh guard with no timeout line is refused, a criterion repeated across steps is refused, `run.sh plan-reviewer` on a failing plan exits 2 before any model call; replay on the 2026-10 findings flags the two timeout findings and the duplicate span and none of the seven judgment findings. `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Cost-control addendum to the lean SDLC design: `docs/lean-sdlc/cost-control.md` v0.2, reviewed in `docs/validation/lean-sdlc-cost-control-review.md`. Measured on 2026-10-04: about $190 over 78 role runs, 4 of 7 plans returned for replan. Owning files and ordering: scripts/specgate.py (new), scripts/run.sh, scripts/steps.py (split default only), agents/planner.md (one line; waits for T-0202 if it touches the same section), skills/handoff-format/SKILL.md, scripts/check.sh, scripts/check.py, docs/maintenance/sdlc-internals.md. Plan level L2. Depends: none (T-0195 is merged).

## Constraints
Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's (change none), no em dashes, one authoritative location for each fact, checks that can fail with a negative control. Read the design first: docs/lean-sdlc/cost-control.md (v0.2) and docs/validation/lean-sdlc-cost-control-review.md; re-read every cited line number at plan time, since T-0196, T-0197, T-0199, T-0200, T-0201 and T-0202 move them. Conductor wording is T-0199's file (agents/conductor.md): do not restate it, and edit it only as a pointer line after T-0199 merges. Merge main into the build branch before each local merge and keep both sides of check.py and check.sh conflicts. Run roles from the main checkout's run.sh in a separate worktree. No version bump, tag, push or publish.
