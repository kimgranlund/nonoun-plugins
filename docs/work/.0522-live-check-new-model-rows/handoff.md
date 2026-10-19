---
id: T-0522
title: "Live host check of the new model rows and of effort: in the messenger and conductor front matter"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0520]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Dated evidence that the model rows changed in 0.22.7 launch on the live Claude host with the model and effort the table names.

## Intent
- Do: on a throwaway project, dispatch one run each for planner, architect, plan-reviewer, verifier L1 and L3, scout, researcher L1, filer, ui-designer L1, and start the messenger and conductor session agents; record the model and effort the host reports for each. Confirm `effort:` in the messenger and conductor front matter is honored or ignored, and say which.
- Do: write `docs/reports/<date>-live-model-rows.md` with the evidence and anything unverified.
- Non-goals: Codex live runs (T-0316 covers those); changing rows.
- Done when: the report exists, each row is marked verified or unverified with a reason, and a row that launched with the wrong model is filed as a bug.

## Context
T-0519 notes say live host behavior is not proven. Pattern to follow: `docs/reports/2026-10-12-live-claude-check.md`.

## Constraints
None beyond the repository guidance.

## Closed

2026-10-13: delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: `docs/reports/2026-10-13-live-model-rows.md`, header: the report says the rows are "the ones T-0519 and T-0520 landed for 0.22.7" while `plugin.json` still reads 0.22.6. The report states this itself, so the evidence binds to commit `35fdddae`, not to a release. | `/tmp/t0522.1v2wMg` was left behind as scratch. It is harmless, and the builder disclosed it.
