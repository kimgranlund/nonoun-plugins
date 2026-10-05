# Release 0.20.6

Recorded: 2026-10-05. SDLC Lite 0.20.6. Progressive Context stays at 0.1.2 (no change since 0.19.0). Previous release: SDLC Lite 0.20.5 (244d0af, tag `v0.20.5`). Built from main commit 01559a6; the release branch merges that commit and adds the version bump and this record, and the release commit is the one tagged `v0.20.6`.

## What changed for consumers

This release makes `fanout` follow the same solo-first rule as the conductor, closes three small limits the 0.20.5 record listed, and adds the benchmark record behind the default. Fanout is the only change that alters what a command does: a run that used to send every ticket through the full chain now starts `solo` for size S and M. The guard renumbering and the skips guard change affect maintainers and `tickets.py check`. The benchmark and live-run records are evidence only.

| Change | Detail | Ticket |
| --- | --- | --- |
| Fanout solo first | `scripts/fanout.py` runs `steps.py lane <task dir>` in each lane worktree after the lane syncs and follows it, recording the lane line in the task's `skips.md` (committed with the lane). Lane `solo` (size S and M by default) starts `agents/solo.md` as a headless session at the tier's model and effort: Claude `SDLC_ROLE=solo claude -p --agent sdlc-lite:solo`, Codex `codex_exec.py solo L1\|L2\|L3`. For tier M or L a new task-dir verifier result with Verdict pass is required before the merge, from the solo itself or else one `run.sh verifier L3 <task dir>/handoff.md` that fanout runs once (outcomes `verifier fail` and `no verifier result`). A solo ticket closes with `tickets.py close --reason`, since it has no filer file. Lane `full` (and `lean`) keep the headless conductor running `/sdlc-lite:chain`. New flags: `--lane auto\|solo\|full`, `--max-lanes N` (default 4; above 16 it also needs `--yes-many`), `--stagger SECS` (default 20), `--allow-overlap`. The plan and the run report print each ticket's lane, and preflight refuses two tickets in different lanes whose planned scope overlaps unless `--allow-overlap`. `check.py` guard 24 ties the fanout tiers to the tiers in `agents/solo.md`. `skills/fanout/SKILL.md` and `docs/maintenance/sdlc-internals.md` describe it | T-0221 |
| Unique guard numbers | `scripts/check.py`'s docstring numbered two guards 17 and two guards 18 and cited items that did not match. The guards now run 1 to 23 once each (spec gate 16, carry forward 17, solo agent 18, conductor rules 19, handoff freeze 20, solo start path 21, ticket budget 22), every `docstring item N` comment names the right guard, and the new guard 23 fails when a number repeats or skips or a comment cites a missing item (two negative controls inside `check.py`). Fanout adds guard 24 after it. `docs/maintenance/sdlc-internals.md` now says the solo agent guard is item 18. Dated validation records keep the old numbers | T-0218 |
| Skips guard covers solo and full | The `tickets.py` skips guard (T-0198) covered only tickets whose last recorded lane was `lean` or `fix`. `skip_missing` now checks lanes `solo`, `lean`, `fix` and `full`. A solo ticket has no steps, so it needs `## Skipped` entries for the planner and the filer; a full ticket needs the planner, per-step verifier and filer results (or entries). A ticket with no `skips.md` or no lane record stays exempt, and open tickets are not checked. Four new selftest cases; the old lean-then-full case now uses full-chain results on purpose. `tickets.py` docs and `skills/handoff-format/SKILL.md` are updated. The guard does not require the batched verifier record of a solo M or L ticket, because that record lives outside the ticket folder | T-0219 |
| T-0212 re-verified | The T-0212 fix (`scripts/check-packaging.py` no longer pins the PreToolUse route count at 3: it asserts four routes and the `Edit\|Write\|NotebookEdit` matcher) was made after the step's L3 verifier returned `fail` and had no committed re-verification. A narrow L2 verifier passed it (`.sdlc/verify-0220/step-1/verifier-L2.md`), including an unregister control in a throwaway worktree where `check-packaging.py` and `check.py` each went red. No code changed in this ticket, and the Codex note in `docs/maintenance/claude-hooks.md` already existed | T-0220 |
| Solo vs lean benchmark record | `docs/validation/solo-vs-lean-benchmark-2026-10-04.md` with raw evidence in `docs/validation/solo-vs-lean-benchmark-2026-10-04/`. It is evidence only and changes no behavior. On three real tickets from this repository all six cells passed the hidden check and `check.sh`. The solo arm cost $2.66 in 18 minutes in total with no replans; the lean arm cost $26.83 in 120 minutes with 2 replans. See Known limits | none |
| Fanout live run record | `docs/validation/fanout-solo-live-run.md` with raw evidence in `docs/validation/fanout-solo-live-run/`: four lanes (three size S, one size M) through real solo sessions, merged by the script. See Known limits for what it does and does not show | T-0221 |

T-0221 was built as one handwritten step on branch `fanout-solo`. T-0218, T-0219 and T-0220 were built as handwritten steps on branch `limits`. Each of T-0218 to T-0220 was checked by an L2 verifier whose result is committed (`.sdlc/verify-0218`, `.sdlc/verify-0219`, `.sdlc/verify-0220`, all `pass`); T-0218's first L2 pass returned `fail` (a stale item number in `sdlc-internals.md` and two vacuous negative-control criteria), both were fixed and a second pass passed, and the first pass is recorded in `.sdlc/verify-0218/first-pass-note.md`.

