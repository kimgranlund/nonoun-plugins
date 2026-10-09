---
id: T-0414
title: "Restart sweep, reused parent pids, and a safe prune --add"
type: feature        # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0413]
created: 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Restart sweep, reused parent pids, and a safe prune --add. Serves goal G-002 (docs/goals/002-restart-and-blocked-run-cost.md); spec: docs/specs/sdlc-lite/restart-and-blocked-run-plan.md; plan step 4 in .sdlc/plan-reliability-docs/plan.md.

## Intent
Ticket: feature, size L2, candidates 1 and 6 of the spec (sections 1 and 6). Depends on: step 3 (same files, same lane).

In `plugins/sdlc-lite/scripts/dispatch.py`:
- `recover --root DIR` (the `recover` parser, `dispatch.py:1129`; handler `1164-1171`): mutually exclusive with the positional handoff dir. Walk `DIR/.sdlc`, skipping `.git`, `.worktrees` and `node_modules` folders, and for each folder holding a `*.attempt.json` run `recover_orphans` (`dispatch.py:443-458`). Print `recovered: <attempt path>` per orphan, then `  resume: python3 <dispatch.py> prepare <role> <level> <handoff>` from that record; print `running: <attempt path> (pid N)` for a live attempt and leave it alone; print `no orphaned attempts` when there are none. Exit 0.
- `attempt_state` (`dispatch.py:432-440`): a parent pid that is alive but whose process started after the attempt's `started_at` is read as dead (the host reused the pid). Read the start time with `ps -o lstart=` under `LC_ALL=C` as `fleet_status.py:236` does; when it cannot be read, keep today's answer.
- `prune --add NAME` (`dispatch.py:1149-1151`, `prune_add` `808-812`): exit 2 with `dispatch.py: <NAME> has a running attempt <path>; record it before queueing it for pruning` when an attempt record under `<root>/.sdlc` with `agent_name` or `name` equal to NAME reads `running` by `attempt_state`. An orphaned or finished attempt does not block it.
- The refusal text at `dispatch.py:465` that names `run_lifecycle.py recover` stays: it is the force path for a spawn that never started, pinned by the case "a second prepare with a running attempt and a live parent refuses" (`dispatch.py:1718-1719`).
Add selftest cases with exactly these labels: `recover --root marks every orphan under the root interrupted and prints its prepare command`, `negative control: recover --root leaves a live-parent attempt running`, `orphaned: a parent pid that started after the attempt is read as dead (reused)`, `prune --add refuses an agent whose attempt is still running, exit 2`, `negative control: prune --add queues an agent whose attempt is completed`.

In `plugins/sdlc-lite/agents/conductor.md`: add a restart rule (after a host or session restart, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py recover --root .` once before any other dispatch and re-dispatch each run it prints with its resume line); and in item 4 (Prune, `conductor.md:36`) add this sentence verbatim: "Stop only the agents `dispatch.py prune` lists; never stop a sub-agent because it looks idle (one waiting on a background command looks idle), and a prune cron or loop runs `dispatch.py prune` and makes only the calls it prints." Then run `codex_roles.py generate` to refresh `sdlc-conductor-l1.toml`. Optionally point the resume paragraph of `plugins/sdlc-lite/skills/chain/SKILL.md:56` at `recover --root`; update `docs/references/sdlc-internals.md` where it describes `recover` or `prune --add`.

Contract dependents (`git grep -n "dispatch.py recover\|prune --add\|run_lifecycle.py recover" -- plugins docs/references`): `conductor.md:36`, `skills/chain/SKILL.md:56`, `docs/references/sdlc-internals.md:31`, the generated Codex agent TOMLs (regenerated, never edited), and `run_lifecycle.py:79` (Codex refusal, unchanged). Write each label as one string literal on one line, so the (red) source greps find them. Validation scope: `dispatch.py selftest`, `lifecycle-selftest.py` (the plugin guide requires it after a recovery change), `codex_roles.py generate --check`.

## Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`

## Done when
- (red) `grep -qF 'recover --root marks every orphan under the root interrupted and prints its prepare command' plugins/sdlc-lite/scripts/dispatch.py`
- `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && for l in 'recover --root marks every orphan under the root interrupted and prints its prepare command' 'negative control: recover --root leaves a live-parent attempt running' 'orphaned: a parent pid that started after the attempt is read as dead (reused)'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (red) `grep -qF 'prune --add refuses an agent whose attempt is still running, exit 2' plugins/sdlc-lite/scripts/dispatch.py`
- `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && for l in 'prune --add refuses an agent whose attempt is still running, exit 2' 'negative control: prune --add queues an agent whose attempt is completed'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (red) `python3 plugins/sdlc-lite/scripts/dispatch.py recover --help | grep -qF -- '--root'`
- (red) `grep -qF 'dispatch.py recover --root' plugins/sdlc-lite/agents/conductor.md`
- (red) `grep -qF 'never stop a sub-agent because it looks idle' plugins/sdlc-lite/agents/conductor.md`
- (guard) `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && printf '%s\n' "$out" | grep -qxF 'ok: a second prepare with a running attempt and a live parent refuses'`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxF -e plugins/sdlc-lite/scripts/dispatch.py -e plugins/sdlc-lite/agents/conductor.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml -e plugins/sdlc-lite/skills/chain/SKILL.md -e docs/references/sdlc-internals.md)"`

## Context
Planner L3 output for the 2026-10-09 retros. KPIs: K-002 restart recovery minutes, K-003 blocked builders per wave, K-004 unsatisfiable criteria caught. The spec marks which candidates may already be fixed or need diagnosis first; follow it.

## Constraints
No em or en dashes. No push or publish. The plan step is the contract: if it is wrong or silent, stop and report a plan defect instead of improvising.
