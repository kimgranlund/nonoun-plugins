---
id: T-0801
title: "measure single session vs solo lane with the diff-scoped verifier on 5 L1 tickets"
type: spike           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0799, T-0800]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-28
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Measure, on the same builds, whether the diff-scoped verifier (T-0799) is cheaper and faster than the full verifier without losing its catch rate, and how the solo lane compares with a single plain session on small tickets.

## Question
On 5 L1 tickets in a throwaway project: (a) one plain sub-agent session per ticket (same model and effort as solo L1, no verifier); (b) a solo L1 build per ticket, then two verifiers on the same ready build, one with `Scope: diff` and one with the full brief. Record wall minutes and dollars per run, interleaving arms per ticket with `uptime` before each run. A planted control (a vacuous criterion plus a false red-first claim) gets both verifiers; each must fail it, or the control does not discriminate.

## Context
Prior evidence: `docs/reports/solo-vs-lean-benchmark-2026-10-04.md` and the bench skill (`/sdlc-lite:bench`). Speed theories: the 2026-10-28 analysis (verification sized to the change, one-command bookkeeping). Report to `docs/reports/2026-10-28-speed-experiment.md` (dated the run day).

## Acceptance criteria
1. A dated report with a table per arm: wall minutes, dollars, verifier verdicts, and the planted-defect result, each number with its source command or record path.
2. The report states adopt or reject for the diff-scoped verifier, by the rule: adopt only when the diff verifier costs less than the full verifier on the same builds and fails the planted control (and the full verifier fails it too).

## Constraints
Runs only in a throwaway project; no change to plugin code in this ticket.
