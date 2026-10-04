# Release 0.20.6

Recorded: [[PENDING: date]]. SDLC Lite 0.20.6. Progressive Context stays at 0.1.2 (no change since 0.19.0). Previous release: SDLC Lite 0.20.5 (244d0af, tag `v0.20.5`). Built from main commit [[PENDING: fixed commit, the main HEAD after T-0221 and T-0218 to T-0220 merged]]; the release branch merges that commit and adds the version bump and this record, and the release commit is the one tagged `v0.20.6`.

DRAFT: every `[[PENDING ...]]` marker below waits on a merge or a measurement and must be resolved against the repository at the fixed commit before the record is final.

## What changed for consumers

This release makes `fanout` follow the same solo-first rule as the conductor, closes three small limits the 0.20.5 record listed, and adds the benchmark record that backs the default. Fanout is the only change that alters what a command does. The check renumbering and the skips guard change affect maintainers and `tickets.py check`, and the benchmark is evidence only.

| Change | Detail | Ticket |
| --- | --- | --- |
| Fanout solo first | `scripts/fanout.py` runs `steps.py lane <task dir>` in each lane worktree after the lane syncs and follows it, recording the lane line in the task's `skips.md` (committed with the lane). Lane `solo` (size S and M by default) starts `agents/solo.md` as a headless session at the tier's model and effort: Claude `SDLC_ROLE=solo claude -p --agent sdlc-lite:solo`, Codex `codex_exec.py solo L1\|L2\|L3`. For tier M or L a new task-dir verifier result with Verdict pass is required before the merge, from the solo itself or else one `run.sh verifier L3 <task dir>/handoff.md` that fanout runs once (outcomes `verifier fail` and `no verifier result`). A solo ticket closes with `tickets.py close --reason`, since it has no filer file. Lane `full` (and `lean`) keep the headless conductor running `/sdlc-lite:chain`. New flags: `--lane auto\|solo\|full`, `--max-lanes N` (default 4; above 16 it also needs `--yes-many`), `--stagger SECS` (default 20), `--allow-overlap`. The plan and the run report print each ticket's lane, and preflight refuses two tickets in different lanes whose planned scope overlaps unless `--allow-overlap`. `check.py` guard 24 ties the fanout tiers to the tiers in `agents/solo.md`. [[PENDING: confirm every flag, default, outcome name and the guard number against fanout.py, skills/fanout/SKILL.md and check.py at the fixed commit]] | T-0221 |
| Unique guard numbers | `scripts/check.py`'s docstring numbered two guards 17 and two guards 18 and cited items that did not match. The guards are renumbered so they run 1 to N once each (spec gate 16, carry forward 17, solo agent 18, conductor rules 19, handoff freeze 20, solo start path 21, ticket budget 22), the code comments cite the right item, and a new guard 23 fails when the numbers repeat or skip, or when a comment cites a missing item, with negative controls. [[PENDING: confirm numbers at the fixed commit; fanout's guard 24 must follow 23 without a gap]] | T-0218 |
| Skips guard covers solo and full | The `tickets.py` skips guard (T-0198) covered only tickets with a recorded lane and exempted any last lane other than `lean` or `fix`, so the new default lane was unguarded. It now also covers lane `solo` and `full`, with a positive case and a negative control. [[PENDING: state exactly what a solo or full ticket must record, from the tickets.py change at the fixed commit]] | T-0219 |
| T-0212 re-verified | The T-0212 fix (`check-packaging.py` count pin and the hook route check) was made after its verifier returned `fail` and was never re-verified in 0.20.5. [[PENDING: the result of the L2 re-verification and where it is committed]] | T-0220 |
| Solo vs lean benchmark record | `docs/validation/solo-vs-lean-benchmark-2026-10-04.md` with raw evidence in `docs/validation/solo-vs-lean-benchmark-2026-10-04/` (merged as 9bc9fb8). It is evidence only and changes no behavior. Result: on three real tickets all six cells passed the hidden check and `check.sh`. Solo cost $2.66 in 18 minutes in total with no replans; the lean arm cost $26.83 in 120 minutes with 2 replans. See Known limits for what that does and does not show | none |
| Docs | `docs/maintenance/sdlc-internals.md` and `skills/fanout/SKILL.md` describe the solo-first fanout and its flags; `docs/README.md` links the benchmark record and [[PENDING: `docs/validation/fanout-solo-live-run.md`]] | T-0221 |

