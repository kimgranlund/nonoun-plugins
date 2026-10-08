---
id: T-0368
title: "A prune flag on the dispatch file so finished sub-agents are stopped after a recorded result"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Finished sub-agents are pruned by a built-in mechanism: the dispatch file carries a `prune` flag, `dispatch.py record` queues the agent when it succeeds, and one command stops everything queued.

## Intent
- Do: (1) `dispatch.py prepare` writes `"prune": true` into the dispatch file for one-shot roles (scout, researcher, architect, archaeologist, planner, plan-reviewer, verifier, filer), `false` for builder and solo (until their work has landed, since a failed one may be resumed) and the messenger; `--no-prune` and `--prune` override it. (2) `dispatch.py record` on exit 0 with `prune: true` prints one line `prune: <agent name>` and appends `{name, agent_id, role, level, recorded_at}` to `.sdlc/runtime/prune.json`; it never queues an agent whose attempt is open or whose result has `follow_up` pending. (3) `dispatch.py prune` lists the queue and prints, per entry, the stop call to make (`TaskStop task_id=<name>`, observed to work, see Context); `dispatch.py prune --done <name>` removes an entry; a landed builder or solo joins the queue through `fanout.py land` or `dispatch.py prune --add <name>`. (4) Skill text: conductor.md "How you run roles" and the launcher skills' record step get one line: after `record`, run `dispatch.py prune` and stop what it lists; the messenger skill too. (5) `fleet_status.py` lists an agent still queued more than 30 minutes after its recorded_at under Stale or stuck.
- Non-goals: model or effort changes; a hook that stops agents on its own (not shown possible here); stopping agents of another session.
- Done when:
  - Selftests: prepare sets the flag per role; record queues exactly the pruneable agents and skips a builder, a failed record and a pending follow-up; prune lists and clears entries (observed failing first).
  - A live probe in a throwaway project: spawn one named one-shot sub-agent through prepare and record, run `dispatch.py prune`, make the printed TaskStop call, and confirm the agent leaves ListAgents.
  - check.py, dispatch and fleet_status selftests, hook-selftest.sh, both generate --check pass.

## Context
User asked on 2026-10-08 for a built-in pruning mechanism after conductors left finished agents idle (maison retro: 27 teammates, 26 idle for hours; ultimate-tokens stopped 25 by hand). Probe on 2026-10-08 in the maintainer session: a named background general-purpose agent that had replied and finished still showed `idle` in ListAgents (it stays an addressable teammate), and `TaskStop task_id=<agent name>` stopped it ("in_process_teammate"). Five finished verifiers were stopped the same way. So the host offers a stop by name but no flag on the Agent call itself that ends an agent on completion; whether a hook could do it is not established. Related: .sdlc/fleet-retro-2026-10-08 (idle-agents row scored 3/10 as a retro finding; filed here by the user's request).

## Constraints
No em or en dashes. No push or publish.

## Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` passes; its `prune flag` cases show prepare sets `prune` true for scout, researcher, architect, archaeologist, planner, plan-reviewer, verifier, filer and false for builder, with `--prune` and `--no-prune` overriding.
- (guard) The same selftest's `prune record` cases show record queues a verifier, a planner and a filer whose `## Follow-ups` is None, and skips a builder, a failed record, a filer with a pending follow-up, a `prune: false` dispatch and an agent with another open attempt; `prune` prints one `TaskStop task_id=<name>` line per entry and `--done` and `--add` edit the queue.
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest` passes (`land` queues a merged solo, not an unmerged one).
- (guard) `python3 plugins/sdlc-lite/scripts/fleet_status.py selftest` passes (an agent queued 45 minutes is under Stale or stuck, one queued 5 minutes is not).
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`, `bash plugins/sdlc-lite/scripts/hook-selftest.sh`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` pass.
- (guard) `agents/conductor.md` step 4 and the launcher skills' dispatch step carry the line to run `dispatch.py prune` after `record`.
- Live probe, observed in a throwaway repo by solo: `dispatch.py prepare scout L1` printed `"prune": true`; an `Agent` spawn of `probe-scout-L1` ran and `dispatch.py record` printed the result path then `prune: probe-scout-L1`; `dispatch.py prune` printed `TaskStop task_id=probe-scout-L1    # scout L1, recorded ...` and `.sdlc/runtime/prune.json` held the entry. Not observed: the TaskStop leg. The solo role's hook forces `run_in_background: false`, so the agent had already ended and `TaskStop task_id=probe-scout-L1` answered "No task found"; ListAgents showed no such agent. The parent must repeat the last two steps (background spawn, TaskStop by the printed name, ListAgents) from a conductor session to close the criterion.
