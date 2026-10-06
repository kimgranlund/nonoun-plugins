# Fix batch 0.20.11

Dated 2026-10-06. Built from three consumer root-cause reports (ui-kit-maison, agent-ui, gen-ui-kit) on branch `worktree-agent-ae9ec401bb7128396`, base `24ef333`, built tree `2cd5342`. Every claim below comes from a command or verifier result recorded in the ticket or batch folders under `.sdlc/`.

## Tickets and lanes

Each ticket was filed with `tickets.py new`, built by a solo lane through `fanout.py run --lane solo --max-lanes 2 --stagger 60` (tier S for T-0293 to T-0300, tier M for T-0303 and T-0304; the M tickets each got a fanout-run L3 verifier, verdict pass), and merged behind `check.py` and `tickets.py check`.

| Ticket | Item | Merge commit |
|---|---|---|
| T-0293 | solo_run kills its process group; refuses a second live run | 678a7ae (lane commit, merged by hand after the first fanout hit its time limit) |
| T-0294 | plan review only for L4 and L5 steps | 48e25a3, repaired in 832bb36, b1b3c74, 2cd5342 |
| T-0295 | steps lint and precheck name the heading found | 9456b37 |
| T-0296 | steps lane refuses size M over 20 criteria | 9d8f3be |
| T-0297 | planner guard dry-run sentence; split inherits earlier widenings | 3a75c8b |
| T-0298 | 429 marker records the reset time (run.sh and solo_run.py) | 91cf128 |
| T-0299 | fanout accepts T-0123 or bare 0123 | 44c7aa7 |
| T-0300 | board reads done for a merged solo ticket | 619fcd5 |
| T-0303 | gate_lock.py semaphore, wired into fanout gates | 2cd4d13 |
| T-0304 | gate_lock.py reap, suggest-only | c24032c |
| T-0301, T-0302 | filed, not built: conductor 429 rerun; ADR number allocator note | none |

The machine-wide gate semaphore idea is also T-0292 on the hook-perf agent's branch; T-0303 builds it, so T-0292 is superseded when the branches meet. The red-under-load re-run rule was not built (not approved).

## Red then green, from the verifiers

Verifier A (`.sdlc/verify-fix-batch-0.20.11-a/verifier-L3.md`, steps.py group) and verifier B (`.sdlc/verify-fix-batch-0.20.11-b/verifier-L3.md`, tools group) reverted only each fix's non-test hunk in a throwaway worktree and ran the matching selftest.

- T-0294: with the old `review_required` body, selftest exit 1 (cases `plan review only for L4 or L5` and the lane case red). CLI: a planner-L3 plan, a replan, a `## Plan review` line, and a Merge title printed `review L1` at base and print `split` now; L4 and L5 still print `review L1`. No change to run.sh model rows, models.json, or the rubric table.
- T-0295: with the hint removed, selftest exit 1 on both new cases; a handoff with `## Task goal` now prints `found ## Task goal instead, expected ## Goal`. The `steps.py lint` command itself never raised that refusal (precheck and split do).
- T-0296: with the check removed, selftest exit 1; size M with 21 criteria prints `solo` at base and `full` with the split reason now; 20 stays `solo`.
- T-0297: with the inheritance removed, selftest exit 1; step 2 gains the widened path in its allow-list and `## Scope widened`; with no widening it is byte-identical to base. `agents/planner.md` carries one sentence on the guard dry-run.
- T-0293: reverts of the group kill, of `start_new_session`, and of the lock each gave selftest exit 1. Real child (a stub `claude` that spawns `sleep 300`): `sleep` gone after a timeout, SIGTERM, SIGINT, and SIGHUP; a TERM-ignoring child is killed by the KILL path; a second run printed `solo_run.py: another solo run is live (pid N)`, exit 2, no new session or record; a dead pid's lock was cleared. At base the same harness left `sleep` alive and started a second session.
- T-0298: reverting the parse in run.sh gave `run selftest: FAIL: session limit reset: marker has no reset 1:40pm`; reverting solo_run.py gave `solo_run selftest FAIL: limit stop with a reset`. Seen live: the first A3 verifier run hit the account limit and printed `run.sh: session limit: resume with: ... (resets 11:40am)`.
- T-0299: with the normalization removed, selftest exit 1 on the bare-id and twice-listed cases. The first fanout of this batch refused bare ids itself (`'0294' is not a ticket id like T-0001`), which is the bug.
- T-0300: with the early `closed` return removed, selftest exit 1 (`got built · builder L2, awaiting verify`); CLI on a temp `.sdlc`: base printed the stale row, the fix prints `🟢 closed`; ready, last-lane-full, and `.running` controls unchanged.
- T-0303: five one-line mutants (slot cap, dead-pid check, SDLC_GATE_WORKERS, exit status, timeout code 3) each gave selftest exit 1; the negative control (cap removed) is observed in the selftest; fanout selftest shows a gate running through gate_lock and `--no-gate-lock` skipping it.
- T-0304: four mutants (list mode, `--kill` no-op, orphans never listed, parent check dropped) each gave selftest exit 1; hand run against real orphans listed exactly the orphans and skipped the live-parent match.

## Verifier verdicts

- Fanout verifiers for T-0303 and T-0304 (L3): pass, pass.
- Verifier B (T-0293, T-0298, T-0299, T-0300; L3): pass.
- Verifier A (T-0294 to T-0297; L3): T-0295, T-0296, T-0297 pass. T-0294 failed on dependents of the changed contract (lean eligibility, usage text, a false "merge step is L4 or higher" claim, `handoff-format`). Re-verify 1 (L3, commit 832bb36): fixture half pass, text half failed (lint usage text versus lint code, `sdlc-internals.md` still stated the old rules). I chose "lean stays strict" in both `lane` and `lint` and fixed the texts (b1b3c74, 2cd5342). Re-verify 2 (A3) could not run: the account session limit hit both `verifier L3` and `verifier L2` (resets 11:40am). 🟡 The T-0294 repair is checked only by `steps.py selftest`, `check.py`, and `codex_roles.py generate --check`, all green on 2cd5342, not by an independent verifier. Resume: `bash plugins/sdlc-lite/scripts/run.sh verifier L3 .sdlc/verify-fix-batch-0.20.11-a3/handoff.md` after 11:40am.

## Checks on the built tree

On 2cd5342 (before this record file): `check.py` ok (19 role levels, 9 agents); `codex_roles.py generate --check` verified; `check-packaging.py` PASS; `tickets.py check` ok (279 tickets); steps, solo_run, fanout, board, run-selftest, gate_lock selftests PASS; full `check.sh` PASS (rc=0) from `/tmp/sdlc-batch-copy`, a `git archive` extract whose path has no `claude`.

## Limits and follow-ups

- Verifier B found that two SIGTERMs 0.5 s apart to `solo_run.py` while its child ignores TERM make `kill_group` re-raise `Stopped` before the KILL (exit 1, child alive, lock removed). One signal works. Not fixed in this batch; a follow-up candidate.
- A first fanout was killed at its 30 minute background limit while T-0293 was stuck in a selftest hang (the stub child held the wrapper's stderr pipe); T-0293 was finished by hand in the lane worktree and merged. Raw `kill` of two orphan stubs it left behind (pids 14284 and 63618) was the only process cleanup.
- A lane left a stray `steps.py.bak`; removed in 0e85edb.
- No push, publish, tag, or merge into `main`.