[[PENDING: state who built and verified each ticket from the run records: T-0221 was built as one handwritten step on branch `fanout-solo` and checked by an L2 verifier; T-0218 to T-0220 were built under the limits lane; list the verifier level and verdict for each, and any ticket with no whole-branch verifier]]

## Upgrade notes

- Behavior change in `/sdlc-lite:fanout`: lanes for size S and M tickets now start `solo` instead of a conductor running the full chain. Pass `--lane full` to keep the old behavior for a run. A repository that wants the old default everywhere has no setting for it in this release. [[PENDING: confirm there is no config key for this at the fixed commit]]
- Lane count and pacing: a run holds at most 4 lanes and starts them 20 seconds apart. Raise the cap with `--max-lanes N` (above 16 needs `--yes-many`) and lower or remove the stagger with `--stagger`. These defaults were chosen, not measured. The real limits are the plan's rate limit and merge conflicts on shared files, not the machine.
- A size M or L solo ticket needs a passing batched verifier result before its fanout merge; fanout runs one verifier if the solo did not.
- Codex: [[PENDING: state whether any generated Codex agent changed between v0.20.5 and the fixed commit (`git diff v0.20.5..<fixed> -- plugins/sdlc-lite/adapters/codex/agents`); only then say whether `codex_roles.py install <project>` is needed]]
- `check.py` guard numbers changed (see the table). Anything outside this repository that cites a guard by number needs the new number.
- No migration is needed and `tickets.py roadmap` is unchanged. [[PENDING: confirm after reading the diff]]

## Known limits

- How far the evidence supports "solo-first is the default for fanout": the benchmark (n=3, one run per cell) shows a solo session matched the chain on pass rate at about a tenth of the cost and a sixth of the time on three small tickets from this repository. It does not measure fanout. [[PENDING: the fanout solo live run record: number of lanes and tickets (planned: 4 tiny disjoint tickets, 3 size S and 1 size M), pass or fail per lane against the hidden check, merges, cost, wall time, and the models used taken from the run records]] Fanout with more than four lanes, tickets with overlapping files, and size L tickets under fanout were not run.
- Benchmark caveats (from the record): one run per cell; not blind to the author; tasks chosen from this repository's own closed tickets; solo has no independent verifier, so a wrong change that passes the hidden check would go undetected; the lean arm used a minimal chain driver and not the released lean lane, so its overhead is an upper bound; no size S or size L task; no Codex arm.
- Solo evidence from 0.20.5 is unchanged: one trial per arm on one machine, the Codex solo did not launch its own verifier, and the Codex conductor start path was not run.
- The lane cap and stagger defaults (4 lanes, 20 seconds) are choices. [[PENDING: add the recommended lane count the live run report gave, if it gave one]]
- [[PENDING: Codex lanes under fanout: say whether one Codex solo lane was run or record it as not run]]
- [[PENDING: carry over only the 0.20.5 limits that are still true at the fixed commit, for example `shellcheck` not installed, the `budget` live run at 85 percent not made, and the `conductor.md` stop-rule wording; drop any the limits lane fixed]]
- The parked tickets are not in this release: replan by delta (T-0200, T-0201, T-0213), the spec gate's second half (T-0211), the folder-layout migration (T-0205 to T-0208) and the board overview (T-0187).

## Checks run for the release

[[PENDING: run on the release branch after the merge and version bump, and list only what actually ran with its result]]

- `bash plugins/sdlc-lite/scripts/check.sh` (shellcheck skipped, not installed)
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- selftests: `messages.py`, `results.py`, `evals.py`, `proposals.py`, `supervisor.py`, `specgate.py`, `footprint.py`, `budget.py`, `board.py`, `fanout.py`
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py` and `codex-selftest.py`
- `git diff --check`
- Version parity: both SDLC Lite manifests read 0.20.6; both Progressive Context manifests read 0.1.2.

[[PENDING: the independent fact-check summary, written after the passes run]]
