---
id: T-0545
title: "Lean records F: Docs and release 0.23.0 (0.23.0)"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0544]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
claimed_by: claude 2026-10-14
branch: lane/T-0545-w75-0545
worktree: .claude/worktrees/T-0545-w75-0545
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Docs and release 0.23.0: part F of SDLC Lite 0.23.0 lean work records (wave 5).

## Intent
- Do: build part F of the design in `.sdlc/.0539-lean-work-records/architect-L1.md` (read its Approach, the row for F, Interfaces and Risks). Files: `skills/handoff-format/{run-operations.md,references/writing-rules.md}` (the T-0529 rules, cut down to the handoff and Outcome), `docs/specs/sdlc-lite/{design.md,solo-lane-contract.md,cost-control.md,cascade-guard.md,plan-doc-executor.md,restart-and-blocked-run-plan.md}`, `docs/specs/ticket-stages/design.md`, `docs/planning/docs-schema/design.md` (B-2, B-4, B-5), `docs/references/sdlc-internals.md`, `docs/specs/doc-standards/{delivery.md,knowledge-ops.md}`, `plugins/sdlc-lite/AGENTS.md`:66, CHANGELOG built from `git log --format=%s <last tag>..HEAD` subjects starting `T-`, both plugin manifests and marketplace parity, dated release report
- Non-goals: the other parts (A to F) of the same design.
- Done when: `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py` and `git diff --check` pass. `git diff --quiet <wave base> -- plugins/sdlc-lite/adapters/claude/levels.json plugins/sdlc-lite/adapters/codex/models.json` exits 0. In a throwaway project, a live solo L2 ticket on the release build leaves `git ls-files .sdlc/.NNNN-*` equal to that ticket's `handoff.md`

## Context
Maintainer decisions: `.sdlc/notes.md` "Lean work records (maintainer decisions 2026-10-13)". Objective: complete the task, update the ticket, hand off a clean merge-ready worktree, minimal documentation. Full chain reason: cross-cutting run-record change across scripts, roles and skills (design T-0539).

## Constraints
Preserve independent verification, the recorded build base, reference-safe closure and restart recovery. Legacy task folders stay readable with no migration.
