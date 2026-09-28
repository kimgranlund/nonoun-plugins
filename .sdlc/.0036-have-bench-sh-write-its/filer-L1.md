<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0036: bench.sh writes exit code and wall-clock duration to each task log

## PR body
### Summary
Each bench task's log (`<bench>/logs/<date>-<task>.txt`) now ends with a line in the form `exit=<code> duration=<N>s`. A clean-context verifier can check the exit code and run time from the log alone. Before this change, both values went only to stdout. Follow-up from T-0032.

### Changes
- `plugins/sdlc-lite/scripts/bench.sh`:
  - Computes the log path once per task, before the run. A run that crosses midnight now appends to the same file.
  - Records the start time with `$SECONDS` and captures `rc=$?` right after the claude call.
  - Appends `exit=<rc> duration=<N>s` to the log and prints the same line to stdout. This replaces the old `echo "exit=$?"`.
  - Adds one header comment line describing the new last line of the log.
- `set -uo pipefail`, the CLI (`--bench-dir`, task args) and the `bench-summary.sh` call are unchanged.
- No docs changed. No line in CLAUDE.md, `skills/bench/SKILL.md` or `sdlc-lite-author.md` describes what the log contains.

### Verification
The verifier ran at L1 and passed every criterion:
- **Stub `claude` exiting 3:** the last log line was `exit=3 duration=0s` and stdout showed the same line. Run against HEAD in a throwaway worktree, the same check fails: the log has no trailer and stdout shows only `exit=3`. So the check really tests the change.
- **Stub that sleeps 2 seconds, then exits 0:** the last log line and the stdout line were both `exit=0 duration=3s`. The nonzero duration shows the time is measured, not a constant.
- **Path computed once:** `grep 'date +%Y-%m-%d'` matches once (bench.sh:23), and the redirect uses `>"$log"`. HEAD also had exactly one match, so the verifier did not rely on the count. The evidence is the variable plus the redirect.
- **`check.sh`:** exit code 0. The role-level check, selftests, shellcheck and plugin validate all passed. As a negative control, shellcheck failed on a copy of bench.sh with a deliberately planted error.
- **Scope:** the diff touches only the loop body and the header comment.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `bench.sh` now appends `exit=<code> duration=<N>s` to each task's log and prints the same line to stdout. The log path is computed once per task, so a run that crosses midnight stays in one file. (T-0036)

## Follow-ups
None
