---
id: T-0493
title: "Research: industry standards and alternatives to plan, build, verify, close, and what they mean for the queue"
type: spike           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
budget_usd: 10
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Question
What are the industry standards and the credible alternatives to our plan, build, verify, close system, what does the evidence say about each, and which of our queued tickets should change, move up, merge, or drop because of it?

## Goal
A sourced research report at `docs/reports/2026-10-12-industry-alternatives-review.md` with a ranked list of queue changes. No code, no ticket edits: the maintainer files changes.

## Intent
- Do: (1) Map the patterns: single agent loop (ReAct, plan mode, Claude Code and Cursor defaults), plan then execute then human review (Devin, Copilot Workspace, OpenHands), test-driven loops (SWE-agent, Aider, Agentless), generator and critic (Reflexion, self-refine, debate), multi-agent roles (MetaGPT, ChatDev, CrewAI, AutoGen), spec-driven (Kiro, GitHub Spec Kit), trunk-based CI with merge queues and trains (GitHub merge queue, Bors, Zuul, GitLab merge trains), and human code review plus CI. Add any pattern the evidence shows is now standard that this list misses. (2) For each: what the published evidence says (benchmarks such as SWE-bench variants, ablations of verification and multi-agent setups, cost and failure data), dated, with the source URL and a note when a number is a vendor claim. Use WebSearch in `standard` mode first; use `extended` only for a claim that stays thin. (3) Compare against our own measured data: `docs/reports/2026-10-11-solo-campaign-baseline.md`, `2026-10-11-solo-fails-and-blocks.md`, `docs/reports/solo-vs-lean-benchmark-2026-10-04.md`, the fleet retros, `docs/kpi/005-solo-first-pass-rate.md`, `docs/reports/2026-10-12-maison-wave-7b-mechanics.md`. Do not read closed `.NNNN-*` ticket folders. (4) Read the open queue from `.sdlc/roadmap.md` (the proposed and ready tickets, about 15) and `docs/planning/merge-ops-and-queue.md`, `docs/planning/light-merge-lane.md`. For each open ticket give one verdict: keep, reshape, merge with another, defer, or drop, with the evidence line that supports it. (5) State what our system does that no surveyed pattern does (independent cross-family verifier, observed negative controls, per-ticket budget stops) and whether the evidence supports keeping each.
- Non-goals: editing tickets or code; choosing models or efforts; re-litigating the solo-first default without new evidence; publishing anything.
- Done when: the report lists every pattern with at least one dated source, separates published evidence from vendor claims and from our inference, gives one verdict per open ticket, ends with a ranked list of at most five changes to the queue each with a cost and the pillar it serves (`docs/specs/sdlc-lite/pillars.md`), and marks anything it could not verify as unverified.

## Context
Origin: maintainer question 2026-10-12 after the merge queue design (T-0488). Prior unsourced answer in this session mapped the patterns from background knowledge; this ticket replaces it with sources. Budget cap 10 USD for the ticket.

## Constraints
Read-only except the report file and the architect result. One architect pass, no replan. Cite, do not paraphrase from memory: a claim with no source is marked unverified. No em dashes.
