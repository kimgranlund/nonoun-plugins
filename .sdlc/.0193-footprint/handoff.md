---
id: T-0193
title: "footprint.py: measure and gate a ticket's footprint"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add scripts/footprint.py that measures a ticket's footprint and can gate on it.

## Intent
- Do: `footprint.py <ticket dir>` prints files, total bytes, `.md` bytes, role runs (lines in every `runs.jsonl` under the dir, by role and level), steps, and planner bytes. `footprint.py check <ticket dir> --max-files N --max-bytes N` exits 1 naming the exceeded limit. Selftest builds fixture ticket dirs (a fix-lane one and a chained one) and asserts exact counts; a negative control fixture with one extra file fails `check --max-files`. Reproduce the Baseline table in the design for T-0188, T-0164, T-0181, T-0175 (closed dot folders) and record the output in the ticket's result.
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the lean SDLC design, `docs/lean-sdlc/design.md` (v0.4, build row L1), reviewed twice: `docs/reports/lean-sdlc-design-review.md` and `docs/reports/lean-sdlc-design-review-2.md`. Supersedes part of T-0189 (lean chain), which is closed in favor of these tickets. Depends on: nothing. Plan level: L2 (size M). Owning files: plugins/sdlc-lite/scripts/footprint.py (new) and its selftest; wiring in scripts/check.sh; a short entry in docs/references/sdlc-internals.md.. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
Read-only on ticket folders; never writes under them. Counts must be derived from the directory at run time, never from a fixed number. No model defaults change. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.
