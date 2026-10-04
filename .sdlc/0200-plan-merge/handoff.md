---
id: T-0200
title: "Replan by delta: merged plan view and steps.py resolve"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0197]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Implement replan-by-delta: a merged plan view used by split, lint, review, lane, and resolve, and a `steps.py resolve` command.

## Intent
- Do: Design section 2 change 1. A replan is the next planner result (usually `planner-L3.md` for an L2 plan, because run.sh adds `-k` only when the same role and level reruns) and carries `revises: <planner file>` naming a file across levels, only the changed or added steps, and the findings it addresses. Delta handling keys on the presence of `revises:` (no version line). `find_plan` (near 236-243) returns the merged plan for a directory target and `split`, `lint` (near 913-916), `review` (`review_action` near 1223-1226), `lane`, and `resolve` all use it. `steps.py resolve <task dir>` prints the merged plan. A delta naming a missing step is refused as a `plan defect:` last line. The plan-reviewer reads `resolve` output so a chain of two deltas keeps the base. Replan split is `--only <changed steps>` after the supersede rename (split without --only refuses when step dirs hold results, near 863-889). Target: an L3 delta at most a quarter of the plan it revises.
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the lean SDLC design, `docs/lean-sdlc/design.md` (v0.4, build row L8), reviewed twice: `docs/validation/lean-sdlc-design-review.md` and `docs/validation/lean-sdlc-design-review-2.md`. Supersedes part of T-0191 (single plan record), which is closed in favor of these tickets. Depends on: T-0197. Plan level: L3 (size L). Owning files: plugins/sdlc-lite/scripts/steps.py, plugins/sdlc-lite/agents/plan-reviewer.md, plugins/sdlc-lite/agents/planner.md (delta rule), plugins/sdlc-lite/skills/handoff-format, selftests, regenerated Codex agents.. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
Result names, order.py newest ordering, and steps.py next unchanged. Regression set: selftest `(r)` (near 2647) and the closed tickets in `.sdlc/` that hold two planner files. Negative controls: a delta naming a missing step is refused; `lint` on a delta sees the base steps; `review` sees a base `unresolved:` assumption and a base step at L4. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.
