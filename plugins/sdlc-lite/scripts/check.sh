#!/usr/bin/env bash
# Plugin checks: level-table and agent consistency, the coverage_check, tickets.py, board.py,
# steps.py, order.py, fanout.py, and onboard.py selftests (fanout: throwaway repos and a stub driver, no model
# call), the run.sh selftest (result numbering, stream-json result pick, Bash timeout env; stub claude, no model call), the hook selftest
# (block-background.sh with Bash, Agent, and Monitor fixtures, block-publish.sh, block-pattern-kill.sh, block-stray-worktree.sh, block-repo-format.sh, and block-disk-scan.sh on fixture JSON), the
# hook live probe selftest
# (hook-live-probe.sh --selftest: offline, a stub claude; the live probe spends a model call and
# never runs here), a shellcheck pass, plugin manifest validation.
set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
python3 "$root/scripts/codex_roles.py" generate --check || fail=1
python3 "$root/scripts/codex-selftest.py" || fail=1
python3 "$root/scripts/lifecycle-selftest.py" || fail=1
python3 "$root/scripts/check.py" "$root" || fail=1
python3 "$root/skills/decompose/scripts/coverage_check.py" selftest || fail=1
python3 "$root/scripts/tickets.py" selftest || fail=1
python3 "$root/scripts/board.py" selftest || fail=1
python3 "$root/scripts/steps.py" selftest || fail=1
python3 "$root/scripts/order.py" selftest || fail=1
python3 "$root/scripts/fanout.py" selftest || fail=1
python3 "$root/scripts/onboard.py" selftest || fail=1
bash "$root/scripts/run-selftest.sh" || fail=1
bash "$root/scripts/hook-selftest.sh" || fail=1
bash "$root/scripts/hook-live-probe.sh" --selftest || fail=1
if command -v shellcheck >/dev/null; then
  shellcheck --severity=warning "$root"/scripts/*.sh "$root"/hooks/*.sh && echo "ok: shellcheck" || fail=1
else
  echo "skip: shellcheck not installed"
fi
if claude plugin validate "$root" >/dev/null 2>&1; then echo "ok: plugin validate"; else echo "FAIL: claude plugin validate"; fail=1; fi
exit $fail
