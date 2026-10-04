---
id: T-0216
title: "Live proof: a size-M ticket delivered by solo with a batched verifier, on Claude and Codex"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0215]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A recorded live run shows the `solo` agent delivering a real size-M ticket end to end, with one independent batched verifier, on Claude Code and Codex.

## Intent
- Do: pick one small real size-M change (a closed ticket with a known solution is fine, in a throwaway project or worktree), run it through `steps.py lane` (it must print `solo`), deliver it with the `solo` agent at tier M on each host (Claude: Sonnet xhigh; Codex: gpt-6.1-sol high), then run one independent batched verifier on a different model family. Record the lane output, the tier and model per host (from the run records, not from memory), pass or fail against hidden checks, cost and wall time, in docs/validation/solo-live-run.md with raw evidence beside it. Run each arm once; record a failure honestly as a limit.
- Non-goals: any change to agents, tables or lane logic (report defects as notes, do not fix here); a version bump, tag, push, or publish.
- Done when: the validation record exists with both hosts, it cites the actual models used, and docs/README.md links it.

## Context
T-0215 shipped with "no live run" as a known limit. This closes it and is the evidence for the 0.20.5 claim that solo is the default lane for S and M. Philosophy: "Done is better than perfect." Use one handwritten builder step or do it directly; no planner, no plan review. Budget about $15.

## Constraints
Keep it small. Bind evidence to the commit and models actually used. No em dashes.

## Closed

2026-10-04: Two steps, each verified L2 pass: step 1 recorded solo on Claude Code and Codex (hidden check 20/20 both, direct launch); step 2 recorded a conductor session starting solo through the documented path (T-0217). No planner, no filer under burn-down.
