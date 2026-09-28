<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0102: Builders format only changed files and never pkill by pattern

## PR body
## Summary
Builders could touch files and processes outside their own work. A repo-wide `prettier --write` dirtied generated files, and a pattern kill took down another session's `vite dev`. This change adds a PreToolUse hook that blocks pattern kills inside role runs. It also adds two builder rules and a check.py guard that keeps the rules in `agents/builder.md`.

## Changes
- New hook `plugins/sdlc-lite/hooks/block-pattern-kill.sh`, registered in `hooks/hooks.json` after block-background.sh.
  - With `SDLC_ROLE` unset it exits 0.
  - Inside a role run it exits 2 on `pkill` or `killall` in command position, and on `kill` fed by `pgrep` (`$(...)`, backticks, or `| xargs kill`).
  - The block message names the role and says to stop only the PIDs you started and never to kill by name pattern.
  - `kill <pid>`, `kill $pid`, `kill %1`, and quoted mentions pass.
  - On a heredoc, a shell or evaluator word, or a parse failure it fails closed and scans the raw text.
- `scripts/hook-selftest.sh` has a new `pk=` variable and fixtures. They cover the blocked forms with a role, the allowed forms with a role, and pkill allowed without a role.
- `agents/builder.md` has two new rules. Rule 6: formatters, `--fix` linters, and code generators run only on the files this step changed. Rule 7: stop only the PIDs you started, and never `pkill`, `killall`, or `kill $(pgrep ...)`.
- `scripts/check.py` has a builder scope guard that fails when `agents/builder.md` lacks either phrase. Its negative control reports `check.py: builder scope guard negative control not flagged`.
- `CLAUDE.md` gets a Layout bullet for the hook, and its check.sh line names the hook. `.claude/agents/sdlc-lite-author.md` gets the same check.sh mention plus a Hazards bullet. The `check.sh` header comment names the hook too.

## Verification
- Step 1, the hook (verifier L2): pass.
  - The five block cases (pkill, killall, `kill $(pgrep ...)`, `pgrep | xargs kill`, `cd x && sudo pkill`) exit 2.
  - The block stderr names PID.
  - `kill 12345`, `grep -n "pkill" f`, and pkill without a role exit 0.
  - The hook is executable and registered under the Bash matcher.
  - `hook-selftest.sh` prints `hook selftest: PASS`.
  - shellcheck at warning severity is clean, and `check.sh` exits 0.
  - Bite check: with the hook replaced by `exit 0`, the selftest printed `FAIL: block-pattern-kill blocks pkill: exit 0, want 2`.
  - The registered hook also denied two of the verifier's own commands (a shell word or heredoc plus the kill word), which is the documented fail-closed path.
- Step 2, the rules, guard, and docs (verifier L1): pass.
  - All seven `grep -q` criteria pass.
  - `check.py` prints `ok: 18 role levels, 8 agents checked`, and `check.sh` exits 0.
  - Bite check: in a copy of the built tree with `PIDs you started` removed from builder.md, check.py exited 1 with `FAIL agents/builder.md: builder scope rule missing "PIDs you started"`.
- Nothing is committed.

## Changelog entry
- Added `hooks/block-pattern-kill.sh`, a PreToolUse(Bash) hook that blocks `pkill`, `killall`, and `kill` fed by `pgrep` inside role runs. Builder rules 6 and 7 now require formatters to run only on the files the step changed and kills to target only PIDs the builder started. `check.py` guards both rules.

## Follow-ups
- Pattern-kill hook misses forms it does not match: `ps aux | grep x | awk ... | xargs kill` and a kill word held in a variable (`p=pkill; $p x`) pass inside role runs.
- Formatter rule is prompt-only: check.py proves only that the phrase is in builder.md, so a builder can still run a repo-wide formatter through a project script such as `npm run format`.
