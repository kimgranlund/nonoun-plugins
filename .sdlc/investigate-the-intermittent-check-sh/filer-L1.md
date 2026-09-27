<!-- role=filer level=L1 model=sonnet effort=medium -->
All steps passed: builder L2 done, verifier L1 pass with confirmed pre/post-fix repro. Single step task, no warnings.

## Warnings
None

## PR title
T-0133: Fix hook-selftest.sh's intermittent SIGPIPE/pipefail race

## PR body
Summary: `plugins/sdlc-lite/scripts/hook-selftest.sh` intermittently reported a hook fixture's exit code as 141 instead of the hook's real exit code (for example `block-pattern-kill without role: exit 141, want 0`), because its `run()` helper fed each hook its JSON payload through a pipe (`printf '%s' "$json" | env ... "$hook"`) under `set -uo pipefail`. When a hook exits before reading stdin (every early-exit path in `block-repo-format.sh`, `block-pattern-kill.sh`, and the role gate in the others), `printf`'s write can get SIGPIPE, and pipefail reports that 141 instead of the hook's own exit code. This is a test-harness artifact only: in production Claude Code writes the payload and a hook exiting without reading stdin is valid.

Changes:
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: `run()` now feeds the hook's stdin by process substitution (`< <(printf '%s' "$json")`) instead of a pipe, so the feeder is no longer a pipeline stage pipefail can misattribute. Kept the `3>&1 1>/dev/null 2>&3` fd juggling so `run()` still returns exactly the hook's exit code and captures its stderr, plus a comment explaining the race. Every existing fixture's expected exit code and stderr check is unchanged. Nothing under `plugins/sdlc-lite/hooks/` changed.

How verified: builder reproduced the race before the fix (a throwaway hook that exits 0 without reading stdin, fed a 200000-byte payload through the old pipe, 20/20 runs wrong under `set -uo pipefail`) and confirmed 0/20 wrong through the fixed helper. The verifier independently reproduced the same race on a pre-build worktree at the prior commit (10 consecutive runs of `hook-selftest.sh`, run 10 failed with the exact reported symptom: `block-stray-worktree without role: exit 141, want 0`), then ran 30 consecutive `hook-selftest.sh` invocations on the built tree, all passing. It also confirmed the negation grep for the vulnerable pipe pattern fails pre-fix and passes post-fix, that `shellcheck --severity=warning` and `hook-live-probe.sh --selftest` stay green both before and after (unaffected gates, as predicted since that script never sets `pipefail` around its own hook-feeding pipe), and that `git diff` shows no change under `plugins/sdlc-lite/hooks/` or to `hook-live-probe.sh`. Verdict: pass.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
Fixed an intermittent race in `hook-selftest.sh` where a hook exiting before reading stdin could report a SIGPIPE exit code (141) instead of its own, causing spurious `check.sh` failures.

## Follow-ups
None
