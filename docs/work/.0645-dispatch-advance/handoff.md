---
id: T-0645
title: "dispatch.py advance runs record, prune, next and prepare in one call"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
One conductor call per role completion does the bookkeeping: `dispatch.py advance` records the role, clears its prune entry, asks `steps.py next`, and prepares the next role, so the conductor spends one request where it now spends about four.

## Intent
- Do: (1) Add `dispatch.py advance [record flags] <dispatch.json>` in `plugins/sdlc-lite/scripts/dispatch.py`: run `record` (same flags, same exit codes on failure, stop there on a non-zero record), then for a pruned role drop its queue entry the way `prune --done` does (`prune_done` plus `prune_lane`) and print `TaskStop task_id=<name>`, then run `steps.py next` on the step dir, and when the action names a role and level (build, rebuild, verify, reverify) run `prepare` for it and print the dispatch JSON; any other action prints `stop: <action> <reason>` and prepares nothing. A dispatch outside a step dir prints `next: <hint>` after the record and prune. (2) Selftest cases for each branch. (3) `agents/conductor.md` "How you run roles" steps 3 and 4, `skills/chain/SKILL.md` and `skills/fanout/SKILL.md` say to call `advance` once per completion and to send the printed TaskStop and the next Agent spawn in the same response.
- Non-goals: changing what standalone `record`, `prune` or `prepare` do (they stay for manual use and for Codex). No Codex `run.sh` change. Solo dispatches from `fanout.py prep` are out of scope.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #9, ui-kit-neue audit 2026-10-20.
- Evidence: one 0.27.0 conductor session, 1,943 requests, 948M cache_read, 450 role runs; about 4.4 conductor requests and about 2.1M cache_read per role run; prune-only requests 127 (about 62.8M), `steps.py next`-only 92 (about 43.7M), prepare-only about 31.5M, prune plus TaskStop about 27.9M.
- `record` is `plugins/sdlc-lite/scripts/dispatch.py:1503`; its CLI branch is `dispatch.py:1871-1895` (with `--agent-id`, `find_subagent_transcript` at `dispatch.py:1469`). Prune queue helpers: `prune_add` `dispatch.py:1339`, `prune_done` `dispatch.py:1346`, `prune_lane` `dispatch.py:1399`, `queue_prune` `dispatch.py:1451`; `prune --done` parser `dispatch.py:1795`. `prepare` is `dispatch.py:944`; the subparsers start at `dispatch.py:1750`.
- `steps.py next` is `plugins/sdlc-lite/scripts/steps.py:3044` (`cmd_next`) over `next_action` at `steps.py:2875`, which returns `(action, level, reason, read)`. Import `next_action` rather than shelling out.
- The issue's "fold `prune --done` into `record`" is met by `advance`; standalone `record` keeps queueing so a conductor that has not stopped the agent yet still sees it in `dispatch.py prune`.
- Docs to update: `plugins/sdlc-lite/agents/conductor.md:41-42` (steps 3 Record and 4 Prune), `plugins/sdlc-lite/skills/chain/SKILL.md:20` and `:69`, `plugins/sdlc-lite/skills/fanout/SKILL.md` where it records a full-lane role (around line 51). T-0646, T-0667 and T-0659 also edit `conductor.md:41` or `chain/SKILL.md`; do not run them in the same wave.

## Constraints
`record`, `prune`, `prepare` and `steps.py next` keep their current output and exit codes. `advance` never prepares after a failed or invalid record. Shared role text stays host-neutral: Codex keeps `run.sh`.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with new `advance` cases: (a) a verifier fail in a step dir records, prints `TaskStop task_id=<verifier name>`, removes that entry from `.sdlc/runtime/prune.json`, and prints a builder dispatch JSON whose dispatch file exists; (b) a verifier pass prints `stop: done` and writes no new dispatch file; (c) an invalid result exits 3 and prepares nothing. Each case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/dispatch.py advance --help` exits 0.
3. `grep -c 'dispatch.py advance' plugins/sdlc-lite/agents/conductor.md plugins/sdlc-lite/skills/chain/SKILL.md plugins/sdlc-lite/skills/fanout/SKILL.md` prints a non-zero count for each file.
4. `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0.
5. `git diff --check` exits 0 and `python3 scripts/check-packaging.py` exits 0.

## Outcome
- `dispatch.py advance [record flags] <dispatch.json>`: runs `record` (a non-zero record returns its code and prepares nothing), drops a queued role with `prune_done` plus `prune_lane` and prints `TaskStop task_id=<name>`, runs `steps.next_action` on the step dir, and prepares `build`, `rebuild`, `verify` or `reverify` (printing the dispatch JSON); any other action prints `stop: <action> <reason>`, a handoff outside a step dir prints `next: <hint>`. Before a rebuild after a verifier fail it appends that verifier's `## For the next attempt` to the step handoff under `## Previous attempt` (/chain 4.4), so the prepared brief and handoff sha already carry it. The lane tree is kept with `--tree` when the old dispatch ran in another tree.
- `bump` is left to the conductor (`stop: bump ...`): it needs the recurring-finding check first.
- Selftest: three `T-0645 advance` cases (verifier fail, pass, invalid); all three fail with the `advance` subcommand removed.
- Docs: `agents/conductor.md` steps 3 and 4, `skills/chain/SKILL.md` (dispatch paragraph, section 4 action list, item 4.4), `skills/fanout/SKILL.md` (solo verifier, full lane); regenerated `adapters/codex/agents/sdlc-conductor-l1.toml`.
- Checks: `dispatch.py selftest` exit 0; `dispatch.py advance --help` exit 0; the criterion 3 grep prints 2, 3, 2; `steps.py selftest` exit 0; `git diff --check` exit 0; `scripts/check-packaging.py` exit 0; `check.py` ok.

## Outcome

2026-10-20 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 92b2df57cd83
- Changed: see commits
- Commits: 71508be T-0645: dispatch.py advance runs record, prune, next and prepare in one call
- Check: 1 selftest with new advance cases: pass
- Check: 2 `advance --help`: pass
- Check: 3 doc grep: pass
- Check: 4 steps selftest: pass
- Check: 5 diff check and packaging: pass
- Follow-up: note: plugins/sdlc-lite/scripts/dispatch.py advance: a solo dispatch... -> notes.md
