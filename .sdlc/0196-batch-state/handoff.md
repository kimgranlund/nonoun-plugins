---
id: T-0196
title: "Step state for a whole-ticket (batched) verifier result"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0195]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Teach steps.py and board.py the step state of a whole-ticket (task-dir) verifier result so batched verification is visible and a rebuild after the batch is detected.

## Intent
- Do: Rule from the design (row S): a task-dir verifier result lists the builder result files it verified (a `## Verified` section naming `step-<n>/builder-L<k>[-j].md` paths); `steps.py next` and `resume` treat a listed, unchanged step as verified; a step whose builder result is newer than the listing, or one not listed, still resumes at `verify`; `board.py` renders the batched verification on those steps. Ordering uses `order.py` newest-result rules, never file mtime. Selftest positive (listed steps verified) and negative controls (newer builder result; unlisted step; per-step verification still required for L4 or L5 and merge steps, so a listing for those is ignored). If this grows into a larger steps.py change than a small rule, stop and report so batching can be deferred to a later release (design risk).
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the lean SDLC design, `docs/lean-sdlc/design.md` (v0.4, build row L4), reviewed twice: `docs/validation/lean-sdlc-design-review.md` and `docs/validation/lean-sdlc-design-review-2.md`. Supersedes part of T-0192 (conductor batching), which is closed in favor of these tickets. Depends on: T-0195. Plan level: L3 (size L). Owning files: plugins/sdlc-lite/scripts/steps.py (`next`, `resume`), plugins/sdlc-lite/scripts/board.py, plugins/sdlc-lite/skills/handoff-format (result contract), selftests.. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
Per-step verification stays mandatory for any step at L4 or L5, any merge step, and the gates green step. Preserve the one-criterion verifier swap rules and the missing-verdict versus plan-defect distinction. Depends on the runner family rule so batched verification is independent. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.

## Burn-down brief
Standing frame: done is better than perfect; trust capable models given useful context. Make the smallest change that meets the Intent. One or two steps, builder L3 at most unless a step truly needs L4. No per-ticket live run: rely on selftests, checks and the branch verifier, and record a flaky or missing live arm as a known limit. Scope is frozen: a new requirement becomes a new ticket. Report blocked instead of looping.
