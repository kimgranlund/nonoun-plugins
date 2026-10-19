---
id: T-0334
title: "Twelve launcher skills spell dispatch.py record without --transcript (T-0331 finding)"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every launcher skill that spells out a `dispatch.py record` call passes `--transcript <sub-agent transcript jsonl>`, or defers to the conductor contract instead of spelling flags, and a check fails when one omits it. The bug is fixed and a test that failed before the fix passes after it.

## Repro
1. `grep -n 'dispatch.py.*record' plugins/sdlc-lite/skills/*/SKILL.md | grep -v -e '--transcript'`

## Expected
No launcher skill spells a `record` call without `--transcript`: `plugins/sdlc-lite/agents/conductor.md:35` says a call without it prices a run at about a tenth of its cost, and T-0331's Goal is that the conductor and chain skills pass it so the estimate is not undercounted.

## Actual
Twelve skills spell `dispatch.py record <dispatch_file> --agent-id <id> --tokens <n> --tool-uses <n> --duration-ms <ms>` with no `--transcript`: `skills/agent/SKILL.md:28`, `architect:16`, `build:15`, `dig:16`, `file:14`, `fix:16`, `fleet-retro:56`, `plan:16`, `research:16`, `review-traces:12`, `scout:16`, `verify:16`. A conductor following `/build` or `/verify` copies a call that prices the run low.

## Context
Found by the independent verifier of T-0331 (criterion T0331-1), `.sdlc/verify-subagent/T-0331.md`. Root cause: T-0331 edited only `agents/conductor.md` and `skills/chain/SKILL.md`; each launcher skill spells its own record call. Skills not spelling flags (`bench`, `fanout`, `handoff-format`, `level-rubric`, `sdlc-lite`) defer to the conductor contract and are not affected. Fix either by adding the flag or by replacing the enumerated flags with a reference to the conductor contract (smaller, one place to keep right).

## Constraints
The failing check lands before or with the fix: a `check.py` guard that lists the offending skill and has an observed negative control. No em or en dashes. No push or publish.

## Closed

2026-10-07: built and merged by fanout lane (batch fix021)
