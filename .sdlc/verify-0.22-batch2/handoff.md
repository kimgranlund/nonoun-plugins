# Verify T-0363, T-0367, T-0368, T-0370, T-0372, T-0373 on main

## Goal
Independently verify six closed solo tickets on main at HEAD (builders were solo sonnet; you are a different family). Earlier lane verifiers found and the lanes fixed small gaps in T-0368, T-0372 and T-0373; confirm the final tree. Also run the live-host claims you can: T-0368's live probe record is .sdlc/.0368-prune-flag/live-probe.md (read it; you may rerun the dispatch.py prepare, record and prune steps in a throwaway project but you cannot call TaskStop). Codex host behavior cannot be run here, so for T-0372 and T-0373 judge the no-model tests and mark live Codex claims unverified.

## Intent
- Do: for each ticket read its closed folder (.sdlc/.NNNN-*/handoff.md) and check each Done-when criterion with an observed command in a throwaway git archive copy of HEAD (git-initialised, under your tmp prefix; no worktrees), with a red control where a criterion is a guard.
- Non-goals: editing anything.
- Done when: a pass or fail per ticket with the command and output per criterion.

## Context
T-0363 Done-when (.sdlc/.0363-subagent-list-style/handoff.md):
  - A selftest prints names and first prompt lines for two attempts of two tickets and asserts the first 24 name characters differ and each first line is at most 50 characters (observed failing first).
  - hook-selftest.sh, dispatch, solo_run and fanout selftests, check.py, both generate --check pass.

T-0367 Done-when (.sdlc/.0367-messenger-read-backlog/handoff.md):
  - A selftest case: empty new queue and a nonempty read queue surfaces the backlog once; a second poll does not repeat it (observed failing first).
  - A message for another receiver is never claimed or listed; a new arrival is still claimed and forwarded; ack and follow-up rules are unchanged (existing cases pass).
  - messages.py selftest, check.py, tickets.py check, both generate --check pass.

T-0368 Done-when (.sdlc/.0368-prune-flag/handoff.md):
  - Selftests: prepare sets the flag per role; record queues exactly the pruneable agents and skips a builder, a failed record and a pending follow-up; prune lists and clears entries (observed failing first).
  - A live probe in a throwaway project: spawn one named one-shot sub-agent through prepare and record, run `dispatch.py prune`, make the printed TaskStop call, and confirm the agent leaves ListAgents.
  - check.py, dispatch and fleet_status selftests, hook-selftest.sh, both generate --check pass.

T-0370 Done-when (.sdlc/.0370-mailbox-registry-handshake/handoff.md):
  - Selftests: send to an unregistered receiver is refused; send to a reader-less receiver warns; handshake reports both states; default sender names repo and harness (observed failing first).
  - check.py, tickets.py check, hook-selftest.sh, the affected selftests and both generate --check pass.

T-0372 Done-when (.sdlc/.0372-codex-solo-native-transport/handoff.md):
  - A no-model integration test starts solo with backend codex and transport subagent, observes a valid request file, submits a fixture response through scripts/codex_exchange.py, and completes with an accurate run record (observed failing first; repro in docs/reports/2026-10-08-codex-report-solo-native-transport/repro.json).
  - It covers solo L1, L2 and L3 routing, response failure, timeout, and a rerun request name that does not overwrite an earlier attempt, and it fails when the request-file wiring is removed (assert the request lifecycle, not only command construction).
  - The native record says backend codex and transport subagent; unknown cost is null with a reason; no Claude model, agent name or nested codex exec appears.
  - check.py, tickets.py check, codex_roles.py generate --check, run-selftest.sh and codex-selftest pass.

T-0373 Done-when (.sdlc/.0373-codex-role-preflight/handoff.md):
  - Tests with fixture catalogs: current definitions plus a stale live catalog, stale definitions plus loaded older roles, and a fresh session with the required role available; the first two must not report ready (observed failing first).
  - The readiness text and resume packet are in the Codex adapter and the skill, and `codex_roles.py install --check` behavior is unchanged.
  - check.py, tickets.py check, codex_roles.py generate --check, run-selftest.sh and codex-selftest pass.

## Constraints
Read-only. No em or en dashes.
