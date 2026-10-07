---
id: T-0252
title: "Record which context a run loaded"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Make a role run record which entry files and references it actually read, so loaded context is inspectable.

## Intent
- Do: Extend plugins/sdlc-lite/scripts/run.sh and trace ingestion to write a loaded-context list (paths read, from the Claude stream-json log and the Codex rollout when present) into the runs.jsonl record.
- Non-goals: enforcing what a role may read.
- Done when: a live run on Claude Code records its read paths, the Codex arm records them or states 'rollout absent', and a negative control shows a missing log is reported, not silently empty.

## Context
Gap analysis R3 (docs/specs/generative-constructs/progressive-context-gap-analysis.md): only routing_reason is stored today (run.sh:520-524). Codex rollout files can be absent (docs/reports/codex-conductor-solo-live-run.md:23). Do not edit run.sh while a role run uses it. Lane: solo. Philosophy: Done is better than perfect.

## Constraints
No push, tag, version bump, or publish. No em dashes. Preserve other agents' worktrees.
