---
id: T-0255
title: "Write one real capability contract for the solo lane"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Write one capability contract and evidence-bound assessment for the solo lane using the Progressive Context format.

## Intent
- Do: Use plugins/progressive-context/skills/progressive-context/references/contracts.md and evidence.md to write a contract and assessment for the SDLC Lite solo lane under docs/.
- Non-goals: editing the plugin, building a registry.
- Done when: the contract and assessment exist, an independent reader finds the format held or lists where it did not, and a short note records what the format lacked.

## Context
Gap analysis R7: no real contract exists in this repository or maison to learn from (git grep for an ID line finds only the format example, contracts.md:7). Solo lane facts live in plugins/sdlc-lite/agents/solo.md and scripts/steps.py lane. Lane: solo. Philosophy: Done is better than perfect.

## Constraints
No push, tag, version bump, or publish. No em dashes. Preserve other agents' worktrees.

## Closed

2026-10-05: Contract docs/lean-sdlc/solo-lane-contract.md and assessment docs/lean-sdlc/solo-lane-assessment.md written in the Progressive Context format; steps, fanout, solo_run and budget selftests rc=0 at the assessed revision; the independent reader check is the batched L3 verifier at the end of wave-b (a fail there is fixed forward and noted); format gaps recorded in the assessment.
