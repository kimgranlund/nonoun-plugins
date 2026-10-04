<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0193: footprint.py: measure and gate a ticket's footprint

## PR body
### Summary
Adds `plugins/sdlc-lite/scripts/footprint.py`. It measures a ticket folder's footprint and can fail a gate on it. It is the L1 build row of the lean SDLC design (`docs/lean-sdlc/design.md`). The script is stdlib only and read-only on ticket folders.

### Changes
- `plugins/sdlc-lite/scripts/footprint.py` (new, executable):
  - `footprint.py <ticket dir>` prints `ticket`, `files`, `bytes`, `md_bytes`, `steps`, `planner_bytes` and `role_runs`. It also prints one `role_runs <role> <level>: N` line per group.
  - Steps are `step-<n>` dirs only. Superseded dirs such as `step-2.superseded-1` are excluded.
  - `footprint.py check <ticket dir> [--max-files N] [--max-bytes N]` exits 1 and names each exceeded flag on stderr. It exits 2 for no limit, a missing dir, or bad args.
  - `footprint.py selftest` builds a fix-lane fixture and a chained fixture and asserts exact counts. It includes a negative control, an extra file that fails `check --max-files 8`. It also asserts that measuring writes nothing.
- `plugins/sdlc-lite/scripts/check.sh`: runs the `footprint.py` selftest after the `messages.py` selftest. The header comment's selftest list now names `footprint.py`.
- `docs/maintenance/sdlc-internals.md`: a new `scripts/footprint.py` entry after the `order.py` entry. It does not copy the Baseline table, which stays in `docs/lean-sdlc/design.md`.

Recorded output for the four closed folders, from the step 2 builder result. Columns are steps / role runs / files / bytes / `.md` bytes. The Baseline table in `docs/lean-sdlc/design.md` ("Baseline (measured 2026-10-03)") matches all four rows.

| Ticket | Steps | Role runs | Files | Bytes | `.md` bytes |
|---|---|---|---|---|---|
| T-0188 | 1 | 2 | 8 | 8010 | 4521 |
| T-0164 | 1 | 2 | 8 | 10050 | 6586 |
| T-0181 | 5 | 15 | 51 | 214502 | 185323 |
| T-0175 | 8 | 21 | 69 | 224330 | 187209 |

### Verification
Each step had an independent verifier, and both passed.
- Step 1 (verifier L1, pass):
  - The selftest passed with 11 `ok:` lines, including `ok: negative control: extra file fails check --max-files`.
  - Exact-value greps on the four closed folders matched.
  - `check --max-files 7` and `check --max-bytes 8009` on the T-0188 folder both exited 1 and named their flag. At the real values (8 files, 8010 bytes) `check` printed `ok`.
  - `check` with no limit and `check` on a missing dir both exited 2.
  - The four closed folders are unchanged against the base SHA.
  - The only file changed outside `.sdlc` was `footprint.py`.
- Step 2 (verifier L1, pass):
  - The `check.sh` and docs greps pass on the built tree. At the base SHA, in a throwaway worktree, the `check.sh` grep and both docs greps exit 1, so they can fail.
  - The scope predicate exits 1 when a stray file is added.
  - The verifier reran `footprint.py` on all four folders and the numbers match.
  - `bash plugins/sdlc-lite/scripts/check.sh` passed and printed `footprint selftest: PASS`.
  - `python3 scripts/check-packaging.py`, `codex_roles.py generate --check`, `tickets.py --root .sdlc check` and `git diff --check` all exited 0.
- shellcheck was not installed on this host, so `check.sh` skipped it. It does not cover the Python file.
- No model or effort defaults changed, and there is no version bump, tag, push or publish.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added `scripts/footprint.py`. It reports a ticket folder's files, bytes, `.md` bytes, steps, planner bytes and role runs by role and level. `check --max-files N --max-bytes N` exits 1 and names the exceeded limit. `check.sh` now runs its selftest.

## Follow-ups
- note: Step 2 builder did not run the three `grep -qF` criteria itself; the step 2 verifier ran them and they passed, so nothing is open.
- note: The planner run reported a stray worktree and branch `t0185` (`.worktrees/t0185`); clean it up if it is no longer needed.
- note: The exact-count criteria for the four closed dot folders go red if any of those folders is edited on main, for example by the T-0190 layout migration. Re-baseline them if that happens.
