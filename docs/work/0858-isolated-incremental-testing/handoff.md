---
id: T-0858
title: "check.sh --changed runs only the jobs a diff touches"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
During a ticket, one command runs only the check jobs that cover the files changed, in seconds to a few minutes, so nobody runs the 10-minute suite to test a small change.

## Intent
- Do: add a selector that maps changed paths to `check.sh` job names, and a `check.sh --changed [<base>]` mode that runs just those jobs.
- Non-goals: role instructions (T-0859); making the full suite faster (T-0860); release reruns (T-0861).
- Done when: the criteria below hold.

## Context
- User feedback 2026-11-19: "workflows for testing need to be improved and less sequential and slow. focus on isolated testing during incremental development work so that the project doesnt grind to a halt with excessive testing ceremony."
- `plugins/sdlc/scripts/check.sh` (100 lines) queues jobs with `job <fast|full> <name> <command...>` and runs them through `check_pool.py`. The full run takes about 600 s; most jobs are one script's selftest.
- Design: a new `plugins/sdlc/scripts/check_select.py` with `select <path>...` (prints job names) and a `selftest`. Rules, first match wins per path: `scripts/<name>.py` or `.sh` selects the job whose command runs that script, plus `check.py`; `agents/`, `adapters/` select the generated-definition and `check.py` jobs; `hooks/` selects the hook jobs; `skills/` and docs select `check.py` (and prompt or reply lint where they apply); a path outside `plugins/sdlc` and `docs` selects nothing; `check.sh`, `check_pool.py` or an unmapped `plugins/sdlc` path selects every job. Derive the script-to-job map from `check.sh` itself so a new job needs no second edit. A script imported by others (for example `roots.py`, `tickets.py`, `results.py`) also selects the jobs of scripts that import it; compute that from the `import` lines.
- `check.sh --changed [<base>]`: paths from `git diff --name-only <base>` plus untracked files, base default `HEAD`; prints the selected job names and `skipped: N jobs`, and exits 0 with `nothing to check` when none apply.
- Add a `check_select` job (fast) to `check.sh` and a line to the usage comment. Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `plugins/sdlc/AGENTS.md` first.
- T-0860 edits `check.sh` in parallel; keep your edits to the option parsing, one job line and the usage comment.

## Do
1. Write `check_select.py` with its selftest.
2. Add `--changed` to `check.sh`.
3. Document it in `plugins/sdlc/AGENTS.md` (validation section) and the CHANGELOG `[Unreleased]`.

## Acceptance criteria
- `python3 plugins/sdlc/scripts/check_select.py selftest` exits 0 with cases for: one leaf script, a shared module (selects its importers' jobs), a docs-only path, a path outside the plugin (nothing), `check.sh` itself (all), and an unmapped plugin path (all).
- After `touch`-style edits in a throwaway worktree: changing only `plugins/sdlc/scripts/wtroot.py` and running `bash plugins/sdlc/scripts/check.sh --changed` runs fewer than 6 jobs and exits 0; state the job names and wall time in the report.
- With no changes, `check.sh --changed` prints `nothing to check` and exits 0.
- `bash plugins/sdlc/scripts/check.sh --fast` exits 0 and `git diff --check` is clean.

## Constraints
- `check.sh` with no flag and with `--fast` keep their current job sets.
