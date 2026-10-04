---
id: T-0195
title: "Runner: verifier family rule for a task-dir verifier"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Make the verifier model-family rule fire for a verifier launched at the task directory, on Claude and on Codex.

## Intent
- Do: Today the rule reads the newest builder in the verifier's own handoff dir (`order.py newest "$dir" builder`), so a verifier at the task dir finds none and the rule never fires; run.sh remaps silently and has no refusal path. Fix: when the handoff dir holds no builder result, read the newest builder result of any `step-*/` under it, excluding superseded step directories (the rename the chain applies on replan). Negative control = the pre-fix behavior: `run-selftest.sh` already dry-runs the family rule on a step fixture (cf. lines 132-147); add a task-dir fixture that printed `--model sonnet` before the fix and must print `--model opus` after, and a case that fails if the rule is reverted. In `codex-selftest.py` add a resolve case (cf. 256-262) where a task-dir argument returned `shared` false with no builder before the fix and must name the alternate after. Focused live run on a throwaway project for the Claude path.
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the lean SDLC design, `docs/lean-sdlc/design.md` (v0.4, build row L3), reviewed twice: `docs/validation/lean-sdlc-design-review.md` and `docs/validation/lean-sdlc-design-review-2.md`. Supersedes part of T-0192 (conductor batching), which is closed in favor of these tickets. Depends on: nothing. Plan level: L3 (size L). Owning files: plugins/sdlc-lite/scripts/run.sh (family rule near lines 198-207), plugins/sdlc-lite/scripts/codex_roles.py (`resolve`, near 100-120), plugins/sdlc-lite/scripts/run-selftest.sh, plugins/sdlc-lite/scripts/codex-selftest.py.. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
Existing step-dir behavior unchanged. Do not edit run.sh while a role or benchmark is using it: build in a separate worktree and run roles from the main checkout. Model and effort defaults are untouched. This is a runner change: run `bash plugins/sdlc-lite/scripts/check.sh`. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.