T-0221's verification has a gap, stated plainly: its first L3 branch verifier returned `fail` on one of its eight criteria because the live-run evidence was not committed. A narrow L3 re-verify (`.sdlc/verify-0221-7/verifier-L3.md`) returned `fail` once more, because three evidence files matched the `*.log` ignore pattern and a token range in the record disagreed with the transcript summary. Those fixes (the files renamed so they are tracked, the range corrected to 743 to 6,044) were confirmed with `git ls-tree` and `git check-ignore`, and no third verifier was run. The committed verifier result is the failing one, so no passing whole-branch verifier exists for T-0221. The selftest, `check.sh` and the live run pass.

## Upgrade notes

- Behavior change in `/sdlc-lite:fanout`: lanes for size S and M tickets now start `solo` instead of a conductor running the full chain. Pass `--lane full` to restore the chain for a run. There is no setting that restores the old default for every run.
- Lane count and pacing: a run holds at most 4 lanes and starts them 20 seconds apart. Raise the cap with `--max-lanes N` (above 16 also needs `--yes-many`) and change the pacing with `--stagger SECS`. These defaults were chosen, not measured. The real limits are the plan's rate limit and merge conflicts on shared files, not the machine.
- A size M or L solo ticket needs a passing batched verifier result before its fanout merge; fanout runs one verifier if the solo did not.
- Two tickets in different lanes whose planned scope overlaps are refused at preflight unless `--allow-overlap`.
- Codex: no generated Codex agent changed between `v0.20.5` and this release, so `codex_roles.py install` is not needed for this release.
- `check.py` guard numbers changed (see the table). Anything outside this repository that cites a guard by number needs the new number.
- `tickets.py check` can now fail a done ticket whose skips record names lane `solo` or `full` and lacks the required result or `## Skipped` entry. A ticket with no `skips.md` or no lane record is unaffected.
- No migration is needed and `tickets.py roadmap` is unchanged.

## Known limits

- How far the evidence supports "solo-first is the default for fanout": the benchmark (n=3, one run per cell) shows a solo session matched the chain on pass rate at about a tenth of the cost and a sixth of the time on three small tickets from this repository, and the fanout live run shows four disjoint tiny tickets going through four solo lanes and merging. Together that supports the default for small, disjoint tickets on Claude Code and no further.
- Fanout live run (T-0221): one run of four tiny tickets (three size S, one size M) on one machine, 5 minutes 43 seconds end to end, hidden check 24 of 24. The lanes started 3 seconds apart because the run set `--stagger 3`, a test setting, so the 20 second default was not exercised live. The solo sessions ran on `claude-sonnet-5-5` and the size M ticket's independent verifier on `claude-fable-5-1` (a different family). The $3.13 in the record is the verifier only: the solo sessions' own cost was not captured, so the run has no total cost. No more than four lanes were tried and the tickets were disjoint by construction, so merge-time overlap handling, a lane count above four and a size L ticket were not run live (the selftest covers the overlap refusal and the cap). The full-chain branch was exercised only by the selftest. The record's recommended lane count for the plan is 4, to be raised only after watching limit use and merge conflicts.
- No Codex lane was run under fanout: `codex_exec.py solo` is built and selftested, not exercised live.
- Verification gap on T-0221 (above): no passing whole-branch verifier.
- Benchmark caveats (from the record): one run per cell; not blind to the author; tasks chosen from this repository's own closed tickets; solo has no independent verifier, so a wrong change that passes the hidden check would go undetected; the lean arm used a minimal chain driver and not the released lean lane, so its overhead is an upper bound; no size S or size L task; no Codex arm.
- Solo evidence from 0.20.5 is unchanged: one trial per arm on one machine, the Codex solo did not launch its own verifier, and the Codex conductor start path was not run.
- The plugin under test in the fanout live run was the `fanout-solo` worktree (0.20.5 manifests), and its `check.py` guard number was renumbered when main was merged in.
- Still true from the 0.20.5 record: `shellcheck` is not installed, so `run.sh` and `run-selftest.sh` are not shellchecked; the budget stop at 80 percent is exercised only by selftests with a stub `claude`; and spend counts Claude `run.sh` roles only.
- The parked tickets are not in this release: replan by delta (T-0200, T-0201, T-0213), the spec gate's second half (T-0211), the folder-layout migration (T-0205 to T-0208) and the board overview (T-0187).

## Checks run for the release

Run from the release worktree on branch `release-0.20.6` (main's 01559a6 merged in, plus the version bump and this record), 2026-10-05, all exit 0:

- `bash plugins/sdlc-lite/scripts/check.sh` (shellcheck skipped, not installed)
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` (221 tickets, roadmap current)
- `python3 plugins/sdlc-lite/scripts/messages.py selftest`, `results.py selftest`, `evals.py selftest`, `proposals.py selftest`, `supervisor.py selftest`, `specgate.py selftest`, `footprint.py selftest`, `budget.py selftest`, `board.py selftest`, `fanout.py selftest`
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- `git diff --check`
- Version parity: both SDLC Lite manifests read 0.20.6; both Progressive Context manifests read 0.1.2.

FACTCHECK_PLACEHOLDER
