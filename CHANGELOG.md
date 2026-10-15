# Changelog

SDLC Lite releases, newest first, in [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) form. Each entry is built from the `T-NNNN:` commit subjects since the previous tag (`git log --format=%s <last tag>..HEAD`); the dated release report in `docs/reports/` holds the upgrade notes and the verification record. Releases before 0.23.0 are recorded only in those reports. Progressive Context is versioned separately.

## [0.23.1] - 2026-10-15

Report: [docs/reports/2026-10-15-release-0-23-1.md](docs/reports/2026-10-15-release-0-23-1.md).

### Fixed

- Bare-clone repos (lanes beside a bare git dir, as in gen-ui-kit): the worktree root is `<bare parent>/lanes`, or a `worktree_root:` line in `.sdlc/config`, for `wtroot.py`, `lanes.py`, `fanout.py`, the tmp reaper and both role hooks, so nothing nests inside a lane; `migrate-0.23.sh` prints the root and "nothing to move" there (T-0561).
- Role sub-agents can no longer run Bash in the background or use Monitor, so they cannot go idle waiting for a notification that never reaches them; the main session and the conductor are unaffected (T-0562).
- A fanout close writes the real `base:` and `Commits:` into `## Outcome` for solo lanes, from the solo dispatch's `base_sha` (T-0559).
- `tickets.py close` moves `skips.md` into the records dir, so a closed ticket tracks only `handoff.md` (T-0560).
- `dispatch.py selftest` uses a private `TMPDIR`, so another run's scratch under `$TMPDIR/sdlc-lite/` cannot fail it (T-0558).
- Release CI uses actions/checkout and setup-node v7 (Node 24) and pins `ubuntu-24.04`.

## [0.23.0] - 2026-10-14

Report: [docs/reports/2026-10-14-release-0-23-0.md](docs/reports/2026-10-14-release-0-23-0.md).

### Added

- Records dir: role results, step dirs, attempts, dispatch files, `runs.jsonl`, `base-sha`, `red-checkpoint.jsonl` and `budget-ack.md` go to `.sdlc/runtime/tasks/<folder>/`, local and ignored; `order.py records-dir <task dir>` prints it (T-0540).
- `tickets.py close` appends a `## Outcome` (lane, verdict, verifier, base, changed, commits, checks, deviations, follow-ups) and gates on the newest verifier verdict; `--changed "<line>"` fills the changed line (T-0543).
- `tickets.py tidy [--apply]` moves loose top-level `.sdlc/` entries into `archive/`; `check` warns on them; `top_level_allow:` and `citation_skip:` config lines (T-0544, T-0535).
- `tickets.py claim <id> --by <agent>` and `release <id>`, with claim lint (T-0526); a `successor:` field, for which `check` prints the ready `close --reason` line once the successor is done (T-0528).
- `branch:` and `worktree:` ticket fields, written by `lanes.py open` and `tickets.py branch`, removed by `lanes.py close`; `lanes.py list --all` shows the newest verdict of verified, unmerged work (T-0530, T-0550).
- `scripts/migrate-0.23.sh`: a per-repo dry run, then `--apply`, that moves `.worktrees/` lanes to `.claude/worktrees/` and runs `tickets.py tidy` (T-0550).
- Hard gates: a third planner run on a ticket, and a plan with more steps than its level allows (L1 and L2 3, L3 6, L4 10, L5 15), stop until `--approved "<who: why>"` (T-0553).
- Wall-clock budgets per role level and per ticket in `dispatch.py`: `status` and `recover` flag a role past its budget, and `prepare` refuses the next role on a ticket past its budget until `--approved` (T-0555).
- `/sdlc-lite:fleet-doctor`: why runs are slow or stuck, with ranked resolutions carried out only on a yes (T-0552).
- `dispatch.py resume --limit <name>` for a sub-agent stopped by a spend or session limit; `prepare` prints a line when a role's model or effort changed since the last attempt (T-0537).
- Builder amend route: `steps.py amend` changes one criterion of an unbuilt step after a builder-reported plan defect; lint catches a criterion that needs a later step (T-0536).
- `check.sh --fast`, a quick tier for builders and CI; the full suite runs its selftests in parallel (T-0557).
- Release-only CI: `.github/workflows/release-check.yml` runs the fast tier and the packaging check on `v*` tags and manual dispatch only (T-0554).
- Writing rules for the handoff and its Outcome: `skills/handoff-format/references/writing-rules.md` (T-0529, T-0545).

### Changed

- A closed ticket's committed record is its `handoff.md` with the Outcome. The filer runs only when asked (`/file`, `close --filer`); `## Closed` is no longer written. Fanout carries records between worktrees by copy, and its close commit keeps only `handoff.md` in the closed folder (T-0539, T-0541, T-0542, T-0543).
- Cost, board, fleet, traces and budget readers read the records dir, and still read legacy in-folder records (T-0541).
- Every worktree lives under `<main checkout>/.claude/worktrees/`, role scratch under `$TMPDIR/sdlc-lite/`, each with an `.owner.json`; `lanes.py sweep` removes a dead owner's folder (T-0550).
- Builders run their step's own checks and the narrow suites they touch, not the full `check.sh` when a land gate runs it (T-0551).
- Heavy checks a role runs inside its lane go through `gate_lock.py` (T-0556).
- Role guidance: run each check as a plain command, never a built string through `bash -c`, `sh -c` or `eval` (T-0549); the solo brief needs the `Tree:` line and leaves the verifier to the parent (T-0550).
- A role's result header is added at record time, and cleanup under the role's tmp prefix is allowed (T-0538).
- Run records: a retry is named `-2` like the host names it, a filer with follow-ups is pruned, and an empty solo result is a failed run (T-0531).
- `prices.json` recalibrated for the model rows changed in 0.22.7 (T-0521).
- Live host check of the new model rows: `effort:` in agent front matter applies to sub-agent spawns and is ignored for a session agent (`--agent`), so the conductor and messenger `effort:` lines have no effect there (T-0522).

### Fixed

- The build base is taken from the tree the role builds in, also for `solo_run --cwd` and resumed lanes (T-0546).
- A role's Bash call that reads stdin no longer hangs the run: a hook closes stdin for role calls (T-0548).
- `check.sh` stays green inside a role run with in-flight attempt records under `.sdlc/runtime/tasks/` (T-0547).
- `steps.py split` lints each step alone, so a path an earlier step creates (`[creates: ...]`) is no plan defect (T-0533).
- Step tooling for long suites, close references and router links, the launcher and its root guard (T-0532, T-0527).

### Removed

- Side files in task folders: `process-deviations.md` (deviations are audit rows and Outcome lines), `refusals.jsonl` (a `## Plan review` line), and per-ticket dated reports (T-0543, T-0545).
