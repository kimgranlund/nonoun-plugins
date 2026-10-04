---
id: T-0203
title: "fanout.py merge-time file-overlap check"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add a merge-time file-overlap check to fanout.py.

## Intent
- Do: Design section 4 Parallelize. Lanes plan inside the lane (near fanout.py:432), so no plan exists at launch and a separate `Files:` line would duplicate the scope criterion. Check at merge time: `git diff --name-only` of each lane against the integration branch; report overlapping files between lanes in report.md and order the locked merges so an overlapping lane merges after the lane it overlaps. For tickets already planned, also report overlap of their scope allow-lists in `--dry-run`. Selftest with a stub driver: disjoint lanes report none; two lanes touching one file report it.
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the lean SDLC design, `docs/lean-sdlc/design.md` (v0.4, build row L11), reviewed twice: `docs/validation/lean-sdlc-design-review.md` and `docs/validation/lean-sdlc-design-review-2.md`. Supersedes part of T-0192 (conductor batching), which is closed in favor of these tickets. Depends on: nothing. Plan level: L2 (size M). Owning files: plugins/sdlc-lite/scripts/fanout.py and its selftest; docs/maintenance/sdlc-internals.md fanout entry.. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
Main is never touched. Preserve the locked merge, the integration-dirty refusal, and the run-id logging. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.
