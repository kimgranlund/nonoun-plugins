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
Measure whether the solo lane with the diff-scoped verifier (T-0799) and the one-command lane (T-0800) comes close to a single agent session on small tickets, without losing the verifier's catch rate.

## Question
On 5 L1 tickets in a throwaway project, what are wall minutes and dollars per ticket for (a) one plain Claude Code session doing the ticket and its checks, and (b) the solo lane plus diff-scoped verifier? Does (b)'s verifier still fail a planted defect (one ticket built with a criterion-passing but wrong change)?

## Context
Prior evidence: `docs/reports/solo-vs-lean-benchmark-2026-10-04.md` and the bench skill (`/sdlc-lite:bench`). Speed theories: the 2026-10-28 analysis (verification sized to the change, one-command bookkeeping). Report to `docs/reports/2026-10-28-speed-experiment.md` (dated the run day).

## Acceptance criteria
1. A dated report with a table per arm: wall minutes, dollars, verifier verdicts, and the planted-defect result, each number with its source command or record path.
2. The report states adopt or reject for the diff-scoped verifier, by the rule: adopt only when (b) is cheaper and its verifier fails the planted defect.

## Constraints
Runs only in a throwaway project; no change to plugin code in this ticket.
