---
id: T-0745
title: "prepare prints no warning for the normal lane-start base of a ticket verifier"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py prepare verifier` on a lane ticket prints no `nothing recorded for this step ... name another with a line base:` line when the lane start is the expected base; the line stays only when it is a real ambiguity.

## Intent
- Do: Find where `dispatch.py` prints it (about line 560) and suppress it for a ticket verifier whose base is the lane start (or reword it as an info line naming the base used).
- Non-goals: the other parts of the same issue.
- Done when: the criteria pass.

## Context
GitHub issue #72 (quoted):

> **Version:** sdlc-lite 0.33.0, Claude Code host, sub-agent lanes. Seen in ui-kit-neue 2026-10-22.
>
> **What happened**
> 1. `dispatch.py advance --agent-id <id> --tokens ... <task>/T-0296-solo.dispatch.json` on a solo dispatch file written by `fanout.py prep` exited 2:
>    `... is not a dispatch file (missing tmp_prefix, tree, artifacts_dir, handoff_sha256, attempt_file, routing_reason)`
>    As a result, no L1 solo from prep has a `runs.jsonl` cost row or a closed attempt. The fanout skill's step 3 says to run `advance` on the solo's dispatch file.
> 2. `dispatch.py prepare --solo-model opus verifier L2 <worktree>/<task>/handoff.md` printed `nothing recorded for this step: Base sha is the lane start 9b987fe333fa, not its HEAD 499e42200979; name another with a line 'base: <sha>'`. It then dispatched correctly with Base sha at the lane start. The message reads like an error but is the expected case for a ticket verifier.
> 3. `dispatch.py prune` printed `TaskStop task_id=T-0296-solo` for a finished background solo. The Claude Code TaskStop call failed with `No task found with ID: T-0296-solo`, because a finished background agent is no longer a task. This happened 5 of 5 times for solos (verifiers, still idle teammates, stopped fine).
>
> **Expected**
> - `advance` or `record` accepts the dispatch file `prep` writes, or `prep` writes a full one.
> - The verifier prepare prints no warning for the normal lane-start base.
> - `prune` lists only agents that still exist, or says a failed TaskStop for a finished agent is fine.
>
> **Workaround used**
> L1 solos landed without a record. `prune --done <name>` was run after each failed TaskStop.
>
> **Ask**
> Make prep's solo dispatch file recordable, which also gives cost rows for L1 solo lanes. Soften or drop the base-sha line for ticket verifiers. Make prune skip finished agents. Related to #54.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `dispatch.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
