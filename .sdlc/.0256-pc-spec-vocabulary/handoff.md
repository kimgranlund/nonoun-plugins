---
id: T-0256
title: "Reconcile construct and capability vocabulary in the specs"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add a status banner to each numbered spec and a glossary mapping construct, revision, instance to capability, contract, assessment.

## Intent
- Do: Edit docs/generative-constructs/01 to 06 only to add a banner pointing at the shipped skill and one glossary in the README.
- Non-goals: rewriting the proposals, editing the plugin.
- Done when: each numbered spec carries the banner and the glossary names each shipped term once.

## Context
Gap analysis R8: the specs say construct, revision, instance (02-construct-model.md:5-14) while the shipped skill says capability, contract, assessment; the README says the specs preserve the initial proposal. Lane: solo. Philosophy: Done is better than perfect.

## Constraints
No push, tag, version bump, or publish. No em dashes. Preserve other agents' worktrees.

## Closed

2026-10-05: Banner added to docs/generative-constructs 01 to 06 and a vocabulary table in the README mapping construct, contract, criterion/evidence/assessment, revision, release, qualification, run and instance to the shipped terms (instance has no shipped counterpart); git diff --check, tickets.py check and link checks clean; the batched L3 verifier at the end of wave-b reads the diff.
