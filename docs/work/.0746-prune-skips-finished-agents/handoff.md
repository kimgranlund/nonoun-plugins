---
id: T-0746
title: "dispatch.py prune lists only agents that still exist"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py prune` does not print a `TaskStop task_id=<name>` line for a background agent that already finished (a TaskStop on it fails with "No task found"); it marks such entries done itself, or says a failed TaskStop for a finished agent is safe.

## Intent
- Do: In `dispatch.py prune`, use what the records show (a recorded result, a finished solo) to drop finished background agents from the TaskStop list, or print the safe-to-ignore note.
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

## Outcome
`dispatch.py prune` keeps the `TaskStop task_id=<name>` line for every entry (a queued teammate may still be live, and a finished one is not distinguishable from the records) but a queued solo, which is always a finished background agent, now ends with `; finished background agent: a 'No task found' failure from TaskStop is safe to ignore, still run --done`. Change: `BACKGROUND_NOTE` and `prune_lines` in `plugins/sdlc-lite/scripts/dispatch.py`, plus the Prune paragraph of its docstring.

- Selftest case `T-0746 prune: a queued solo ...` added. Negative control (note removed from `prune_lines`, case kept): `FAIL: T-0746 prune: a queued solo (a finished background agent) keeps its TaskStop line and says a No task found failure is safe to ignore; a teammate entry does not`, selftest exit 1. With the change: exit 0.
- `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exit 0.
- `python3 plugins/sdlc-lite/scripts/check.py` exit 0, `python3 scripts/check-packaging.py` exit 0, `git diff --check fd6963b9` exit 0.

## Outcome

2026-10-22 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: fd6963b96133
- Changed: see commits
- Commits: 93a889a T-0746: prune notes that a failed TaskStop on a finished background solo is safe to ignore
- Check: 1 A `dispatch.py` selftest case reproduces the issue's report and passes; with the change reverted ...: pass
- Check: 2 `gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py ...: pass
- Check: 3 `check.py` exits 0, `check-packaging.py` passes, `git diff --check <base sha>` exits 0: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/dispatch.py:1641 the comment "A queued... -> notes.md
