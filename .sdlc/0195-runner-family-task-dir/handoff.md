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

## Plan review
plan defect: step 3 blocked (step-3/builder-L2.md): the dry-run base criterion cannot hold, because SDLC_BASE_SHA (aa59ebc) is the step-2 checkpoint and already contains the fix, so the base run.sh also picks Opus and the negative control does not discriminate. The real pre-fix commit is 171e13b (T-0195 plan split, parent of the step-1 commit d87cc4b). Replan step 3 (and step 4 if it depends on it): archive 171e13b for the base dry run and rerun only the two dry runs; the live proof already passed (builder on Sonnet, verifier on Opus, evidence in docs/validation/runner-family-task-dir-live-run/fam/), so do not rerun live roles. Steps 1 and 2 are committed, not uncommitted.

plan review: replan: .sdlc/0195-runner-family-task-dir/plan-reviewer-L1-2.md
plan review: replan: step 4: acceptance criteria: the `(guard) bash plugins/sdlc-lite/scripts/check.sh` criterion runs at split time under `steps.py split --only`'s default 300 s guard timeout, and on this host it takes longer than that, so the split refuses with `plan defect` before any builder starts; the plan names the remedy (`--guard-timeout`) only under `## Risks`, and no step Do or chain instruction tells the conductor to pass it. A full split is not available because `step-1/` and `step-2/` hold role output (`steps.py:885-889`), so `--only 3 4` (or `--only 4`) and therefore the step 4 guards are unavoidable. Evidence: `bash plugins/sdlc-lite/scripts/check.sh` exited 0 in 417 s (`uptime` load averages 12.16 17.22 19.73); planner-L3-2.md:284 measured 253 s and planner-L3-2.md:293 flags the 300 s default; `plugins/sdlc-lite/scripts/steps.py:28` (`--guard-timeout SECONDS (default 300)`), `steps.py:496-500` (timeout kills the span, rc None), `steps.py:519-522` (a timed-out guard is red and `Fail(... plan defect ...)`); `grep -rn 'guard-timeout' plugins/sdlc-lite/skills plugins/sdlc-lite/agents` printed nothing; `plugins/sdlc-lite/skills/chain/SKILL.md:40` routes a `--only` refusal to a replan.
